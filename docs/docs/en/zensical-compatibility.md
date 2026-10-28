# Zensical Compatibility Report — Phase 3

**Decision:** retain the current production build until trilingual folder-based i18n is supported without regression.

The migration was re-evaluated against current official Zensical installation, MkDocs migration, and plugin compatibility documentation. The site requires EN/PT/FR folder routing from `mkdocs-static-i18n`, plus search, tags, glightbox, custom JavaScript, CSS, catalog JSON, quizzes, progress, and generated kits. Zensical can read MkDocs configuration and supports several Material surfaces, but its documented compatibility does not provide an equivalent supported path for this repository's folder-based `mkdocs-static-i18n` contract.

Changing the production engine would therefore violate the Phase 3 no-degradation requirement. CI continues to run the strict MkDocs build, while the configuration and content remain migration-ready.

## Re-test gate

Migrate only when a clean Zensical build proves identical EN/PT/FR page counts and routes, navigation, search, tags, glightbox, custom JS/CSS, quizzes, progress, catalogs, and strict internal links.

## Official references

- [Zensical get started](https://zensical.org/docs/get-started/)
- [Migrate from MkDocs](https://zensical.org/docs/compatibility/mkdocs/migration/)
- [Compatible plugins](https://zensical.org/docs/compatibility/mkdocs/plugins/)
