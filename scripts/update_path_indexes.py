#!/usr/bin/env python3
"""Update all path index pages with current lab listings."""

import os
import re
import sys
import glob

sys.stdout.reconfigure(encoding="utf-8")

LABS_DIR = "docs/docs/en/labs"
PATHS_DIR = "docs/docs/en/paths"


def extract_labs():
    labs = []
    for f in sorted(glob.glob(os.path.join(LABS_DIR, "lab-0*.md"))):
        content = open(f, "r", encoding="utf-8").read()
        num = int(re.search(r"lab-(\d+)", os.path.basename(f)).group(1))

        level_m = re.search(r'level-(\d+)">(L\d+)<', content)
        level = level_m.group(2) if level_m else "?"
        level_num = int(level_m.group(1)) if level_m else 0

        title_m = re.search(r"^# Lab \d+[^:]*: (.+)$", content, re.MULTILINE)
        title = title_m.group(1).strip() if title_m else os.path.basename(f)

        time_m = re.search(r"~(\d+)\s*min", content)
        time_min = int(time_m.group(1)) if time_m else 0

        cost = "Free"
        if "cost-free" in content:
            cost = "✅ Free"
        elif "cost-github" in content:
            cost = "✅ GitHub Free"
        elif "cost-azure" in content:
            cost = "⚠️ Azure"

        path_m = re.search(r"paths/([^/]+)/", content)
        path_key = path_m.group(1) if path_m else None

        labs.append(
            {
                "num": num,
                "title": title,
                "level": level,
                "level_num": level_num,
                "time": time_min,
                "cost": cost,
                "path_key": path_key,
                "file": os.path.basename(f),
            }
        )
    return labs


def update_path_index(path_dir, path_labs):
    idx_path = os.path.join(PATHS_DIR, path_dir, "index.md")
    if not os.path.exists(idx_path):
        return

    content = open(idx_path, "r", encoding="utf-8").read()

    table_start = content.find("## Path Labs")
    if table_start < 0:
        print(f"  SKIP {path_dir}: no 'Path Labs' section")
        return

    # Find end of table section
    rest = content[table_start + 12 :]
    next_h2 = re.search(r"\n## ", rest)
    next_hr = rest.find("\n---\n")
    if next_h2 and (next_hr < 0 or next_h2.start() < next_hr):
        table_end = table_start + 12 + next_h2.start()
    elif next_hr >= 0:
        table_end = table_start + 12 + next_hr
    else:
        table_end = len(content)

    total_time = sum(l["time"] for l in path_labs)
    rows = []
    for l in path_labs:
        badge = f'<span class="level-badge level-{l["level_num"]}">{l["level"]}</span>'
        rows.append(
            f'| [Lab {l["num"]:03d}](../../labs/{l["file"]}) '
            f'| {l["title"]} | {badge} | {l["cost"]} |'
        )

    new_section = (
        f"## Path Labs ({len(path_labs)} labs, ~{total_time} min total)\n\n"
        f"| Lab | Title | Level | Cost |\n"
        f"|-----|-------|-------|------|\n"
        + "\n".join(rows)
        + "\n"
    )

    content = content[:table_start] + new_section + content[table_end:]
    open(idx_path, "w", encoding="utf-8").write(content)
    print(f"  {path_dir}: {len(path_labs)} labs, ~{total_time} min")


def main():
    labs = extract_labs()
    print(f"Found {len(labs)} labs total")

    path_dirs = [
        d
        for d in os.listdir(PATHS_DIR)
        if os.path.isdir(os.path.join(PATHS_DIR, d))
    ]

    for path_dir in sorted(path_dirs):
        path_labs = sorted(
            [l for l in labs if l["path_key"] == path_dir],
            key=lambda x: x["level_num"] * 1000 + x["num"],
        )
        if path_labs:
            update_path_index(path_dir, path_labs)

    unassigned = len([l for l in labs if l["path_key"] is None])
    print(f"\nUnassigned (All paths): {unassigned}")


if __name__ == "__main__":
    main()
