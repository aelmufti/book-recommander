from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import pandas as pd
import re
import os

app = FastAPI(title="Book Finder API - Cloud Run", description="56k+ livres français")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chargement des données au démarrage
books_df = None

def load_books_data():
    """Charger les 56k livres français depuis le parquet"""
    global books_df
    
    try:
        parquet_file = "books_french.parquet"
        
        if not os.path.exists(parquet_file):
            print(f"❌ Fichier {parquet_file} non trouvé")
            return False
        
        print(f"📊 Chargement de {parquet_file}...")
        books_df = pd.read_parquet(parquet_file)
        
        # Nettoyer les données
        books_df = books_df.dropna(subset=['title', 'authors'])
        books_df['keywords'] = books_df['keywords'].fillna('')
        books_df['genres'] = books_df['genres'].fillna('')
        
        print(f"✅ {len(books_df):,} livres chargés en mémoire")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du chargement : {e}")
        return False

# Charger les données au démarrage
load_success = load_books_data()

class RecommendRequest(BaseModel):
    prompt: str
    language: Optional[str] = "fre"
    use_llm: Optional[bool] = False

def search_books_pandas(prompt: str, language: str = "fre", limit: int = 20):
    """Recherche dans les 56k livres avec pandas"""
    global books_df
    
    if books_df is None or books_df.empty:
        return []
    
    # Nettoyer et préparer la requête
    prompt_clean = re.sub(r'[^\w\s]', ' ', prompt.lower())
    keywords = [k.strip() for k in prompt_clean.split() if len(k.strip()) > 2]
    
    if not keywords:
        return []
    
    # Filtrer par langue si spécifié
    df_filtered = books_df.copy()
    if language and language != 'all':
        if ',' in language:
            langs = [l.strip() for l in language.split(',')]
            df_filtered = df_filtered[df_filtered['language'].isin(langs)]
        else:
            df_filtered = df_filtered[df_filtered['language'] == language]
    
    # Recherche vectorisée avec pandas
    results = []
    
    # Créer un texte de recherche pour chaque livre
    search_texts = (
        df_filtered['title'].fillna('').str.lower() + ' ' +
        df_filtered['authors'].fillna('').str.lower() + ' ' +
        df_filtered['keywords'].fillna('').str.lower() + ' ' +
        df_filtered['genres'].fillna('').str.lower()
    )
    
    # Calculer les scores pour chaque mot-clé
    total_scores = pd.Series(0, index=df_filtered.index)
    
    for keyword in keywords:
        # Bonus pour titre (x5)
        title_matches = df_filtered['title'].fillna('').str.lower().str.contains(keyword, regex=False)
        total_scores += title_matches * 5
        
        # Bonus pour auteur (x3)
        author_matches = df_filtered['authors'].fillna('').str.lower().str.contains(keyword, regex=False)
        total_scores += author_matches * 3
        
        # Bonus pour mots-clés (x2)
        keyword_matches = df_filtered['keywords'].fillna('').str.lower().str.contains(keyword, regex=False)
        total_scores += keyword_matches * 2
        
        # Score normal pour genres (x1)
        genre_matches = df_filtered['genres'].fillna('').str.lower().str.contains(keyword, regex=False)
        total_scores += genre_matches * 1
    
    # Garder seulement les livres avec un score > 0
    matching_indices = total_scores[total_scores > 0].index
    
    if len(matching_indices) == 0:
        return []
    
    # Créer le DataFrame des résultats
    results_df = df_filtered.loc[matching_indices].copy()
    results_df['score'] = total_scores[matching_indices]
    
    # Trier par score puis par popularité
    results_df = results_df.sort_values(['score', 'ratings_count'], ascending=[False, False])
    
    # Convertir en liste de dictionnaires
    books_list = []
    for _, book in results_df.head(limit).iterrows():
        book_dict = {
            'title': book['title'],
            'authors': book['authors'],
            'genres': book.get('genres', ''),
            'keywords': book.get('keywords', ''),
            'avg_rating': float(book.get('avg_rating', 0)) if pd.notna(book.get('avg_rating')) else None,
            'ratings_count': int(book.get('ratings_count', 0)) if pd.notna(book.get('ratings_count')) else 0,
            'popularity_tier': book.get('popularity_tier', 'unknown'),
            'language': book.get('language', 'fre'),
            'first_publish_date': int(book.get('first_publish_date', 0)) if pd.notna(book.get('first_publish_date')) and str(book.get('first_publish_date')).isdigit() else None,
            'score': int(book['score'])
        }
        books_list.append(book_dict)
    
    return books_list

@app.post("/api/recommend")
async def recommend(request: RecommendRequest):
    """Endpoint de recommandation avec 56k livres"""
    try:
        books = search_books_pandas(request.prompt, request.language)
        
        response = {
            "recommendation": f"{books[0]['title']} - {books[0]['authors']}" if books else None,
            "book": books[0] if books else None,
            "keywords_used": request.prompt.split() if request.prompt else [],
            "candidates_count": len(books),
            "all_candidates": books[:10],
            "language": request.language,
            "llm_used": False,
            "semantic_used": False,
            "meilisearch_used": False,
            "firestore_used": False,
            "demo_mode": False,
            "dataset_size": len(books_df) if books_df is not None else 0,
            "platform": "Cloud Run + Pandas"
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/")
async def root():
    """Endpoint racine avec stats du dataset"""
    return {
        "status": "ready",
        "message": "Book Finder API - 56k livres français",
        "dataset_size": len(books_df) if books_df is not None else 0,
        "platform": "Google Cloud Run",
        "demo_mode": False,
        "data_loaded": books_df is not None
    }

@app.get("/api/random-unknown")
async def random_unknown(language: str = "fre"):
    """Livre aléatoire depuis les 56k livres"""
    global books_df
    
    if books_df is None or books_df.empty:
        return {"book": None}
    
    try:
        # Filtrer par langue
        df_filtered = books_df.copy()
        if language != 'all':
            df_filtered = df_filtered[df_filtered['language'] == language]
        
        # Prendre les livres moins connus
        unknown_books = df_filtered[
            df_filtered['popularity_tier'].isin(['unknown', 'obscure', 'niche']) |
            (df_filtered['ratings_count'] < 1000)
        ]
        
        if unknown_books.empty:
            unknown_books = df_filtered
        
        # Sélectionner un livre aléatoire
        random_book = unknown_books.sample(n=1).iloc[0]
        
        book_dict = {
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
        
        return {"book": book_dict}
        
    except Exception as e:
        return {"book": None, "error": str(e)}

@app.get("/api/stats")
async def stats():
    """Statistiques du dataset"""
    global books_df
    
    if books_df is None:
        return {"error": "Dataset not loaded"}
    
    try:
        stats = {
            "total_books": len(books_df),
            "languages": books_df['language'].value_counts().to_dict(),
            "popularity_tiers": books_df['popularity_tier'].value_counts().to_dict(),
            "avg_rating_distribution": {
                "mean": float(books_df['avg_rating'].mean()) if books_df['avg_rating'].notna().any() else None,
                "median": float(books_df['avg_rating'].median()) if books_df['avg_rating'].notna().any() else None
            },
            "top_authors": books_df['authors'].value_counts().head(10).to_dict()
        }
        return stats
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)