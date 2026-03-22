# Pousser ce dépôt vers ton GitHub (`saghro/BIG_DATA_PIPLINE`)

## Ne pas utiliser `git init` ici

Ce projet est **déjà** un dépôt Git (cloné puis modifié). Les commandes GitHub du type « first commit avec seulement README.md » **écraseraient l’historique** ou créeraient un conflit. Utilise plutôt les étapes ci-dessous.

## 1. Nettoyage déjà fait dans ce fork

- **README** : mainteneur **saghro**, lien vers `github.com/saghro/BIG_DATA_PIPLINE`, section *Acknowledgments* pour l’équipe initiale.
- **Airflow DAG** : `owner` = `saghro`.
- **docs/** (rapport & présentation LaTeX) : auteur principal **saghro** + crédit équipe initiale.
- **`.gitignore`** : `.DS_Store` (macOS).

## 2. Créer le dépôt vide sur GitHub

Sur [github.com/new](https://github.com/new), crée **`saghro/BIG_DATA_PIPLINE`** **sans** README / .gitignore / licence (dépôt vide).

## 3. Changer le remote et pousser

À la racine du projet :

```bash
cd /path/to/Projet_Pipeline_BigData_org

# Option A — garder une trace de l’ancien dépôt
git remote rename origin upstream
git remote add origin https://github.com/saghro/BIG_DATA_PIPLINE.git

# Option B — remplacer directement l’URL (sans renommer)
# git remote set-url origin https://github.com/saghro/BIG_DATA_PIPLINE.git

# Ajouter tous les fichiers (hors .gitignore), commit, push
git add -A
git status
git commit -m "Fork: maintainer saghro, docs, Mastodon, nettoyage métadonnées"
git branch -M main
git push -u origin main
```

Si GitHub refuse le push (historique différent), en dernier recours seulement :

```bash
git push -u origin main --force
```

⚠️ `--force` réécrit l’historique sur GitHub ; à utiliser seulement si tu es sûr d’être seul sur ce dépôt.

## 4. Authentification

- **HTTPS** : utiliser un [Personal Access Token](https://github.com/settings/tokens) au lieu du mot de passe.
- **SSH** : `git@github.com:saghro/BIG_DATA_PIPLINE.git` après avoir ajouté une clé SSH sur GitHub.
