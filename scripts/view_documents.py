"""
Script pour visualiser le contenu de la table tenant_documents
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database import SessionLocal
from backend.models import TenantDocument

def view_tenant_documents():
    """Affiche le contenu de la table tenant_documents."""
    
    db = SessionLocal()
    
    try:
        print("\n" + "="*80)
        print("📚 TENANT DOCUMENTS")
        print("="*80)
        
        # Récupérer tous les documents
        documents = db.query(TenantDocument).order_by(
            TenantDocument.tenant_id, 
            TenantDocument.doc_id
        ).all()
        
        if not documents:
            print("\n⚠️  Aucun document trouvé dans la base de données")
            print("\n💡 Exécutez: python scripts/populate_documents.py")
            return
        
        current_tenant = None
        for doc in documents:
            if doc.tenant_id != current_tenant:
                current_tenant = doc.tenant_id
                print(f"\n🔵 {current_tenant.upper()}")
                print("-" * 80)
            
            print(f"  📄 {doc.doc_id}")
            print(f"     Chunks: {doc.chunks_count}")
            print(f"     Path: {doc.doc_path}")
            print(f"     Indexed: {doc.indexed_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Statistiques
        print("\n" + "="*80)
        print("📊 STATISTIQUES")
        print("="*80)
        
        for tenant_id in ["tenantA", "tenantB"]:
            tenant_docs = [d for d in documents if d.tenant_id == tenant_id]
            if tenant_docs:
                total_chunks = sum(d.chunks_count for d in tenant_docs)
                print(f"\n{tenant_id}:")
                print(f"  Documents: {len(tenant_docs)}")
                print(f"  Total chunks: {total_chunks}")
        
        print("\n")
        
    finally:
        db.close()

if __name__ == "__main__":
    view_tenant_documents()
