#!/usr/bin/env python3
"""
Créer un dataset d'exemple pour tester Firebase
"""

import json

# Dataset d'exemple avec des livres français populaires
sample_books = [
    {
        "title": "Le Petit Prince",
        "authors": "Antoine de Saint-Exupéry",
        "genres": "Fiction, Jeunesse",
        "keywords": "prince planète rose renard amitié voyage",
        "avg_rating": 4.5,
        "ratings_count": 50000,
        "popularity_tier": "popular",
        "language": "fre",
        "first_publish_date": 1943
    },
    {
        "title": "Harry Potter à l'école des sorciers",
        "authors": "J.K. Rowling",
        "genres": "Fantasy, Jeunesse",
        "keywords": "magie sorcier école amitié poudlard",
        "avg_rating": 4.7,
        "ratings_count": 120000,
        "popularity_tier": "popular",
        "language": "fre",
        "first_publish_date": 1997
    },
    {
        "title": "L'Étranger",
        "authors": "Albert Camus",
        "genres": "Fiction, Philosophie",
        "keywords": "absurde étranger société existentialisme",
        "avg_rating": 4.1,
        "ratings_count": 30000,
        "popularity_tier": "known",
        "language": "fre",
        "first_publish_date": 1942
    },
    {
        "title": "Les Misérables",
        "authors": "Victor Hugo",
        "genres": "Fiction, Historique",
        "keywords": "révolution paris jean valjean justice",
        "avg_rating": 4.4,
        "ratings_count": 25000,
        "popularity_tier": "known",
        "language": "fre",
        "first_publish_date": 1862
    },
    {
        "title": "Madame Bovary",
        "authors": "Gustave Flaubert",
        "genres": "Fiction, Classique",
        "keywords": "femme mariage ennui province réalisme",
        "avg_rating": 3.9,
        "ratings_count": 18000,
        "popularity_tier": "known",
        "language": "fre",
        "first_publish_date": 1857
    }
]

# Sauvegarder en JSON pour import manuel
with open('sample_books.json', 'w', encoding='utf-8') as f:
    json.dump(sample_books, f, ensure_ascii=False, indent=2)

print(f"✅ Créé sample_books.json avec {len(sample_books)} livres")
print("📋 Vous pouvez importer ces données manuellement dans Firestore")