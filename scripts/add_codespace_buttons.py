#!/usr/bin/env python3
"""Add Codespace buttons to labs with Python exercises."""

import re
import glob
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

CODESPACE_BTN = (
    '\n!!! tip "Quick Start with GitHub Codespaces"\n'
    "    [![Open in GitHub Codespaces]"
    "(https://github.com/codespaces/badge.svg)]"
    "(https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)\n\n"
    "    All dependencies are pre-installed in the devcontainer.\n\n"
)

LABS_DIR = "docs/docs/en/labs"
updated = 0

for md in sorted(glob.glob(os.path.join(LABS_DIR, "lab-0*.md"))):
    content = open(md, "r", encoding="utf-8").read()

    if "codespaces" in content.lower():
        continue

    num = re.search(r"lab-(\d+)", os.path.basename(md)).group(1)
    lab_dir = os.path.join(LABS_DIR, f"lab-{num}")
    if not os.path.isdir(lab_dir):
        continue
    py_files = [f for f in os.listdir(lab_dir) if f.endswith(".py")]
    if not py_files:
        continue

    # Insert after Prerequisites --- separator
    prereq = re.search(r"## Prerequisites", content)
    if not prereq:
        continue

    # Find the --- after prerequisites
    rest = content[prereq.start():]
    hr = re.search(r"\n---\n", rest)
    if hr:
        insert_pos = prereq.start() + hr.end()
    else:
        next_h = re.search(r"\n## ", rest[20:])
        if next_h:
            insert_pos = prereq.start() + 20 + next_h.start()
        else:
            continue

    content = content[:insert_pos] + CODESPACE_BTN + content[insert_pos:]
    open(md, "w", encoding="utf-8").write(content)
    updated += 1

print(f"Added Codespace buttons to {updated} labs")
