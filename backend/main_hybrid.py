#!/usr/bin/env python3
"""
Book Finder API - Version hybride sophistiquée
Combine Meilisearch + LLM (si disponible) avec fallback pandas
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import os
import re
import json
import requests
from typing import Optional, List, Dict
import math

# Configuration FastAPI
app = FastAPI(
    title="Book Finder API - Hybrid",
    description="API sophistiquée avec Meilisearch + LLM + fallback pandas",
    version="3.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variables globales
books_df = None
meilisearch_available = False
ollama_available = False
ollama_base_url = "http://localhost:11434"  # URL par défaut
meilisearch_client = None
meilisearch_index = None

class SearchRequest(BaseModel):
    prompt: str
    language: Optional[str] = "fre"
    use_llm: Optional[bool] = True

def check_meilisearch():
    """Vérifier si Meilisearch est disponible"""
    global meilisearch_available, meilisearch_client, meilisearch_index
    
    try:
        import meilisearch
        meilisearch_client = meilisearch.Client("http://127.0.0.1:7700")
        meilisearch_index = meilisearch_client.index("books")
        
        stats = meilisearch_index.get_stats()
        doc_count = stats.number_of_documents
        
        if doc_count > 0:
            print(f"✅ Meilisearch: {doc_count:,} books indexed")
            meilisearch_available = True
            return True
        else:
            print("⚠️ Meilisearch: No documents indexed")
            
    except Exception as e:
        print(f"⚠️ Meilisearch not available: {e}")
    
    meilisearch_available = False
    return False

def check_ollama():
    """Vérifier si Ollama ou Groq est disponible"""
    global ollama_available
    
    # Vérifier d'abord Groq API
    groq_api_key = os.environ.get("GROQ_API_KEY")
    if groq_api_key:
        try:
            headers = {"Authorization": f"Bearer {groq_api_key}"}
            r = requests.get("https://api.groq.com/openai/v1/models", headers=headers, timeout=5)
            if r.status_code == 200:
                print("✅ Groq API available")
                ollama_available = True
                return True
        except Exception as e:
            print(f"⚠️ Groq API test failed: {e}")
    
    # URLs Ollama à tester (local puis public)
    ollama_urls = [
        "http://localhost:11434/api/tags",  # Local
        "https://gtk-rangers-nevertheless-majority.trycloudflare.com/api/tags"  # Public
    ]
    
    for url in ollama_urls:
        try:
            print(f"🔍 Testing Ollama at: {url}")
            r = requests.get(url, timeout=15)  # Timeout plus long
            if r.status_code == 200:
                print(f"✅ Ollama available at: {url}")
                ollama_available = True
                # Stocker l'URL de base pour les requêtes
                global ollama_base_url
                ollama_base_url = url.replace('/api/tags', '')
                return True
            else:
                print(f"❌ Ollama responded with status {r.status_code}")
        except Exception as e:
            print(f"❌ Ollama test failed for {url}: {e}")
            continue
    
    print("⚠️ No LLM service available (Groq or Ollama)")
    ollama_available = False
    return False

def enrich_query_with_llm(user_input: str) -> Dict:
    """Enrichissement LLM sophistiqué de la requête"""
    if not ollama_available:
        return {
            "original": user_input, 
            "expanded": user_input, 
            "auteurs": [], 
            "oeuvres": [], 
            "mots_cles": user_input.split()
        }
    
    prompt = f"""Tu es un expert en littérature française et internationale. L'utilisateur cherche des livres avec: "{user_input}"

IMPORTANT: Tu DOIS remplir TOUTES les catégories, même si tu dois deviner.

Réponds UNIQUEMENT en JSON valide:
{{"auteurs": ["auteur1", "auteur2"], "oeuvres": ["titre exact 1", "titre exact 2"], "mots_cles": ["mot1", "mot2", "mot3", "mot4"]}}

EXEMPLES:
- "marx" → {{"auteurs": ["Karl Marx", "Friedrich Engels"], "oeuvres": ["Le Capital", "Manifeste du Parti communiste"], "mots_cles": ["communisme", "socialisme", "économie politique", "capitalisme"]}}
- "science fiction" → {{"auteurs": ["Isaac Asimov", "Philip K. Dick"], "oeuvres": ["Foundation", "Blade Runner"], "mots_cles": ["futur", "technologie", "espace", "robot"]}}
- "philosophie" → {{"auteurs": ["Platon", "Aristote", "Descartes"], "oeuvres": ["République", "Éthique à Nicomaque"], "mots_cles": ["pensée", "existence", "morale", "métaphysique"]}}

