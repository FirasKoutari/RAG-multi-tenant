import './QueryResults.css';

/**
 * Affichage des résultats de recherche avec sources
 */
const QueryResults = ({ result }) => {
  if (!result) return null;

  const { tenant_id, answer, sources, no_answer } = result;

  return (
    <div className="query-results">
      <div className="tenant-badge">
        <strong>📍 Tenant:</strong> {tenant_id}
      </div>

      <div className="results-section">
        <h2>💬 Réponse</h2>
        {no_answer ? (
          <div className="no-answer-message">
            ℹ️ Aucune réponse possible pour ce client (pas de passage pertinent dans ses documents).
          </div>
        ) : (
          <div className="answer-box">
            <pre>{answer}</pre>
          </div>
        )}
      </div>

      <div className="results-section">
        <h2>📚 Sources</h2>
        {!sources || sources.length === 0 ? (
          <p className="no-sources">Aucune source trouvée</p>
        ) : (
          <div className="sources-list">
            {sources.map((source, index) => (
              <div key={index} className="source-item">
                <div className="source-header">
                  <span className="source-doc">
                    📄 <strong>{source.doc_id}</strong>
                  </span>
                  <span className="source-meta">
                    Chunk {source.chunk_id} • Score: <code>{source.score}</code>
                  </span>
                </div>
                <div className="source-excerpt">
                  {source.excerpt}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default QueryResults;
