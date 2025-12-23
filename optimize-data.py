#!/usr/bin/env python3
import sys
import os

# Ajouter le chemin de l'environnement virtuel si disponible
venv_path = os.path.join(os.path.dirname(__file__), '.venv', 'lib', 'python3.14', 'site-packages')
if os.path.exists(venv_path):
    sys.path.insert(0, venv_path)
"""
Script d'optimisation des données pour le déploiement gratuit
Réduit la taille du dataset pour respecter les limites gratuites
"""

import pandas as pd
import os

def optimize_dataset():
    """Optimiser le dataset pour les plateformes gratuites"""
    
    print("🔍 Recherche des fichiers de données...")
    
    # Trouver le fichier de données
    data_file = None
    for file in ["backend/openlibrary_books.parquet", "openlibrary_books.parquet", "backend/books_french.parquet"]:
        if os.path.exists(file):
            data_file = file
            break
    
    if not data_file:
        print("❌ Aucun fichier de données trouvé")
        return
    
    print(f"📊 Lecture de {data_file}...")
    df = pd.read_parquet(data_file)
    
    print(f"📈 Dataset original : {len(df):,} livres ({df.memory_usage(deep=True).sum() / 1024**2:.1f} MB)")
    
    # Stratégies d'optimisation
    print("\n🎯 Application des optimisations...")
    
    # 1. Garder seulement les livres avec des données complètes
    df_clean = df.dropna(subset=['title', 'authors'])
    print(f"   ✅ Suppression des livres incomplets : {len(df_clean):,} restants")
    
    # 2. Filtrer par popularité si la colonne existe
    if 'popularity_tier' in df_clean.columns:
        df_clean = df_clean[df_clean['popularity_tier'].isin(['popular', 'known'])]
        print(f"   ✅ Garde seulement popular/known : {len(df_clean):,} restants")
    
    # 3. Filtrer par nombre de ratings si disponible
    elif 'ratings_count' in df_clean.columns:
        df_clean = df_clean[df_clean['ratings_count'] >= 10]
        print(f"   ✅ Garde seulement ratings_count >= 10 : {len(df_clean):,} restants")
    
    # 4. Limiter à 200k livres max pour les plateformes gratuites
    if len(df_clean) > 200000:
        # Prioriser par ratings_count si disponible
        if 'ratings_count' in df_clean.columns:
            df_clean = df_clean.nlargest(200000, 'ratings_count')
        else:
            df_clean = df_clean.sample(n=200000, random_state=42)
        print(f"   ✅ Limitation à 200k livres : {len(df_clean):,} restants")
    
    # 5. Optimiser les types de données
    for col in df_clean.columns:
        if df_clean[col].dtype == 'object':
            # Convertir les strings en catégories si peu de valeurs uniques
            unique_ratio = df_clean[col].nunique() / len(df_clean)
            if unique_ratio < 0.1:  # Moins de 10% de valeurs uniques
                df_clean[col] = df_clean[col].astype('category')
    
    print(f"\n📉 Dataset optimisé : {len(df_clean):,} livres ({df_clean.memory_usage(deep=True).sum() / 1024**2:.1f} MB)")
    
    # Sauvegarder
    output_file = "backend/books_optimized.parquet"
    df_clean.to_parquet(output_file, compression='snappy')
    
    print(f"💾 Sauvegardé dans {output_file}")
    print(f"📊 Réduction : {(1 - len(df_clean)/len(df)) * 100:.1f}% des livres")
    
    # Statistiques finales
    print(f"\n📈 Statistiques finales :")
    if 'language' in df_clean.columns:
        print(f"   Langues : {df_clean['language'].value_counts().head().to_dict()}")
    if 'popularity_tier' in df_clean.columns:
        print(f"   Popularité : {df_clean['popularity_tier'].value_counts().to_dict()}")
    
    return output_file

def create_sample_dataset():
    """Créer un dataset d'exemple pour les tests"""
    print("\n🧪 Création d'un dataset d'exemple...")
    
    sample_data = {
        'title': [
            'Le Petit Prince', 'Harry Potter à l\'école des sorciers', '1984',
            'L\'Étranger', 'Dune', 'Le Seigneur des anneaux'
        ],
        'authors': [
            'Antoine de Saint-Exupéry', 'J.K. Rowling', 'George Orwell',
            'Albert Camus', 'Frank Herbert', 'J.R.R. Tolkien'
        ],
        'genres': [
            'Fiction, Jeunesse', 'Fantasy, Jeunesse', 'Science Fiction, Dystopie',
            'Fiction, Philosophie', 'Science Fiction', 'Fantasy, Épique'
        ],
        'keywords': [
            'prince, planète, rose, renard', 'magie, sorcier, école, amitié',
            'surveillance, totalitarisme, liberté', 'absurde, étranger, société',
            'épice, désert, politique, prophétie', 'anneau, hobbit, aventure, magie'
        ],
        'avg_rating': [4.5, 4.7, 4.2, 4.1, 4.6, 4.8],
        'ratings_count': [50000, 120000, 80000, 30000, 45000, 150000],
        'popularity_tier': ['popular', 'popular', 'popular', 'known', 'popular', 'popular'],
        'language': ['fre', 'fre', 'eng', 'fre', 'eng', 'eng'],
        'first_publish_date': [1943, 1997, 1949, 1942, 1965, 1954]
    }
    
    df_sample = pd.DataFrame(sample_data)
    sample_file = "backend/books_sample.parquet"
    df_sample.to_parquet(sample_file)
    
    print(f"💾 Dataset d'exemple créé : {sample_file}")
    print(f"📊 {len(df_sample)} livres d'exemple")
    
    return sample_file

if __name__ == "__main__":
    print("🚀 Optimisation des données pour déploiement gratuit\n")
    
    try:
        optimized_file = optimize_dataset()
        print(f"\n✅ Optimisation terminée !")
        print(f"📁 Utilisez {optimized_file} pour le déploiement")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'optimisation : {e}")
        print("🧪 Création d'un dataset d'exemple à la place...")
        sample_file = create_sample_dataset()
        print(f"📁 Utilisez {sample_file} pour tester le déploiement")