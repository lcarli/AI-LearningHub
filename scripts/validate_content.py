#!/usr/bin/env python3
"""Validate language parity, lab metadata, and Phase 0 retirement notices."""

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "docs"
LANGS = ("en", "pt", "fr")
ALLOWED_TIERS = {"free", "free-gh", "free-conditional", "paid"}
NOTICE_MARKERS = (
    "Backend update (October 2026)",
    "Atualização de backend (outubro de 2026)",
    "Mise à jour du backend (octobre 2026)",
)
LEGACY_BACKEND = re.compile(
    r"models\.inference\.ai\.azure\.com|github\.com/marketplace/models",
    re.IGNORECASE,
)


def parse_frontmatter(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, text
    _, raw, body = text.split("---\n", 2)
    return yaml.safe_load(raw) or {}, body


def validate_lab(path: Path, errors: list[str]) -> None:
    frontmatter, body = parse_frontmatter(path)
    lab = frontmatter.get("lab")
    if not isinstance(lab, dict):
        errors.append(f"{path}: missing lab metadata")
        return

    required = {
        "id",
        "level",
        "journey",
        "time_min",
        "cost",
        "status",
        "last_verified",
        "languages",
    }
    missing = required - lab.keys()
    if missing:
        errors.append(f"{path}: missing lab fields {sorted(missing)}")
        return

    expected_id = re.search(r"lab-(\d+)", path.stem).group(1)
    if str(lab["id"]) != expected_id:
        errors.append(f"{path}: lab id {lab['id']} does not match {expected_id}")
    if lab["languages"] != list(LANGS):
        errors.append(f"{path}: languages must be {list(LANGS)}")

    cost = lab["cost"]
    if not isinstance(cost, dict) or cost.get("tier") not in ALLOWED_TIERS:
        errors.append(f"{path}: invalid cost tier")
    elif cost["tier"] == "paid":
        if not cost.get("estimate_usd"):
            errors.append(f"{path}: paid labs require estimate_usd")
        if cost.get("cleanup") is not True:
            errors.append(f"{path}: paid labs require cleanup: true")

    if LEGACY_BACKEND.search(body) and not any(marker in body for marker in NOTICE_MARKERS):
        errors.append(f"{path}: legacy GitHub Models instructions lack a Phase 0 notice")


def main() -> int:
    errors: list[str] = []
    lab_sets = {
        lang: {path.name for path in (DOCS / lang / "labs").glob("lab-*.md")}
        for lang in LANGS
    }
    if lab_sets["en"] != lab_sets["pt"] or lab_sets["en"] != lab_sets["fr"]:
        errors.append("Lab file parity differs across EN/PT/FR.")

    for lang in LANGS:
        for path in sorted((DOCS / lang / "labs").glob("lab-*.md")):
            validate_lab(path, errors)

    for lang in LANGS:
        for lab_id in ("041", "045"):
            matches = list((DOCS / lang / "labs").glob(f"lab-{lab_id}-*.md"))
            if len(matches) != 1:
                errors.append(f"{lang}: expected one retired Lab {lab_id}")
                continue
            frontmatter, _ = parse_frontmatter(matches[0])
            if frontmatter.get("lab", {}).get("status") != "retired":
                errors.append(f"{matches[0]}: retired lab must declare status: retired")

    if errors:
        print("Content validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Content validation passed for {len(lab_sets['en'])} labs in 3 languages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
