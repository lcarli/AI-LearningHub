# Rapport de compatibilité Zensical — Phase 3

**Décision :** conserver le build actuel jusqu'à un support sans régression de l'i18n trilingue par dossiers.

La migration a été réévaluée avec la documentation officielle actuelle d'installation, migration MkDocs et compatibilité des plugins. Le site exige le routage EN/PT/FR de `mkdocs-static-i18n`, ainsi que recherche, tags, glightbox, JavaScript, CSS, catalogue JSON, quiz, progression et kits. La compatibilité documentée ne fournit pas encore une voie équivalente prise en charge.

Changer de moteur dégraderait le site. La CI conserve le build MkDocs strict et le contenu reste prêt à migrer.

## Porte de nouveau test

Migrer uniquement lorsqu'un build propre prouve des routes et comptes EN/PT/FR identiques, navigation, recherche, tags, glightbox, JS/CSS, quiz, progression, catalogues et liens stricts.

## Références officielles

- [Démarrer avec Zensical](https://zensical.org/docs/get-started/)
- [Migrer depuis MkDocs](https://zensical.org/docs/compatibility/mkdocs/migration/)
- [Plugins compatibles](https://zensical.org/docs/compatibility/mkdocs/plugins/)
