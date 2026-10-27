# Learning kit generation

`manifest.yml` defines the P0/P1 labs that must ship as reproducible learning kits in English, Portuguese, and French.

Run locally:

```bash
python scripts/phase2_content.py
python scripts/generate_kits.py --check
```

The generator writes deterministic PDF and ZIP files to `artifacts/kits/`. The directory is ignored by Git; `.github/workflows/kits.yml` publishes it as a workflow artifact instead of committing unstable binaries.

Each ZIP includes the localized lab guide, its support directory when present, and machine-readable kit metadata. `index.json` records SHA-256 hashes for release verification.
