# 🚀 Déploiement sur Render.com - Guide Complet

## Étape 1: Créer un compte Render

1. Allez sur **https://render.com**
2. Cliquez sur **"Get Started for Free"**
3. Connectez-vous avec votre compte **GitHub**

## Étape 2: Préparer votre Repository

Assurez-vous que votre code est poussé sur GitHub avec le dossier `backend/` contenant:
- ✅ `main.py` (API FastAPI)
- ✅ `requirements.txt` (dépendances Python)
- ✅ `books_french.parquet` (dataset 56k livres - 32MB)

## Étape 3: Créer un Web Service

1. Sur le dashboard Render, cliquez sur **"New +"**
2. Sélectionnez **"Web Service"**
3. Connectez votre repository GitHub
4. Sélectionnez votre repository `book-recommander`

## Étape 4: Configuration du Service

### Paramètres de base:
- **Name**: `book-finder-api` (ou votre nom préféré)
- **Region**: `Oregon (US West)` (recommandé)
- **Branch**: `main` (ou votre branche principale)
- **Root Directory**: `backend`

### Paramètres de build:
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Plan:
- **Instance Type**: `Free` (512 MB RAM, 0.1 CPU)
- **Auto-Deploy**: `Yes` (recommandé)

## Étape 5: Variables d'environnement (optionnel)

Dans la section "Environment Variables", vous pouvez ajouter:
- `PYTHON_VERSION`: `3.11`

## Étape 6: Déployer

1. Cliquez sur **"Create Web Service"**
2. Render va automatiquement:
   - Cloner votre repository
   - Installer les dépendances
   - Démarrer votre API
   - Vous donner une URL publique

## Étape 7: Attendre le déploiement

⏱️ **Temps estimé**: 5-10 minutes

Vous verrez les logs en temps réel:
```
==> Cloning from https://github.com/votre-username/book-recommander...
==> Using Python version 3.11.x
==> Installing dependencies from requirements.txt
==> Starting server with uvicorn main:app --host 0.0.0.0 --port $PORT
📊 Chargement de books_french.parquet...
✅ 56,323 livres français chargés en mémoire
INFO: Uvicorn running on http://0.0.0.0:10000
```

## Étape 8: Tester votre API

Une fois déployé, votre API sera disponible à:
```
https://book-finder-api-XXXX.onrender.com
```

Testez avec:
```bash
# Test de base
curl https://votre-url.onrender.com/

# Test de recherche
curl -X POST https://votre-url.onrender.com/recommend \
  -H "Content-Type: application/json" \
  -d '{"prompt": "science fiction", "language": "fre"}'
```

## Étape 9: Mettre à jour le Frontend

1. Copiez l'URL de votre API Render
2. Modifiez `frontend/.env`:
   ```
   REACT_APP_API_URL=https://votre-url.onrender.com
   ```
3. Redéployez le frontend:
   ```bash
   cd frontend
   npm run build
   firebase deploy --only hosting
   ```

## 🎉 Félicitations !

Votre Book Finder est maintenant entièrement déployé avec:
- ✅ **Frontend**: https://book-recommander-sarah.web.app
- ✅ **Backend**: https://votre-url.onrender.com
- ✅ **Dataset**: 56,323 livres français

## 📊 Limites du plan gratuit Render

- **RAM**: 512 MB (suffisant pour 56k livres)
- **CPU**: 0.1 CPU partagé
- **Stockage**: 1 GB (votre dataset fait 32MB)
- **Bande passante**: Illimitée
- **Temps d'activité**: Service peut s'endormir après 15min d'inactivité
- **Réveil**: ~30 secondes pour redémarrer

## 🔧 Dépannage

### Problème: Service ne démarre pas
- Vérifiez que `requirements.txt` est dans le dossier `backend/`
- Vérifiez que `books_french.parquet` est bien présent

### Problème: Mémoire insuffisante
- Le dataset de 32MB devrait passer sur le plan gratuit
- Si problème, contactez le support Render

### Problème: Service lent au réveil
- Normal sur le plan gratuit
- Première requête après inactivité prend ~30s

## 📞 Support

- Documentation Render: https://render.com/docs
- Support: help@render.com
- Communauté: https://community.render.com