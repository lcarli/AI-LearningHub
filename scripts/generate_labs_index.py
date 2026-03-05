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

REPO_ROOT = Path(__file__).resolve().parent.parent
LABS_DIR = REPO_ROOT / "docs" / "docs" / "en" / "labs"
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

    # Title
    title_match = re.search(r"^# Lab \d+[^:]*: (.+)$", content, re.MULTILINE)
    if not title_match:
        title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else filepath.stem

    # Level
    level_match = re.search(r'level-(\d+)">(L\d+)<', content)
    level = level_match.group(2) if level_match else "?"
    level_num = int(level_match.group(1)) if level_match else 0

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
    time_min = int(time_match.group(1)) if time_match else 0

    # Cost
    cost = "Free"
    if "cost-free" in content:
        cost = "✅ Free"
    elif "cost-github" in content:
        cost = "✅ GitHub Free"
    elif "cost-azure" in content or "Azure" in content[:500]:
        cost = "⚠️ Azure"
    if "M365" in content[:600] or "Copilot license" in content[:600]:
        cost = "⚠️ M365"
    if "cost-free" in content:
        cost = "✅ Free"

    return {
        "num": lab_num,
        "title": title,
        "level": level,
        "level_num": level_num,
        "path_name": path_name,
        "path_key": path_key,
        "time_min": time_min,
        "cost": cost,
        "file": filepath.name,
    }


def generate_labs_index(labs: list[dict]) -> str:
    """Generate the full labs/index.md content."""
    lines = [
        "# All Labs",
        "",
        "Browse all labs by level. Each lab is self-contained.",
        "",
        "→ [How to read a lab page](../how-to-use.md#reading-a-lab-page)",
        "",
    ]

    level_groups = {
        50: ("L50", "Awareness — No account required"),
        100: ("L100", "Foundations"),
        200: ("L200", "Intermediate"),
        300: ("L300", "Advanced"),
        400: ("L400", "Expert"),
    }

    for level_num, (badge, desc) in level_groups.items():
        level_labs = sorted(
            [l for l in labs if l["level_num"] == level_num], key=lambda x: x["num"]
        )
        if not level_labs:
            continue

        total_time = sum(l["time_min"] for l in level_labs)
        lines.append("---")
        lines.append("")
        lines.append(
            f'## <span class="level-badge level-{level_num}">{badge}</span> '
            f"{desc} ({len(level_labs)} labs, ~{total_time} min)"
        )
        lines.append("")
        lines.append("| Lab | Title | Path | Time | Cost |")
        lines.append("|-----|-------|------|------|------|")
        for l in level_labs:
            lines.append(
                f"| [Lab {l['num']:03d}]({l['file']}) "
                f"| {l['title']} "
                f"| {l['path_name']} "
                f"| ~{l['time_min']} min "
                f"| {l['cost']} |"
            )
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(f"**Total: {len(labs)} labs**")
    lines.append("")

    return "\n".join(lines)


def main():
    lab_files = sorted(LABS_DIR.glob("lab-*.md"))
    labs = []
    for f in lab_files:
        meta = extract_lab_meta(f)
        if meta:
            labs.append(meta)

    # Generate labs index
    index_content = generate_labs_index(labs)
    INDEX_FILE.write_text(index_content, encoding="utf-8")
    print(f"✅ Generated {INDEX_FILE} ({len(labs)} labs)")


if __name__ == "__main__":
    main()
