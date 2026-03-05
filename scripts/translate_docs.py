#!/usr/bin/env python3
"""
Translate MkDocs markdown files to target languages.

This script:
1. Reads English .md files from docs/docs/en/
2. Translates text content (preserving code, HTML, frontmatter, links)
3. Writes translated files to docs/docs/{locale}/
4. Tracks translated file hashes to avoid re-translating unchanged files

Usage:
    python scripts/translate_docs.py --lang pt       # Translate to Portuguese
    python scripts/translate_docs.py --lang fr       # Translate to French
    python scripts/translate_docs.py --lang pt,fr    # Both
    python scripts/translate_docs.py --lang pt --force  # Re-translate all
    python scripts/translate_docs.py --lang pt --file labs/lab-001-what-are-ai-agents.md

Requires: GITHUB_TOKEN env var (for GitHub Models free API)
"""

import argparse
import hashlib
import json
import os
import re
import sys
import shutil
from pathlib import Path

# Try to import OpenAI client
try:
    from openai import OpenAI
except ImportError:
    print("pip install openai")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
EN_DIR = REPO_ROOT / "docs" / "docs" / "en"
DOCS_DIR = REPO_ROOT / "docs" / "docs"
HASH_FILE = REPO_ROOT / "scripts" / ".translation-hashes.json"

LANG_NAMES = {
    "pt": "Portuguese (Brazilian)",
    "fr": "French",
}

SYSTEM_PROMPT_TEMPLATE = """You are a professional translator for technical documentation. Translate the following MkDocs Markdown content from English to {lang_name}.

CRITICAL RULES:
1. Translate ALL human-readable text (headings, paragraphs, descriptions, admonition text)
2. DO NOT translate:
   - Code blocks (```python ... ```) — keep code exactly as-is
   - Inline code (`variable_name`) — keep as-is
   - URLs, file paths, and links — keep as-is
   - YAML frontmatter (--- tags: [...] ---) — keep as-is
   - HTML tags and attributes — keep as-is
   - SVG references and image paths — keep as-is
   - Product names (GitHub Copilot, Microsoft Foundry, Azure, etc.)
   - Technical terms when no good translation exists (keep original + add translation in parentheses if helpful)
3. Preserve ALL markdown formatting: headers ##, bold **, italic *, lists -, tables |, admonitions ??? / !!!
4. Preserve the EXACT indentation of admonition content (4 spaces)
5. Keep emoji intact
6. Translate Knowledge Check questions and answers
7. Output ONLY the translated markdown — no explanations or wrappers"""


def get_client():
    """Get OpenAI client configured for GitHub Models (free)."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("ERROR: Set GITHUB_TOKEN environment variable")
        print("  Get a free token at: https://github.com/settings/tokens")
        sys.exit(1)
    return OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=token,
    )


def load_hashes() -> dict:
    if HASH_FILE.exists():
        return json.loads(HASH_FILE.read_text(encoding="utf-8"))
    return {}


def save_hashes(hashes: dict):
    HASH_FILE.write_text(json.dumps(hashes, indent=2, sort_keys=True), encoding="utf-8")


def file_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def translate_markdown(client: OpenAI, content: str, lang: str) -> str:
    """Translate a markdown file's content."""
    lang_name = LANG_NAMES.get(lang, lang)

    # Split into chunks if too large (>12K chars)
    if len(content) > 12000:
        return translate_large_file(client, content, lang, lang_name)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE.format(lang_name=lang_name)},
            {"role": "user", "content": content},
        ],
        temperature=0.1,
        max_tokens=16000,
    )
    return response.choices[0].message.content


