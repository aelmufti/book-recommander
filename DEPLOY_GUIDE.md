# 🚀 Guide de déploiement - Book Finder

Votre projet est maintenant **prêt pour le déploiement gratuit** !

## 📊 Optimisations effectuées

✅ **Base de données légère** : `books_deployment.duckdb` (35MB au lieu de 7.3GB)  
✅ **Dataset français** : 56,323 livres (au lieu de 43M)  
✅ **Adaptateur multi-base** : DuckDB local → PostgreSQL production  
✅ **Configuration Docker** : Dockerfile + railway.json  
✅ **Requirements mis à jour** : PostgreSQL + SQLAlchemy  

## 🎯 Déploiement Railway (Recommandé)

### Étape 1 : Préparer le repository
```bash
# Ajouter tous les fichiers de déploiement
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

### Étape 2 : Déployer sur Railway
1. Aller sur [railway.app](https://railway.app)
2. Se connecter avec GitHub
3. "New Project" → "Deploy from GitHub repo"
4. Sélectionner votre repository `book-recommander`
5. Railway détecte automatiquement :
   - **Backend** : Dockerfile → API Python
   - **Frontend** : package.json → Site React
   - **Database** : PostgreSQL automatique

### Étape 3 : Configuration automatique
Railway configure automatiquement :
- ✅ Variables d'environnement (`DATABASE_URL`)
- ✅ Migration des données (56k livres français)
- ✅ Index de performance
- ✅ CORS pour le frontend

### Étape 4 : URLs finales
Après déploiement (~5 minutes) :
- **Frontend** : `https://book-finder-frontend.up.railway.app`
- **API** : `https://book-finder-backend.up.railway.app`
- **Docs** : `https://book-finder-backend.up.railway.app/docs`

## 📋 Limites gratuites Railway
- **500h/mois** (~16h/jour)
- **1GB RAM** par service
- **1GB base PostgreSQL**
- **100GB bande passante**

## 🔄 Alternatives

### Option 2 : Vercel + Supabase
```bash
# Frontend sur Vercel
npm i -g vercel
cd frontend && vercel --prod

# Base sur Supabase
# 1. Créer projet sur supabase.com
# 2. Importer books_french.parquet
# 3. Configurer les variables d'env
```

### Option 3 : Render
```bash
# Backend : Web Service
# Build: pip install -r backend/requirements.txt
# Start: uvicorn backend.main:app --host 0.0.0.0 --port $PORT

# Frontend : Static Site  
# Build: cd frontend && npm install && npm run build
# Publish: frontend/dist
```

## 🧪 Test local avant déploiement

```bash
# Backend
source .venv/bin/activate
cd backend && uvicorn main:app --reload

# Frontend (nouveau terminal)
cd frontend && npm run dev
```

Ouvrir http://localhost:5173 et tester une recherche.

## 🎉 Après déploiement

Votre moteur de recherche sera accessible avec :
- **56k livres français** indexés
- **Recherche par mots-clés** intelligente
- **Interface Liquid Glass** moderne
- **API REST** documentée
- **0€ de coût** !

## 🆘 Dépannage

**Erreur de migration** : Les données se migrent automatiquement au premier démarrage  
**Timeout** : Normal au premier lancement (migration des 56k livres)  
**CORS** : Configuré automatiquement pour Railway  
**Variables d'env** : `DATABASE_URL` ajouté automatiquement par Railway  

---

🚀 **Prêt à déployer ?** Lancez `./deploy.sh` et choisissez Railway !