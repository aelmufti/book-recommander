#!/usr/bin/env python3
"""
Large-scale book recommender for 43M+ books
- Fast SQL queries
- Semantic search with FAISS + sentence-transformers
- LLM enrichment (Ollama)
- No corpus files needed (authors in keywords)
"""
import duckdb
import json
import re
import time
import requests
import numpy as np
from typing import List, Dict, Optional
import os

# Lazy load heavy dependencies
faiss = None
SentenceTransformer = None


def _load_faiss():
    global faiss
    if faiss is None:
        import faiss as _faiss
        faiss = _faiss
    return faiss


def _load_sentence_transformer():
    global SentenceTransformer
    if SentenceTransformer is None:
        from sentence_transformers import SentenceTransformer as _ST
        SentenceTransformer = _ST
    return SentenceTransformer


class LargeScaleRecommender:
    LANG_CODES = {
        'fr': 'fre', 'french': 'fre', 'français': 'fre',
        'en': 'eng', 'english': 'eng', 'anglais': 'eng',
        'es': 'spa', 'spanish': 'spa', 'espagnol': 'spa',
        'de': 'ger', 'german': 'ger', 'allemand': 'ger',
        'it': 'ita', 'italian': 'ita', 'italien': 'ita',
        'pt': 'por', 'portuguese': 'por', 'portugais': 'por',
    }
    
    def __init__(self, db_file: str = None, default_language: str = "fre",
                 faiss_index: str = None, db_adapter=None):
        
        # Use database adapter if provided, otherwise create DuckDB connection
        if db_adapter:
            self.db_adapter = db_adapter
            self.conn = db_adapter.conn if hasattr(db_adapter, 'conn') else None
        else:
            # Fallback to direct DuckDB connection
            script_dir = os.path.dirname(os.path.abspath(__file__))
            if db_file is None:
                # Essayer d'abord la base de déploiement, sinon la base complète
                deployment_db = os.path.join(script_dir, "books_deployment.duckdb")
                full_db = os.path.join(script_dir, "books.duckdb")
                
                if os.path.exists(deployment_db):
                    db_file = deployment_db
                else:
                    db_file = full_db
            
            self.conn = duckdb.connect(db_file, read_only=True)
            self.db_adapter = None
        
        self.default_language = default_language
        
        # LLM config
        self.ollama_url = "http://localhost:11434/api/generate"
        self.use_llm = self._check_ollama()
        
        # FAISS semantic search
        if faiss_index is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            faiss_index = os.path.join(script_dir, "faiss_index.bin")
        
        self.faiss_index = None
        self.semantic_model = None
        self.faiss_available = False
        self._load_faiss_index(faiss_index)
        
        # Verify DB
        try:
            if self.db_adapter:
                count_result = self.db_adapter.execute_query("SELECT COUNT(*) FROM books")
                count = count_result[0][0] if count_result else 0
            else:
                count = self.conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
            print(f"✅ Database: {count:,} books")
        except Exception as e:
            print(f"⚠️ Database verification failed: {e}")
    
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

    def _load_faiss_index(self, faiss_file: str):
        """Load FAISS index and sentence-transformer model"""
        if not os.path.exists(faiss_file):
            print(f"⚠️ FAISS index not found: {faiss_file}")
            return
        
        try:
            print("📦 Loading FAISS index...")
            _faiss = _load_faiss()
            self.faiss_index = _faiss.read_index(faiss_file)
            print(f"   ✅ FAISS: {self.faiss_index.ntotal:,} vectors")
            
            print("📦 Loading sentence-transformer model...")
            ST = _load_sentence_transformer()
            self.semantic_model = ST('all-MiniLM-L6-v2')
            print("   ✅ Model ready")
            
            self.faiss_available = True
        except Exception as e:
            print(f"⚠️ FAISS load error: {e}")
            self.faiss_available = False

    # ==================== LLM ====================
    
    def llm_enrich_query(self, user_input: str) -> Dict:
        if not self.use_llm:
            return {"keywords": user_input.split()}
        
        prompt = f"""Tu analyses des requêtes de recherche de livres. 

RÈGLES STRICTES:
- Si la requête contient un NOM D'AUTEUR (marx, gramsci, sartre, king...), garde-le tel quel
- Ajoute 1-2 mots-clés SPÉCIFIQUES au sujet, pas de mots génériques
- Évite les mots trop vagues: "book", "literature", "reading", "classic", "famous"

Requête: "{user_input}"

Réponds UNIQUEMENT en JSON (rien d'autre):
{{"original": ["mots de la requête"], "enriched": ["1-2 mots spécifiques"]}}

EXEMPLES:
"marx politique" -> {{"original": ["marx", "politique"], "enriched": ["communisme", "capital"]}}
"livre relaxant été" -> {{"original": ["relaxant", "été"], "enriched": ["feel-good", "romance"]}}
"gramsci" -> {{"original": ["gramsci"], "enriched": ["marxisme", "hégémonie"]}}
"stephen king horreur" -> {{"original": ["stephen", "king", "horreur"], "enriched": ["thriller", "suspense"]}}
"philosophie existentialisme" -> {{"original": ["philosophie", "existentialisme"], "enriched": ["sartre", "camus"]}}
"""
        try:
            r = requests.post(self.ollama_url, json={
                "model": "llama3.2", "prompt": prompt, "stream": False
            }, timeout=30)
            if r.status_code == 200:
                response = r.json().get("response", "")
                match = re.search(r'\{.*\}', response, re.DOTALL)
                if match:
                    data = json.loads(match.group())
                    # Combine original + enriched, filter out generic words
                    generic = {'book', 'books', 'literature', 'reading', 'classic', 'famous', 'author', 'novel', 'story'}
                    enriched = [w.lower() for w in data.get("enriched", []) if w.lower() not in generic]
                    return {"keywords": data.get("original", []), "enriched_keywords": enriched[:2]}
        except Exception as e:
            print(f"   ⚠️ LLM error: {e}")
        return {"keywords": user_input.split()}

    # ==================== SEARCH ====================
    
    def search_semantic(self, query: str, language: str = None, limit: int = 20) -> List[Dict]:
        """Semantic search using FAISS + sentence-transformers"""
        if not self.faiss_available:
            return []
        
        start = time.time()
        
        # Encode query (model already loaded at startup)
        query_vec = self.semantic_model.encode([query], normalize_embeddings=True, show_progress_bar=False)
        query_vec = query_vec.astype('float32')
        
        # Search FAISS
        k = limit * 5 if language and language != 'all' else limit * 2
        scores, indices = self.faiss_index.search(query_vec, k)
        
        # Filter valid indices and create score map
        valid_pairs = [(int(idx), float(score)) for idx, score in zip(indices[0], scores[0]) if idx >= 0]
        if not valid_pairs:
            return []
        
        # Create index to score mapping
        idx_to_score = {idx: score for idx, score in valid_pairs}
        indices_list = [idx for idx, _ in valid_pairs[:limit * 3]]
        
        # Build language filter
        lang = language or self.default_language
        lang_filter = ""
        if lang and lang != 'all':
            if ',' in lang:
                langs = [f"'{l.strip()}'" for l in lang.split(',')]
                lang_filter = f"AND language IN ({','.join(langs)})"
            else:
                lang_filter = f"AND language = '{lang}'"
        
        # BATCH QUERY: Use row_number() to fetch all rows at once
        indices_str = ','.join(map(str, indices_list))
        query_sql = f"""
            WITH numbered AS (
                SELECT *, ROW_NUMBER() OVER () - 1 as rn
                FROM popular_books
            )
            SELECT title, authors, genres, keywords, avg_rating,
                   ratings_count, popularity_tier, language, rn
            FROM numbered
            WHERE rn IN ({indices_str})
            {lang_filter}
        """
        
        rows = self.conn.execute(query_sql).fetchall()
        
        results = []
        for row in rows:
            idx = row[8]  # rn column
            results.append({
                "title": row[0], "authors": row[1], "genres": row[2] or "",
                "keywords": row[3] or "", "avg_rating": row[4], "ratings_count": row[5],
                "popularity_tier": row[6], "language": row[7],
                "semantic_score": idx_to_score.get(idx, 0)
            })
        
        # Sort by semantic score and limit
        results.sort(key=lambda x: -x['semantic_score'])
        results = results[:limit]
        
        print(f"   🧠 Semantic: {time.time()-start:.3f}s, {len(results)} results")
        return results
    
    def search_fast(self, keywords: List[str], language: str = None, limit: int = 20) -> List[Dict]:
        lang = language or self.default_language
        
        where_parts = []
        if lang and lang != 'all':
            # Support multiple languages separated by comma
            if ',' in lang:
                langs = [l.strip() for l in lang.split(',')]
                lang_conds = [f"language = '{l}'" for l in langs]
                where_parts.append(f"({' OR '.join(lang_conds)})")
            else:
                where_parts.append(f"language = '{lang}'")
        
        if keywords:
            # Use AND for multiple keywords - ALL must match (in keywords OR authors)
            for kw in keywords[:4]:
                escaped_kw = kw.replace(chr(39), chr(39)+chr(39)).lower()
                where_parts.append(f"(keywords LIKE '%{escaped_kw}%' OR LOWER(authors) LIKE '%{escaped_kw}%')")
        
        where = " AND ".join(where_parts) if where_parts else "1=1"
        
        # Build score expression to rank by keyword matches - prioritize author matches
        if keywords:
            score_parts = []
            for kw in keywords[:4]:
                escaped_kw = kw.replace(chr(39), chr(39)+chr(39)).lower()
                # Author match = 2 points, keyword match = 1 point
                score_parts.append(f"CASE WHEN LOWER(authors) LIKE '%{escaped_kw}%' THEN 2 WHEN keywords LIKE '%{escaped_kw}%' THEN 1 ELSE 0 END")
            score_expr = " + ".join(score_parts)
        else:
            score_expr = "0"
        
        query = f"""
            SELECT title, authors, genres, keywords, avg_rating, 
                   ratings_count, popularity_tier, language,
                   ({score_expr}) as match_score
            FROM popular_books WHERE {where}
            ORDER BY match_score DESC, ratings_count DESC NULLS LAST
            LIMIT {limit}
        """
        
        start = time.time()
        results = self.conn.execute(query).fetchall()
        print(f"   ⚡ Fast: {time.time()-start:.3f}s, {len(results)} results")
        
        return [{"title": r[0], "authors": r[1], "genres": r[2] or "", 
                 "keywords": r[3] or "", "avg_rating": r[4], "ratings_count": r[5],
                 "popularity_tier": r[6], "language": r[7], "match_score": r[8]} for r in results]
    
    def search_full(self, keywords: List[str], language: str = None, limit: int = 20) -> List[Dict]:
        """Smart search: find books matching ALL keywords, prioritize author matches"""
        lang = language or self.default_language
        
        # Build language filter
        lang_filter = ""
        if lang and lang != 'all':
            if ',' in lang:
                langs = [f"'{l.strip()}'" for l in lang.split(',')]
                lang_filter = f"AND language IN ({','.join(langs)})"
            else:
                lang_filter = f"AND language = '{lang}'"
        
        # Build WHERE conditions - ALL keywords must match somewhere
        keyword_conditions = []
        for kw in keywords[:4]:
            escaped_kw = kw.replace("'", "''").lower()
            keyword_conditions.append(
                f"(LOWER(authors) LIKE '%{escaped_kw}%' OR LOWER(title) LIKE '%{escaped_kw}%' OR keywords LIKE '%{escaped_kw}%')"
            )
        
        # Build score - prioritize author matches
        score_parts = []
        for kw in keywords[:4]:
            escaped_kw = kw.replace("'", "''").lower()
            score_parts.append(f"CASE WHEN LOWER(authors) LIKE '%{escaped_kw}%' THEN 3 WHEN LOWER(title) LIKE '%{escaped_kw}%' THEN 2 WHEN keywords LIKE '%{escaped_kw}%' THEN 1 ELSE 0 END")
        score_expr = " + ".join(score_parts) if score_parts else "0"
        
        where_clause = " AND ".join(keyword_conditions) if keyword_conditions else "1=1"
        
        query = f"""
            SELECT title, authors, genres, keywords, avg_rating,
                   ratings_count, popularity_tier, language,
                   ({score_expr}) as match_score
            FROM books 
            WHERE {where_clause}
            AND title IS NOT NULL
            {lang_filter}
            ORDER BY match_score DESC, ratings_count DESC NULLS LAST
            LIMIT {limit * 3}
        """
        
        start = time.time()
        results = self.conn.execute(query).fetchall()
        print(f"   📊 Search: {time.time()-start:.3f}s, {len(results)} results")
        
        return [self._row_to_dict(r) for r in results[:limit]]
    
    def _row_to_dict(self, row) -> Dict:
        return {
            "title": row[0], "authors": row[1], "genres": row[2] or "",
            "keywords": row[3] or "", "avg_rating": row[4], "ratings_count": row[5],
            "popularity_tier": row[6], "language": row[7], "match_score": row[8]
        }

    def search_full_and(self, keywords: List[str], language: str = None, limit: int = 20) -> List[Dict]:
        """Search with AND logic - all keywords must match"""
        lang = language or self.default_language
        
        where_parts = ["title IS NOT NULL"]
        if lang and lang != 'all':
            if ',' in lang:
                langs = [l.strip() for l in lang.split(',')]
                lang_conds = [f"language = '{l}'" for l in langs]
                where_parts.append(f"({' OR '.join(lang_conds)})")
            else:
                where_parts.append(f"language = '{lang}'")
        
        if keywords:
            # Use AND - ALL keywords must match (in keywords OR authors)
            for kw in keywords[:4]:
                escaped_kw = kw.replace(chr(39), chr(39)+chr(39)).lower()
                where_parts.append(f"(keywords LIKE '%{escaped_kw}%' OR LOWER(authors) LIKE '%{escaped_kw}%')")
        
        query = f"""
            SELECT title, authors, genres, keywords, avg_rating,
                   ratings_count, popularity_tier, language,
                   {len(keywords)} as match_score
            FROM books WHERE {" AND ".join(where_parts)}
            ORDER BY ratings_count DESC NULLS LAST
            LIMIT {limit}
        """
        
        start = time.time()
        results = self.conn.execute(query).fetchall()
        print(f"   📊 Full+AND: {time.time()-start:.3f}s, {len(results)} results")
        
        return [{"title": r[0], "authors": r[1], "genres": r[2] or "",
                 "keywords": r[3] or "", "avg_rating": r[4], "ratings_count": r[5],
                 "popularity_tier": r[6], "language": r[7], "match_score": r[8]} for r in results]

    # ==================== MAIN ====================
    
    def recommend(self, user_input: str, language: str = None, use_llm: bool = True,
                  use_semantic: bool = True) -> Dict:
        print(f"🔍 Query: '{user_input}' | Language: '{language}'")
        lang = self.LANG_CODES.get(language, language) if language else self.default_language
        
        # Get keywords
        original_keywords = user_input.lower().split()
        enriched_keywords = []
        
        if use_llm and self.use_llm:
            print("   🤖 LLM enriching...")
            result = self.llm_enrich_query(user_input)
            enriched_keywords = result.get("enriched_keywords", [])
        
        print(f"   🔑 Original: {original_keywords}, Enriched: {enriched_keywords}")
        
        candidates = []
        semantic_used = False
        
        # 1. Search with original keywords only (AND logic)
        sql_results = self.search_full(original_keywords, lang, limit=50)
        candidates.extend(sql_results)
        
        popular_results = self.search_fast(original_keywords, lang, limit=30)
        candidates.extend(popular_results)
        
        # 2. If not enough results and we have enriched keywords, try original + enriched (AND)
        if len(candidates) < 5 and enriched_keywords:
            print("   📚 Trying original + enriched keywords (AND)...")
            combined_keywords = original_keywords + enriched_keywords[:2]
            extra = self.search_full_and(combined_keywords, lang, limit=15)
            candidates.extend(extra)
        
        # Fallback to full search only if no results at all
        if len(candidates) == 0:
            print("   📚 Expanding to full search...")
            candidates.extend(self.search_full(original_keywords, lang, limit=20))
        
        # Deduplicate - prefer results with higher match_score
        seen = {}
        for book in candidates:
            key = book['title'].lower()[:30]
            if key not in seen:
                seen[key] = book
            else:
                # Keep the one with higher match_score
                existing_score = seen[key].get('match_score', 0)
                new_score = book.get('match_score', 0)
                if new_score > existing_score:
                    seen[key] = book
        candidates = list(seen.values())
        
        # Sort: EXACT MATCHES FIRST (match_score > 0), then semantic, then ratings
        def sort_key(x):
            match_score = x.get('match_score', 0)
            has_semantic = 'semantic_score' in x
            semantic_score = x.get('semantic_score', 0)
            ratings = x.get('ratings_count') or 0
            
            # Priority: 1) match_score (higher = better), 2) semantic_score, 3) ratings
            if match_score > 0:
                return (0, -match_score, -ratings)  # Exact matches first
            elif has_semantic:
                return (1, -semantic_score)  # Then semantic
            return (2, -ratings)  # Then by ratings
        
        candidates.sort(key=sort_key)
        
        print(f"   📚 {len(candidates)} results (semantic: {semantic_used})")
        
        all_keywords = original_keywords + enriched_keywords
        
        return {
            "recommendation": candidates[0] if candidates else None,
            "keywords_used": all_keywords,
            "candidates_count": len(candidates),
            "all_candidates": candidates[:20],
            "language": lang,
            "llm_used": use_llm and self.use_llm,
            "semantic_used": semantic_used
        }
    
    def set_language(self, lang: str):
        self.default_language = self.LANG_CODES.get(lang, lang)
    
    def close(self):
        self.conn.close()


if __name__ == "__main__":
    rec = LargeScaleRecommender()
    for q in ["marx politique", "gramsci", "stephen king horror"]:
        print(f"\n{'='*40}")
        r = rec.recommend(q, language="all", use_llm=False)
        if r["recommendation"]:
            print(f"📖 {r['recommendation']['title'][:40]} - {r['recommendation']['authors'][:25]}")
    rec.close()
