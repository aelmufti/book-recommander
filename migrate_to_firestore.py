#!/usr/bin/env python3
"""
Migrer les données du parquet vers Firestore
"""

import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import os
from tqdm import tqdm

def migrate_books_to_firestore():
    """Migrer les livres vers Firestore"""
    
    # Initialiser Firebase Admin
    if not firebase_admin._apps:
        # En local, utiliser les credentials par défaut
        firebase_admin.initialize_app()
    
    db = firestore.client()
    
    # Charger les données
    print("📊 Chargement des données...")
    df = pd.read_parquet('backend/books_french.parquet')
    
    # Limiter à 10k livres pour rester dans les limites gratuites
    df_top = df.nlargest(10000, 'ratings_count')
    print(f"📚 Sélection des {len(df_top):,} meilleurs livres")
    
    # Nettoyer les données
    df_top = df_top.dropna(subset=['title', 'authors'])
    df_top['keywords'] = df_top['keywords'].fillna('')
    df_top['genres'] = df_top['genres'].fillna('')
    
    # Migrer vers Firestore par batch
    batch_size = 500
    collection_ref = db.collection('books')
    
    print("🔄 Migration vers Firestore...")
    
    for i in tqdm(range(0, len(df_top), batch_size)):
        batch = db.batch()
        batch_data = df_top.iloc[i:i+batch_size]
        
        for idx, book in batch_data.iterrows():
            doc_ref = collection_ref.document()
            
            book_data = {
                'title': book['title'],
                'authors': book['authors'],
                'genres': book.get('genres', ''),
                'keywords': book.get('keywords', ''),
                'avg_rating': float(book.get('avg_rating', 0)) if pd.notna(book.get('avg_rating')) else None,
                'ratings_count': int(book.get('ratings_count', 0)) if pd.notna(book.get('ratings_count')) else 0,
                'popularity_tier': book.get('popularity_tier', 'unknown'),
                'language': book.get('language', 'fre'),
                'first_publish_date': int(book.get('first_publish_date', 0)) if pd.notna(book.get('first_publish_date')) else None
            }
            
            batch.set(doc_ref, book_data)
        
        # Commit le batch
        batch.commit()
    
    print(f"✅ Migration terminée : {len(df_top):,} livres dans Firestore")

if __name__ == "__main__":
    migrate_books_to_firestore()