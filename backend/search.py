from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterable

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

@dataclass(frozen=True)
class Chunk:
    tenant_id: str
    doc_id: str
    chunk_id: int
    text: str
    embedding: np.ndarray | None = None  # Embedding pour recherche sémantique

@dataclass
class SearchHit:
    chunk: Chunk
    score: float

def _read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def _chunk_text(text: str, chunk_size: int = 420, overlap: int = 80) -> list[str]:
    """Simple character-based chunking with overlap (good enough for the test)."""
    text = " ".join(text.split())  # normalize whitespace
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = max(0, end - overlap)
    return chunks

class TenantIndex:
    """Index de recherche isolé par tenant (isolation complète).
    
     ARCHITECTURE D'ISOLATION:
    - Chaque tenant a son propre TF-IDF vectorizer
    - Le vocabulaire est construit UNIQUEMENT sur les docs du tenant
    - La matrice TF-IDF est stockée en mémoire séparée
    - Aucun partage de données entre tenants
    
     RECHERCHE SÉMANTIQUE (Ollama + Mistral):
    - Génération d'embeddings pour chaque chunk
    - Recherche par similarité cosinus (sémantique)
    - Fallback sur TF-IDF si Ollama indisponible
    
     Garantie: Un tenant ne peut physiquement pas accéder aux
       embeddings/tokens d'un autre tenant car ils sont dans des
       espaces vectoriels complètement distincts.
    """

    def __init__(self, tenant_id: str, tenant_dir: str, use_embeddings: bool = True):
        self.tenant_id = tenant_id
        self.tenant_dir = tenant_dir
        self.use_embeddings = use_embeddings
        self.chunks: list[Chunk] = []
        self.vectorizer: TfidfVectorizer | None = None
        self.matrix = None  # sparse (TF-IDF) ou None si embeddings
        self._build()

    def _build(self) -> None:
        if not os.path.isdir(self.tenant_dir):
            raise FileNotFoundError(f"Missing tenant directory: {self.tenant_dir}")

        chunk_texts: list[str] = []
        
        # 📚 Lecture et chunking des documents
        for filename in sorted(os.listdir(self.tenant_dir)):
            if not filename.lower().endswith(".txt"):
                continue
            path = os.path.join(self.tenant_dir, filename)
            raw = _read_text(path)
            parts = _chunk_text(raw)
            for i, part in enumerate(parts):
                ch = Chunk(
                    tenant_id=self.tenant_id,
                    doc_id=filename,
                    chunk_id=i,
                    text=part,
                    embedding=None  # Sera généré à la demande
                )
                self.chunks.append(ch)
                chunk_texts.append(part)

        # Si tenant has no docs, keep index empty
        if not chunk_texts:
            self.vectorizer = TfidfVectorizer()
            self.matrix = None
            return

        
        if self.use_embeddings:
            try:
                from .services.embeddings import embeddings_service
                
                if embeddings_service.is_available():
                    print(f"🤖 Génération embeddings pour {self.tenant_id}...")
                    embeddings = embeddings_service.embed_batch(chunk_texts)
                    
                    # Mettre à jour les chunks avec leurs embeddings
                    for i, (chunk, embedding) in enumerate(zip(self.chunks, embeddings)):
                        if embedding is not None:
                            # Recréer le chunk avec l'embedding (dataclass frozen)
                            self.chunks[i] = Chunk(
                                tenant_id=chunk.tenant_id,
                                doc_id=chunk.doc_id,
                                chunk_id=chunk.chunk_id,
                                text=chunk.text,
                                embedding=embedding
                            )
                    
                    print(f"✅ {len([e for e in embeddings if e is not None])}/{len(embeddings)} embeddings générés")
                    return  # Pas besoin de TF-IDF si embeddings OK
                else:
                    print(f"⚠️ Ollama indisponible, fallback sur TF-IDF pour {self.tenant_id}")
            except Exception as e:
                print(f"⚠️ Erreur embeddings pour {self.tenant_id}: {e}, fallback sur TF-IDF")
        
        # 📊 Fallback: TF-IDF si embeddings désactivés ou indisponibles
        self.vectorizer = TfidfVectorizer(
            stop_words=None,
            lowercase=True,
            ngram_range=(1, 2),
            min_df=1,
            norm="l2",
        )
        self.matrix = self.vectorizer.fit_transform(chunk_texts)

    def search(self, query: str, top_k: int = 3) -> list[SearchHit]:
        """Recherche avec embeddings sémantiques (ou TF-IDF en fallback).
        
        🤖 MODE EMBEDDINGS (préféré):
        - Génère l'embedding de la query avec Mistral
        - Compare avec tous les chunks via similarité cosinus
        - Retourne les top_k plus similaires
        
        📊 MODE TF-IDF (fallback):
        - Vectorise la query avec TF-IDF
        - Compare avec la matrice TF-IDF
        - Retourne les top_k avec meilleurs scores
        """
        if not query.strip():
            return []
        
        
        if self.chunks and self.chunks[0].embedding is not None:
            try:
                from .services.embeddings import embeddings_service
                
                # Générer l'embedding de la query
                query_embedding = embeddings_service.embed_text(query)
                
                if query_embedding is not None:
                    # Calculer les similarités avec tous les chunks
                    scores = []
                    for chunk in self.chunks:
                        if chunk.embedding is not None:
                            similarity = embeddings_service.cosine_similarity(
                                query_embedding, 
                                chunk.embedding
                            )
                            scores.append(similarity)
                        else:
                            scores.append(0.0)
                    
                    # Trier et prendre les top_k
                    scores_array = np.array(scores)
                    top_idx = np.argsort(-scores_array)[:top_k]
                    
                    hits: list[SearchHit] = []
                    for idx in top_idx:
                        score = float(scores_array[idx])
                        if score > 0:
                            hits.append(SearchHit(
                                chunk=self.chunks[int(idx)], 
                                score=score
                            ))
                    
                    return hits
            except Exception as e:
                print(f"⚠️ Erreur recherche embeddings: {e}, fallback TF-IDF")
        
        # 📊 Fallback: Recherche TF-IDF
        if self.matrix is None or self.vectorizer is None:
            return []

        q_vec = self.vectorizer.transform([query])
        # cosine similarity (TF-IDF is l2-normalized) => dot product
        scores = (self.matrix @ q_vec.T).toarray().ravel()
        if scores.size == 0:
            return []

        top_idx = np.argsort(-scores)[:top_k]
        hits: list[SearchHit] = []
        for idx in top_idx:
            score = float(scores[idx])
            if score <= 0:
                continue
            hits.append(SearchHit(chunk=self.chunks[int(idx)], score=score))
        return hits

