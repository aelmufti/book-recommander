# 🔧 Dépannage Render - Guide Complet

## 🚨 Problème Actuel

Votre API sur Render retourne encore des erreurs DuckDB alors que le nouveau code utilise pandas.

## ✅ Solutions (dans l'ordre)

### 1. **Vérifier le Redéploiement** (2 minutes)

1. Allez sur **https://dashboard.render.com**
2. Cliquez sur votre service (book-finder-api ou similaire)
3. Regardez l'onglet **"Events"** - vous devriez voir un nouveau déploiement
4. Si pas de nouveau déploiement, cliquez **"Manual Deploy"** → **"Deploy latest commit"**

### 2. **Vérifier les Logs** (1 minute)

Dans l'onglet **"Logs"** de votre service Render, vous devriez voir :
```
🚀 Initialisation de l'API Book Finder...
📊 Chargement du dataset: books_french.parquet
✅ Dataset chargé: 56,323 livres
INFO: Uvicorn running on http://0.0.0.0:10000
```

**Si vous voyez encore des références à DuckDB ou Meilisearch**, le cache n'est pas encore vidé.

### 3. **Test de l'API** (30 secondes)

```bash
# Test rapide
curl https://book-recommander.onrender.com/

# Devrait retourner quelque chose comme :
# {"status":"ready","message":"Book Finder API - 56k livres français","dataset_size":56323,"version":"2.0.0"}
```

### 4. **Si ça ne marche toujours pas** (5 minutes)

#### Option A: Recréer le service
1. Sur Render, **supprimez** votre service actuel
2. Créez un **nouveau service** avec les mêmes paramètres :
   ```
   Root Directory: backend
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```

#### Option B: Vérifier la configuration
1. Vérifiez que **Root Directory** = `backend`
2. Vérifiez que **Start Command** = `uvicorn main:app --host 0.0.0.0 --port $PORT`

## 🧪 Tests Automatiques

Une fois que ça marche, testez avec :

```bash
# Test complet
./test-simple.sh

# Test spécifique
curl -X POST https://book-recommander.onrender.com/recommend \
  -H "Content-Type: application/json" \
  -d '{"prompt": "science fiction", "language": "fre"}'
```

## ✅ Résultat Attendu

Quand tout fonctionne, vous devriez voir :

```json
{
  "status": "ready",
  "message": "Book Finder API - 56k livres français", 
  "dataset_size": 56323,
  "platform": "Render + Pandas",
  "version": "2.0.0",
  "data_loaded": true
}
```

## 🎯 Prochaines Étapes

Une fois l'API fonctionnelle :

1. **Testez** : `./test-simple.sh`
2. **Mettez à jour le frontend** : `./update-frontend.sh https://book-recommander.onrender.com`
3. **Profitez** de vos 56k livres ! 🎉

## 📞 Support

- **Render Support** : help@render.com
- **Logs Render** : Dashboard → Votre service → Logs
- **Status Render** : https://status.render.com

---

**⏰ Temps de résolution estimé : 5-15 minutes**