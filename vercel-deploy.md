# Déploiement Vercel + Supabase 🚀

## Architecture
- **Frontend** : Vercel (React/Vite)
- **Backend** : Vercel Functions (API Routes)
- **Base de données** : Supabase PostgreSQL (gratuit)

## Avantages
- **Frontend illimité** sur Vercel
- **Base PostgreSQL** 500MB gratuit sur Supabase
- **Déploiement automatique** depuis Git
- **Edge Functions** rapides

## 📋 Configuration

### 1. Structure pour Vercel
```
book-recommander/
├── api/                    # Vercel Functions
│   └── recommend.py
├── frontend/              # React app
└── vercel.json           # Config Vercel
```

### 2. Créer vercel.json
```json
{
  "builds": [
    {
      "src": "frontend/package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    },
    {
      "src": "api/*.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/$1"
    },
    {
      "src": "/(.*)",
      "dest": "/frontend/$1"
    }
  ]
}
```

### 3. API Function (api/recommend.py)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import psycopg2
import json

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"])

def handler(request):
    # Logique de recommandation simplifiée
    # Connexion Supabase via DATABASE_URL
    pass
```

## 🗄️ Configuration Supabase

### 1. Créer un projet Supabase
1. Aller sur [supabase.com](https://supabase.com)
2. Créer un nouveau projet
3. Récupérer l'URL et la clé API

### 2. Migrer les données
```sql
-- Dans l'éditeur SQL Supabase
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    title TEXT,
    authors TEXT,
    genres TEXT,
    keywords TEXT,
    avg_rating FLOAT,
    ratings_count INTEGER,
    popularity_tier TEXT,
    language TEXT,
    first_publish_date INTEGER
);

-- Créer un index pour les recherches
CREATE INDEX idx_books_search ON books USING gin(to_tsvector('english', title || ' ' || authors || ' ' || keywords));
```

## 🚀 Déploiement

### 1. Variables d'environnement Vercel
```bash
vercel env add SUPABASE_URL
vercel env add SUPABASE_ANON_KEY
vercel env add DATABASE_URL
```

### 2. Déployer
```bash
# Installer Vercel CLI
npm i -g vercel

# Déployer
vercel --prod
```

## 📊 Limitations gratuites

### Vercel
- **100GB bande passante/mois**
- **1000 déploiements/mois**
- **Functions : 100GB-Hrs/mois**

### Supabase
- **500MB base de données**
- **2GB bande passante/mois**
- **50MB stockage fichiers**

## 💡 Optimisations

### Réduire la taille des données
```python
# Garder seulement 100k livres les plus populaires
df_top = df.nlargest(100000, 'ratings_count')
```

### Cache avec Vercel Edge Config
```javascript
// Cacher les recherches populaires
import { get } from '@vercel/edge-config';

export default async function handler(req, res) {
  const cached = await get(req.query.prompt);
  if (cached) return res.json(cached);
  
  // Sinon, faire la recherche...
}
```