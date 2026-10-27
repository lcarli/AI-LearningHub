#!/usr/bin/env python3
"""Add structured Phase 0 metadata to every translated lab."""

import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "docs"
LANGS = ("en", "pt", "fr")
RETIRED = {41, 45}

PATH_TO_JOURNEY = {
    "copilot": "github-copilot",
    "foundry": "microsoft-foundry",
    "mcp": "mcp",
    "semantic-kernel": "agent-framework",
    "rag": "llm-foundations",
    "agent-builder-teams": "m365-agents",
    "agent-builder-vscode": "github-copilot",
    "pro-code": "ai-agents",
}


def split_frontmatter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    _, raw, body = text.split("---\n", 2)
    return yaml.safe_load(raw) or {}, body


def classify_cost(text: str) -> tuple[str, list[str]]:
    head = text[:1500].lower()
    if "cost-github" in head:
        return "free-gh", ["github", "copilot-free"]
    if "cost-free" in head or "no account required" in head:
        return "free", []
    if any(term in head for term in ("trial", "student", "credits", "gpu")):
        return "free-conditional", ["conditional-access"]
    if any(term in head for term in ("azure", "m365", "license", "subscription", "paid")):
        return "paid", ["paid-service"]
    return "free", []


def extract_metadata(path: Path, text: str) -> dict:
    lab_id = int(re.search(r"lab-(\d+)", path.stem).group(1))
    level = re.search(r'level-\d+">(L\d+)<', text)
    time = re.search(r"~(\d+)\s*min", text)
    path_match = re.search(r"paths/([^/]+)/", text[:1500])
    journey = PATH_TO_JOURNEY.get(
        path_match.group(1) if path_match else "",
        "ai-agents",
    )
    tier, requires = classify_cost(text)
    paid = tier == "paid"
    return {
        "id": f"{lab_id:03d}",
        "level": level.group(1) if level else "L100",
        "journey": journey,
        "time_min": int(time.group(1)) if time else 30,
        "cost": {
            "tier": tier,
            "requires": requires,
            "estimate_usd": (
                "Varies by selected service; see the lab cost section."
                if paid
                else "0 within the documented free path or quota."
            ),
            "simulation": 47 <= lab_id <= 84,
            "cleanup": paid,
        },
        "status": "retired" if lab_id in RETIRED else "active",
        "last_verified": "2026-10-27",
        "languages": list(LANGS),
    }


def main() -> None:
    source_files = sorted((DOCS / "en" / "labs").glob("lab-*.md"))
    for source in source_files:
        source_text = source.read_text(encoding="utf-8")
        metadata = extract_metadata(source, source_text)
        for lang in LANGS:
            path = DOCS / lang / "labs" / source.name
            text = path.read_text(encoding="utf-8")
            frontmatter, body = split_frontmatter(text)
            frontmatter["lab"] = metadata
            rendered = yaml.safe_dump(
                frontmatter,
                allow_unicode=True,
                sort_keys=False,
                width=1000,
            )
            path.write_text(f"---\n{rendered}---\n{body}", encoding="utf-8")
    print(f"Updated metadata for {len(source_files)} labs in {len(LANGS)} languages.")


if __name__ == "__main__":
    main()
