#!/bin/bash

echo "🚀 Script de déploiement Book Recommender"
echo ""

# Vérifier si Git est initialisé
if [ ! -d ".git" ]; then
    echo "📁 Initialisation du repository Git..."
    git init
    git add .
    git commit -m "Initial commit"
fi

echo "Choisissez votre plateforme de déploiement :"
echo "1) Railway (Recommandé - Backend + Frontend + DB)"
echo "2) Vercel + Supabase (Frontend + API Functions + DB)"
echo "3) Render (Backend + Frontend séparés)"
echo ""
read -p "Votre choix (1-3) : " choice

case $choice in
    1)
        echo "🚂 Déploiement Railway sélectionné"
        echo ""
        echo "Étapes à suivre :"
        echo "1. Aller sur https://railway.app"
        echo "2. Se connecter avec GitHub"
        echo "3. 'New Project' → 'Deploy from GitHub repo'"
        echo "4. Sélectionner ce repository"
        echo "5. Railway détectera automatiquement la config"
        echo ""
        echo "📋 Fichiers de configuration créés :"
        echo "   ✅ Dockerfile"
        echo "   ✅ railway.json"
        echo "   ✅ database_adapter.py"
        echo ""
        echo "🔗 Après déploiement, votre app sera disponible sur :"
        echo "   https://your-app.up.railway.app"
        ;;
    2)
        echo "⚡ Déploiement Vercel + Supabase sélectionné"
        echo ""
        echo "Étapes à suivre :"
        echo "1. Créer un compte Supabase : https://supabase.com"
        echo "2. Créer un nouveau projet et noter l'URL + clé API"
        echo "3. Installer Vercel CLI : npm i -g vercel"
        echo "4. Déployer : vercel --prod"
        echo "5. Configurer les variables d'environnement"
        echo ""
        echo "📋 Fichiers de configuration créés :"
        echo "   ✅ vercel.json"
        echo ""
        ;;
    3)
        echo "🎨 Déploiement Render sélectionné"
        echo ""
        echo "Étapes à suivre :"
        echo "1. Aller sur https://render.com"
        echo "2. Créer 2 services :"
        echo "   - Web Service (backend Python)"
        echo "   - Static Site (frontend React)"
        echo "3. Connecter votre repository GitHub"
        echo ""
        echo "Configuration backend :"
        echo "   Build Command: pip install -r backend/requirements.txt"
        echo "   Start Command: uvicorn backend.main:app --host 0.0.0.0 --port \$PORT"
        echo ""
        echo "Configuration frontend :"
        echo "   Build Command: cd frontend && npm install && npm run build"
        echo "   Publish Directory: frontend/dist"
        ;;
    *)
        echo "❌ Choix invalide"
        exit 1
        ;;
esac

echo ""
echo "📚 Documentation complète disponible dans :"
echo "   - railway-deploy.md"
echo "   - vercel-deploy.md"
echo ""
echo "💡 Conseil : Railway est le plus simple pour commencer !"