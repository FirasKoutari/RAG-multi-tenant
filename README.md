# 🏢 RAG Multi-Tenant - Plateforme Intelligente de Recherche Documentaire

<div align="center">

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green?logo=fastapi)
![React](https://img.shields.io/badge/React-18-61dafb?logo=react)
![Ollama](https://img.shields.io/badge/Ollama-Mistral-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

**Système RAG (Retrieval Augmented Generation) multi-tenant sécurisé avec recherche sémantique par embeddings Mistral**

[Démo](#-utilisation) • [Installation](#-installation) • [Architecture](#-architecture) • [API](#-api-endpoints) • [Tests](#-tests)

</div>

---

## 🎯 Objectif

Plateforme SaaS de recherche documentaire intelligente avec **isolation complète multi-tenant** :

- ✅ **2 clients indépendants** (Tenant A & Tenant B)
- ✅ **Recherche sémantique** via embeddings Mistral (Ollama)
- ✅ **LLM local gratuit** pour génération de réponses contextuelles
- ✅ **Authentification sécurisée** via header `X-API-KEY`
- ✅ **SQLite logging** avec analytics par tenant
- ✅ **Interface React moderne** avec design professionnel
- ✅ **Zéro fuite de données** entre tenants (index isolés)

---

## 🚀 Architecture

### **Backend (FastAPI + Ollama)**
- **API REST** multi-tenant avec authentification par API key
- **Recherche sémantique** : Embeddings Mistral 7B (similarité cosinus)
- **RAG (Retrieval Augmented Generation)** : Génération de réponses avec anti-hallucination
- **Fallback TF-IDF** : Si Ollama indisponible
- **SQLite** : Logging des requêtes, tracking usage, analytics

### **Frontend (React + Vite)**
- Interface moderne avec design system professionnel
- Sélection tenant dynamique
- Affichage des sources avec scores de pertinence
- Indicateur de statut backend en temps réel

### **LLM Local (Ollama + Mistral)**
- **Modèle** : Mistral 7B (4.4GB)
- **Embeddings** : 4096 dimensions pour recherche sémantique
- **Génération** : Réponses contextuelles basées sur documents
- **Gratuit & Local** : Pas d'API externe, données privées

---

## 📋 Pré-requis

- **Python 3.10+**
- **Node.js 18+** (pour l'interface React)
- **Ollama** installé avec modèle Mistral ([installer Ollama](https://ollama.ai))

---

## 🔧 Installation

### 1️⃣ **Cloner le repository**
```bash
git clone https://github.com/FirasKoutari/RAG-multi-tenant.git
cd RAG-multi-tenant
```

### 2️⃣ **Installer Ollama et télécharger Mistral**
```bash
# Installer Ollama : https://ollama.ai/download
# Puis télécharger Mistral (4.4GB)
ollama pull mistral
```

### 3️⃣ **Backend Python**
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

### 4️⃣ **Frontend React**
```bash
cd ui-react
npm install
cd ..
```

### 5️⃣ **Initialiser la base de données**
```bash
# Créer les tables SQLite
python -c "from backend.database import init_db; init_db()"

# Peupler les documents dans la DB (optionnel)
python scripts/populate_documents.py
```

---

## 🎮 Démarrage

### **Backend (Terminal 1)**
```bash
uvicorn backend.main:app --reload --port 8000
```
✅ API disponible sur `http://localhost:8000`  
📖 Documentation auto-générée : `http://localhost:8000/docs`

### **Frontend React (Terminal 2)** ⭐ Recommandé
```bash
cd ui-react
npm run dev
```
✅ Interface disponible sur `http://localhost:5173`

### **Alternative : Interface Streamlit (Terminal 2)**
```bash
streamlit run ui/streamlit_app.py
```
✅ Interface disponible sur `http://localhost:8501`

---

## 🔍 Utilisation

### **Interface Web**

1. Ouvrir `http://localhost:5173`
2. Sélectionner un tenant (Tenant A ou Tenant B)
3. Poser une question en langage naturel
4. Obtenir une réponse avec sources citées

**Exemples de questions :**
- *"Quel est l'email du service sinistre ?"*
- *"Sous combien de jours doit-on déclarer un sinistre ?"*
- *"Quelle est la procédure de résiliation ?"*

### **API (curl)**

#### **Tenant A - Recherche dans ses documents**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: tenantA_key" \
  -d '{"question":"Quel est l email pour déclarer un sinistre ?"}'
```

#### **Tenant B - Isolation complète**
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -H "X-API-KEY: tenantB_key" \
  -d '{"question":"Sous combien de jours doit-on déclarer un sinistre ?"}'
```

#### **Analytics par tenant**
```bash
curl "http://localhost:8000/stats/tenantA" \
  -H "X-API-KEY: tenantA_key"
```

---

## 🧪 Tests

### **Lancer tous les tests**
```bash
pytest backend/tests/ -v
```

### **Tests de sécurité multi-tenant**
```bash
pytest backend/tests/test_tenants.py -v
```

**Suite de tests (6 tests) :**
- ✅ `test_invalid_key` : Refus sans `X-API-KEY`
- ✅ `test_tenantA_resiliation` : Tenant A voit uniquement ses docs
- ✅ `test_tenantB_sinistre` : Tenant B voit uniquement ses docs
- ✅ `test_cross_tenant_impossible_question` : Question hors sujet → `no_answer`
- ✅ `test_tenantB_cannot_access_tenantA_data` : Zéro fuite B→A
- ✅ `test_wrong_api_key` : Clé inexistante → 401

---

## 📁 Structure du Projet

```
RAG-multi-tenant/
├── backend/
│   ├── main.py                 # API FastAPI
│   ├── search.py               # Moteur de recherche (embeddings + TF-IDF)
│   ├── tenants.py              # Résolution multi-tenant
│   ├── models.py               # Modèles SQLAlchemy
│   ├── database.py             # Connexion SQLite
│   ├── services/
│   │   ├── llm.py             # Service Ollama pour génération
│   │   └── embeddings.py      # Service embeddings Mistral
│   ├── data/
│   │   ├── tenantA/           # Documents Tenant A
│   │   ├── tenantB/           # Documents Tenant B
│   │   └── app.db             # Base SQLite
│   └── tests/
│       └── test_tenants.py    # Tests sécurité multi-tenant
├── ui-react/                   # Interface React moderne
│   ├── src/
│   │   ├── components/        # Composants React
│   │   ├── services/          # API client
│   │   └── App.jsx            # Application principale
│   └── package.json
├── ui/
│   └── streamlit_app.py       # Interface Streamlit alternative
├── scripts/
│   ├── populate_documents.py  # Peupler la DB
│   └── view_documents.py      # Visualiser la DB
├── requirements.txt           # Dépendances Python
└── README.md
```

---

## 🛡️ Sécurité Multi-Tenant

### **Isolation Complète**
Chaque tenant dispose de :
- ✅ **Index de recherche isolé** (vocabulaire TF-IDF séparé)
- ✅ **Embeddings distincts** (espace vectoriel indépendant)
- ✅ **Répertoire de documents privé** (`backend/data/tenantA` vs `tenantB`)
- ✅ **Authentification par API key** (header `X-API-KEY`)

### **Garanties**
- ❌ **Aucun partage de tokens/embeddings** entre tenants
- ❌ **Impossible d'accéder aux données d'un autre tenant**
- ❌ **Pas de fuite via le LLM** (contexte limité au tenant)

---

## 🤖 Recherche Sémantique vs TF-IDF

### **Mode Embeddings (Préféré)**
- 🧠 Compréhension sémantique de la question
- 📊 Similarité cosinus sur vecteurs 4096D
- ✅ Trouve "email du service" même si document dit "adresse électronique"

### **Mode TF-IDF (Fallback)**
- 📝 Recherche par mots-clés
- 🔤 Nécessite correspondance lexicale exacte
- ⚡ Plus rapide mais moins intelligent

---

## 📊 Base de Données (SQLite)

### **Tables**
- **`query_log`** : Historique des requêtes par tenant
- **`tenant_documents`** : Métadonnées des documents indexés
- **`api_key_usage`** : Tracking utilisation par API key

### **Visualiser les données**
```bash
python scripts/view_documents.py
```

---

## 🎨 Interface React

Design professionnel moderne avec :
- ✅ Palette de couleurs verte corporate
- ✅ Typographie Inter (Google Fonts)
- ✅ Animations fluides et élégantes
- ✅ Header sticky avec branding
- ✅ Cartes avec ombres et bordures
- ✅ Responsive (mobile, tablette, desktop)

---

## 📚 API Endpoints

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| `GET` | `/health` | Vérifier statut backend |
| `POST` | `/query` | Recherche documentaire (header `X-API-KEY` requis) |
| `GET` | `/stats/{tenant_id}` | Analytics du tenant |

### **Exemple de réponse**
```json
{
  "tenant_id": "tenantA",
  "answer": "L'email pour déclarer un sinistre est sinistres@assureur-a.fr",
  "sources": [
    {
      "doc_id": "docA1_procedure_sinistre.txt",
      "chunk_id": 2,
      "score": "0.89",
      "excerpt": "...déclarer un sinistre à sinistres@assureur-a.fr..."
    }
  ],
  "no_answer": false
}
```

---

## 🌟 Fonctionnalités Avancées

- ✅ **Anti-hallucination** : Réponses strictement basées sur documents
- ✅ **Sources citées** : Traçabilité complète (doc + chunk + score)
- ✅ **Chunking intelligent** : Découpage avec overlap (420 chars + 80 overlap)
- ✅ **Fallback automatique** : TF-IDF si Ollama indisponible
- ✅ **Logging SQL** : Tracking des performances et usage
- ✅ **Tests automatisés** : 6 tests de sécurité multi-tenant

---

## 🛠️ Technologies

| Catégorie | Technologies |
|-----------|-------------|
| **Backend** | FastAPI 0.115, Python 3.13, Uvicorn |
| **LLM** | Ollama, Mistral 7B (local) |
| **Recherche** | Scikit-learn (TF-IDF), NumPy (cosine similarity) |
| **Database** | SQLite, SQLAlchemy 2.0 |
| **Frontend** | React 18, Vite, CSS3 |
| **Testing** | Pytest, HTTPx |

---

## 📝 Ajouter vos Documents

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

---

## 📄 License

MIT License - Voir [LICENSE](LICENSE) pour détails.

---

## 👤 Auteur

**Firas Koutari**  
🔗 [GitHub](https://github.com/FirasKoutari)  
📧 Contact: [via GitHub](https://github.com/FirasKoutari/RAG-multi-tenant/issues)

---

## ⭐ Contribuer

Les contributions sont les bienvenues ! N'hésitez pas à :
1. Fork le projet
2. Créer une branche (`git checkout -b feature/amelioration`)
3. Commit vos changements (`git commit -m 'Ajout fonctionnalité'`)
4. Push vers la branche (`git push origin feature/amelioration`)
5. Ouvrir une Pull Request

---

<div align="center">

**⭐ Si ce projet vous a aidé, n'hésitez pas à lui donner une étoile sur GitHub ! ⭐**

</div>
