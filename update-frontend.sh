#!/bin/bash

# Script pour mettre à jour le frontend avec l'URL de l'API Render
# Usage: ./update-frontend.sh https://book-finder-api-xxxx.onrender.com

if [ -z "$1" ]; then
    echo "❌ Usage: ./update-frontend.sh <URL_API_RENDER>"
    echo "   Exemple: ./update-frontend.sh https://book-finder-api-xxxx.onrender.com"
    exit 1
fi

API_URL=$1
echo "🔧 Mise à jour du frontend avec l'API: $API_URL"

# Mettre à jour le fichier .env
echo "REACT_APP_API_URL=$API_URL" > frontend/.env
echo "✅ Fichier frontend/.env mis à jour"

# Construire et déployer
echo "🏗️ Construction du frontend..."
cd frontend
npm run build

echo "🚀 Déploiement sur Firebase..."
firebase deploy --only hosting

echo ""
echo "🎉 Frontend mis à jour avec succès !"
echo "📱 Votre app: https://book-recommander-sarah.web.app"
echo "🔗 Votre API: $API_URL"
echo ""
echo "✅ Votre Book Finder est maintenant live avec 56k livres !"