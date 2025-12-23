# Déploiement sur Railway 🚂

## Pourquoi Railway ?
- **500h/mois gratuit** (suffisant pour un projet personnel)
- **Support natif** Python + React
- **Base de données** PostgreSQL incluse
- **Déploiement automatique** depuis GitHub
- **Variables d'environnement** intégrées

## 📋 Préparation du projet

### 1. Adapter le backend pour PostgreSQL

Railway ne supporte pas DuckDB en production. Il faut migrer vers PostgreSQL :

```python
# backend/database.py (nouveau fichier)
import os
import psycopg2
from sqlalchemy import create_engine
import pandas as pd

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def migrate_data():
    """Migrer les données de DuckDB vers PostgreSQL"""
    # Lire depuis le parquet
    df = pd.read_parquet("openlibrary_books.parquet")
    
    # Écrire vers PostgreSQL
    df.to_sql("books", engine, if_exists="replace", index=False)
```

### 2. Créer les fichiers de configuration

```dockerfile
# Dockerfile (backend)
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```json
// railway.json
{
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT"
  }
}
```

## 🚀 Étapes de déploiement

### 1. Préparer le repository
```bash
# Ajouter les fichiers de config
git add railway.json Dockerfile
git commit -m "Add Railway deployment config"
git push origin main
```

### 2. Déployer sur Railway
1. Aller sur [railway.app](https://railway.app)
2. Se connecter avec GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Sélectionner votre repository
5. Railway détecte automatiquement Python + React

### 3. Configurer les services
Railway créera automatiquement :
- **Backend** : Service Python (port 8000)
- **Frontend** : Service Node.js (port 3000)
- **Database** : PostgreSQL

### 4. Variables d'environnement
Dans Railway dashboard :
```
DATABASE_URL=postgresql://... (auto-généré)
OLLAMA_URL=https://your-ollama-service.com (optionnel)
```

## 📊 Limitations gratuites
- **500h/mois** (~16h/jour)
- **1GB RAM** par service
- **1GB stockage** base de données
- **100GB bande passante**

## 🔧 Optimisations

### Réduire la taille des données
```python
# Garder seulement les livres populaires
df_filtered = df[df['popularity_tier'].isin(['popular', 'known'])]
df_filtered.to_parquet("books_optimized.parquet")
```

### Cache Redis (optionnel)
Railway propose Redis gratuit pour le cache des recherches.

## 🌐 URLs finales
- **Frontend** : `https://your-app.up.railway.app`
- **API** : `https://your-api.up.railway.app`
- **Docs** : `https://your-api.up.railway.app/docs`