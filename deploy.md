# 🚀 Guide de Déploiement

## 📦 Structure de Production

```
book-recommender/
├── backend/                    # API FastAPI
│   ├── main.py                # Application principale
│   ├── large_scale_recommender.py
│   ├── openlibrary_books.parquet  # Dataset (100K+ livres)
│   └── requirements.txt
├── frontend/                   # Interface React
│   ├── dist/                  # Build de production
│   └── package.json
└── README.md
```

## 🌐 Options de Déploiement Gratuit

### 1. **Vercel** (Recommandé)
```bash
# Frontend
cd frontend
npm run build
vercel --prod

# Backend (Vercel Functions)
cd backend
vercel --prod
```

### 2. **Railway**
```bash
# Déploiement full-stack
railway login
railway init
railway up
```

### 3. **Render**
- Frontend: Static Site
- Backend: Web Service
- Dataset: Inclus dans le build

## ⚙️ Variables d'Environnement

```env
# Backend
OLLAMA_URL=http://localhost:11434
PORT=8000

# Frontend  
VITE_API_URL=https://your-backend-url.com
```

## 📊 Dataset

Le fichier `openlibrary_books.parquet` (8MB) contient :
- **100,000 livres** internationaux
- **Genres en anglais** 
- **Format optimisé** pour des requêtes rapides

## 🔧 Ollama en Production

### Option 1: Ollama Cloud (Futur)
Attendre le service cloud officiel d'Ollama.

### Option 2: Serveur Dédié
```bash
# Sur un VPS
ollama serve --host 0.0.0.0
ollama pull llama3
```

### Option 3: API Alternative
Remplacer Ollama par OpenAI API ou Anthropic Claude.

## 🚀 Déploiement Rapide

1. **Build Frontend**
   ```bash
   cd frontend
   npm run build
   ```

2. **Préparer Backend**
   ```bash
   cd backend
   # Le dataset est déjà inclus
   ```

3. **Déployer**
   - Frontend → Vercel/Netlify
   - Backend → Railway/Render
   - Dataset → Inclus automatiquement

## 💡 Optimisations

- **Compression**: Le dataset Parquet est déjà optimisé
- **Cache**: DuckDB met en cache les requêtes
- **CDN**: Vercel/Netlify fournissent un CDN gratuit
- **Scaling**: Le système supporte des millions de requêtes

## 🔗 URLs de Production

- **Frontend**: `https://book-recommender.vercel.app`
- **Backend**: `https://book-recommender-api.railway.app`
- **Docs**: `https://book-recommender-api.railway.app/docs`