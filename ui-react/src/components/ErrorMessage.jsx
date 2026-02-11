import './ErrorMessage.css';

/**
 * Affichage des erreurs
 */
const ErrorMessage = ({ error, onDismiss }) => {
  if (!error) return null;

  return (
    <div className="error-message">
      <div className="error-content">
        <span className="error-icon">⚠️</span>
        <div className="error-text">
          <strong>Erreur:</strong> {error}
        </div>
        <button className="error-dismiss" onClick={onDismiss}>
          ✕
        </button>
      </div>
    </div>
  );
};

export default ErrorMessage;
