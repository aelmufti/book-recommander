#!/usr/bin/env python3
"""
Index French books from DuckDB into Meilisearch for fast full-text search.
"""
import duckdb
import meilisearch
import time
import os

MEILISEARCH_URL = "http://127.0.0.1:7700"
BATCH_SIZE = 10000

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "books.duckdb")
    
    print("📦 Connecting to DuckDB...")
    conn = duckdb.connect(db_path, read_only=True)
    
    print("🔍 Connecting to Meilisearch...")
    client = meilisearch.Client(MEILISEARCH_URL)
    
    # Delete existing index and recreate
    print("🗑️ Deleting existing index...")
    try:
        client.delete_index("books")
        time.sleep(2)
    except:
        pass
    
    print("📚 Creating new index...")
    client.create_index("books", {"primaryKey": "id"})
    index = client.index("books")
    
    # Configure index settings for French search
    print("⚙️ Configuring index settings for French...")
    index.update_settings({
        "searchableAttributes": ["title", "authors", "keywords", "genres"],
        "filterableAttributes": ["popularity_tier"],
        "sortableAttributes": ["ratings_count", "avg_rating"],
        "rankingRules": [
            "words",
            "typo", 
            "proximity",
            "attribute",
            "sort",
            "exactness"
        ],
        "typoTolerance": {
            "enabled": True,
            "minWordSizeForTypos": {
                "oneTypo": 4,
                "twoTypos": 8
            }
        }
    })
    
    # Count total French books
    total = conn.execute("SELECT COUNT(*) FROM books_french WHERE title IS NOT NULL").fetchone()[0]
    print(f"📚 Total French books to index: {total:,}")
    
    # Index in batches
    offset = 0
    start_time = time.time()
    
    while offset < total:
        # Fetch batch
        query = f"""
            SELECT 
                ol_key as id,
                title,
                authors,
                genres,
                keywords,
                avg_rating,
                ratings_count,
                popularity_tier
            FROM books_french 
            WHERE title IS NOT NULL
            ORDER BY ratings_count DESC NULLS LAST
            LIMIT {BATCH_SIZE} OFFSET {offset}
        """
        
        rows = conn.execute(query).fetchall()
        
        # Convert to documents
        documents = []
        for idx, row in enumerate(rows):
            # Create unique ID from ol_key + index to avoid duplicates
            raw_id = row[0] or f"book_{offset + idx}"
            clean_id = f"{raw_id.replace('/', '_')}_{offset + idx}"
            
            doc = {
                "id": clean_id,
                "title": row[1] or "",
                "authors": row[2] or "",
                "genres": row[3] or "",
                "keywords": row[4] or "",
                "avg_rating": row[5] or 0,
                "ratings_count": row[6] or 0,
                "popularity_tier": row[7] or "unknown"
            }
            documents.append(doc)
        
        # Index batch
        task = index.add_documents(documents)
        
        offset += len(rows)
        elapsed = time.time() - start_time
        rate = offset / elapsed if elapsed > 0 else 0
        eta = (total - offset) / rate if rate > 0 else 0
        
        print(f"   📤 Indexed {offset:,}/{total:,} ({100*offset/total:.1f}%) - {rate:.0f} docs/s - ETA: {eta:.0f}s")
        
        if len(rows) < BATCH_SIZE:
            break
    
    print(f"\n⏳ Waiting for Meilisearch to process...")
    client.wait_for_task(task.task_uid)
    
    # Get stats
    stats = index.get_stats()
    print(f"✅ Done! Index has {stats['numberOfDocuments']:,} documents")
    
    # Test search
    print("\n🔍 Testing search...")
    tests = ["marx", "victor hugo", "petit prince", "harry potter", "camus", "simone de beauvoir"]
    for query in tests:
        results = index.search(query, {"limit": 3})
        hits = results.get("hits", [])
        print(f"\n   '{query}':")
        for hit in hits:
            print(f"      • {hit['title'][:50]} - {hit['authors'][:25]}")

if __name__ == "__main__":
    main()
