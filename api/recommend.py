from http.server import BaseHTTPRequestHandler
import json
import os
import sqlite3
import tempfile

# Dataset d'exemple pour Vercel (limité mais fonctionnel)
SAMPLE_BOOKS = [
    {
        "title": "Le Petit Prince",
        "authors": "Antoine de Saint-Exupéry", 
        "genres": "Fiction, Jeunesse",
        "keywords": "prince, planète, rose, renard",
        "avg_rating": 4.5,
        "ratings_count": 50000,
        "popularity_tier": "popular",
        "language": "fre"
    },
    {
        "title": "Harry Potter à l'école des sorciers",
        "authors": "J.K. Rowling",
        "genres": "Fantasy, Jeunesse", 
        "keywords": "magie, sorcier, école, amitié",
        "avg_rating": 4.7,
        "ratings_count": 120000,
        "popularity_tier": "popular",
        "language": "fre"
    },
    {
        "title": "1984",
        "authors": "George Orwell",
        "genres": "Science Fiction, Dystopie",
        "keywords": "surveillance, totalitarisme, liberté",
        "avg_rating": 4.2,
        "ratings_count": 80000,
        "popularity_tier": "popular", 
        "language": "eng"
    },
    {
        "title": "L'Étranger",
        "authors": "Albert Camus",
        "genres": "Fiction, Philosophie",
        "keywords": "absurde, étranger, société",
        "avg_rating": 4.1,
        "ratings_count": 30000,
        "popularity_tier": "known",
        "language": "fre"
    },
    {
        "title": "Dune",
        "authors": "Frank Herbert",
        "genres": "Science Fiction",
        "keywords": "épice, désert, politique, prophétie",
        "avg_rating": 4.6,
        "ratings_count": 45000,
        "popularity_tier": "popular",
        "language": "eng"
    },
    {
        "title": "Le Seigneur des anneaux",
        "authors": "J.R.R. Tolkien",
        "genres": "Fantasy, Épique",
        "keywords": "anneau, hobbit, aventure, magie",
        "avg_rating": 4.8,
        "ratings_count": 150000,
        "popularity_tier": "popular",
        "language": "eng"
    }
]

def search_books(prompt, language=None):
    """Recherche simple dans le dataset d'exemple"""
    prompt_lower = prompt.lower()
    keywords = prompt_lower.split()
    
    results = []
    for book in SAMPLE_BOOKS:
        # Filtrer par langue si spécifié
        if language and language != 'all' and book['language'] != language:
            continue
            
        # Calculer le score de correspondance
        score = 0
        searchable_text = f"{book['title']} {book['authors']} {book['keywords']}".lower()
        
        for keyword in keywords:
            if keyword in searchable_text:
                score += 1
        
        if score > 0:
            results.append((book, score))
    
    # Trier par score puis par popularité
    results.sort(key=lambda x: (x[1], x[0]['ratings_count']), reverse=True)
    
    return [book for book, score in results]

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Headers CORS
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        try:
            # Lire le body de la requête
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            prompt = data.get('prompt', '')
            language = data.get('language', 'fre')
            
            # Rechercher les livres
            books = search_books(prompt, language)
            
            # Préparer la réponse
            response = {
                "recommendation": f"{books[0]['title']} - {books[0]['authors']}" if books else None,
                "book": books[0] if books else None,
                "keywords_used": prompt.split(),
                "candidates_count": len(books),
                "all_candidates": books[:10],  # Limiter à 10 résultats
                "language": language,
                "llm_used": False,
                "semantic_used": False,
                "meilisearch_used": False,
                "demo_mode": True,
                "message": "Version démo avec 6 livres d'exemple"
            }
            
            self.wfile.write(json.dumps(response, ensure_ascii=False).encode('utf-8'))
            
        except Exception as e:
            error_response = {
                "error": str(e),
                "recommendation": None,
                "book": None
            }
            self.wfile.write(json.dumps(error_response).encode('utf-8'))
    
    def do_OPTIONS(self):
        # Gérer les requêtes preflight CORS
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(b'')