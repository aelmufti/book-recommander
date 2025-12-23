from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import re
from functions_framework import create_app

app = FastAPI(title="Book Finder API - Firebase")

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dataset intégré avec des livres français populaires
BOOKS_DATABASE = [
    {
        "title": "Le Petit Prince",
        "authors": "Antoine de Saint-Exupéry",
        "genres": "Fiction, Jeunesse",
        "keywords": "prince planète rose renard amitié voyage",
        "avg_rating": 4.5,
        "ratings_count": 50000,
        "popularity_tier": "popular",
        "language": "fre",
        "first_publish_date": 1943
    },
    {
        "title": "Harry Potter à l'école des sorciers",
        "authors": "J.K. Rowling",
        "genres": "Fantasy, Jeunesse",
        "keywords": "magie sorcier école amitié poudlard",
        "avg_rating": 4.7,
        "ratings_count": 120000,
        "popularity_tier": "popular",
        "language": "fre",
        "first_publish_date": 1997
    },
    {
        "title": "1984",
        "authors": "George Orwell",
        "genres": "Science Fiction, Dystopie",
        "keywords": "surveillance totalitarisme liberté big brother",
        "avg_rating": 4.2,
        "ratings_count": 80000,
        "popularity_tier": "popular",
        "language": "eng",
        "first_publish_date": 1949
    },
    {
        "title": "L'Étranger",
        "authors": "Albert Camus",
        "genres": "Fiction, Philosophie",
        "keywords": "absurde étranger société existentialisme",
        "avg_rating": 4.1,
        "ratings_count": 30000,
        "popularity_tier": "known",
        "language": "fre",
        "first_publish_date": 1942
    },
    {
        "title": "Dune",
        "authors": "Frank Herbert",
        "genres": "Science Fiction",
        "keywords": "épice désert politique prophétie arrakis",
        "avg_rating": 4.6,
        "ratings_count": 45000,
        "popularity_tier": "popular",
        "language": "eng",
        "first_publish_date": 1965
    },
    {
        "title": "Le Seigneur des anneaux",
        "authors": "J.R.R. Tolkien",
        "genres": "Fantasy, Épique",
        "keywords": "anneau hobbit aventure magie terre milieu",
        "avg_rating": 4.8,
        "ratings_count": 150000,
        "popularity_tier": "popular",
        "language": "eng",
        "first_publish_date": 1954
    },
    {
        "title": "Les Misérables",
        "authors": "Victor Hugo",
        "genres": "Fiction, Historique",
        "keywords": "révolution paris jean valjean justice",
        "avg_rating": 4.4,
        "ratings_count": 25000,
        "popularity_tier": "known",
        "language": "fre",
        "first_publish_date": 1862
    },
    {
        "title": "Madame Bovary",
        "authors": "Gustave Flaubert",
        "genres": "Fiction, Classique",
        "keywords": "femme mariage ennui province réalisme",
        "avg_rating": 3.9,
        "ratings_count": 18000,
        "popularity_tier": "known",
        "language": "fre",
        "first_publish_date": 1857
    },
    {
        "title": "Cent ans de solitude",
        "authors": "Gabriel García Márquez",
        "genres": "Réalisme magique",
        "keywords": "famille solitude amérique latine magie",
        "avg_rating": 4.3,
        "ratings_count": 35000,
        "popularity_tier": "known",
        "language": "spa",
        "first_publish_date": 1967
    },
    {
        "title": "Don Quichotte",
        "authors": "Miguel de Cervantes",
        "genres": "Fiction, Classique",
        "keywords": "chevalier aventure espagne rêve",
        "avg_rating": 4.0,
        "ratings_count": 20000,
        "popularity_tier": "known",
        "language": "spa",
        "first_publish_date": 1605
    }
]

class RecommendRequest(BaseModel):
    prompt: str
    language: Optional[str] = "fre"
    use_llm: Optional[bool] = False

def search_books_local(prompt: str, language: str = "fre", limit: int = 10):
    """Recherche dans le dataset local"""
    
    # Nettoyer et préparer la requête
    prompt_clean = re.sub(r'[^\w\s]', ' ', prompt.lower())
    keywords = [k.strip() for k in prompt_clean.split() if len(k.strip()) > 2]
    
    if not keywords:
        return []
    
    results = []
    for book in BOOKS_DATABASE:
        # Filtrer par langue si spécifié
        if language and language != 'all':
            if ',' in language:
                langs = [l.strip() for l in language.split(',')]
                if book['language'] not in langs:
                    continue
            elif book['language'] != language:
                continue
        
        # Calculer le score de correspondance
        score = 0
        searchable_text = f"{book.get('title', '')} {book.get('authors', '')} {book.get('keywords', '')} {book.get('genres', '')}".lower()
        
        for keyword in keywords:
            if keyword in searchable_text:
                # Bonus pour titre
                if keyword in book.get('title', '').lower():
                    score += 5
                # Bonus pour auteur
                elif keyword in book.get('authors', '').lower():
                    score += 3
                # Bonus pour mots-clés
                elif keyword in book.get('keywords', '').lower():
                    score += 2
                else:
                    score += 1
        
        if score > 0:
            book_copy = book.copy()
            book_copy['score'] = score
            results.append(book_copy)
    
    # Trier par score puis par popularité
    results.sort(key=lambda x: (x['score'], x.get('ratings_count', 0)), reverse=True)
    
    return results[:limit]

@app.post("/api/recommend")
async def recommend(request: RecommendRequest):
    """Endpoint de recommandation de livres"""
    try:
        books = search_books_local(request.prompt, request.language)
        
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
            "dataset_size": len(BOOKS_DATABASE)
        }
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/")
async def root():
    """Endpoint racine"""
    return {
        "status": "ready",
        "message": "Book Finder API - Firebase Functions",
        "dataset_size": len(BOOKS_DATABASE),
        "platform": "Firebase Functions",
        "demo_mode": False
    }

@app.get("/api/random-unknown")
async def random_unknown(language: str = "fre"):
    """Livre aléatoire"""
    try:
        # Filtrer par langue
        filtered_books = [book for book in BOOKS_DATABASE 
                         if language == 'all' or book['language'] == language]
        
        if filtered_books:
            import random
            random_book = random.choice(filtered_books)
            return {"book": random_book}
        
        return {"book": None}
        
    except Exception as e:
        return {"book": None, "error": str(e)}

# Créer l'app pour Firebase Functions
firebase_app = create_app(app)