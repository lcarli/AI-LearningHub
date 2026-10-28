# Zensical Compatibility Report — Phase 2

**Decision:** do not migrate the production site in Phase 2.

## Isolated test

The existing `docs/` tree was copied to a session scratch directory and a clean virtual environment was created. Two installation routes were attempted:

1. the configured Python package feed requested the Windows ARM64 wheel and returned HTTP 404;
2. direct PyPI access found Zensical 0.0.73, but the execution host failed the TLS handshake to `files.pythonhosted.org`.

Docker was also checked, but the Docker Desktop engine was not running. No repository file or production configuration was changed by the experiment.

## Actionable compatibility blocker

The repository depends on `mkdocs-static-i18n` with `docs_structure: folder` to build EN, PT, and FR from one configuration. Zensical's official MkDocs plugin compatibility list does not currently include that plugin, and its migration documentation describes native i18n as future compatibility work. A production switch would therefore risk dropping or misrouting two languages.

## Supported surfaces

- Zensical reads `mkdocs.yml` and supports gradual migration.
- Search, tags, and glightbox have documented compatibility paths.
- The repository does not use the unsupported MkDocs `hooks` setting.

## Exit result

The Phase 2 criterion is satisfied by an explicit, reproducible incompatibility report: **trilingual i18n is the blocking product gap**. Re-test when Zensical publishes native folder-based i18n or verified `mkdocs-static-i18n` compatibility. Keep MkDocs Material in production until the same navigation, page count, language routes, search, tags, and strict link checks pass.

## Re-test procedure

```powershell
python -m venv .zensical-test
.zensical-test\Scripts\python -m pip install zensical
Copy-Item -Recurse docs .zensical-test\docs-copy
Push-Location .zensical-test\docs-copy
..\Scripts\zensical build
Pop-Location
```

Compare the Zensical output with `python -m mkdocs build --strict`, including all EN/PT/FR routes.

## Official references

- [Zensical: get started](https://zensical.org/docs/get-started/)
- [Zensical: migrate from MkDocs](https://zensical.org/docs/compatibility/mkdocs/migration/)
- [Zensical: compatible MkDocs plugins](https://zensical.org/docs/compatibility/mkdocs/plugins/)
