#!/usr/bin/env python3
"""
Book Finder API - Version propre pour Render
Utilise uniquement pandas + parquet (pas de DuckDB)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
import re
from typing import Optional

# Configuration FastAPI
app = FastAPI(
    title="Book Finder API",
    description="API de recherche dans 25k livres français",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variable globale pour le dataset
books_df = None

def load_dataset():
    """Charger le dataset de 25k livres français"""
    global books_df
    
    try:
        parquet_path = "books_25k.parquet"
        
        if not os.path.exists(parquet_path):
            print(f"❌ Fichier {parquet_path} introuvable")
            return False
        
        print(f"📊 Chargement du dataset: {parquet_path}")
        books_df = pd.read_parquet(parquet_path)
        
        # Nettoyage des données
        books_df = books_df.dropna(subset=['title', 'authors'])
        books_df['keywords'] = books_df['keywords'].fillna('')
        books_df['genres'] = books_df['genres'].fillna('')
        
        print(f"✅ Dataset chargé: {len(books_df):,} livres")
        return True
        
    except Exception as e:
        print(f"❌ Erreur chargement dataset: {e}")
        return False

# Charger le dataset au démarrage
print("🚀 Initialisation de l'API Book Finder...")
dataset_loaded = load_dataset()

if not dataset_loaded:
    print("⚠️ Dataset non chargé - Mode dégradé")

class SearchRequest(BaseModel):
    prompt: str
    language: Optional[str] = "fre"
    use_llm: Optional[bool] = False

def search_in_dataset(query: str, language: str = "fre", max_results: int = 20):
    """Recherche dans le dataset avec pandas"""
    global books_df
    
    if books_df is None or books_df.empty:
        return []
    
    # Préparation de la requête
    query_clean = re.sub(r'[^\w\s]', ' ', query.lower())
    terms = [term.strip() for term in query_clean.split() if len(term.strip()) > 2]
    
    if not terms:
        return []
    
    # Filtrage par langue
    df_work = books_df.copy()
    if language and language != 'all':
        if ',' in language:
            languages = [lang.strip() for lang in language.split(',')]
            df_work = df_work[df_work['language'].isin(languages)]
        else:
            df_work = df_work[df_work['language'] == language]
    
    # Calcul des scores de pertinence
    scores = pd.Series(0, index=df_work.index)
    
    for term in terms:
        # Score titre (x5)
        title_match = df_work['title'].fillna('').str.lower().str.contains(term, regex=False)
        scores += title_match * 5
        
        # Score auteur (x3)
        author_match = df_work['authors'].fillna('').str.lower().str.contains(term, regex=False)
        scores += author_match * 3
        
        # Score mots-clés (x2)
        keywords_match = df_work['keywords'].fillna('').str.lower().str.contains(term, regex=False)
        scores += keywords_match * 2
        
        # Score genres (x1)
        genres_match = df_work['genres'].fillna('').str.lower().str.contains(term, regex=False)
        scores += genres_match * 1
    
    # Sélection des résultats avec score > 0
    valid_indices = scores[scores > 0].index
    
    if len(valid_indices) == 0:
        return []
    
    # Création du DataFrame de résultats
    results_df = df_work.loc[valid_indices].copy()
    results_df['relevance_score'] = scores[valid_indices]
    
    # Tri par score puis par popularité
    results_df = results_df.sort_values(
        ['relevance_score', 'ratings_count'], 
        ascending=[False, False]
    )
    
    # Conversion en liste de dictionnaires
    books_list = []
    for _, book in results_df.head(max_results).iterrows():
        book_data = {
            'title': book['title'],
            'authors': book['authors'],
            'genres': book.get('genres', ''),
            'keywords': book.get('keywords', ''),
            'avg_rating': float(book.get('avg_rating', 0)) if pd.notna(book.get('avg_rating')) else None,
            'ratings_count': int(book.get('ratings_count', 0)) if pd.notna(book.get('ratings_count')) else 0,
            'popularity_tier': book.get('popularity_tier', 'unknown'),
            'language': book.get('language', 'fre'),
            'first_publish_date': int(book.get('first_publish_date', 0)) if pd.notna(book.get('first_publish_date')) and str(book.get('first_publish_date')).isdigit() else None,
            'score': int(book['relevance_score'])
        }
        books_list.append(book_data)
    
    return books_list

@app.get("/")
async def api_info():
    """Informations sur l'API"""
    return {
        "status": "ready" if books_df is not None else "degraded",
        "message": "Book Finder API - 25k livres français",
        "dataset_size": len(books_df) if books_df is not None else 0,
        "platform": "Render + Pandas",
        "version": "2.0.0",
        "data_loaded": books_df is not None
    }

