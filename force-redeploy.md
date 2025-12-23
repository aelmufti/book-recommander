# 🔄 Forcer le Redéploiement sur Render

## Méthode 1: Via l'interface Render

1. Allez sur https://dashboard.render.com
2. Cliquez sur votre service "book-finder-api" (ou le nom que vous avez donné)
3. Cliquez sur **"Manual Deploy"** → **"Deploy latest commit"**
4. Attendez 5-10 minutes

## Méthode 2: Push vide pour déclencher le redéploiement

```bash
git commit --allow-empty -m "Force redeploy on Render"
git push origin main
```

## Méthode 3: Vérifier les logs Render

1. Sur le dashboard Render, cliquez sur votre service
2. Allez dans l'onglet **"Logs"**
3. Vous devriez voir :
   ```
   🚀 Initialisation de l'API Book Finder...
   📊 Chargement du dataset: books_french.parquet
   ✅ Dataset chargé: 56,323 livres
   ```

## Test après redéploiement

```bash
./test-simple.sh
```

Vous devriez voir :
```json
{
  "status": "ready",
  "message": "Book Finder API - 56k livres français",
  "dataset_size": 56323,
  "platform": "Render + Pandas",
  "version": "2.0.0"
}
```

## Si le problème persiste

Le problème peut venir de :
1. **Cache Render** : Attendez 15-20 minutes
2. **Fichier manquant** : Vérifiez que `books_french.parquet` est bien dans le repo
3. **Dépendances** : Vérifiez que pandas et pyarrow sont dans requirements.txt

## Vérification du fichier parquet

```bash
# Vérifiez que le fichier est bien présent et de la bonne taille
ls -lh backend/books_french.parquet
# Devrait afficher ~32MB
```