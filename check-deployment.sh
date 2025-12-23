#!/bin/bash

echo "🔍 Vérification de l'état du déploiement"
echo "========================================"
echo ""

# Vérifier les fichiers essentiels
echo "📁 Fichiers de configuration :"
files=("Dockerfile" "railway.json" "backend/requirements.txt" "backend/database_adapter.py" "backend/books_deployment.duckdb")

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        size=$(ls -lh "$file" | awk '{print $5}')
        echo "   ✅ $file ($size)"
    else
        echo "   ❌ $file (manquant)"
    fi
done

echo ""

# Vérifier la base de données
echo "💾 Base de données :"
if [ -f "backend/books_deployment.duckdb" ]; then
    size=$(ls -lh backend/books_deployment.duckdb | awk '{print $5}')
    echo "   ✅ books_deployment.duckdb ($size)"
    echo "   📊 Base optimisée pour déploiement gratuit"
else
    echo "   ❌ Base de déploiement manquante"
    echo "   💡 Exécutez: python backend/create_deployment_db.py"
fi

echo ""

# Vérifier le frontend
echo "🎨 Frontend :"
if [ -f "frontend/package.json" ]; then
    echo "   ✅ package.json"
    if [ -d "frontend/node_modules" ]; then
        echo "   ✅ node_modules installés"
    else
        echo "   ⚠️  node_modules manquants (npm install)"
    fi
else
    echo "   ❌ Frontend non configuré"
fi

echo ""

# Vérifier Git
echo "📝 Repository Git :"
if [ -d ".git" ]; then
    echo "   ✅ Repository Git initialisé"
    
    # Vérifier les commits
    commits=$(git rev-list --count HEAD 2>/dev/null || echo "0")
    echo "   📊 $commits commits"
    
    # Vérifier les fichiers non commités
    if [ -n "$(git status --porcelain)" ]; then
        echo "   ⚠️  Fichiers non commités :"
        git status --porcelain | head -5
        echo "   💡 Exécutez: git add . && git commit -m 'Ready for deployment'"
    else
        echo "   ✅ Tous les fichiers commités"
    fi
else
    echo "   ❌ Repository Git non initialisé"
    echo "   💡 Exécutez: git init && git add . && git commit -m 'Initial commit'"
fi

echo ""

# Résumé
echo "🎯 État du déploiement :"
if [ -f "Dockerfile" ] && [ -f "railway.json" ] && [ -f "backend/books_deployment.duckdb" ]; then
    echo "   ✅ PRÊT POUR RAILWAY"
    echo ""
    echo "🚀 Prochaines étapes :"
    echo "   1. Aller sur https://railway.app"
    echo "   2. Se connecter avec GitHub"
    echo "   3. 'New Project' → 'Deploy from GitHub repo'"
    echo "   4. Sélectionner ce repository"
    echo "   5. Attendre le déploiement (~5 minutes)"
    echo ""
    echo "📊 Votre app aura :"
    echo "   • 56,323 livres français"
    echo "   • Interface moderne"
    echo "   • API REST complète"
    echo "   • 0€ de coût !"
else
    echo "   ⚠️  CONFIGURATION INCOMPLÈTE"
    echo ""
    echo "🔧 Actions requises :"
    [ ! -f "Dockerfile" ] && echo "   • Créer Dockerfile"
    [ ! -f "railway.json" ] && echo "   • Créer railway.json"
    [ ! -f "backend/books_deployment.duckdb" ] && echo "   • Créer base de déploiement"
fi

echo ""