JSON pour "{user_input}":"""
    
    try:
        # Essayer d'abord Groq API (gratuit)
        groq_api_key = os.environ.get("GROQ_API_KEY")
        if groq_api_key:
            headers = {
                "Authorization": f"Bearer {groq_api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "messages": [{"role": "user", "content": prompt}],
                "model": "llama3-8b-8192",
                "temperature": 0.1,
                "max_tokens": 500
            }
            
            r = requests.post("https://api.groq.com/openai/v1/chat/completions", 
                            json=payload, headers=headers, timeout=10)
            
            if r.status_code == 200:
                response = r.json()
                content = response["choices"][0]["message"]["content"]
                
                # Extract JSON
                match = re.search(r'\{.*\}', content, re.DOTALL)
                if match:
                    data = json.loads(match.group())
                    
                    # Build expanded query
                    parts = [user_input]
                    parts.extend(data.get("auteurs", [])[:3])
                    parts.extend(data.get("oeuvres", [])[:2])
                    parts.extend(data.get("mots_cles", [])[:4])
                    
                    expanded = " ".join(parts)
                    
                    print(f"🤖 Groq LLM enriched: {user_input} → {expanded[:100]}...")
                    
                    return {
                        "original": user_input,
                        "expanded": expanded,
                        "auteurs": data.get("auteurs", []),
                        "oeuvres": data.get("oeuvres", []),
                        "mots_cles": data.get("mots_cles", [])
                    }
        
        # Fallback vers Ollama local/tunnel
        r = requests.post(f"{ollama_base_url}/api/generate", json={
            "model": "llama3.2",
            "prompt": prompt,
            "stream": False
        }, timeout=15)
        
        if r.status_code == 200:
            response = r.json().get("response", "")
            # Extract JSON
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                data = json.loads(match.group())
                
                # Build expanded query
                parts = [user_input]  # Keep original
                parts.extend(data.get("auteurs", [])[:3])
                parts.extend(data.get("oeuvres", [])[:2])
                parts.extend(data.get("mots_cles", [])[:4])
                
                expanded = " ".join(parts)
                
                print(f"🤖 Ollama LLM enriched: {user_input} → {expanded[:100]}...")
                
                return {
                    "original": user_input,
                    "expanded": expanded,
                    "auteurs": data.get("auteurs", []),
                    "oeuvres": data.get("oeuvres", []),
                    "mots_cles": data.get("mots_cles", [])
                }
    except Exception as e:
        print(f"⚠️ LLM error: {e}")
    
    return {
        "original": user_input, 
        "expanded": user_input, 
        "auteurs": [], 
        "oeuvres": [], 
        "mots_cles": user_input.split()
    }

def search_meilisearch(query: str, limit: int = 50, language: str = None) -> List[Dict]:
    """Recherche sophistiquée avec Meilisearch"""
    if not meilisearch_available:
        return []
    
    search_params = {
        "limit": limit,
        "attributesToRetrieve": [
            "title", "authors", "genres", "keywords",
            "avg_rating", "ratings_count", "popularity_tier", "language"
        ]
    }
    
    # Language filter
    filters = []
    if language and language != 'all':
        if ',' in language:
            langs = [l.strip() for l in language.split(',')]
            lang_filter = ' OR '.join([f'language = "{l}"' for l in langs])
            filters.append(f"({lang_filter})")
        else:
            filters.append(f'language = "{language}"')
    
    if filters:
        search_params["filter"] = " AND ".join(filters)
    
    try:
        results = meilisearch_index.search(query, search_params)
        
        books = []
        for hit in results['hits']:
            books.append({
                "title": hit.get('title', ''),
                "authors": hit.get('authors', ''),
                "genres": hit.get('genres', ''),
                "keywords": hit.get('keywords', ''),
                "avg_rating": hit.get('avg_rating'),
                "ratings_count": hit.get('ratings_count'),
                "popularity_tier": hit.get('popularity_tier', 'unknown'),
                "language": hit.get('language', '')
            })
        
        return books
    except Exception as e:
        print(f"⚠️ Meilisearch search error: {e}")
        return []

def recommend_sophisticated(user_input: str, language: str = None, use_llm: bool = True) -> Dict:
    """Système de recommandation sophistiqué avec Meilisearch + LLM"""
    print(f"🔍 Sophisticated search: '{user_input}' | Language: '{language}' | LLM: {use_llm}")
    
    # Step 1: Enrichissement LLM
    enriched = enrich_query_with_llm(user_input) if use_llm else {
        "original": user_input, "expanded": user_input, 
        "auteurs": [], "oeuvres": [], "mots_cles": user_input.split()
    }
    
    all_candidates = []
    seen_titles = set()
    
    def add_results(results, base_priority):
        """Ajouter des résultats avec scoring sophistiqué"""
        import unicodedata
        
        def normalize_text(text):
            return unicodedata.normalize('NFC', text.lower())
        
        for book in results:
            title_key = book['title'].lower()
            if title_key not in seen_titles:
                seen_titles.add(title_key)
                
                # Calculate match bonus
                bonus = 0
                book_authors = normalize_text(book.get('authors') or '')
                book_title = normalize_text(book['title'])
                
                # Bonus pour auteurs enrichis
                for author in enriched.get("auteurs", []):
                    author_norm = normalize_text(author)
                    if author_norm in book_authors:
                        bonus += 50  # Gros bonus pour correspondance auteur
                        break
                
                # Bonus pour œuvres enrichies
                for oeuvre in enriched.get("oeuvres", []):
                    oeuvre_norm = normalize_text(oeuvre)
                    oeuvre_words = [w for w in oeuvre_norm.split() if len(w) > 3]
                    matches = sum(1 for w in oeuvre_words if w in book_title)
                    if matches >= len(oeuvre_words) * 0.5:
                        bonus += 40
                        break
                
                book['_priority'] = base_priority + bonus
                all_candidates.append(book)
    
    # Step 2: Recherche par auteurs enrichis
    for author in enriched.get("auteurs", [])[:3]:
        results = search_meilisearch(author, limit=30, language=language)
        add_results(results, base_priority=80)
    
    # Step 3: Recherche avec requête enrichie
    expanded_query = enriched.get("expanded", user_input)
    results = search_meilisearch(expanded_query, limit=100, language=language)
    add_results(results, base_priority=50)
    
    # Step 4: Recherche requête originale
    if expanded_query != user_input:
        results = search_meilisearch(user_input, limit=50, language=language)
        add_results(results, base_priority=40)
    
    # Step 5: Recherche par mots-clés enrichis
    for keyword in enriched.get("mots_cles", [])[:3]:
        results = search_meilisearch(keyword, limit=20, language=language)
        add_results(results, base_priority=30)
    
    # Step 6: Déduplication et scoring final
    candidates = deduplicate_books(all_candidates)
    
    for book in candidates:
        priority = book.pop('_priority', 50)
        ratings = book.get('ratings_count') or 0
        popularity_boost = math.log10(ratings + 1) * 1.0 if ratings > 0 else 0
        book['_score'] = priority + popularity_boost
    
    # Tri par score
    candidates.sort(key=lambda x: x.get('_score', 0), reverse=True)
    
    # Nettoyage
    for book in candidates:
        book.pop('_score', None)
    
    candidates = candidates[:20]
    
    print(f"📚 Sophisticated results: {len(candidates)}")
    
    return {
        "recommendation": f"{candidates[0]['title']} - {candidates[0]['authors']}" if candidates else None,
        "book": candidates[0] if candidates else None,
        "keywords_used": enriched.get("mots_cles", user_input.split()),
        "candidates_count": len(candidates),
        "all_candidates": candidates,
        "language": language,
        "llm_used": use_llm and ollama_available,
        "semantic_used": False,
        "meilisearch_used": True,
        "firestore_used": False,
        "demo_mode": False,
        "dataset_size": len(books_df) if books_df is not None else 0,
        "platform": "Meilisearch + LLM + Pandas v3.0",
        "enriched_query": enriched
    }

def deduplicate_books(books: List[Dict]) -> List[Dict]:
    """Déduplication intelligente des livres"""
    STOP_WORDS = {'the', 'a', 'an', 'of', 'on', 'in', 'to', 'and', 'or', 'for', 'by', 'with',
                  'de', 'la', 'le', 'les', 'du', 'des', 'un', 'une', 'et', 'en', 'au', 'aux',
                  'vol', 'volume', 'part', 'edition', 'book', 'tome'}
    
    def normalize(t):
        t = t.lower()
        t = re.sub(r'[^\w\s]', ' ', t)
        words = [w for w in t.split() if w not in STOP_WORDS and len(w) > 2]
        return ' '.join(sorted(words[:4])[:3])
    
    seen = set()
    unique = []
    for book in books:
        key = normalize(book['title'])
        if key and key not in seen:
            seen.add(key)
            unique.append(book)
    return unique

def search_pandas_fallback(query: str, language: str = "fre", max_results: int = 20):
    """Fallback pandas amélioré (comme avant)"""
    global books_df
    
    if books_df is None or books_df.empty:
        return []
    
    # Enrichissement basique des termes
    query_clean = re.sub(r'[^\w\s]', ' ', query.lower())
    terms = [term.strip() for term in query_clean.split() if len(term.strip()) > 2]
    
    enriched_terms = []
    for term in terms:
        enriched_terms.append(term)
        if term in ['sf', 'science-fiction', 'sci-fi']:
            enriched_terms.extend(['science', 'fiction', 'futur', 'espace'])
        elif term in ['fantasy', 'fantastique']:
            enriched_terms.extend(['magie', 'dragon', 'épée', 'quête'])
        elif term in ['romance', 'amour']:
            enriched_terms.extend(['amour', 'coeur', 'passion', 'relation'])
    
    terms = list(set(enriched_terms))
    
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
    
    # Scoring amélioré
    scores = pd.Series(0, index=df_work.index)
    
    for term in terms:
        title_match = df_work['title'].fillna('').str.lower().str.contains(term, regex=False)
        scores += title_match * 10
        
        author_match = df_work['authors'].fillna('').str.lower().str.contains(term, regex=False)
        scores += author_match * 8
        
        keywords_match = df_work['keywords'].fillna('').str.lower().str.contains(term, regex=False)
        scores += keywords_match * 5
        
        genres_match = df_work['genres'].fillna('').str.lower().str.contains(term, regex=False)
        scores += genres_match * 3
    
    # Bonus popularité et qualité
    popularity_bonus = np.log1p(df_work['ratings_count'].fillna(0)) * 0.5
    scores += popularity_bonus
    
    rating_bonus = (df_work['avg_rating'].fillna(0) - 3.5) * 2
    scores += rating_bonus.clip(lower=0)
    
    valid_indices = scores[scores > 0].index
    
    if len(valid_indices) == 0:
        return []
    
    results_df = df_work.loc[valid_indices].copy()
    results_df['relevance_score'] = scores[valid_indices]
    
    results_df = results_df.sort_values(
        ['relevance_score', 'ratings_count', 'avg_rating'], 
        ascending=[False, False, False]
    )
    
    # Conversion en liste
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

def load_dataset():
    """Charger le dataset pandas"""
    global books_df
    
    try:
        parquet_path = "books_french.parquet"
        
        if not os.path.exists(parquet_path):
            print(f"❌ Fichier {parquet_path} introuvable")
            return False
        
        print(f"📊 Chargement du dataset: {parquet_path}")
        books_df = pd.read_parquet(parquet_path)
        
        books_df = books_df.dropna(subset=['title', 'authors'])
        books_df['keywords'] = books_df['keywords'].fillna('')
        books_df['genres'] = books_df['genres'].fillna('')
        
        print(f"✅ Dataset pandas chargé: {len(books_df):,} livres")
        return True
        
    except Exception as e:
        print(f"❌ Erreur chargement dataset: {e}")
        return False

# Initialisation au démarrage
print("🚀 Initialisation Book Finder API Hybride...")

# Charger le dataset pandas (toujours disponible)
dataset_loaded = load_dataset()

# Vérifier les services avancés
meilisearch_available = check_meilisearch()
ollama_available = check_ollama()

print(f"📊 Status: Pandas={'✅' if dataset_loaded else '❌'} | Meilisearch={'✅' if meilisearch_available else '❌'} | LLM={'✅' if ollama_available else '❌'}")

@app.get("/")
async def api_info():
    """Informations sur l'API hybride"""
    return {
        "status": "ready",
        "message": "Book Finder API Hybride - Meilisearch + LLM + Pandas",
        "dataset_size": len(books_df) if books_df is not None else 0,
        "platform": "Hybrid v3.0",
        "version": "3.0.0",
        "services": {
            "pandas": books_df is not None,
            "meilisearch": meilisearch_available,
            "llm_ollama": ollama_available
        },
        "capabilities": {
            "basic_search": True,
            "advanced_search": meilisearch_available,
            "semantic_search": False,  # FAISS pas encore intégré
            "llm_enrichment": ollama_available,
            "author_search": meilisearch_available,
            "query_expansion": ollama_available
        }
    }

