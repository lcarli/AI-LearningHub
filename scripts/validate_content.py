#!/usr/bin/env python3
"""Validate language parity, metadata, catalogs, and retirement notices."""

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "docs"
KIT_MANIFEST = ROOT / "kits" / "manifest.yml"
MATERIALS_MANIFEST = ROOT / "kits" / "materials.yml"
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
PHASE2_LABS = {
    "004",
    "005",
    "007",
    "017",
    "018",
    "019",
    "022",
    "090",
    "092",
    "093",
    "095",
    "096",
    "098",
    "099",
    "100",
    "101",
}
PHASE2_CHALLENGES = {"010", "011"}
PHASE3_LABS = {"014", "023", "034", "040", "042", "102", "103", "104", "105", "106"}
PHASE3_CHALLENGES = {"012"}


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
    if not isinstance(lab.get("journey"), str) or not lab["journey"]:
        errors.append(f"{path}: journey must be a non-empty string")
    if not isinstance(lab.get("time_min"), int) or lab["time_min"] <= 0:
        errors.append(f"{path}: time_min must be a positive integer")

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
    challenge_sets = {
        lang: {
            path.name
            for path in (DOCS / lang / "challenges").glob("challenge-*.md")
        }
        for lang in LANGS
    }
    if (
        challenge_sets["en"] != challenge_sets["pt"]
        or challenge_sets["en"] != challenge_sets["fr"]
    ):
        errors.append("Challenge file parity differs across EN/PT/FR.")

    for lang in LANGS:
        for path in sorted((DOCS / lang / "labs").glob("lab-*.md")):
            validate_lab(path, errors)

        catalog_path = DOCS / lang / "labs.json"
        if not catalog_path.exists():
            errors.append(f"{catalog_path}: generated catalog is missing")
        else:
            try:
                catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                errors.append(f"{catalog_path}: invalid JSON ({exc})")
            else:
                expected = len(lab_sets[lang])
                if len(catalog) != expected:
                    errors.append(
                        f"{catalog_path}: expected {expected} entries, found {len(catalog)}"
                    )
                ids = [entry.get("id") for entry in catalog]
                if len(ids) != len(set(ids)):
                    errors.append(f"{catalog_path}: duplicate lab ids")

        question_path = DOCS / lang / "paths" / "gh-300" / "questions.json"
        try:
            questions = json.loads(question_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{question_path}: invalid or missing question bank ({exc})")
        else:
            if len(questions) != 50:
                errors.append(f"{question_path}: expected 50 questions")
            if any(len(question.get("options", [])) != 4 for question in questions):
                errors.append(f"{question_path}: every question requires four options")

        for lab_id in PHASE2_LABS:
            matches = list((DOCS / lang / "labs").glob(f"lab-{lab_id}-*.md"))
            if len(matches) != 1:
                errors.append(f"{lang}: expected one Phase 2 Lab {lab_id}")
                continue
            support = DOCS / lang / "labs" / f"lab-{lab_id}"
            if not support.exists() or not (support / "CHEATSHEET.md").exists():
                errors.append(f"{support}: Phase 2 lab requires a supporting kit directory")

        for challenge_id in PHASE2_CHALLENGES:
            matches = list((DOCS / lang / "challenges").glob(f"challenge-{challenge_id}-*.md"))
            support = DOCS / lang / "challenges" / f"challenge-{challenge_id}"
            if len(matches) != 1:
                errors.append(f"{lang}: expected one Phase 2 Challenge {challenge_id}")
            for required_file in ("test_challenge.py", "validate.py"):
                if not (support / required_file).exists():
                    errors.append(f"{support}: missing {required_file}")

        for lab_id in PHASE3_LABS:
            matches = list((DOCS / lang / "labs").glob(f"lab-{lab_id}-*.md"))
            if len(matches) != 1:
                errors.append(f"{lang}: expected one Phase 3 Lab {lab_id}")
                continue
            support = DOCS / lang / "labs" / f"lab-{lab_id}"
            for required_file in ("README.md", "CHEATSHEET.md", "scenario.json", "test_scenario.py"):
                if not (support / required_file).exists():
                    errors.append(f"{support}: missing {required_file}")
            body = matches[0].read_text(encoding="utf-8")
            if "data-phase3-tabs" not in body or "??? question" not in body or "```mermaid" not in body:
                errors.append(f"{matches[0]}: Phase 3 lab requires tabs, scored questions, and Mermaid")

        for challenge_id in PHASE3_CHALLENGES:
            matches = list((DOCS / lang / "challenges").glob(f"challenge-{challenge_id}-*.md"))
            support = DOCS / lang / "challenges" / f"challenge-{challenge_id}"
            if len(matches) != 1:
                errors.append(f"{lang}: expected one Phase 3 Challenge {challenge_id}")
            for required_file in ("test_challenge.py", "validate.py"):
                if not (support / required_file).exists():
                    errors.append(f"{support}: missing {required_file}")

        instructor = DOCS / lang / "instructor"
        for required_file in ("index.md", "two-hour.md", "four-hour.md", "four-week-cohort.md", "hackathon.md"):
            if not (instructor / required_file).exists():
                errors.append(f"{instructor}: missing {required_file}")

    for lang in LANGS:
        for lab_id in ("041", "045"):
            matches = list((DOCS / lang / "labs").glob(f"lab-{lab_id}-*.md"))
            if len(matches) != 1:
                errors.append(f"{lang}: expected one retired Lab {lab_id}")
                continue
            frontmatter, _ = parse_frontmatter(matches[0])
            if frontmatter.get("lab", {}).get("status") != "retired":
                errors.append(f"{matches[0]}: retired lab must declare status: retired")

    kit_manifest: dict = {}
    try:
        kit_manifest = yaml.safe_load(KIT_MANIFEST.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        errors.append(f"{KIT_MANIFEST}: invalid or missing kit manifest ({exc})")
    else:
        kit_ids = {str(item["id"]).zfill(3) for item in kit_manifest.get("labs", [])}
        missing_kits = PHASE2_LABS - kit_ids
        if missing_kits:
            errors.append(f"{KIT_MANIFEST}: missing Phase 2 kits {sorted(missing_kits)}")
        missing_phase3_kits = PHASE3_LABS - kit_ids
        if missing_phase3_kits:
            errors.append(f"{KIT_MANIFEST}: missing Phase 3 kits {sorted(missing_phase3_kits)}")
        if any(item.get("priority") not in {"P0", "P1"} for item in kit_manifest.get("labs", [])):
            errors.append(f"{KIT_MANIFEST}: every kit must declare priority P0 or P1")

    try:
        materials_manifest = yaml.safe_load(
            MATERIALS_MANIFEST.read_text(encoding="utf-8")
        )
    except (OSError, yaml.YAMLError) as exc:
        errors.append(
            f"{MATERIALS_MANIFEST}: invalid or missing materials manifest ({exc})"
        )
    else:
        kit_ids = {
            str(item["id"]).zfill(3) for item in (kit_manifest or {}).get("labs", [])
        }
        priority_scope = materials_manifest.get("priority_scope", {})
        missing_priority = set(priority_scope.get("required", [])) - kit_ids
        if missing_priority:
            errors.append(
                f"{KIT_MANIFEST}: missing roadmap P0/P1 kits {sorted(missing_priority)}"
            )
        retired_kits = set(priority_scope.get("excluded_retired", [])) & kit_ids
        if retired_kits:
            errors.append(
                f"{KIT_MANIFEST}: retired/replaced labs must not promise kits {sorted(retired_kits)}"
            )
        for lab_id, spec in materials_manifest.get("labs", {}).items():
            if lab_id not in kit_ids:
                errors.append(f"{MATERIALS_MANIFEST}: Lab {lab_id} is not in kit manifest")
            for lang in LANGS:
                support = DOCS / lang / "labs" / f"lab-{lab_id}"
                for relative in spec.get("required", []):
                    if not (support / relative).is_file():
                        errors.append(
                            f"{support}: missing roadmap material {relative}"
                        )

    if errors:
        print("Content validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Content validation passed for {len(lab_sets['en'])} labs in 3 languages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