class MultiTenantSearch:
    """Gestionnaire d'index multi-tenant avec isolation stricte.
    
    🔒 SÉPARATION DES CLIENTS:
    - Chaque `tenant_id` a son propre TenantIndex
    - Les index sont chargés à la demande (lazy loading)
    - Aucun croisement de données entre les index
    
    Usage:
        search_engine.get('tenantA')  # Retourne uniquement l'index de tenantA
        search_engine.get('tenantB')  # Retourne uniquement l'index de tenantB
    """
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self.indexes: dict[str, TenantIndex] = {}  

    def load_tenant(self, tenant_id: str) -> None:
        tenant_dir = os.path.join(self.base_dir, tenant_id)
        self.indexes[tenant_id] = TenantIndex(tenant_id=tenant_id, tenant_dir=tenant_dir)

    def reload_tenant(self, tenant_id: str) -> None:
        """Recharge l'index d'un tenant (après ajout/modification de documents)."""
        tenant_dir = os.path.join(self.base_dir, tenant_id)
        self.indexes[tenant_id] = TenantIndex(tenant_id=tenant_id, tenant_dir=tenant_dir)
        print(f"🔄 Index rechargé pour {tenant_id}")

    def get(self, tenant_id: str) -> TenantIndex:
        if tenant_id not in self.indexes:
            self.load_tenant(tenant_id)
        return self.indexes[tenant_id]
    
    def get_tenant_index(self, tenant_id: str) -> TenantIndex | None:
        """Retourne l'index d'un tenant s'il existe, sinon None."""
        return self.indexes.get(tenant_id)

def build_extractive_answer(hits: list[SearchHit]) -> str:
    """Construit une réponse strictement extractive (anti-hallucination).
    
    🛡️ SÉCURITÉ ANTI-HALLUCINATION:
    - Pas de génération libre de texte
    - Copie littérale des extraits trouvés
    - Sources toujours citées (doc_id + chunk_id)
    
    Ce choix évite l'invention d'informations et garantit la traçabilité.
    """
    if not hits:
        return ""
    lines = ["Extraits pertinents trouvés dans vos documents :"]
    for h in hits:
        excerpt = h.chunk.text
        lines.append(f"- ({h.chunk.doc_id} | chunk {h.chunk.chunk_id}) {excerpt}")
    return "\n".join(lines)

def build_llm_answer(hits: list[SearchHit], question: str) -> tuple[str | None, bool]:
    """Construit une réponse avec LLM local (Ollama + Mistral).
    
    🤖 GÉNÉRATION IA:
    - Utilise Ollama avec modèle Mistral
    - RAG: Réponse basée sur les chunks récupérés
    - Prompt strict pour éviter les hallucinations
    - Fallback sur réponse extractive si LLM indisponible
    
    Args:
        hits: Résultats de recherche TF-IDF
        question: Question de l'utilisateur
    
    Returns:
        tuple[réponse, llm_used]: (texte de réponse, booléen si LLM utilisé)
    """
    if not hits:
        return "", False
    
    try:
        # Import du service LLM
        from .services.llm import llm_service
        
        # Vérifier si Ollama est disponible
        if not llm_service.is_available():
            print("⚠️ Ollama non disponible, utilisation de la réponse extractive")
            return build_extractive_answer(hits), False
        
        # Préparer les chunks pour le LLM
        context_chunks = [h.chunk.text for h in hits]
        
        # Générer la réponse avec le LLM
        llm_answer = llm_service.build_rag_answer(question, context_chunks)
        
        if llm_answer:
            return llm_answer, True
        else:
            # Fallback sur extractif si LLM échoue
            print("⚠️ Échec génération LLM, fallback sur extractif")
            return build_extractive_answer(hits), False
            
    except Exception as e:
        print(f"⚠️ Erreur LLM: {e}, fallback sur extractif")
        return build_extractive_answer(hits), False
