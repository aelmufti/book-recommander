#!/usr/bin/env python3
"""
Index books from DuckDB into Meilisearch for fast full-text search.
"""
import duckdb
import meilisearch
import time
import json

MEILISEARCH_URL = "http://127.0.0.1:7700"
BATCH_SIZE = 50000  # Meilisearch handles large batches well

def main():
    # Connect to DuckDB
    print("📦 Connecting to DuckDB...")
    import os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "books.duckdb")
    conn = duckdb.connect(db_path, read_only=True)
    
    # Limit memory usage
    conn.execute("SET threads=1")
    conn.execute("SET memory_limit='2GB'")
    
    # Connect to Meilisearch
    print("🔍 Connecting to Meilisearch...")
    client = meilisearch.Client(MEILISEARCH_URL)
    
    # Create or get index
    index = client.index("books")
    
    # Configure index settings for better search
    print("⚙️ Configuring index settings...")
    index.update_settings({
        "searchableAttributes": ["title", "authors", "keywords", "genres"],
        "filterableAttributes": ["language", "popularity_tier"],
        "sortableAttributes": ["ratings_count", "avg_rating"],
        "rankingRules": [
            "words",
            "typo", 
            "proximity",
            "attribute",
            "sort",
            "exactness"
        ]
        # Note: distinctAttribute removed - we deduplicate in the app instead
    })
    
    # Check if books_clean exists, otherwise use books
    table_exists = conn.execute("""
        SELECT COUNT(*) FROM information_schema.tables 
        WHERE table_name = 'books_clean'
    """).fetchone()[0]
    
    table_name = "books_clean" if table_exists else "books"
    print(f"📚 Using table: {table_name}")
    
    # Count total books
    total = conn.execute(f"SELECT COUNT(*) FROM {table_name} WHERE title IS NOT NULL").fetchone()[0]
    print(f"📚 Total books to index: {total:,}")
    
    # Index in batches
    offset = 0
    start_time = time.time()
    
    while offset < total:
        batch_start = time.time()
        
        # Fetch batch
        query = f"""
            SELECT 
                ol_key as id,
                title,
                authors,
                genres,
                keywords,
                language,
                avg_rating,
                ratings_count,
                popularity_tier
            FROM {table_name} 
            WHERE title IS NOT NULL
            ORDER BY ratings_count DESC NULLS LAST
            LIMIT {BATCH_SIZE} OFFSET {offset}
        """
        
        rows = conn.execute(query).fetchall()
        
        # Convert to documents
        documents = []
        for idx, row in enumerate(rows):
            # Clean ID - replace invalid characters
            raw_id = row[0] or f"book_{offset + idx}"
            clean_id = raw_id.replace("/", "_").replace(" ", "_")
            
            # Normalize title for deduplication
            title = row[1] or ""
            title_norm = title.lower().strip()[:100]  # First 100 chars, lowercased
            
            doc = {
                "id": clean_id,
                "title": title,
                "title_norm": title_norm,
                "authors": row[2] or "",
                "genres": row[3] or "",
                "keywords": row[4] or "",
                "language": row[5] or "",
                "avg_rating": row[6] or 0,
                "ratings_count": row[7] or 0,
                "popularity_tier": row[8] or "unknown"
            }
            documents.append(doc)
        
        # Index batch
        task = index.add_documents(documents)
        
        offset += len(rows)
        elapsed = time.time() - start_time
        rate = offset / elapsed if elapsed > 0 else 0
        eta = (total - offset) / rate if rate > 0 else 0
        
        print(f"   📤 Indexed {offset:,}/{total:,} ({100*offset/total:.1f}%) - {rate:.0f} docs/s - ETA: {eta/60:.1f}min")
        
        if len(rows) < BATCH_SIZE:
            break
    
    print(f"\n✅ Indexing complete in {(time.time()-start_time)/60:.1f} minutes")
    print(f"   Waiting for Meilisearch to process...")
    
    # Wait for indexing to complete
    client.wait_for_task(task.task_uid)
    
    # Get stats
    stats = index.get_stats()
    print(f"   📊 Index stats: {stats['numberOfDocuments']:,} documents")

if __name__ == "__main__":
    main()
