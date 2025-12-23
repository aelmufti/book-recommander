# 📚 Backend - Book Recommender API

API FastAPI pour les recommandations de livres avec OpenLibrary et Ollama.

## 🚀 Démarrage rapide

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Démarrer le serveur
python start.py
```

## 📋 Prérequis

### Ollama
```bash
# Installer Ollama
brew install ollama  # macOS
# ou télécharger depuis ollama.com

# Démarrer Ollama
ollama serve

# Installer les modèles
ollama pull llama3
```

### Dataset
Le fichier `openlibrary_books.parquet` doit être présent (100K+ livres).

## 🌐 Endpoints

### `POST /recommend`
Recommandation de livre basée sur une description.

**Request:**
```json
{
  "prompt": "fantasy adventure with magic"
}
```

**Response:**
```json
{
  "recommendation": "The Lord of the Rings - J.R.R. Tolkien",
  "genres": ["Fantasy", "Adventure", "Epic Fantasy"],
  "candidates_count": 15,
  "reasoning": "Fantasy and adventure themes match perfectly",
  "dataset_size": 100000
}
```

### `GET /stats`
Statistiques du dataset.

### `GET /docs`
Documentation interactive Swagger.

## 🏗️ Architecture

```
FastAPI → LargeScaleRecommender → DuckDB (Parquet) → Ollama LLM
```

1. **Classification des genres** avec Ollama
2. **Recherche rapide** avec DuckDB sur Parquet
3. **Sélection intelligente** avec LLM

## 📊 Performance

- **100K+ livres** internationaux
- **Requêtes en millisecondes** avec DuckDB
- **Genres intelligents** avec classification LLM
- **Recommandations précises** avec sélection LLM

## 🔧 Configuration

Le recommender utilise automatiquement :
- `openlibrary_books.parquet` pour les données
- `http://localhost:11434` pour Ollama
- Port `8000` pour l'API