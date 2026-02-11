/**
 * Service API pour communiquer avec le backend FastAPI multi-tenant
 * 
 * 🔐 Sécurité: Le tenant est envoyé uniquement via le header X-API-KEY
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Effectue une requête de recherche documentaire
 * @param {string} question - La question à poser
 * @param {string} apiKey - La clé API du tenant (tenantA_key ou tenantB_key)
 * @returns {Promise<Object>} Réponse avec answer, sources, no_answer
 */
export const queryDocuments = async (question, apiKey) => {
  try {
    const response = await fetch(`${API_BASE_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-API-KEY': apiKey, // 🔑 Header obligatoire pour l'isolation multi-tenant
      },
      body: JSON.stringify({ question }),
    });

    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('Clé API invalide ou manquante');
      }
      throw new Error(`Erreur serveur: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Erreur API:', error);
    throw error;
  }
};

/**
 * Vérifie l'état de santé du backend
 * @returns {Promise<Object>} Status de santé
 */
export const checkHealth = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    return await response.json();
  } catch (error) {
    console.error('Backend non disponible:', error);
    throw error;
  }
};
