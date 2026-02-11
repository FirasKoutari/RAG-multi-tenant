from __future__ import annotations

import os
import time
from datetime import datetime
from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .tenants import resolve_tenant
from .search import MultiTenantSearch, build_llm_answer
from .database import get_db, init_db
from .models import QueryLog, APIKeyUsage

# 🔒 SÉCURITÉ MULTI-TENANT: Architecture d'isolation stricte
# ----------------------------------------------------------------
# Chaque tenant (client) a:
# 1. Son propre répertoire de documents: data/tenantA/, data/tenantB/
# 2. Son propre index TF-IDF (vectorizer + matrice entièrement séparés)
# 3. Son propre espace mémoire (pas de vocabulaire partagé)
#
# ✅ Zéro fuite garanti: TenantA ne peut physiquement pas accéder aux docs de TenantB
# ----------------------------------------------------------------

APP_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(APP_DIR, "data")  # backend/data/<tenant_id>/*.txt

search_engine = MultiTenantSearch(base_dir=DATA_DIR)
# Preload the two tenants (optional, but nice for faster first request)
search_engine.load_tenant("tenantA")
search_engine.load_tenant("tenantB")

app = FastAPI(title="Multi-tenant SaaS Search API", version="2.0.0")

# Événement de démarrage: initialiser la base de données
@app.on_event("startup")
async def startup_event():
    """Initialise la base de données au démarrage de l'application."""
    init_db()
    print("✅ Application démarrée avec BDD SQLite et LLM Ollama")

# For Streamlit local dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    # 🔒 SÉCURITÉ CRITIQUE: Le tenant_id n'est JAMAIS dans le body
    # La séparation des clients doit être transparente pour l'utilisateur
    # et gérée uniquement côté serveur via le header X-API-KEY
    question: str = Field(..., min_length=1, max_length=2000)

class Source(BaseModel):
    doc_id: str
    chunk_id: int
    score: float
    excerpt: str

class QueryResponse(BaseModel):
    tenant_id: str
    answer: str | None
    sources: list[Source]
    no_answer: bool
    llm_used: bool = False  # Indique si le LLM a été utilisé

def get_tenant_or_401(x_api_key: str | None) -> str:
    """Résout l'identité du tenant via X-API-KEY.
    
    🔒 SÉCURITÉ: Point d'entrée critique de l'isolation multi-tenant.
    Si la clé est invalide/manquante → 401 (pas d'accès).
    
    Cette fonction est appelée sur CHAQUE requête pour garantir que
    le backend ne traite que les données du tenant authentifié.
    """
    tenant = resolve_tenant(x_api_key)
    if tenant is None:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-KEY")
    return tenant.id

@app.get("/health")
def health():
    """Endpoint de santé avec informations sur les services."""
    from .services.llm import llm_service
    
    return {
        "status": "ok",
        "database": "sqlite",
        "llm": {
            "available": llm_service.is_available(),
            "model": llm_service.model
        }
    }

@app.get("/stats/{tenant_id}")
def get_tenant_stats(
    tenant_id: str,
    x_api_key: str | None = Header(default=None, alias="X-API-KEY"),
    db: Session = Depends(get_db)
):
    """Récupère les statistiques d'utilisation d'un tenant.
    
    Nécessite une authentification via X-API-KEY du tenant concerné.
    """
    # Vérifier que l'API key correspond au tenant demandé
    authenticated_tenant = get_tenant_or_401(x_api_key)
    if authenticated_tenant != tenant_id:
        raise HTTPException(status_code=403, detail="Access denied to this tenant's stats")
    
    # Récupérer les statistiques
    total_queries = db.query(QueryLog).filter(QueryLog.tenant_id == tenant_id).count()
    llm_queries = db.query(QueryLog).filter(
        QueryLog.tenant_id == tenant_id,
        QueryLog.query_metadata.contains('"llm_used": true')
    ).count()
    no_answer_queries = db.query(QueryLog).filter(
        QueryLog.tenant_id == tenant_id,
        QueryLog.no_answer == True
    ).count()
    
    # Récupérer les dernières requêtes
    recent_queries = db.query(QueryLog).filter(
        QueryLog.tenant_id == tenant_id
    ).order_by(QueryLog.created_at.desc()).limit(10).all()
    
    return {
        "tenant_id": tenant_id,
        "total_queries": total_queries,
        "llm_queries": llm_queries,
        "extractive_queries": total_queries - llm_queries,
        "no_answer_queries": no_answer_queries,
        "recent_queries": [
            {
                "id": q.id,
                "question": q.question[:100],  # Tronquer pour sécurité
                "no_answer": q.no_answer,
                "sources_count": q.sources_count,
                "execution_time_ms": q.execution_time_ms,
                "created_at": q.created_at.isoformat()
            }
            for q in recent_queries
        ]
    }

