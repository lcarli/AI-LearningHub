#!/usr/bin/env python3
"""
Auto-generate labs/index.md and update path index pages.

Scans all lab-*.md files, extracts metadata (level, path, time, cost),
and regenerates the labs index + each path's lab table.

Usage:
    python scripts/generate_labs_index.py
"""

import os
import re
import sys
from collections import defaultdict
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "docs" / "docs"
LABS_DIR = DOCS_DIR / "en" / "labs"
PATHS_DIR = REPO_ROOT / "docs" / "docs" / "en" / "paths"
INDEX_FILE = LABS_DIR / "index.md"


def extract_lab_meta(filepath: Path) -> dict | None:
    """Extract metadata from a lab markdown file."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return None

    num_match = re.search(r"lab-(\d+)", filepath.stem)
    if not num_match:
        return None
    lab_num = int(num_match.group(1))

    frontmatter = {}
    if content.startswith("---\n"):
        _, raw, _ = content.split("---\n", 2)
        frontmatter = yaml.safe_load(raw) or {}
    structured = frontmatter.get("lab", {})

    # Title
    title_match = re.search(r"^# Lab \d+[^:]*: (.+)$", content, re.MULTILINE)
    if not title_match:
        title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else filepath.stem

    # Level
    level_match = re.search(r'level-(\d+)">(L\d+)<', content)
    level = structured.get("level") or (level_match.group(2) if level_match else "?")
    level_num = int(level.removeprefix("L")) if level.startswith("L") else 0

    # Path
    path_link = re.search(r'<a href="(\.\./paths/[^"]+)">([^<]+)</a>', content)
    if path_link:
        path_url = path_link.group(1)
        path_name = path_link.group(2).strip()
        # Extract path key from URL
        path_key_match = re.search(r"paths/([^/]+)/", path_url)
        path_key = path_key_match.group(1) if path_key_match else "all"
    else:
        plain = re.search(r"<strong>Path:</strong>\s*([^<\n]+)", content)
        path_name = plain.group(1).strip() if plain else "All paths"
        path_key = "all"

    # Time
    time_match = re.search(r"~(\d+)\s*min", content)
    time_min = structured.get("time_min") or (int(time_match.group(1)) if time_match else 0)

    tier_labels = {
        "free": "✅ Free",
        "free-gh": "✅ GitHub Free",
        "free-conditional": "⚠️ Free with conditions",
        "paid": "💳 Paid",
    }
    cost = tier_labels.get(structured.get("cost", {}).get("tier"), "Unknown")

    return {
        "num": lab_num,
        "title": title,
        "level": level,
        "level_num": level_num,
        "path_name": path_name,
        "path_key": path_key,
        "time_min": time_min,
        "cost": cost,
        "status": structured.get("status", "active"),
        "file": filepath.name,
    }


def generate_labs_index(lang: str) -> str:
    """Generate the localized catalog shell rendered from labs.json."""
    copy = {
        "en": (
            "Lab Catalog",
            "Combine search, journey, level, cost, simulation, role, time, "
            "technology, language, and sorting. The cards are generated from lab frontmatter.",
        ),
        "pt": (
            "Catálogo de Labs",
            "Combine busca, jornada, nível, custo, simulação, papel, tempo, "
            "tecnologia, idioma e ordenação. Os cards são gerados do frontmatter dos labs.",
        ),
        "fr": (
            "Catalogue des Labs",
            "Combinez recherche, parcours, niveau, coût, simulation, rôle, durée, "
            "technologie, langue et tri. Les cartes proviennent du frontmatter.",
        ),
    }
    title, intro = copy[lang]
    return (
        f"# {title}\n\n{intro}\n\n"
        '<div data-lab-catalog data-source="../labs.json" data-catalog-error></div>\n\n'
        "<noscript>This catalog requires JavaScript. "
        "Use the navigation menu to open individual labs.</noscript>\n"
    )


def main():
    lab_files = sorted(LABS_DIR.glob("lab-*.md"))
    labs = []
    for f in lab_files:
        meta = extract_lab_meta(f)
        if meta:
            labs.append(meta)

    for lang in ("en", "pt", "fr"):
        index_file = DOCS_DIR / lang / "labs" / "index.md"
        index_file.write_text(generate_labs_index(lang), encoding="utf-8")
        print(f"Generated {index_file} ({len(labs)} labs)")


if __name__ == "__main__":
    main()