def translate_large_file(client: OpenAI, content: str, lang: str, lang_name: str) -> str:
    """Split large files by ## sections and translate each chunk."""
    sections = re.split(r"(\n## )", content)

    # Reconstruct: first element is everything before first ##
    chunks = [sections[0]]
    for i in range(1, len(sections), 2):
        if i + 1 < len(sections):
            chunks.append(sections[i] + sections[i + 1])
        else:
            chunks.append(sections[i])

    translated_parts = []
    for i, chunk in enumerate(chunks):
        if not chunk.strip():
            translated_parts.append(chunk)
            continue
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE.format(lang_name=lang_name)},
                    {"role": "user", "content": chunk},
                ],
                temperature=0.1,
                max_tokens=16000,
            )
            translated_parts.append(response.choices[0].message.content)
        except Exception as e:
            print(f"    WARNING: chunk {i} failed: {e}, keeping original")
            translated_parts.append(chunk)

    return "\n".join(translated_parts)


def copy_non_md_assets(lang: str):
    """Copy non-markdown files (CSS, JS, images, SVGs) to language folder."""
    target_dir = DOCS_DIR / lang
    for subdir in ["css", "js", "media", "assets"]:
        src = EN_DIR / subdir
        dst = target_dir / subdir
        if src.exists() and not dst.exists():
            shutil.copytree(src, dst)
            print(f"  Copied {subdir}/ to {lang}/")


def translate_file(client: OpenAI, rel_path: str, lang: str, hashes: dict) -> bool:
    """Translate a single file. Returns True if translated."""
    src = EN_DIR / rel_path
    dst = DOCS_DIR / lang / rel_path

    if not src.exists():
        return False

    # Check hash to skip unchanged files
    hash_key = f"{lang}:{rel_path}"
    current_hash = file_hash(src)
    if hashes.get(hash_key) == current_hash:
        return False  # Already translated, no changes

    # Read source
    content = src.read_text(encoding="utf-8")

    # Translate
    translated = translate_markdown(client, content, lang)

    # Write
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(translated, encoding="utf-8")

    # Update hash
    hashes[hash_key] = current_hash
    return True


def get_all_md_files() -> list[str]:
    """Get all .md files relative to EN_DIR."""
    files = []
    for path in sorted(EN_DIR.rglob("*.md")):
        rel = path.relative_to(EN_DIR)
        files.append(str(rel).replace("\\", "/"))
    return files


def main():
    parser = argparse.ArgumentParser(description="Translate docs to target languages")
    parser.add_argument("--lang", required=True, help="Target language(s): pt, fr, or pt,fr")
    parser.add_argument("--force", action="store_true", help="Re-translate all files")
    parser.add_argument("--file", help="Translate only this file (relative to en/)")
    args = parser.parse_args()

    languages = [l.strip() for l in args.lang.split(",")]
    client = get_client()
    hashes = {} if args.force else load_hashes()

    if args.file:
        files = [args.file]
    else:
        files = get_all_md_files()

    print(f"Found {len(files)} markdown files")

    for lang in languages:
        print(f"\n{'='*50}")
        print(f"Translating to {LANG_NAMES.get(lang, lang)} ({lang})")
        print(f"{'='*50}")

        # Copy static assets
        copy_non_md_assets(lang)

        # Also copy lab supporting files (CSV, JSON, PY)
        for lab_dir in sorted(EN_DIR.glob("labs/lab-*")):
            if lab_dir.is_dir():
                dst_dir = DOCS_DIR / lang / "labs" / lab_dir.name
                if not dst_dir.exists():
                    shutil.copytree(lab_dir, dst_dir)

        translated = 0
        skipped = 0
        for rel_path in files:
            try:
                if translate_file(client, rel_path, lang, hashes):
                    translated += 1
                    print(f"  ✅ {rel_path}")
                else:
                    skipped += 1
            except Exception as e:
                print(f"  ❌ {rel_path}: {e}")

        print(f"\n{lang}: {translated} translated, {skipped} skipped (unchanged)")

    save_hashes(hashes)
    print(f"\nDone! Hashes saved to {HASH_FILE}")


if __name__ == "__main__":
    main()
