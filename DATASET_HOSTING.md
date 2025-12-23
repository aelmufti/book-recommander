# 📦 Hébergement du Dataset - Solutions

## Option 1: GitHub Repository séparé (Recommandé)

1. **Créer un nouveau repo** : `book-finder-data`
2. **Uploader** `books_french.parquet` (31MB)
3. **URL publique** : `https://github.com/username/book-finder-data/raw/main/books_french.parquet`

## Option 2: Google Drive

1. **Uploader** le fichier sur Google Drive
2. **Partager** avec accès public
3. **Obtenir l'URL directe** : `https://drive.google.com/uc?id=FILE_ID`

## Option 3: Dropbox

1. **Uploader** sur Dropbox
2. **Créer un lien public**
3. **Modifier l'URL** : remplacer `?dl=0` par `?dl=1`

## Option 4: GitHub Releases (si push fonctionne)

1. **Créer une release** sur GitHub
2. **Attacher** le fichier parquet
3. **URL** : `https://github.com/username/repo/releases/download/v1.0.0/books_french.parquet`

## Configuration dans main.py

```python
# Remplacer cette URL par l'URL réelle
DATASET_URL = "https://github.com/username/book-finder-data/raw/main/books_french.parquet"
```

## Avantages

- ✅ **Pas de limite Git** (fichier externe)
- ✅ **Téléchargement à la demande** (économise l'espace)
- ✅ **Cache local** (télécharge une seule fois)
- ✅ **56k livres complets** (pas de compromis)
- ✅ **Déploiement rapide** (pas de gros fichiers dans le repo)

## Test Local

```bash
# Tester le téléchargement
curl -L "URL_DU_DATASET" -o test_download.parquet
ls -lh test_download.parquet
```