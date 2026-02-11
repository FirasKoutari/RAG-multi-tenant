"""
Service LLM utilisant Ollama avec Mistral
Génération de réponses contextuelles basées sur les documents trouvés
"""
from __future__ import annotations

import os
import requests
from typing import Optional

# URL locale d'Ollama (installer avec: ollama pull mistral)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

class OllamaLLM:
    """Service LLM local avec Ollama."""
    
    def __init__(self, model: str = OLLAMA_MODEL, base_url: str = OLLAMA_BASE_URL):
        self.model = model
        self.base_url = base_url
        self.timeout = 60  # secondes
    
    def is_available(self) -> bool:
        """Vérifie si Ollama est disponible."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False
    
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Optional[str]:
        """
        Génère une réponse avec Ollama.
        
        Args:
            prompt: Question utilisateur + contexte
            system_prompt: Instructions système (optionnel)
        
        Returns:
            Réponse générée ou None si erreur
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Réponses plus déterministes
                    "top_p": 0.9,
                    "top_k": 40,
                }
            }
            
            if system_prompt:
                payload["system"] = system_prompt
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            else:
                print(f"Erreur Ollama: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Erreur génération LLM: {e}")
            return None
    
    def build_rag_answer(self, question: str, context_chunks: list[str]) -> Optional[str]:
        """
        Construit une réponse RAG basée sur les chunks récupérés.
        
        🛡️ Sécurité anti-hallucination:
        - Prompt strict: répondre UNIQUEMENT depuis les documents
        - Si pas d'info → dire explicitement "non trouvé"
        - Citer les sources dans la réponse
        
        Args:
            question: Question de l'utilisateur
            context_chunks: Extraits de documents pertinents
        
        Returns:
            Réponse générée ou None si erreur
        """
        if not context_chunks:
            return None
        
        # Construction du contexte
        context = "\n\n---\n\n".join([
            f"Document {i+1}:\n{chunk}" 
            for i, chunk in enumerate(context_chunks)
        ])
        
        # System prompt strict pour éviter les hallucinations
        system_prompt = """Tu es un assistant documentaire pour une entreprise SaaS multi-tenant.

RÈGLES STRICTES:
1. Réponds UNIQUEMENT en te basant sur les documents fournis
2. Si l'information n'est PAS dans les documents, dis clairement "Je ne trouve pas cette information dans vos documents"
3. Ne jamais inventer ou supposer des informations
4. Cite toujours la source (Document 1, Document 2, etc.)
5. Sois concis et précis
6. Réponds en français"""

        prompt = f"""Contexte (documents disponibles):
{context}

Question: {question}

Réponds à la question en te basant STRICTEMENT sur les documents ci-dessus."""

        return self.generate(prompt, system_prompt)


# Instance globale du service LLM
llm_service = OllamaLLM()
