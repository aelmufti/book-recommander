from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from large_scale_recommender import LargeScaleRecommender
from database_adapter import DatabaseAdapter

# Initialize database adapter
db_adapter = DatabaseAdapter()
db_adapter.migrate_data_if_needed()

# Try to use Meilisearch if available
try:
    from meilisearch_recommender import MeilisearchRecommender
    meilisearch_rec = MeilisearchRecommender()
    USE_MEILISEARCH = meilisearch_rec.available
except Exception as e:
    print(f"⚠️ Meilisearch not available: {e}")
    meilisearch_rec = None
    USE_MEILISEARCH = False

app = FastAPI(title="Book Recommender API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fallback recommender (DuckDB or PostgreSQL)
recommender = LargeScaleRecommender(default_language="fre", db_adapter=db_adapter)


class RecommendRequest(BaseModel):
    prompt: str
    language: str = None  # None = default (fre), "all" = all languages
    use_llm: bool = False  # Disabled by default - too slow
    use_semantic: bool = True  # Use FAISS semantic search if available


@app.post("/recommend")
async def recommend(request: RecommendRequest):
    try:
        # Use Meilisearch if available (much faster and better)
        if USE_MEILISEARCH:
            result = meilisearch_rec.recommend(
                request.prompt,
                language=request.language
            )
        else:
            result = recommender.recommend(
                request.prompt,
                language=request.language,
                use_llm=request.use_llm,
                use_semantic=request.use_semantic
            )

        book = result.get("recommendation")

        return {
            "recommendation": f"{book['title']} - {book['authors']}" if book else None,
            "book": book,
            "keywords_used": result.get("keywords_used", []),
            "candidates_count": result.get("candidates_count", 0),
            "all_candidates": result.get("all_candidates", []),
            "language": result.get("language"),
            "llm_used": result.get("llm_used", False),
            "semantic_used": result.get("semantic_used", False),
            "meilisearch_used": USE_MEILISEARCH
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/language")
async def set_language(lang: str = "fre"):
    recommender.set_language(lang)
    return {"default_language": recommender.default_language}


@app.get("/")
async def root():
    return {
        "status": "ready",
        "dataset": "43M books",
        "meilisearch_available": USE_MEILISEARCH,
        "fallback_available": True
    }


@app.get("/random-unknown")
async def random_unknown(language: str = None):
    """Get a random book from the 'unknown' tier (obscure books)"""
    try:
        lang_filter = ""
        if language and language != 'all':
            if ',' in language:
                langs = [f"'{l.strip()}'" for l in language.split(',')]
                lang_filter = f"AND language IN ({','.join(langs)})"
            else:
                lang_filter = f"AND language = '{language}'"
        
        # Check if books_clean exists
        table_exists = recommender.conn.execute("""
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_name = 'books_clean'
        """).fetchone()[0]
        
        table_name = "books_clean" if table_exists else "books"
        
        # Get random book from unknown/obscure tier (low ratings count)
        query = f"""
            SELECT title, authors, genres, keywords, avg_rating,
                   ratings_count, popularity_tier, language, first_publish_date
            FROM {table_name}
            WHERE (popularity_tier = 'unknown' OR popularity_tier = 'obscure' OR ratings_count IS NULL OR ratings_count < 100)
            AND title IS NOT NULL
            AND authors IS NOT NULL
            AND LENGTH(title) > 3
            {lang_filter}
            ORDER BY RANDOM()
            LIMIT 1
        """
        
        result = recommender.conn.execute(query).fetchone()
        
        if result:
            return {
                "book": {
                    "title": result[0],
                    "authors": result[1],
                    "genres": result[2] or "",
                    "keywords": result[3] or "",
                    "avg_rating": result[4],
                    "ratings_count": result[5],
                    "popularity_tier": result[6] or "unknown",
                    "language": result[7],
                    "first_publish_date": result[8]
                }
            }
        return {"book": None}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
