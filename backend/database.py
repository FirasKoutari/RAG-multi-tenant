"""
Configuration de la base de données SQLite
"""
from __future__ import annotations

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Chemin de la base de données SQLite
DB_PATH = os.path.join(os.path.dirname(__file__), "data", "app.db")
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

# Création du moteur SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Nécessaire pour SQLite
    echo=False  # Mettre True pour voir les requêtes SQL
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base pour les modèles
Base = declarative_base()

def get_db():
    """
    Dependency pour obtenir une session de base de données.
    Usage avec FastAPI:
        @app.get("/")
        def route(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialise la base de données (créer les tables)."""
    # Créer le dossier data s'il n'existe pas
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    
    # Import des modèles (nécessaire pour que SQLAlchemy les connaisse)
    from . import models  # noqa
    
    # Créer toutes les tables
    Base.metadata.create_all(bind=engine)
    print(f"✅ Base de données initialisée: {DB_PATH}")
