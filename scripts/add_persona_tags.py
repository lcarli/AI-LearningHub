#!/usr/bin/env python3
"""Add persona tags to all lab files based on their content and path."""

import re
import glob
import os
import sys

sys.stdout.reconfigure(encoding="utf-8")

LABS_DIR = "docs/docs/en/labs"

# Persona mapping: lab number → persona tags
PERSONA_MAP = {
    # L50 — everyone
    1: ["student", "developer", "analyst", "architect", "admin"],
    2: ["student", "developer", "analyst", "architect", "admin"],
    3: ["student", "developer", "analyst", "architect", "admin"],
    4: ["student", "developer", "analyst", "architect"],
    5: ["student", "developer", "analyst"],
    6: ["student", "developer", "analyst"],
    7: ["student", "developer", "analyst"],
    8: ["student", "developer", "analyst", "architect", "admin"],
    # L100 — foundations
    9: ["developer", "architect"],
    10: ["developer", "student"],
    11: ["analyst", "admin"],
    12: ["developer", "architect", "engineer"],
    13: ["developer", "student"],
    14: ["developer", "student"],
    15: ["developer", "student"],
    16: ["developer", "student"],
    17: ["developer"],
    18: ["developer"],
    19: ["developer"],
    # L200 — intermediate
    20: ["developer", "engineer"],
    21: ["developer", "engineer"],
    22: ["developer", "student"],
    23: ["developer"],
    24: ["developer"],
    25: ["developer"],
    26: ["developer", "architect"],
    27: ["developer", "architect"],
    28: ["developer", "engineer"],
    29: ["developer"],
    # L300 — advanced
    30: ["developer", "architect"],
    31: ["developer", "engineer"],
    32: ["developer", "engineer", "admin"],
    33: ["developer", "architect"],
    34: ["developer", "architect"],
    35: ["developer", "architect"],
    36: ["developer", "admin"],
    37: ["developer"],
    38: ["developer", "architect"],
    39: ["developer", "architect"],
    # L400 — expert
    40: ["developer", "architect"],
    41: ["developer"],
    42: ["developer", "architect"],
    43: ["developer"],
    44: ["developer"],
    45: ["developer", "student"],
    # New labs
    46: ["architect", "admin"],
    47: ["analyst", "admin"],
    48: ["analyst", "admin"],
    49: ["developer", "architect"],
    50: ["developer", "architect"],
    51: ["developer", "analyst", "engineer"],
    52: ["analyst", "developer"],
    53: ["developer", "analyst", "engineer"],
    54: ["developer", "architect"],
    55: ["developer", "architect"],
    56: ["developer", "engineer", "admin"],
    57: ["developer"],
    58: ["developer"],
    59: ["developer"],
    60: ["developer", "architect"],
    61: ["developer"],
    62: ["developer"],
    63: ["developer", "admin", "architect"],
    64: ["architect", "admin", "engineer"],
    65: ["admin"],
    66: ["admin"],
    67: ["developer", "architect"],
    68: ["developer"],
    69: ["analyst", "admin"],
    70: ["developer", "analyst"],
    71: ["developer", "architect"],
    72: ["developer", "student"],
    73: ["developer", "architect"],
    74: ["developer", "architect"],
    75: ["analyst"],
    76: ["developer", "architect"],
    77: ["developer", "architect"],
    78: ["developer", "student"],
    79: ["developer", "architect"],
    80: ["developer", "engineer"],
    81: ["developer", "student"],
    82: ["developer", "architect"],
    83: ["developer", "architect"],
    84: ["developer", "architect"],
}

updated = 0
for md in sorted(glob.glob(os.path.join(LABS_DIR, "lab-0*.md"))):
    num_match = re.search(r"lab-(\d+)", os.path.basename(md))
    if not num_match:
        continue
    num = int(num_match.group(1))
    if num not in PERSONA_MAP:
        continue

    content = open(md, "r", encoding="utf-8").read()

    # Check if persona tags already exist
    if "persona-" in content:
        continue

    # Find existing tags line
    tags_match = re.search(r"tags: \[(.+?)\]", content)
    if not tags_match:
        continue

    existing_tags = tags_match.group(1)
    persona_tags = ", ".join(f"persona-{p}" for p in PERSONA_MAP[num])
    new_tags = f"{existing_tags}, {persona_tags}"

    content = content.replace(f"tags: [{existing_tags}]", f"tags: [{new_tags}]")
    open(md, "w", encoding="utf-8").write(content)
    updated += 1

print(f"Added persona tags to {updated} labs")
