# 🚀 Render.com - Guide Pas à Pas (5 minutes)

## ✅ Étape 1: Aller sur Render.com

1. Ouvrez votre navigateur
2. Allez sur **https://render.com**
3. Cliquez sur **"Get Started for Free"**
4. Connectez-vous avec **GitHub**

## ✅ Étape 2: Créer un Web Service

1. Sur le dashboard Render, cliquez sur **"New +"** (bouton bleu en haut à droite)
2. Dans le menu, sélectionnez **"Web Service"**
3. Vous verrez vos repositories GitHub
4. Trouvez **"book-recommander"** et cliquez sur **"Connect"**

## ✅ Étape 3: Configuration (COPIEZ-COLLEZ exactement)

Vous verrez un formulaire. Remplissez avec ces valeurs EXACTES :

```
┌─────────────────────────────────────────┐
│ Name: book-finder-api                   │
│ Region: Oregon (US West)                │
│ Branch: main                            │
│ Root Directory: backend                 │ ← IMPORTANT !
│                                         │
│ Runtime: Python 3                      │
│                                         │
│ Build Command:                          │
│ pip install -r requirements.txt        │
│                                         │
│ Start Command:                          │
│ uvicorn main:app --host 0.0.0.0 --port $PORT │
│                                         │
│ Instance Type: Free                     │
│ Auto-Deploy: Yes                        │
└─────────────────────────────────────────┘
```

## ✅ Étape 4: Déployer

1. Vérifiez que tous les champs sont corrects
2. Cliquez sur **"Create Web Service"** (bouton bleu en bas)
3. Render va commencer le déploiement automatiquement

## ✅ Étape 5: Attendre (5-10 minutes)

Vous verrez des logs comme ça :
```
==> Cloning from https://github.com/votre-username/book-recommander...
==> Using Python version 3.11.x
==> Installing dependencies from requirements.txt
==> Starting server...
📊 Chargement de books_french.parquet...
✅ 56,323 livres français chargés en mémoire
INFO: Uvicorn running on http://0.0.0.0:10000
==> Your service is live 🎉
```

## ✅ Étape 6: Récupérer votre URL

1. Une fois déployé, vous verrez en haut de la page :
   **"Your service is live at https://book-finder-api-XXXX.onrender.com"**
2. **COPIEZ cette URL** - vous en aurez besoin !

## ✅ Étape 7: Tester votre API

Dans votre terminal, testez :
```bash
# Remplacez par votre vraie URL
./test-api.sh https://book-finder-api-XXXX.onrender.com
```

Vous devriez voir :
```
✅ 56,323 livres français
✅ Recherche fonctionne
✅ API prête !
```

## ✅ Étape 8: Mettre à jour le Frontend

1. Éditez le fichier `frontend/.env` :
   ```
   REACT_APP_API_URL=https://book-finder-api-XXXX.onrender.com
   ```

2. Redéployez le frontend :
   ```bash
   cd frontend
   npm run build
   firebase deploy --only hosting
   ```

## 🎉 TERMINÉ !

Votre Book Finder est maintenant live avec 56k livres :
- **Frontend** : https://book-recommander-sarah.web.app
- **Backend** : https://book-finder-api-XXXX.onrender.com

## 🆘 Problèmes ?

### "Build failed" ?
- Vérifiez que **Root Directory** = `backend`
- Vérifiez que **Build Command** = `pip install -r requirements.txt`

### "Service won't start" ?
- Vérifiez que **Start Command** = `uvicorn main:app --host 0.0.0.0 --port $PORT`

### Besoin d'aide ?
- 📧 help@render.com
- 💬 https://community.render.com

---
**Temps total : 5-10 minutes** ⏰