#!/bin/bash

echo "🧪 Test complet du déploiement Book Finder"
echo "=========================================="

# Test 1: API Backend sur Render
echo "📡 Test 1: API Backend (Render)"
API_STATUS=$(curl -s https://book-recommander.onrender.com/ | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f'Status: {data[\"status\"]}')
    print(f'Dataset: {data[\"dataset_size\"]} livres')
    print(f'Version: {data[\"version\"]}')
except:
    print('❌ Erreur API')
")
echo "$API_STATUS"

# Test 2: Recherche de livres
echo ""
echo "🔍 Test 2: Recherche de livres"
SEARCH_RESULT=$(curl -s -X POST "https://book-recommander.onrender.com/recommend" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "harry potter", "language": "fre"}' | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f'Résultats: {data[\"candidates_count\"]} livres')
    if data['book']:
        print(f'Premier: {data[\"book\"][\"title\"]}')
    print(f'Plateforme: {data[\"platform\"]}')
except Exception as e:
    print(f'❌ Erreur: {e}')
")
echo "$SEARCH_RESULT"

# Test 3: Frontend Firebase
echo ""
echo "🌐 Test 3: Frontend (Firebase)"
FRONTEND_STATUS=$(curl -s -I https://book-recommander-sarah.web.app | head -1)
echo "Status: $FRONTEND_STATUS"

echo ""
echo "✅ URLs de déploiement:"
echo "🔗 Frontend: https://book-recommander-sarah.web.app"
echo "🔗 API: https://book-recommander.onrender.com"
echo "🔗 API Docs: https://book-recommander.onrender.com/docs"

echo ""
echo "📊 Statistiques:"
echo "• 56,323 livres français dans la base"
echo "• API FastAPI + Pandas sur Render.com"
echo "• Frontend React sur Firebase Hosting"
echo "• Déploiement 100% gratuit ✅"