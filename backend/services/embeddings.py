"""
Service d'embeddings utilisant Ollama avec Mistral
Pour la recherche sémantique (RAG)
"""
from __future__ import annotations

import os
import requests
import numpy as np
from typing import Optional

# Configuration Ollama
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "mistral")

class OllamaEmbeddings:
    """Service d'embeddings avec Ollama."""
    
    def __init__(self, model: str = OLLAMA_EMBEDDING_MODEL, base_url: str = OLLAMA_BASE_URL):
        self.model = model
        self.base_url = base_url
        self.timeout = 30
    
    def is_available(self) -> bool:
        """Vérifie si Ollama est disponible."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def embed_text(self, text: str) -> Optional[np.ndarray]:
        """
        Génère un embedding pour un texte.
        
        Args:
            text: Texte à embedder
        
        Returns:
            Vecteur numpy ou None si erreur
        """
        try:
            response = requests.post(
                f"{self.base_url}/api/embeddings",
                json={
                    "model": self.model,
                    "prompt": text
                },
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                embedding = response.json().get("embedding")
                if embedding:
                    return np.array(embedding, dtype=np.float32)
            else:
                print(f"⚠️ Erreur embeddings Ollama: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"⚠️ Erreur génération embeddings: {e}")
            return None
    
    def embed_batch(self, texts: list[str]) -> list[Optional[np.ndarray]]:
        """
        Génère des embeddings pour plusieurs textes.
        
        Args:
            texts: Liste de textes à embedder
        
        Returns:
            Liste de vecteurs numpy
        """
        return [self.embed_text(text) for text in texts]
    
    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Calcule la similarité cosinus entre deux vecteurs.
        
        Args:
            vec1: Premier vecteur
            vec2: Deuxième vecteur
        
        Returns:
            Score de similarité (0 à 1)
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))


# Instance globale du service d'embeddings
embeddings_service = OllamaEmbeddings()
