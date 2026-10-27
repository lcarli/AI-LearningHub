#!/usr/bin/env python3
"""Generate localized labs.json catalogs from lab frontmatter."""

import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "docs"
LANGS = ("en", "pt", "fr")


def parse_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, text
    _, raw, body = text.split("---\n", 2)
    return yaml.safe_load(raw) or {}, body


def first_match(pattern: str, body: str, default: str = "", dotall: bool = False) -> str:
    flags = re.MULTILINE | (re.DOTALL if dotall else 0)
    match = re.search(pattern, body, flags)
    return re.sub(r"\s+", " ", match.group(1)).strip() if match else default


def catalog_entry(path: Path, lang: str) -> dict:
    frontmatter, body = parse_frontmatter(path)
    lab = frontmatter["lab"]
    cost = lab["cost"]
    title = first_match(r"^#\s+(.+)$", body, path.stem)
    summary = first_match(
        r"## (?:What You'll Learn|O que você aprenderá|Ce que vous apprendrez)\s+(.+?)(?:\n## |\Z)",
        body,
        "",
        dotall=True,
    )
    tags = frontmatter.get("tags", [])
    if not isinstance(tags, list):
        tags = []

    roles = lab.get("roles") or []
    technologies = lab.get("technologies") or tags
    return {
        "id": str(lab["id"]).zfill(3),
        "title": title,
        "summary": summary[:280],
        "url": f"labs/{path.name}",
        "level": lab["level"],
        "journey": lab["journey"],
        "time_min": lab["time_min"],
        "cost": cost["tier"],
        "simulation": bool(cost.get("simulation")),
        "roles": roles,
        "technologies": technologies,
        "language": lang,
        "status": lab["status"],
        "last_verified": str(lab["last_verified"]),
        "tags": tags,
    }


def main() -> None:
    for lang in LANGS:
        labs_dir = DOCS / lang / "labs"
        entries = [
            catalog_entry(path, lang)
            for path in sorted(labs_dir.glob("lab-*.md"))
        ]
        output = DOCS / lang / "labs.json"
        output.write_text(
            json.dumps(entries, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Generated {output} ({len(entries)} labs)")


if __name__ == "__main__":
    main()
