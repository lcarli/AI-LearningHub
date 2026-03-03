#!/usr/bin/env python3
"""
Auto-generate docs/docs/en/whats-new.md from the git history of lab files.

Run this script from the repository root before `mkdocs build`:
    python scripts/generate_whats_new.py

The script:
1. Scans all lab-*.md files under docs/docs/en/labs/
2. Gets the date of the first git commit that added each file
3. Extracts title, level, and learning path from the file content
4. Groups labs by month/year (newest first)
5. Writes whats-new.md, preserving a static "footer" section
"""

import os
import re
import subprocess
from collections import defaultdict
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LABS_DIR = REPO_ROOT / "docs" / "docs" / "en" / "labs"
OUTPUT_FILE = REPO_ROOT / "docs" / "docs" / "en" / "whats-new.md"

# ── Static footer kept at the bottom of whats-new.md ────────────────────────
STATIC_FOOTER = """
## 📦 Sample Datasets

All labs share a consistent **OutdoorGear Inc.** scenario with ready-to-use datasets:

| File | Contents |
|------|----------|
| [`data/products.csv`](https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/products.csv) | 25 outdoor gear products with categories, prices, specs |
| [`data/knowledge-base.json`](https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/knowledge-base.json) | 42 RAG-ready documents: policies, FAQs, product guides |
| [`data/orders.csv`](https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/orders.csv) | 20 sample customer orders for RLS and order tracking labs |

---

## 🏗️ Infrastructure Templates

Deploy-to-Azure one-click buttons for three Bicep templates:

| Template | What it deploys |
|----------|----------------|
| `infra/lab-028-mcp-container-apps/` | Azure Container Apps + ACR for MCP servers |
| `infra/lab-030-foundry/` | Azure AI Foundry + Storage + AI Services |
| `infra/lab-031-pgvector/` | Azure PostgreSQL Flexible Server with pgvector |

---

## 🗺️ Roadmap

See the [Proposed Labs](proposed-labs.md) page for the full list of upcoming labs.

Want to contribute? See [CONTRIBUTING.md](https://github.com/lcarli/AI-LearningHub/blob/main/CONTRIBUTING.md) or [open a proposal](https://github.com/lcarli/AI-LearningHub/issues/new?template=new_lab_proposal.md).
"""


def get_first_commit_date(filepath: Path) -> datetime | None:
    """Return the date the file was first added to git, or None if untracked."""
    rel = filepath.relative_to(REPO_ROOT)
    result = subprocess.run(
        ["git", "log", "--follow", "--format=%ai", "--diff-filter=A", "--", str(rel)],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    lines = [l.strip() for l in result.stdout.strip().splitlines() if l.strip()]
    if lines:
        # lines[-1] is the *oldest* (first) commit
        date_str = lines[-1].split(" ")[0]
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            pass
    # Fall back to file mtime if not in git yet (e.g. local dev)
    mtime = filepath.stat().st_mtime
    return datetime.fromtimestamp(mtime)


def extract_lab_info(filepath: Path) -> dict | None:
    """Return a dict with num, title, level, path_name, path_url, file."""
    try:
        content = filepath.read_text(encoding="utf-8")
    except Exception:
        return None

    # Lab number from filename
    num_match = re.search(r"lab-(\d+)", filepath.stem)
    if not num_match:
        return None
    lab_num = int(num_match.group(1))

    # Title: first H1 line
    title_match = re.search(r"^# Lab \d+[^:]*: (.+)$", content, re.MULTILINE)
    if not title_match:
        title_match = re.search(r"^# (.+)$", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else filepath.stem

    # Level badge e.g. level-300">L300<
    level_match = re.search(r'level-(\d+)">(L\d+)<', content)
    level = level_match.group(2) if level_match else "?"

    # Path: <a href="../paths/...">Name</a>  OR plain text "All paths"
    path_link_match = re.search(r'<a href="(\.\./paths/[^"]+)">([^<]+)</a>', content)
    if path_link_match:
        path_url = path_link_match.group(1)
        path_name = path_link_match.group(2).strip()
    else:
        # Might be plain "All paths"
        plain_match = re.search(
            r"<strong>Path:</strong>\s*([^<\n]+)", content
        )
        path_name = plain_match.group(1).strip() if plain_match else "—"
        path_url = None

    return {
        "num": lab_num,
        "title": title,
        "level": level,
        "path_name": path_name,
        "path_url": path_url,
        "file": filepath.name,
    }


def lab_link(info: dict) -> str:
    return f"[Lab {info['num']:03d}](labs/{info['file']})"


def path_link(info: dict) -> str:
    if info["path_url"]:
        return f"[{info['path_name']}]({info['path_url']})"
    return info["path_name"]


def month_key(dt: datetime) -> str:
    return dt.strftime("%B %Y")


def month_sort_key(month_str: str) -> datetime:
    return datetime.strptime(month_str, "%B %Y")


def build_whats_new() -> str:
    lab_files = sorted(LABS_DIR.glob("lab-*.md"))

    # Collect (date, info) for each lab
    entries: list[tuple[datetime, dict]] = []
    for f in lab_files:
        info = extract_lab_info(f)
        if not info:
            continue
        date = get_first_commit_date(f)
        if not date:
            continue
        entries.append((date, info))

    # Group by month
    by_month: dict[str, list[tuple[datetime, dict]]] = defaultdict(list)
    for date, info in entries:
        by_month[month_key(date)].append((date, info))

    # Sort months newest first
    sorted_months = sorted(by_month.keys(), key=month_sort_key, reverse=True)

    lines = [
        "# What's New",
        "",
        "Track the latest labs, content updates, and improvements to the AI Agents Learning Hub.",
        "",
        "> ✨ This page is **auto-generated** from the git history on every deploy.",
        "",
        "---",
        "",
    ]

    for month in sorted_months:
        month_entries = sorted(by_month[month], key=lambda x: x[1]["num"])
        lines.append(f"## {month}")
        lines.append("")
        lines.append("### 🚀 New Labs Added")
        lines.append("")
        lines.append("| Lab | Title | Level | Path |")
        lines.append("|-----|-------|-------|------|")
        for _, info in month_entries:
            lines.append(
                f"| {lab_link(info)} | {info['title']} | {info['level']} | {path_link(info)} |"
            )
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append(STATIC_FOOTER.strip())
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    content = build_whats_new()
    OUTPUT_FILE.write_text(content, encoding="utf-8")
    print(f"✅ Generated {OUTPUT_FILE} ({len(content)} chars)")
