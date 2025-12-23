#!/bin/bash

# Test simple de l'API sans dépendances
API_URL=${1:-"https://book-recommander.onrender.com"}

echo "🧪 Test de l'API Book Finder: $API_URL"
echo "================================================"

echo "📊 Test 1: Informations de l'API..."
curl -s "$API_URL/" && echo ""

echo ""
echo "🔍 Test 2: Recherche 'roman'..."
curl -s -X POST "$API_URL/recommend" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "roman", "language": "fre"}' && echo ""

echo ""
echo "🎲 Test 3: Livre aléatoire..."
curl -s "$API_URL/random-unknown?language=fre" && echo ""

echo ""
echo "📈 Test 4: Statistiques..."
curl -s "$API_URL/stats" && echo ""

echo ""
echo "✅ Tests terminés !"