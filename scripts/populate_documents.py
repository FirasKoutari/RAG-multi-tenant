"""
Script pour peupler la table tenant_documents avec les documents existants
"""
from __future__ import annotations

import os
import sys

# Ajouter le répertoire parent au path pour importer les modules backend
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal, init_db
from backend.models import TenantDocument
from backend.search import _chunk_text, _read_text

def populate_tenant_documents():
    """Peuple la table tenant_documents avec les documents existants."""
    
    # Initialiser la base de données
    init_db()
    
    # Créer une session
    db = SessionLocal()
    
    try:
        # Chemin vers le répertoire data
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", "data")
        
        # Liste des tenants
        tenants = ["tenantA", "tenantB"]
        
        for tenant_id in tenants:
            tenant_dir = os.path.join(data_dir, tenant_id)
            
            if not os.path.isdir(tenant_dir):
                print(f"⚠️  Répertoire {tenant_dir} non trouvé")
                continue
            
            print(f"\n📂 Traitement du tenant: {tenant_id}")
            print(f"   Répertoire: {tenant_dir}")
            
            # Parcourir tous les fichiers .txt du tenant
            for filename in os.listdir(tenant_dir):
                if not filename.lower().endswith(".txt"):
                    continue
                
                file_path = os.path.join(tenant_dir, filename)
                
                # Vérifier si le document existe déjà dans la BD
                existing_doc = db.query(TenantDocument).filter(
                    TenantDocument.tenant_id == tenant_id,
                    TenantDocument.doc_id == filename
                ).first()
                
                if existing_doc:
                    print(f"   ⏭️  {filename} (déjà en base)")
                    continue
                
                # Lire le contenu du fichier
                try:
                    content = _read_text(file_path)
                    
                    # Chunker le texte pour compter les chunks
                    chunks = _chunk_text(content)
                    chunks_count = len(chunks)
                    
                    # Créer l'entrée dans la base de données
                    tenant_doc = TenantDocument(
                        tenant_id=tenant_id,
                        doc_id=filename,
                        doc_path=file_path,
                        chunks_count=chunks_count
                    )
                    
                    db.add(tenant_doc)
                    db.commit()
                    
                    print(f"   ✅ {filename} ({chunks_count} chunks)")
                    
                except Exception as e:
                    print(f"   ❌ Erreur avec {filename}: {e}")
                    db.rollback()
        
        # Afficher le résumé
        print("\n" + "="*60)
        print("📊 RÉSUMÉ")
        print("="*60)
        
        for tenant_id in tenants:
            count = db.query(TenantDocument).filter(
                TenantDocument.tenant_id == tenant_id
            ).count()
            
            total_chunks = db.query(TenantDocument).filter(
                TenantDocument.tenant_id == tenant_id
            ).with_entities(TenantDocument.chunks_count).all()
            
            total_chunks_sum = sum([c[0] for c in total_chunks if c[0]])
            
            print(f"\n{tenant_id}:")
            print(f"  - Documents: {count}")
            print(f"  - Total chunks: {total_chunks_sum}")
        
        print("\n✅ Population terminée avec succès!")
        
    except Exception as e:
        print(f"\n❌ Erreur: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_tenant_documents()
