# Book Finder 📚

Moteur de recherche de livres intelligent avec 43+ millions de livres issus d'OpenLibrary.

## 🚀 Déploiement gratuit

Votre projet est maintenant prêt pour le déploiement gratuit ! Trois options disponibles :

### 1. **Railway** (Recommandé) 🚂
- **500h/mois gratuit** - Backend + Frontend + DB
- Configuration automatique
- `./deploy.sh` puis choisir option 1

### 2. **Vercel + Supabase** ⚡
- Frontend illimité + API Functions + PostgreSQL 500MB
- `./deploy.sh` puis choisir option 2

### 3. **Render** 🎨
- Services séparés Backend/Frontend
- `./deploy.sh` puis choisir option 3

## 📊 Optimisation des données

Avant le déploiement, optimisez vos données :
```bash
python optimize-data.py
```
Réduit le dataset pour respecter les limites gratuites (200k livres max).

## 📁 Fichiers de déploiement créés

- `Dockerfile` - Configuration Railway
- `railway.json` - Config Railway
- `vercel.json` - Config Vercel
- `database_adapter.py` - Support PostgreSQL/DuckDB
- `deploy.sh` - Script de déploiement interactif
- `optimize-data.py` - Optimisation des données

## Fonctionnalités

- **Recherche par mots-clés** : système de tags intuitif (Espace/Entrée pour ajouter, Backspace pour supprimer)
- **Multi-langues** : recherche dans 6 langues (FR, EN, ES, DE, IT, PT), sélection multiple possible
- **Enrichissement IA** : les requêtes sont enrichies par Ollama/Llama3 pour de meilleurs résultats
- **Interface Liquid Glass** : design moderne avec effets de verre transparent et distorsion SVG
- **Détection automatique** : l'interface s'adapte à la langue du navigateur

## Architecture

```
book-recommander/
├── backend/
│   ├── main.py                    # API FastAPI
│   ├── large_scale_recommender.py # Moteur de recherche
│   ├── books.duckdb               # Base indexée (7.3GB)
│   ├── openlibrary_books.parquet  # Dataset brut (3.9GB)
│   ├── generate_embeddings_safe.py # Génération embeddings
│   └── merge_embeddings.py        # Création index FAISS
├── frontend/
│   ├── src/App.jsx                # Interface React
│   └── src/index.css              # Styles Liquid Glass
└── README.md
```

## Dataset

- **Source** : OpenLibrary Data Dumps
- **43,6 millions de livres** avec :
  - Titre, auteurs, genres, mots-clés
  - Notes moyennes et nombre d'avis
  - Tier de popularité (popular, known, niche, obscure)
  - Langue (code ISO)

Les noms d'auteurs sont inclus dans les mots-clés (prénom et nom séparés) pour améliorer la recherche.

## Recherche

### Actuelle (SQL)
- Recherche dans la vue `popular_books` (2.4M livres popular/known)
- Opérateur AND entre les mots-clés
- Fallback sur la table complète si peu de résultats
- Temps de réponse : ~0.5-1s

### En cours (Embeddings)
- Modèle : `all-MiniLM-L6-v2`
- 4.6M livres (tiers popular, known, niche)
- Index FAISS pour recherche sémantique
- Permettra des recherches plus flexibles ("livres comme 1984" → dystopie, surveillance, etc.)

## Installation

### Backend
```bash
cd backend
pip install -r requirements.txt
# Ollama pour l'enrichissement IA (optionnel)
ollama pull llama3
# Lancer l'API
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## API

### POST /recommend
```json
{
  "prompt": "philosophie marx",
  "language": "fre",      // ou "fre,eng" ou "all"
  "use_llm": true
}
```

Réponse :
```json
{
  "recommendation": { ... },
  "keywords_used": ["philosophie", "marx", "communisme"],
  "candidates_count": 15,
  "all_candidates": [ ... ],
  "llm_used": true
}
```

## Stack technique

- **Backend** : Python, FastAPI, DuckDB, Sentence-Transformers, FAISS
- **Frontend** : React, Vite, Tailwind CSS
- **IA** : Ollama (Llama3) pour l'enrichissement des requêtes
- **Data** : OpenLibrary dumps (domaine public)

## Contraintes

- Budget : 0€ (APIs et données gratuites uniquement)
- RAM : 16GB (génération embeddings optimisée par chunks)
- GPU : Apple Silicon MPS (batch=128 optimal)
