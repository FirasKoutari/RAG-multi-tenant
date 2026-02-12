import { useState } from 'react';
import './UploadDocument.css';

/**
 * Composant d'upload de documents pour un tenant
 */
const UploadDocument = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [success, setSuccess] = useState(null);
  const [error, setError] = useState(null);
  const [apiKey, setApiKey] = useState('tenantA_key');
  
  // Mapper API key vers nom de tenant
  const getTenantName = (key) => {
    return key === 'tenantA_key' 
      ? 'Tenant A - Assureur Principal' 
      : 'Tenant B - Assureur Secondaire';
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    
    // Validation du fichier
    if (selectedFile) {
      if (!selectedFile.name.endsWith('.txt')) {
        setError('Seuls les fichiers .txt sont acceptés');
        setFile(null);
        return;
      }
      
      if (selectedFile.size === 0) {
        setError('Le fichier est vide');
        setFile(null);
        return;
      }
      
      if (selectedFile.size > 5 * 1024 * 1024) { // 5MB max
        setError('Le fichier est trop volumineux (max 5MB)');
        setFile(null);
        return;
      }
      
      setFile(selectedFile);
      setError(null);
      setSuccess(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Veuillez sélectionner un fichier');
      return;
    }

    setUploading(true);
    setError(null);
    setSuccess(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        headers: {
          'X-API-KEY': apiKey,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Erreur lors de l\'upload');
      }

      const data = await response.json();
      
      setSuccess({
        message: `Document "${data.filename}" téléversé avec succès !`,
        chunks: data.chunks_count,
        size: (data.file_size_bytes / 1024).toFixed(2),
      });
      
      // Réinitialiser le formulaire
      setFile(null);
      const fileInput = document.getElementById('file-input');
      if (fileInput) fileInput.value = '';
      
    } catch (err) {
      setError(err.message || 'Une erreur est survenue lors de l\'upload');
    } finally {
      setUploading(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      // Simuler un changement de fichier
      const event = { target: { files: [droppedFile] } };
      handleFileChange(event);
    }
  };

  return (
    <div className="upload-document">
      <div className="upload-header">
        <h2>📤 Téléverser un Document</h2>
        <p className="upload-subtitle">
          Sélectionnez votre tenant et ajoutez de nouveaux documents .txt
        </p>
      </div>

      {/* Sélecteur de tenant */}
      <div className="tenant-selector">
        <label htmlFor="tenant-select-upload">
          <strong>🏢 Sélectionnez votre tenant</strong>
        </label>
        <select
          id="tenant-select-upload"
          value={apiKey}
          onChange={(e) => {
            setApiKey(e.target.value);
            setSuccess(null);
            setError(null);
          }}
          className="tenant-select"
          disabled={uploading}
        >
          <option value="tenantA_key">🔵 Tenant A - Assureur Principal</option>
          <option value="tenantB_key">🟢 Tenant B - Assureur Secondaire</option>
        </select>
        <p className="tenant-info">
          Les documents seront stockés dans <code>{apiKey === 'tenantA_key' ? 'data/tenantA/' : 'data/tenantB/'}</code>
        </p>
      </div>

      <div 
        className={`upload-zone ${file ? 'has-file' : ''}`}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <div className="upload-icon">📄</div>
        
        {!file ? (
          <>
            <p className="upload-text">
              Glissez-déposez votre fichier .txt ici
            </p>
            <p className="upload-text-secondary">ou</p>
            <label htmlFor="file-input" className="upload-button-label">
              <span>Parcourir les fichiers</span>
            </label>
            <input
              id="file-input"
              type="file"
              accept=".txt"
              onChange={handleFileChange}
              className="file-input-hidden"
            />
          </>
        ) : (
          <div className="file-selected">
            <div className="file-info">
              <span className="file-name">📄 {file.name}</span>
              <span className="file-size">
                {(file.size / 1024).toFixed(2)} KB
              </span>
            </div>
            <button 
              className="file-remove" 
              onClick={() => {
                setFile(null);
                const fileInput = document.getElementById('file-input');
                if (fileInput) fileInput.value = '';
              }}
            >
              ✕ Retirer
            </button>
          </div>
        )}
      </div>

      {file && (
        <button
          className="upload-submit-button"
          onClick={handleUpload}
          disabled={uploading}
        >
          {uploading ? '⏳ Téléversement en cours...' : '📤 Téléverser le document'}
        </button>
      )}

      {/* Message de succès */}
      {success && (
        <div className="upload-success">
          <div className="success-icon">✅</div>
          <div className="success-content">
            <p className="success-message">{success.message}</p>
            <div className="success-stats">
              <span>📊 {success.chunks} chunks indexés</span>
              <span>💾 {success.size} KB</span>
            </div>
          </div>
        </div>
      )}

      {/* Message d'erreur */}
      {error && (
        <div className="upload-error">
          <span className="error-icon">⚠️</span>
          <span>{error}</span>
        </div>
      )}

      <div className="upload-info">
        <h3>ℹ️ Informations</h3>
        <ul>
          <li>Format accepté : <code>.txt</code> uniquement</li>
          <li>Taille maximale : <strong>5 MB</strong></li>
          <li>Le document sera automatiquement indexé pour la recherche</li>
          <li>Les embeddings sémantiques seront générés avec Mistral</li>
        </ul>
      </div>
    </div>
  );
};

export default UploadDocument;
