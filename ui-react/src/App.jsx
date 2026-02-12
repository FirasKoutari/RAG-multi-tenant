import { useState, useEffect } from 'react';
import QueryForm from './components/QueryForm';
import QueryResults from './components/QueryResults';
import ErrorMessage from './components/ErrorMessage';
import UploadDocument from './components/UploadDocument';
import { queryDocuments, checkHealth } from './services/api';
import './App.css';

/**
 * Application principale - Multi-tenant SaaS avec recherche documentaire
 * 
 * Architecture:
 * - Frontend React communique avec Backend FastAPI
 * - Isolation multi-tenant via header X-API-KEY
 * - Recherche sémantique avec embeddings Mistral
 * - Upload de documents par tenant
 * - Sources toujours citées pour traçabilité
 */
function App() {
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [backendStatus, setBackendStatus] = useState(null);
  const [activeTab, setActiveTab] = useState('search'); // 'search' ou 'upload'

  // Vérification de l'état du backend au chargement
  useEffect(() => {
    checkHealth()
      .then((status) => setBackendStatus(status))
      .catch(() => setBackendStatus({ status: 'error' }));
  }, []);

  const handleQuery = async (question, apiKey) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await queryDocuments(question, apiKey);
      setResult(data);
    } catch (err) {
      setError(err.message || 'Une erreur est survenue');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      {/* Professional Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="header-brand">
            <div className="brand-icon">🏢</div>
            <div className="brand-text">
              <h1>Actudata Intelligence</h1>
              <p>Multi-Tenant Document Search Platform</p>
            </div>
          </div>
          
          {/* Backend Status Badge */}
          <div className="backend-status">
            {backendStatus?.status === 'ok' ? (
              <>
                <div className="status-indicator"></div>
                <span className="status-ok">Système opérationnel</span>
              </>
            ) : backendStatus?.status === 'error' ? (
              <>
                <div className="status-indicator"></div>
                <span className="status-error">Service indisponible</span>
              </>
            ) : (
              <>
                <div className="status-indicator"></div>
                <span className="status-loading">Connexion en cours...</span>
              </>
            )}
          </div>
        </div>
      </header>

      <div className="container">
        {/* Onglets de navigation */}
        <div className="tabs-container">
          <button
            className={`tab ${activeTab === 'search' ? 'active' : ''}`}
            onClick={() => setActiveTab('search')}
          >
            🔍 Recherche Documentaire
          </button>
          <button
            className={`tab ${activeTab === 'upload' ? 'active' : ''}`}
            onClick={() => setActiveTab('upload')}
          >
            📤 Téléverser un Document
          </button>
        </div>

        {/* Contenu selon l'onglet actif */}
        {activeTab === 'search' ? (
          <>
            {/* Formulaire de recherche */}
            <QueryForm onSubmit={handleQuery} loading={loading} />

            {/* Affichage des erreurs */}
            <ErrorMessage error={error} onDismiss={() => setError(null)} />

            {/* Affichage des résultats */}
            <QueryResults result={result} />
          </>
        ) : (
          <>
            {/* Composant d'upload */}
            <UploadDocument />
          </>
        )}

        {/* Footer */}
        <footer className="app-footer">
          <div className="footer-content">
            <div className="footer-feature">
              <div className="feature-icon">🔐</div>
              <div className="feature-content">
                <h3>Architecture Sécurisée</h3>
                <p>Isolation multi-tenant complète via authentification API KEY avec gestion des permissions</p>
              </div>
            </div>
            <div className="footer-feature">
              <div className="feature-icon">🤖</div>
              <div className="feature-content">
                <h3>Recherche Intelligente</h3>
                <p>Embeddings Mistral pour recherche sémantique avec génération de réponses contextuelles</p>
              </div>
            </div>
            <div className="footer-feature">
              <div className="feature-icon">📊</div>
              <div className="feature-content">
                <h3>Traçabilité Totale</h3>
                <p>Sources toujours citées avec scores de pertinence et logging SQL des requêtes</p>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;
