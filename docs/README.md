# Documentation LaTeX du projet

Ce dossier contient le **rapport** et la **présentation** du pipeline Big Data en LaTeX.

## Fichiers

| Fichier | Description |
|--------|-------------|
| `rapport.tex` | Rapport complet du projet (article) |
| `presentation.tex` | Présentation orale (Beamer) |
| `Makefile` | Règles de compilation |

## Compilation

### Prérequis

- Une distribution LaTeX (TeX Live, MacTeX, ou MiKTeX) avec `pdflatex` et les paquets : `babel`, `graphicx`, `hyperref`, `listings`, `booktabs`, `beamer`, `geometry`, `amsmath`.

### Commandes

```bash
cd docs

# Générer le PDF du rapport
make rapport
# ou : pdflatex rapport.tex && pdflatex rapport.tex

# Générer le PDF de la présentation
make presentation
# ou : pdflatex presentation.tex && pdflatex presentation.tex

# Tout compiler
make all

# Nettoyer les fichiers auxiliaires
make clean
```

Les PDF produits sont : `rapport.pdf` et `presentation.pdf`.