@app.post("/recommend")
async def recommend_books(request: SearchRequest):
    """Recherche et recommandation de livres"""
    try:
        if books_df is None:
            raise HTTPException(status_code=503, detail="Dataset non disponible")
        
        results = search_in_dataset(request.prompt, request.language)
        
        response = {
            "recommendation": f"{results[0]['title']} - {results[0]['authors']}" if results else None,
            "book": results[0] if results else None,
            "keywords_used": request.prompt.split(),
            "candidates_count": len(results),
            "all_candidates": results[:10],
            "language": request.language,
            "llm_used": False,
            "semantic_used": False,
            "meilisearch_used": False,
            "firestore_used": False,
            "demo_mode": False,
            "dataset_size": len(books_df),
            "platform": "Render + Pandas v2.0"
        }
        
        return response
        
    except Exception as e:
        print(f"❌ Erreur dans /recommend: {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de recherche: {str(e)}")

@app.get("/random-unknown")
async def get_random_book(language: str = "fre"):
    """Livre aléatoire peu connu"""
    global books_df
    
    if books_df is None or books_df.empty:
        return {"book": None}
    
    try:
        # Filtrage par langue
        df_filtered = books_df.copy()
        if language != 'all':
            df_filtered = df_filtered[df_filtered['language'] == language]
        
        # Sélection des livres peu connus
        unknown_books = df_filtered[
            df_filtered['popularity_tier'].isin(['unknown', 'obscure', 'niche']) |
            (df_filtered['ratings_count'] < 1000)
        ]
        
        if unknown_books.empty:
            unknown_books = df_filtered
        
        # Livre aléatoire
        random_book = unknown_books.sample(n=1).iloc[0]
        
        book_data = {
            'title': random_book['title'],
            'authors': random_book['authors'],
            'genres': random_book.get('genres', ''),
            'keywords': random_book.get('keywords', ''),
            'avg_rating': float(random_book.get('avg_rating', 0)) if pd.notna(random_book.get('avg_rating')) else None,
            'ratings_count': int(random_book.get('ratings_count', 0)) if pd.notna(random_book.get('ratings_count')) else 0,
            'popularity_tier': random_book.get('popularity_tier', 'unknown'),
            'language': random_book.get('language', 'fre'),
            'first_publish_date': int(random_book.get('first_publish_date', 0)) if pd.notna(random_book.get('first_publish_date')) and str(random_book.get('first_publish_date')).isdigit() else None
        }
        
        return {"book": book_data}
        
    except Exception as e:
        return {"book": None, "error": str(e)}

@app.get("/stats")
async def dataset_stats():
    """Statistiques du dataset"""
    global books_df
    
    if books_df is None:
        return {"error": "Dataset non chargé"}
    
    try:
        stats_data = {
            "total_books": len(books_df),
            "languages": books_df['language'].value_counts().to_dict(),
            "popularity_tiers": books_df['popularity_tier'].value_counts().to_dict(),
            "avg_rating_stats": {
                "mean": float(books_df['avg_rating'].mean()) if books_df['avg_rating'].notna().any() else None,
                "median": float(books_df['avg_rating'].median()) if books_df['avg_rating'].notna().any() else None
            },
            "top_authors": books_df['authors'].value_counts().head(10).to_dict()
        }
        return stats_data
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    """Vérification de santé"""
    return {
        "status": "healthy" if books_df is not None else "unhealthy",
        "dataset_loaded": books_df is not None and not books_df.empty,
        "dataset_size": len(books_df) if books_df is not None else 0
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)