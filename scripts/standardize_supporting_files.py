#!/usr/bin/env python3
"""Standardize Supporting Files sections across all labs."""

import os
import re
import sys
import glob

sys.stdout.reconfigure(encoding="utf-8")

REPO_BASE = "https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs"
LABS_DIR = "docs/docs/en/labs"


def describe_file(fname: str) -> str:
    low = fname.lower()
    if "broken" in low:
        return "Bug-fix exercise (3 bugs + self-tests)"
    if low.endswith(".csv") and "benchmark" in low:
        return "Benchmark dataset"
    if low.endswith(".csv"):
        return "Dataset"
    if low.endswith(".json"):
        return "Configuration / data file"
    if low.endswith(".jsonl"):
        return "Evaluation dataset"
    if low.endswith(".yml") or low.endswith(".yaml"):
        return "CI/CD workflow template"
    if low.endswith(".txt") and "faq" in low:
        return "FAQ knowledge base file"
    if low.endswith(".txt") and "requirements" in low:
        return "Python dependencies"
    if low.endswith(".txt"):
        return "Text data file"
    if "starter" in low or "hello" in low:
        return "Starter script with TODOs"
    if "builder" in low or "analyzer" in low or "pipeline" in low or "traced" in low:
        return "Starter script with TODOs"
    if low.endswith(".py") and ("exercise" in low or "challenge" in low or "explorer" in low):
        return "Interactive exercise script"
    if low.endswith(".py"):
        return "Python script"
    if low.endswith(".cs"):
        return "C# source file"
    if low == "modelfile":
        return "Ollama model configuration"
    if low == "requirements.txt":
        return "Python dependencies"
    if low == "migrations":
        return "Database migration files"
    return "Supporting file"


def build_section(lab_dir_name: str, files: list[str]) -> str:
    rows = []
    for fname in files:
        url = f"{REPO_BASE}/{lab_dir_name}/{fname}"
        desc = describe_file(fname)
        rows.append(f"| `{fname}` | {desc} | [📥 Download]({url}) |")

    table = "\n".join(rows)
    return (
        f'## 📦 Supporting Files\n'
        f'\n'
        f'!!! note "Download these files before starting the lab"\n'
        f'    Save all files to a `{lab_dir_name}/` folder in your working directory.\n'
        f'\n'
        f'| File | Description | Download |\n'
        f'|------|-------------|----------|\n'
        f'{table}\n'
        f'\n'
        f'---\n'
        f'\n'
    )


def process_lab(md_path: str) -> bool:
    num = re.search(r"lab-(\d+)", os.path.basename(md_path)).group(1)
    lab_dir_name = f"lab-{num}"
    lab_dir_path = os.path.join(LABS_DIR, lab_dir_name)

    if not os.path.isdir(lab_dir_path):
        return False
    files = sorted(os.listdir(lab_dir_path))
    if not files:
        return False

    with open(md_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "## 📦 Supporting Files" in content:
        return False

    new_section = build_section(lab_dir_name, files)

    # Find insertion point: before first Step/Part heading
    step_match = re.search(
        r"\n(## (?:Step 1|Part 1|Part 2|Exercise 1|Lab Exercise)[:\s —])", content
    )
    if step_match:
        insert_pos = step_match.start() + 1
    else:
        # Fallback: before Bug-Fix or Knowledge Check
        for fallback in ["## 🐛", "## 🧠 Knowledge", "## Knowledge Check", "## Summary"]:
            idx = content.find(fallback)
            if idx > 0:
                insert_pos = idx
                break
        else:
            print(f"  SKIP Lab {num}: no insertion point")
            return False

    content = content[:insert_pos] + new_section + content[insert_pos:]

    # Remove old sections
    # Pattern 1: ## 📁 Supporting Files ... (until next ##)
    content = re.sub(
        r"\n## 📁 Supporting Files\n.*?(?=\n## )",
        "\n",
        content,
        flags=re.DOTALL,
    )
    # Pattern 2: ## 📥 Download Supporting Files ... (until next --- or ##)
    content = re.sub(
        r"\n## 📥 Download Supporting Files\n.*?(?=\n---\n|\n## )",
        "\n",
        content,
        flags=re.DOTALL,
    )
    # Clean up double --- separators
    content = re.sub(r"\n---\n\n+---\n", "\n---\n", content)
    # Clean up triple+ blank lines
    content = re.sub(r"\n{4,}", "\n\n\n", content)

    # Add inline download links for first mention of each file in steps
    section_end = content.find("---", content.find("## 📦 Supporting Files") + 10)
    if section_end > 0:
        # Skip past the table area (find the next ## heading after Supporting Files)
        next_heading = content.find("\n## ", section_end + 4)
        if next_heading < 0:
            next_heading = section_end + 10
        for fname in files:
            url = f"{REPO_BASE}/{lab_dir_name}/{fname}"
            # Find first backtick-quoted mention AFTER the supporting files section ends
            pattern = f"`{fname}`"
            idx = content.find(pattern, next_heading)
            if idx > 0:
                # Check not already linked
                before = content[max(0, idx - 10) : idx]
                if "📥" not in before and "[" not in before[-2:]:
                    linked = f"[📥 `{fname}`]({url})"
                    content = content[:idx] + linked + content[idx + len(pattern) :]

    with open(md_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"  Lab {num}: {len(files)} files standardized")
    return True


def main():
    updated = 0
    for md_path in sorted(glob.glob(os.path.join(LABS_DIR, "lab-0*.md"))):
        if process_lab(md_path):
            updated += 1
    print(f"\nTotal: {updated} labs updated")


if __name__ == "__main__":
    main()