@app.post("/query", response_model=QueryResponse)
def query(
    req: QueryRequest, 
    x_api_key: str | None = Header(default=None, alias="X-API-KEY"),
    db: Session = Depends(get_db)
):
    """Endpoint de recherche multi-tenant sécurisé avec LLM et logging BDD.
    
    🔒 FLUX DE SÉCURITÉ:
    1. Résolution du tenant via X-API-KEY (401 si invalide)
    2. Récupération de l'index isolé du tenant
    3. Recherche UNIQUEMENT dans les documents de CE tenant
    4. Génération de réponse avec LLM (Ollama + Mistral)
    5. Logging de la requête dans la base de données
    6. Retour avec sources traçables (doc_id, chunk_id, score)
    
    ✅ Garantie zéro fuite: Impossible d'accéder aux docs d'un autre tenant
    ✅ Anti-hallucination: Prompt strict + seuil MIN_SCORE
    🤖 IA générative: LLM local Ollama/Mistral pour réponses naturelles
    📊 Traçabilité: Toutes les requêtes loggées en base
    """
    start_time = time.time()
    
    # 🔑 Étape 1: Authentification et résolution du tenant
    tenant_id = get_tenant_or_401(x_api_key)
    
    # 📊 Mise à jour des statistiques d'utilisation de l'API Key
    api_usage = db.query(APIKeyUsage).filter(
        APIKeyUsage.tenant_id == tenant_id,
        APIKeyUsage.api_key == x_api_key
    ).first()
    
    if api_usage:
        api_usage.request_count += 1
        api_usage.last_used_at = datetime.now()
    else:
        api_usage = APIKeyUsage(
            tenant_id=tenant_id,
            api_key=x_api_key,
            request_count=1,
            last_used_at=datetime.now()
        )
        db.add(api_usage)
    
    db.commit()

    # 📚 Étape 2: Chargement de l'index isolé du tenant
    idx = search_engine.get(tenant_id)
    hits = idx.search(req.question, top_k=3)

    # 🛡️ Étape 3: Filtrage anti-hallucination (seuil de confiance)
    MIN_SCORE = 0.12
    hits = [h for h in hits if h.score >= MIN_SCORE]

    if not hits:
        # Pas de résultats pertinents
        execution_time_ms = (time.time() - start_time) * 1000
        
        # Logging dans la base de données
        query_log = QueryLog(
            tenant_id=tenant_id,
            question=req.question,
            answer=None,
            no_answer=True,
            sources_count=0,
            execution_time_ms=execution_time_ms,
            query_metadata={"min_score": MIN_SCORE}
        )
        db.add(query_log)
        db.commit()
        
        return QueryResponse(
            tenant_id=tenant_id,
            answer=None,
            sources=[],
            no_answer=True,
            llm_used=False,
        )

    # 🤖 Étape 4: Génération de réponse avec LLM (Ollama + Mistral)
    answer, llm_used = build_llm_answer(hits, req.question)
    
    # 📊 Étape 5: Préparation des sources
    sources = [
        Source(
            doc_id=h.chunk.doc_id,
            chunk_id=h.chunk.chunk_id,
            score=round(h.score, 4),
            excerpt=h.chunk.text,
        )
        for h in hits
    ]
    
    # Calcul du temps d'exécution
    execution_time_ms = (time.time() - start_time) * 1000
    
    # 💾 Étape 6: Logging dans la base de données
    query_log = QueryLog(
        tenant_id=tenant_id,
        question=req.question,
        answer=answer,
        no_answer=False,
        sources_count=len(sources),
        execution_time_ms=execution_time_ms,
        query_metadata={
            "llm_used": llm_used,
            "min_score": MIN_SCORE,
            "sources": [
                {
                    "doc_id": s.doc_id,
                    "chunk_id": s.chunk_id,
                    "score": s.score
                }
                for s in sources
            ]
        }
    )
    db.add(query_log)
    db.commit()
    
    return QueryResponse(
        tenant_id=tenant_id,
        answer=answer,
        sources=sources,
        no_answer=False,
        llm_used=llm_used,
    )
