#!/usr/bin/env python3
"""
Créer une base DuckDB légère pour le déploiement gratuit
Utilise le dataset français (56k livres) au lieu du dataset complet (43M livres)
"""

import duckdb
import os
import time

def create_deployment_db():
    """Créer une base DuckDB optimisée pour le déploiement"""
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parquet_file = os.path.join(script_dir, 'books_french.parquet')
    db_file = os.path.join(script_dir, 'books_deployment.duckdb')
    
    if not os.path.exists(parquet_file):
        print(f"❌ Fichier {parquet_file} non trouvé")
        return False
    
    print("🚀 Création de la base DuckDB pour déploiement...")
    print(f"📊 Source: {parquet_file}")
    print(f"💾 Destination: {db_file}")
    
    # Supprimer l'ancienne base si elle existe
    if os.path.exists(db_file):
        os.remove(db_file)
    
    # Créer la nouvelle base
    conn = duckdb.connect(db_file)
    
    # Charger les données depuis le parquet
    print("📥 Chargement des données...")
    conn.execute(f"""
        CREATE TABLE books AS 
        SELECT * FROM read_parquet('{parquet_file}')
    """)
    
    # Vérifier les données
    count = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    print(f"✅ {count:,} livres chargés")
    
    # Créer des index pour optimiser les performances
    print("🔍 Création des index...")
    conn.execute("CREATE INDEX idx_books_title ON books(title)")
    conn.execute("CREATE INDEX idx_books_authors ON books(authors)")
    conn.execute("CREATE INDEX idx_books_language ON books(language)")
    conn.execute("CREATE INDEX idx_books_popularity ON books(popularity_tier)")
    
    # Créer une vue pour les livres populaires (pour les recherches rapides)
    print("📋 Création de la vue popular_books...")
    conn.execute("""
        CREATE VIEW popular_books AS
        SELECT * FROM books 
        WHERE popularity_tier IN ('popular', 'known')
        ORDER BY ratings_count DESC
    """)
    
    popular_count = conn.execute("SELECT COUNT(*) FROM popular_books").fetchone()[0]
    print(f"✅ Vue popular_books: {popular_count:,} livres")
    
    # Statistiques finales
    print("\n📊 Statistiques de la base:")
    
    # Par popularité
    result = conn.execute("""
        SELECT popularity_tier, COUNT(*) as count
        FROM books 
        GROUP BY popularity_tier 
        ORDER BY count DESC
    """).fetchall()
    
    for tier, count in result:
        print(f"   {tier}: {count:,} livres")
    
    # Taille du fichier
    file_size = os.path.getsize(db_file) / (1024 * 1024)
    print(f"\n💾 Taille de la base: {file_size:.1f} MB")
    
    conn.close()
    
    print(f"\n✅ Base de déploiement créée: {db_file}")
    print("🚀 Prête pour Railway/Vercel/Render !")
    
    return True

if __name__ == "__main__":
    create_deployment_db()