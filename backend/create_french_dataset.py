#!/usr/bin/env python3
"""
Create a French books dataset from OpenLibrary data.
Filters for French language books with Latin character titles, then deduplicates.
"""

import duckdb
import time
import os
import unicodedata
import re

def main():
    start = time.time()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, 'books.duckdb')
    conn = duckdb.connect(db_path)
    
    # Register UDFs
    def normalize_text(text):
        if not text:
            return ""
        normalized = unicodedata.normalize('NFD', text)
        ascii_text = ''.join(c for c in normalized if unicodedata.category(c) != 'Mn')
        clean = ''.join(c if c.isalnum() or c.isspace() else ' ' for c in ascii_text)
        return ' '.join(clean.lower().split())
    
    def is_latin_title(text):
        """Check if title is primarily Latin characters (French/English/etc)"""
        if not text:
            return False
        # Count Latin vs non-Latin characters
        latin = sum(1 for c in text if c.isascii() or c in 'àâäéèêëïîôùûüçœæÀÂÄÉÈÊËÏÎÔÙÛÜÇŒÆ')
        total = sum(1 for c in text if c.isalpha())
        if total == 0:
            return False
        return latin / total > 0.8  # At least 80% Latin characters
    
    conn.create_function('normalize_text', normalize_text, return_type='VARCHAR')
    conn.create_function('is_latin_title', is_latin_title, return_type='BOOLEAN')
    
    print("🇫🇷 Creating French books dataset...")
    print()
    
    # Step 1: Extract French books with ratings AND Latin titles
    print("📚 Step 1: Extracting French books with Latin titles...")
    conn.execute("""
        CREATE OR REPLACE TABLE books_french_raw AS
        SELECT 
            title,
            authors,
            author_keys,
            genres,
            keywords,
            first_publish_date,
            'fre' as language,
            ol_key,
            avg_rating,
            ratings_count,
            popularity_tier
        FROM books 
        WHERE language IN ('fre', 'fr', 'fra', 'french')
        AND ratings_count > 0
        AND is_latin_title(title)
    """)
    
    count = conn.execute("SELECT COUNT(*) FROM books_french_raw").fetchone()[0]
    print(f"   Found {count:,} French books with Latin titles")
    
    # Step 2: Aggressive deduplication
    print()
    print("🔄 Step 2: Deduplicating...")
    conn.execute("""
        CREATE OR REPLACE TABLE books_french AS
        WITH normalized AS (
            SELECT 
                *,
                normalize_text(
                    REGEXP_REPLACE(
                        REGEXP_REPLACE(
                            REGEXP_REPLACE(
                                REGEXP_REPLACE(title, '\\([^)]*\\)', '', 'g'),
                                '\\[[^\\]]*\\]', '', 'g'
                            ),
                            '(tome|volume|t\\.|vol\\.|#|:)\\s*\\d*', '', 'gi'
                        ),
                        '\\d{4}', '', 'g'
                    )
                ) as clean_title,
                normalize_text(authors) as clean_author
            FROM books_french_raw
        ),
        with_key AS (
            SELECT 
                *,
                CONCAT(
                    COALESCE(SPLIT_PART(TRIM(clean_title), ' ', 1), ''), ' ',
                    COALESCE(SPLIT_PART(TRIM(clean_title), ' ', 2), ''), ' ',
                    COALESCE(SPLIT_PART(TRIM(clean_author), ' ', -1), '')
                ) as dedup_key
            FROM normalized
            WHERE LENGTH(TRIM(clean_title)) > 2
        ),
        ranked AS (
            SELECT 
                *,
                ROW_NUMBER() OVER (
                    PARTITION BY dedup_key 
                    ORDER BY ratings_count DESC
                ) as rn
            FROM with_key
        )
        SELECT 
            title,
            authors,
            author_keys,
            genres,
            keywords,
            first_publish_date,
            language,
            ol_key,
            avg_rating,
            ratings_count,
            popularity_tier
        FROM ranked
        WHERE rn = 1
    """)
    
    count = conn.execute("SELECT COUNT(*) FROM books_french").fetchone()[0]
    print(f"   After deduplication: {count:,} books")
    
    # Step 3: Show stats
    print()
    print("📊 Dataset statistics:")
    
    result = conn.execute("""
        SELECT 
            COUNT(CASE WHEN ratings_count >= 1000000 THEN 1 END) as million_plus,
            COUNT(CASE WHEN ratings_count >= 100000 AND ratings_count < 1000000 THEN 1 END) as hundred_k,
            COUNT(CASE WHEN ratings_count >= 10000 AND ratings_count < 100000 THEN 1 END) as ten_k,
            COUNT(CASE WHEN ratings_count >= 1000 AND ratings_count < 10000 THEN 1 END) as one_k,
            COUNT(CASE WHEN ratings_count < 1000 THEN 1 END) as under_1k
        FROM books_french
    """).fetchone()
    print(f"   1M+ ratings: {result[0]:,}")
    print(f"   100K-1M ratings: {result[1]:,}")
    print(f"   10K-100K ratings: {result[2]:,}")
    print(f"   1K-10K ratings: {result[3]:,}")
    print(f"   <1K ratings: {result[4]:,}")
    
    # Top authors
    print()
    print("📖 Top 20 authors:")
    result = conn.execute("""
        SELECT authors, COUNT(*) as books, SUM(ratings_count) as total_ratings
        FROM books_french
        GROUP BY authors
        ORDER BY total_ratings DESC
        LIMIT 20
    """).fetchall()
    for i, (author, books, ratings) in enumerate(result, 1):
        print(f"   {i:2}. {author[:35]:35} ({books:3} books, {ratings:,} ratings)")
    
    # Sample books
    print()
    print("📚 Top 30 books:")
    result = conn.execute("""
        SELECT title, authors, ratings_count
        FROM books_french
        ORDER BY ratings_count DESC
        LIMIT 30
    """).fetchall()
    for i, (title, author, ratings) in enumerate(result, 1):
        print(f"   {i:2}. {title[:40]:40} - {author[:20]} ({ratings:,})")
    
    # Check Petit Prince
    print()
    print("🔍 Checking Le Petit Prince:")
    result = conn.execute("""
        SELECT title, authors, ratings_count
        FROM books_french
        WHERE LOWER(title) LIKE '%petit prince%'
        ORDER BY ratings_count DESC
        LIMIT 5
    """).fetchall()
    for title, author, ratings in result:
        print(f"   {title[:50]} - {author} ({ratings:,})")
    
    # Export
    print()
    print("💾 Exporting to parquet...")
    parquet_path = os.path.join(script_dir, 'books_french.parquet')
    conn.execute(f"COPY books_french TO '{parquet_path}' (FORMAT PARQUET)")
    
    conn.execute("DROP TABLE IF EXISTS books_french_raw")
    
    elapsed = time.time() - start
    print()
    print(f"✅ Done in {elapsed:.1f}s!")
    print(f"   Created table 'books_french' with {count:,} books")
    
    conn.close()

if __name__ == "__main__":
    main()
