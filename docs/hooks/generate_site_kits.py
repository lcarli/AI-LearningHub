"""Generate stable learning-kit downloads before MkDocs collects site files."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts import generate_kits


def on_pre_build(config, **kwargs):
    generate_kits.generate_all(generate_kits.DOCS, site_layout=True, check=True)
