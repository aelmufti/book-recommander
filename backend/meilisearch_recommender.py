#!/usr/bin/env python3
"""
Book recommender using Meilisearch + LLM enrichment + popularity boosting.
"""
import meilisearch
import requests
import json
import re
from typing import List, Dict

MEILISEARCH_URL = "http://127.0.0.1:7700"
OLLAMA_URL = "http://localhost:11434/api/generate"


class MeilisearchRecommender:
    def __init__(self):
        self.client = meilisearch.Client(MEILISEARCH_URL)
        self.index = self.client.index("books")
        
        # Check Meilisearch
        try:
            stats = self.index.get_stats()
            doc_count = stats.number_of_documents
            print(f"✅ Meilisearch: {doc_count:,} books indexed")
            self.available = doc_count > 0
        except Exception as e:
            print(f"⚠️ Meilisearch not available: {e}")
            self.available = False
        
        # Check Ollama
        self.ollama_available = self._check_ollama()
    
    def _check_ollama(self) -> bool:
        try:
            r = requests.get("http://localhost:11434/api/tags", timeout=2)
            if r.status_code == 200:
                print("✅ Ollama available")
                return True
        except:
            pass
        print("⚠️ Ollama not available")
        return False
    
    def enrich_query_with_llm(self, user_input: str) -> Dict:
        """Use LLM to understand intent and expand query with relevant terms."""
        if not self.ollama_available:
            return {"original": user_input, "expanded": user_input, "auteurs": [], "oeuvres": [], "mots_cles": []}
        
        prompt = f"""Tu es un expert en littérature française et internationale. L'utilisateur cherche des livres avec: "{user_input}"

IMPORTANT: Tu DOIS remplir TOUTES les catégories, même si tu dois deviner.

Réponds UNIQUEMENT en JSON valide:
{{"auteurs": ["auteur1", "auteur2"], "oeuvres": ["titre exact 1", "titre exact 2"], "mots_cles": ["mot1", "mot2", "mot3", "mot4"]}}

EXEMPLES:
- "marx" → {{"auteurs": ["Karl Marx", "Friedrich Engels"], "oeuvres": ["Le Capital", "Manifeste du Parti communiste"], "mots_cles": ["communisme", "socialisme", "économie politique", "capitalisme"]}}
- "IVG France" → {{"auteurs": ["Gisèle Halimi", "Simone Veil"], "oeuvres": ["La Cause des femmes", "Une vie"], "mots_cles": ["avortement", "féminisme", "droits des femmes", "loi Veil"]}}
- "investissement" → {{"auteurs": ["Benjamin Graham", "Warren Buffett"], "oeuvres": ["L'investisseur intelligent", "Père riche père pauvre"], "mots_cles": ["bourse", "finance", "actions", "épargne"]}}

JSON pour "{user_input}":"""
        
        try:
            r = requests.post(OLLAMA_URL, json={
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
                    
                    print(f"   🤖 LLM expanded: {expanded[:80]}...")
                    
                    return {
                        "original": user_input,
                        "expanded": expanded,
                        "auteurs": data.get("auteurs", []),
                        "oeuvres": data.get("oeuvres", []),
                        "mots_cles": data.get("mots_cles", [])
                    }
        except Exception as e:
            print(f"   ⚠️ LLM error: {e}")
        
        return {"original": user_input, "expanded": user_input, "auteurs": [], "oeuvres": [], "mots_cles": []}
    
    def search(self, query: str, limit: int = 50, language: str = None, 
               sort_by_popularity: bool = False, search_in_authors: bool = False,
               author_filter: str = None) -> List[Dict]:
        """Search - let Meilisearch rank by relevance first."""
        if not self.available:
            return []
        
        search_params = {
            "limit": limit,
            "attributesToRetrieve": [
                "title", "authors", "genres", "keywords",
                "avg_rating", "ratings_count", "popularity_tier", "language"
            ]
        }
        
        # If searching for author, restrict to authors field
        if search_in_authors:
            search_params["attributesToSearchOn"] = ["authors"]
        
        # Language filter
        filters = []
        if language and language != 'all':
            if ',' in language:
                langs = [l.strip() for l in language.split(',')]
                lang_filter = ' OR '.join([f'language = "{l}"' for l in langs])
                filters.append(f"({lang_filter})")
            else:
                filters.append(f'language = "{language}"')
        
        # Author filter (for getting all books by an author)
        if author_filter:
            # Escape quotes in author name
            safe_author = author_filter.replace('"', '\\"')
            filters.append(f'authors CONTAINS "{safe_author}"')
        
        if filters:
            search_params["filter"] = " AND ".join(filters)
        
        results = self.index.search(query, search_params)
        
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
    
    def deduplicate(self, books: List[Dict]) -> List[Dict]:
        """Remove duplicate titles."""
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
    
    def recommend(self, user_input: str, language: str = None, 
                  use_llm: bool = True, use_semantic: bool = False) -> Dict:
        """
        Main recommendation - RELEVANCE FIRST with smart boosting.
        """
        import math
        print(f"🔍 Query: '{user_input}' | Language: '{language}' | LLM: {use_llm}")
        
        # Step 1: Enrich query with LLM
        enriched = {"original": user_input, "expanded": user_input, "auteurs": [], "oeuvres": [], "mots_cles": []}
        if use_llm and self.ollama_available:
            enriched = self.enrich_query_with_llm(user_input)
        
        all_candidates = []
        seen_titles = set()
        
        def add_results(results, base_priority):
            """Add results with priority score, boosting author/title matches."""
            import unicodedata
            
            def normalize_text(text):
                """Normalize Unicode text for comparison."""
                return unicodedata.normalize('NFC', text.lower())
            
            for book in results:
                title_key = book['title'].lower()
                if title_key not in seen_titles:
                    seen_titles.add(title_key)
                    
                    # Calculate match bonus
                    bonus = 0
                    book_authors = normalize_text(book.get('authors') or '')
                    book_title = normalize_text(book['title'])
                    
                    # Bonus for matching enriched authors
                    for author in enriched.get("auteurs", []):
                        author_norm = normalize_text(author)
                        if author_norm in book_authors:
                            bonus += 50  # Big bonus for author match
                            break
                    
                    # Bonus for matching enriched oeuvres (titles)
                    for oeuvre in enriched.get("oeuvres", []):
                        oeuvre_norm = normalize_text(oeuvre)
                        # Check if significant words from oeuvre are in title
                        oeuvre_words = [w for w in oeuvre_norm.split() if len(w) > 3]
                        matches = sum(1 for w in oeuvre_words if w in book_title)
                        if matches >= len(oeuvre_words) * 0.5:  # At least half the words match
                            bonus += 40
                            break
                    
                    book['_priority'] = base_priority + bonus
                    all_candidates.append(book)
        
        # Step 2: First, get books by enriched authors (highest priority)
        for author in enriched.get("auteurs", [])[:3]:
            # Search for author name in authors field only
            results = self.search(author, limit=30, language=language, search_in_authors=True)
            add_results(results, base_priority=80)  # High priority for author matches
        
        # Step 3: Search with expanded query (includes authors, titles, keywords)
        expanded_query = enriched.get("expanded", user_input)
        results = self.search(expanded_query, limit=100, language=language)
        add_results(results, base_priority=50)
        
        # Step 3: Also search original query
        if expanded_query != user_input:
            results = self.search(user_input, limit=50, language=language)
            add_results(results, base_priority=40)
        
        # Step 4: Search each keyword separately for broader coverage
        for keyword in enriched.get("mots_cles", [])[:3]:
            results = self.search(keyword, limit=20, language=language)
            add_results(results, base_priority=30)
        
        # Step 5: Deduplicate
        candidates = self.deduplicate(all_candidates)
        
        # Step 6: Final scoring - priority + small popularity boost
        for book in candidates:
            priority = book.pop('_priority', 50)
            ratings = book.get('ratings_count') or 0
            # Very small popularity boost - relevance matters more
            popularity_boost = math.log10(ratings + 1) * 1.0 if ratings > 0 else 0
            book['_score'] = priority + popularity_boost
        
        # Sort by score
        candidates.sort(key=lambda x: x.get('_score', 0), reverse=True)
        
        # Remove internal score
        for book in candidates:
            book.pop('_score', None)
        
        # Take top 20
        candidates = candidates[:20]
        
        print(f"   📚 {len(candidates)} results")
        
        return {
            "recommendation": candidates[0] if candidates else None,
            "keywords_used": enriched.get("mots_cles", user_input.split()),
            "candidates_count": len(candidates),
            "all_candidates": candidates,
            "language": language,
            "llm_used": use_llm and self.ollama_available,
            "semantic_used": False,
            "enriched_query": enriched
        }


if __name__ == "__main__":
    rec = MeilisearchRecommender()
    
    tests = ["marx", "IVG France", "investissement", "philosophie grecque"]
    
    for q in tests:
        print(f"\n{'='*60}")
        result = rec.recommend(q, language='all', use_llm=True)
        print(f"\nTop 5 for '{q}':")
        for i, book in enumerate(result['all_candidates'][:5]):
            ratings = book.get('ratings_count') or 0
            print(f"  {i+1}. [{book.get('language','?')}] {book['title'][:45]} ({ratings:,} ratings)")
