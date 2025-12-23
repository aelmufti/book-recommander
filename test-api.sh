#!/bin/bash

# Script de test pour l'API Book Finder déployée sur Render
# Usage: ./test-api.sh https://votre-url.onrender.com

if [ -z "$1" ]; then
    echo "❌ Usage: ./test-api.sh <URL_API>"
    echo "   Exemple: ./test-api.sh https://book-finder-api-xxxx.onrender.com"
    exit 1
fi

API_URL=$1
echo "🧪 Test de l'API Book Finder: $API_URL"
echo "================================================"

# Test 1: Endpoint racine
echo "📊 Test 1: Informations de l'API..."
curl -s "$API_URL/" | jq '.' || echo "❌ Échec du test 1"
echo ""

# Test 2: Recherche de livres
echo "🔍 Test 2: Recherche 'science fiction'..."
curl -s -X POST "$API_URL/recommend" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "science fiction", "language": "fre"}' | \
  jq '.recommendation, .candidates_count, .dataset_size' || echo "❌ Échec du test 2"
echo ""

# Test 3: Livre aléatoire
echo "🎲 Test 3: Livre aléatoire..."
curl -s "$API_URL/random-unknown?language=fre" | \
  jq '.book.title, .book.authors' || echo "❌ Échec du test 3"
echo ""

# Test 4: Statistiques
echo "📈 Test 4: Statistiques du dataset..."
curl -s "$API_URL/stats" | \
  jq '.total_books, .languages.fre' || echo "❌ Échec du test 4"
echo ""

echo "✅ Tests terminés !"
echo "💡 Si tous les tests passent, votre API est prête !"