@app.post("/recommend")
async def recommend_books(request: SearchRequest):
    """Recommandation hybride intelligente"""
    try:
        # Utiliser le système sophistiqué si disponible
        if meilisearch_available:
            result = recommend_sophisticated(request.prompt, request.language, request.use_llm)
        else:
            # Fallback vers pandas amélioré
            print(f"🔍 Fallback pandas search: '{request.prompt}'")
            books_list = search_pandas_fallback(request.prompt, request.language)
            
            result = {
                "recommendation": f"{books_list[0]['title']} - {books_list[0]['authors']}" if books_list else None,
                "book": books_list[0] if books_list else None,
                "keywords_used": request.prompt.split(),
                "candidates_count": len(books_list),
                "all_candidates": books_list[:10],
                "language": request.language,
                "llm_used": False,
                "semantic_used": False,
                "meilisearch_used": False,
                "firestore_used": False,
                "demo_mode": False,
                "dataset_size": len(books_df) if books_df is not None else 0,
                "platform": "Pandas Fallback v3.0"
            }
        
        return result
        
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
        df_filtered = books_df.copy()
        if language != 'all':
            df_filtered = df_filtered[df_filtered['language'] == language]
        
        unknown_books = df_filtered[
            df_filtered['popularity_tier'].isin(['unknown', 'obscure', 'niche']) |
            (df_filtered['ratings_count'] < 1000)
        ]
        
        if unknown_books.empty:
            unknown_books = df_filtered
        
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
            "top_authors": books_df['authors'].value_counts().head(10).to_dict(),
            "services_status": {
                "pandas": True,
                "meilisearch": meilisearch_available,
                "llm": ollama_available
            }
        }
        return stats_data
    except Exception as e:
        return {"error": str(e)}

