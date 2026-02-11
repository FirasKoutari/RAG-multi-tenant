"""
Modèles SQLAlchemy pour la base de données
"""
from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, JSON

from .database import Base

class QueryLog(Base):
    """
    Log de toutes les requêtes effectuées par les tenants.
    Permet de tracer l'utilisation et détecter les anomalies.
    """
    __tablename__ = "query_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    no_answer = Column(Boolean, default=False)
    sources_count = Column(Integer, default=0)
    execution_time_ms = Column(Float, nullable=True)  # Temps d'exécution en ms
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Métadonnées JSON (sources, scores, etc.)
    # Note: 'metadata' est réservé par SQLAlchemy, on utilise 'query_metadata'
    query_metadata = Column(JSON, nullable=True)
    
    def __repr__(self):
        return f"<QueryLog(id={self.id}, tenant={self.tenant_id}, created_at={self.created_at})>"


class TenantDocument(Base):
    """
    Métadonnées des documents par tenant.
    Permet de tracer quels documents sont disponibles pour chaque tenant.
    """
    __tablename__ = "tenant_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    doc_id = Column(String(255), nullable=False)  # Nom du fichier
    doc_path = Column(String(500), nullable=False)
    chunks_count = Column(Integer, default=0)
    indexed_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<TenantDocument(id={self.id}, tenant={self.tenant_id}, doc={self.doc_id})>"


class APIKeyUsage(Base):
    """
    Statistiques d'utilisation par clé API.
    Permet de monitorer l'activité et détecter les abus.
    """
    __tablename__ = "api_key_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(String(50), nullable=False, index=True)
    api_key = Column(String(100), nullable=False, index=True)
    request_count = Column(Integer, default=0)
    last_used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<APIKeyUsage(id={self.id}, tenant={self.tenant_id}, requests={self.request_count})>"
