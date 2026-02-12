

##  Objectif

Plateforme SaaS de recherche documentaire intelligente avec **isolation complète multi-tenant** :

-  **2 clients indépendants** (Tenant A & Tenant B)
-  **Recherche sémantique** via embeddings Mistral (Ollama)
-  **LLM local gratuit** pour génération de réponses contextuelles
-  **Authentification sécurisée** via header `X-API-KEY`
-  **SQLite logging** avec analytics par tenant
-  **Interface React moderne** avec design professionnel
-  **Zéro fuite de données** entre tenants (index isolés)

---

##  Pré-requis

- **Python 3.10+**
- **Node.js 18+** (pour l'interface React)
- **Ollama** installé avec modèle Mistral ([installer Ollama](https://ollama.ai))

---

##  Installation

### 1 **Cloner le repository**
```bash
git clone https://github.com/FirasKoutari/RAG-multi-tenant.git
cd RAG-multi-tenant
```

### 2 **Installer Ollama et télécharger Mistral**
```bash
# Installer Ollama : https://ollama.ai/download
# Puis télécharger Mistral (4.4GB)
ollama pull mistral
```

### 3 **Backend Python**
```bash
# Créer environnement virtuel
python -m venv .venv

# Activer (Windows)
.\.venv\Scripts\Activate.ps1

# Activer (macOS/Linux)
source .venv/bin/activate

# Installer dépendances
pip install -r requirements.txt
```

### 4 **Frontend React**
```bash
cd ui-react
npm install
npm run dev
```

### 5 **Initialiser la base de données**
```bash
# Créer les tables SQLite
python -c "from backend.database import init_db; init_db()"

# Peupler les documents dans la DB (optionnel)
python scripts/populate_documents.py
```

---

##  Démarrage

### **Backend (Terminal 1)**
```bash
uvicorn backend.main:app --reload --port 8000
```
 API disponible sur `http://localhost:8000`  
 Documentation auto-générée : `http://localhost:8000/docs`

### **Frontend React (Terminal 2)**  Recommandé
```bash
cd ui-react
npm run dev
```
✅ Interface disponible sur `http://localhost:5173`


---

##  Technologies

| Catégorie | Technologies |
|-----------|-------------|
| **Backend** | FastAPI 0.115, Python 3.13, Uvicorn |
| **LLM** | Ollama, Mistral 7B (local) |
| **Recherche** | Scikit-learn (TF-IDF), NumPy (cosine similarity) |
| **Database** | SQLite, SQLAlchemy 2.0 |
| **Frontend** | React 18, Vite, CSS3 |
| **Testing** | Pytest, HTTPx |

---

##  Ajouter vos Documents

### **Tenant A**
Placer vos fichiers `.txt` dans :
```bash
backend/data/tenantA/mon_document.txt
```

### **Tenant B**
Placer vos fichiers `.txt` dans :
```bash
backend/data/tenantB/mon_document.txt
```

Redémarrer le backend pour réindexer automatiquement.

---

## 🐛 Troubleshooting

### **Ollama indisponible**
```bash
# Vérifier installation
ollama list

# Télécharger Mistral
ollama pull mistral

# Tester
ollama run mistral "Bonjour"
```

### **Backend ne démarre pas**
```bash
# Vérifier environnement Python
python --version  # Doit être 3.10+

# Réinstaller dépendances
pip install -r requirements.txt --force-reinstall
```

### **Frontend React erreur**
```bash
cd ui-react
rm -rf node_modules package-lock.json
npm install
npm run dev
```