@app.get("/debug/ollama")
async def debug_ollama():
    """Debug de la connexion Ollama"""
    debug_info = {
        "ollama_available": ollama_available,
        "ollama_base_url": ollama_base_url if 'ollama_base_url' in globals() else "Not set",
        "test_results": []
    }
    
    # Test des URLs
    test_urls = [
        "http://localhost:11434/api/tags",
        "https://gtk-rangers-nevertheless-majority.trycloudflare.com/api/tags"
    ]
    
    for url in test_urls:
        try:
            import time
            start_time = time.time()
            r = requests.get(url, timeout=20)
            duration = time.time() - start_time
            
            debug_info["test_results"].append({
                "url": url,
                "status": "success" if r.status_code == 200 else f"error_{r.status_code}",
                "duration_ms": int(duration * 1000),
                "response_size": len(r.text) if r.text else 0
            })
        except Exception as e:
            debug_info["test_results"].append({
                "url": url,
                "status": "failed",
                "error": str(e)
            })
    
    return debug_info

@app.get("/health")
async def health_check():
    """Vérification de santé complète"""
    return {
        "status": "healthy",
        "dataset_loaded": books_df is not None and not books_df.empty,
        "dataset_size": len(books_df) if books_df is not None else 0,
        "services": {
            "pandas": books_df is not None,
            "meilisearch": meilisearch_available,
            "llm_ollama": ollama_available
        },
        "recommendation_mode": "sophisticated" if meilisearch_available else "pandas_fallback"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)