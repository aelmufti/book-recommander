# Book Finder - Moteur de Recherche de Livres 📚

Une application web moderne pour découvrir des livres avec une base de données de **56,323 livres français** et une interface élégante en verre morphique.

## 🌟 Fonctionnalités

- **56k+ livres français** dans la base de données
- **Recherche intelligente** par mots-clés avec scoring avancé
- **Interface multilingue** (Français, Anglais, Espagnol, Allemand, Italien, Portugais)
- **Section "Puits de l'Inconnu"** pour découvrir des livres méconnus
- **Design glassmorphism** moderne et responsive
- **API FastAPI** haute performance avec pandas

## 🚀 Déploiement Rapide

### Frontend (Firebase Hosting - Gratuit)
Le frontend est déjà déployé : **https://book-recommander-sarah.web.app**

### Backend (À déployer)

#### Option 1: Render (Recommandé - Gratuit)
1. Créer un compte sur [Render.com](https://render.com)
2. Connecter votre repository GitHub
3. Créer un Web Service avec ces paramètres:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free

#### Option 2: Railway (€5/mois)
1. Aller sur [Railway.app](https://railway.app)
2. Connecter GitHub et déployer le dossier `backend/`

#### Option 3: Google Cloud Run (Gratuit avec limites)
1. Activer la facturation Google Cloud
2. Utiliser le dossier `cloud-run-backend/`
3. Déployer avec `gcloud run deploy`

### Configuration Post-Déploiement

1. **Mettre à jour l'URL de l'API** dans `frontend/.env`:
   ```
   REACT_APP_API_URL=https://votre-api-deployee.onrender.com
   ```

2. **Redéployer le frontend** sur Firebase:
   ```bash
   cd frontend
   npm run build
   firebase deploy --only hosting
   ```

## 🛠️ Développement Local

### Prérequis
- Node.js 18+
- Python 3.11+
- Git

### Installation

1. **Cloner le repository**
   ```bash
   git clone <votre-repo>
   cd book-recommander
   ```

2. **Backend**
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # ou .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   python main.py
   ```

3. **Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Accéder à l'application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - Documentation API: http://localhost:8000/docs

## 📊 Dataset

- **56,323 livres français** au format Parquet (32MB)
- Métadonnées complètes: titre, auteur, genres, mots-clés, notes, popularité
- Recherche optimisée avec pandas et scoring intelligent
- Support multilingue (français, anglais, espagnol, allemand, italien, portugais)

## 🏗️ Architecture

```
book-recommander/
├── frontend/                 # React + Vite
│   ├── src/
│   │   ├── App.jsx          # Interface principale
│   │   ├── BookDatabase.js  # API client
│   │   └── index.css        # Styles glassmorphism
│   └── dist/                # Build de production
├── backend/                 # FastAPI + Pandas
│   ├── main.py             # API principale
│   ├── books_french.parquet # Dataset 56k livres
│   └── requirements.txt
├── cloud-run-backend/      # Version Google Cloud Run
└── functions/              # Firebase Functions (optionnel)
```

## 🎨 Design

- **Glassmorphism** avec effets de verre et flou
- **Responsive** pour mobile et desktop  
- **Animations fluides** et transitions CSS
- **Thème sombre** avec particules animées
- **Interface multilingue** automatique

## 📈 Performance

- **Recherche rapide** avec indexation pandas
- **Scoring intelligent** (titre x5, auteur x3, mots-clés x2, genres x1)
- **Fallback local** si l'API n'est pas disponible
- **Optimisations** pour 56k+ livres en mémoire

## 🔧 API Endpoints

- `GET /` - Informations sur l'API et statistiques
- `POST /recommend` - Recherche de livres par mots-clés
- `GET /random-unknown` - Livre aléatoire méconnu
- `GET /stats` - Statistiques détaillées du dataset
- `GET /docs` - Documentation Swagger interactive

## 📝 Licence

MIT License - Voir le fichier LICENSE pour plus de détails.

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à ouvrir une issue ou une pull request.

---

**Développé avec ❤️ pour les amoureux des livres**
