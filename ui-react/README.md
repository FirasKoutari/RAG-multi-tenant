# Frontend React - Multi-tenant SaaS

Interface utilisateur React pour l'application multi-tenant de recherche documentaire.

## 🚀 Démarrage rapide

### Installation

```bash
npm install
```

### Configuration

Créer un fichier `.env` à la racine du projet (copier `.env.example`):

```bash
VITE_API_URL=http://localhost:8000
```

### Lancement du serveur de développement

```bash
npm run dev
```

L'application sera accessible sur `http://localhost:5173`

### Build pour production

```bash
npm run build
```

Les fichiers optimisés seront dans le dossier `dist/`.

## 🏗️ Architecture

```
src/
├── components/          # Composants React
│   ├── QueryForm.jsx       # Formulaire de recherche
│   ├── QueryResults.jsx    # Affichage des résultats
│   ├── ErrorMessage.jsx    # Messages d'erreur
│   └── *.css              # Styles des composants
├── services/
│   └── api.js             # Communication avec FastAPI
├── App.jsx            # Composant principal
└── main.jsx          # Point d'entrée
```

## 🔐 Sécurité Multi-tenant

- Sélection du tenant via dropdown (tenantA_key / tenantB_key)
- Header X-API-KEY envoyé automatiquement
- Pas de tenant_id dans le body JSON
- Isolation backend garantie

## 🧪 Tester l'application

1. Lancer le backend : `uvicorn backend.main:app --reload`
2. Lancer le frontend : `npm run dev`
3. Ouvrir `http://localhost:5173`

### Exemples de questions

**Tenant A** :
- "Sous combien de temps est envoyé un accusé de réception ?"

**Tenant B** :
- "Sous combien de jours doit-on déclarer un sinistre ?"

---

## React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
