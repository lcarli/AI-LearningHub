# Rapport de compatibilité Zensical — Phase 2

**Décision :** ne pas migrer le site de production pendant la Phase 2.

## Test isolé

L'arborescence `docs/` a été copiée dans un dossier temporaire de session et un environnement virtuel propre a été créé. Deux voies d'installation ont été essayées :

1. le dépôt Python configuré a demandé le wheel Windows ARM64 et renvoyé HTTP 404 ;
2. PyPI direct a trouvé Zensical 0.0.73, mais l'hôte a échoué lors de la négociation TLS avec `files.pythonhosted.org`.

Docker a aussi été vérifié, mais le moteur Docker Desktop n'était pas actif. Aucun fichier du dépôt ni configuration de production n'a été modifié.

## Blocage de compatibilité exploitable

Le dépôt dépend de `mkdocs-static-i18n` avec `docs_structure: folder` pour compiler EN, PT et FR depuis une configuration. La liste officielle des plugins compatibles Zensical n'inclut pas encore ce plugin et la documentation présente l'i18n natif comme un travail futur. Une migration immédiate risquerait de perdre ou mal router deux langues.

## Surfaces compatibles

- Zensical lit `mkdocs.yml` et permet une migration progressive.
- Search, tags et glightbox disposent de chemins de compatibilité documentés.
- Le dépôt n'utilise pas le paramètre MkDocs `hooks`, non pris en charge.

## Résultat

Le critère de Phase 2 est satisfait par un rapport explicite et reproductible : **l'i18n trilingue est le blocage produit**. Refaire le test lorsque Zensical publiera l'i18n natif par dossiers ou une compatibilité vérifiée avec `mkdocs-static-i18n`. Conserver MkDocs Material jusqu'à équivalence de la navigation, du nombre de pages, des routes linguistiques, de la recherche, des tags et des liens stricts.

## Procédure de nouveau test

```powershell
python -m venv .zensical-test
.zensical-test\Scripts\python -m pip install zensical
Copy-Item -Recurse docs .zensical-test\docs-copy
Push-Location .zensical-test\docs-copy
..\Scripts\zensical build
Pop-Location
```

Comparez la sortie à `python -m mkdocs build --strict`, y compris toutes les routes EN/PT/FR.

## Références officielles

- [Zensical : démarrage](https://zensical.org/docs/get-started/)
- [Zensical : migration depuis MkDocs](https://zensical.org/docs/compatibility/mkdocs/migration/)
- [Zensical : plugins MkDocs compatibles](https://zensical.org/docs/compatibility/mkdocs/plugins/)
