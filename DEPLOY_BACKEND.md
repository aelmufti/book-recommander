# Déploiement du Backend Book Finder

## Option 1: Render (Recommandé - Gratuit)

### Étapes:

1. **Créer un compte sur Render.com**
   - Aller sur https://render.com
   - S'inscrire avec GitHub

2. **Créer un nouveau Web Service**
   - Cliquer sur "New +" → "Web Service"
   - Connecter votre repository GitHub
   - Sélectionner le dossier `backend/`

3. **Configuration du service:**
   - **Name**: `book-finder-api`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Plan**: Free (512MB RAM, 750h/mois)

4. **Variables d'environnement:**
   - `PYTHON_VERSION`: `3.11`

5. **Déployer**
   - Cliquer sur "Create Web Service"
   - Attendre le déploiement (5-10 minutes)

### URL de l'API:
Votre API sera disponible à: `https://book-finder-api-XXXX.onrender.com`

## Option 2: Railway (Payant - €5/mois)

Si vous préférez Railway:

1. Aller sur https://railway.app
2. Connecter GitHub
3. Déployer le dossier `backend/`
4. Railway détectera automatiquement Python

## Option 3: Google Cloud Run (Gratuit avec limites)

Nécessite une carte de crédit pour l'activation mais reste gratuit dans les limites:

1. Activer la facturation sur Google Cloud
2. Utiliser le dossier `cloud-run-backend/`
3. Déployer avec: `gcloud run deploy`

## Test de l'API

Une fois déployée, testez avec:

```bash
curl https://VOTRE-URL/
curl -X POST https://VOTRE-URL/recommend \
  -H "Content-Type: application/json" \
  -d '{"prompt": "science fiction", "language": "fre"}'
```

## Mise à jour du Frontend

Une fois l'API déployée, mettez à jour `frontend/src/BookDatabase.js` avec l'URL de votre API.