import { useState } from 'react';
import './QueryForm.css';

/**
 * Formulaire de recherche documentaire multi-tenant
 */
const QueryForm = ({ onSubmit, loading }) => {
  const [question, setQuestion] = useState('');
  const [apiKey, setApiKey] = useState('tenantA_key');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (question.trim()) {
      onSubmit(question, apiKey);
    }
  };

  return (
    <div className="query-form">
      <div className="form-header">
        <h1>Recherche Intelligente Multi-Tenant</h1>
        <p className="subtitle">
          Authentification sécurisée via header <code>X-API-KEY</code> avec isolation complète des données
        </p>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="tenant-select">
            Sélectionnez votre tenant
          </label>
          <select
            id="tenant-select"
            value={apiKey}
            onChange={(e) => setApiKey(e.target.value)}
            className="tenant-select"
            disabled={loading}
          >
            <option value="tenantA_key">🔵 Tenant A - Assureur Principal</option>
            <option value="tenantB_key">🟢 Tenant B - Assureur Secondaire</option>
          </select>
        </div>

        <div className="form-group">
          <label htmlFor="question-input">
            Posez votre question
          </label>
          <textarea
            id="question-input"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Exemple: Sous combien de temps est envoyé un accusé de réception ? Quel est l'email du service sinistre ?"
            rows={4}
            className="question-input"
            disabled={loading}
            required
          />
        </div>

        <button 
          type="submit" 
          className="submit-button"
          disabled={loading || !question.trim()}
        >
          {loading ? '⏳ Recherche en cours...' : '🔍 Rechercher'}
        </button>
      </form>
    </div>
  );
};

export default QueryForm;
