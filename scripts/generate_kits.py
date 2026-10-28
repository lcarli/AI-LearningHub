#!/usr/bin/env python3
"""Build deterministic PDF and ZIP learning kits without external binaries."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import unicodedata
import zipfile
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "docs"
MANIFEST = ROOT / "kits" / "manifest.yml"
LANGS = ("en", "pt", "fr")
ZIP_TIMESTAMP = (2026, 1, 1, 0, 0, 0)


def load_manifest() -> dict:
    return yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))


def find_lab(lang: str, lab_id: str) -> Path:
    matches = sorted((DOCS / lang / "labs").glob(f"lab-{lab_id}-*.md"))
    if len(matches) != 1:
        raise ValueError(f"{lang} Lab {lab_id}: expected one Markdown file, found {len(matches)}")
    return matches[0]


def markdown_text(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.DOTALL)
    text = re.sub(r"```.*?```", "[diagram or code sample]", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"^[#>|!?+\-]+\s*", "", text, flags=re.MULTILINE)
    text = text.replace("**", "").replace("`", "")
    lines: list[str] = []
    for paragraph in re.split(r"\n\s*\n", text):
        clean = " ".join(paragraph.split())
        if not clean:
            continue
        while len(clean) > 92:
            split = clean.rfind(" ", 0, 92)
            split = split if split > 30 else 92
            lines.append(clean[:split])
            clean = clean[split:].strip()
        lines.append(clean)
    return lines


def pdf_bytes(lines: list[str]) -> bytes:
    """Create a small deterministic Latin-1 PDF with wrapped lab text."""
    safe_lines = []
    for line in lines[:250]:
        normalized = unicodedata.normalize("NFKC", line)
        encoded = normalized.encode("latin-1", errors="replace").decode("latin-1")
        safe_lines.append(encoded.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)"))

    pages = [safe_lines[index : index + 48] for index in range(0, len(safe_lines), 48)] or [[""]]
    objects: list[bytes] = []
    page_ids: list[int] = []
    font_id = 3
    first_page_id = 4
    for page_index, page_lines in enumerate(pages):
        page_id = first_page_id + page_index * 2
        content_id = page_id + 1
        page_ids.append(page_id)
        stream_commands = ["BT", "/F1 10 Tf", "48 760 Td", "13 TL"]
        for line in page_lines:
            stream_commands.append(f"({line}) Tj")
            stream_commands.append("T*")
        stream_commands.append("ET")
        stream = "\n".join(stream_commands).encode("latin-1")
        objects.extend(
            [
                (
                    f"{page_id} 0 obj\n"
                    f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
                    f"/Resources << /Font << /F1 {font_id} 0 R >> >> /Contents {content_id} 0 R >>\n"
                    "endobj\n"
                ).encode("ascii"),
                (
                    f"{content_id} 0 obj\n<< /Length {len(stream)} >>\nstream\n".encode("ascii")
                    + stream
                    + b"\nendstream\nendobj\n"
                ),
            ]
        )

    base_objects = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        (
            f"2 0 obj\n<< /Type /Pages /Kids [{' '.join(f'{page_id} 0 R' for page_id in page_ids)}] "
            f"/Count {len(page_ids)} >>\nendobj\n"
        ).encode("ascii"),
        b"3 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>\nendobj\n",
    ]
    all_objects = base_objects + objects
    output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for obj in all_objects:
        offsets.append(len(output))
        output.extend(obj)
    xref = len(output)
    output.extend(f"xref\n0 {len(all_objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    output.extend(
        (
            f"trailer\n<< /Size {len(all_objects) + 1} /Root 1 0 R >>\n"
            f"startxref\n{xref}\n%%EOF\n"
        ).encode("ascii")
    )
    return bytes(output)


def zip_add(archive: zipfile.ZipFile, path: Path, name: str) -> None:
    info = zipfile.ZipInfo(name, ZIP_TIMESTAMP)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    archive.writestr(info, path.read_bytes())


def build_kit(lang: str, lab: dict, output_root: Path) -> dict:
    lab_id = str(lab["id"]).zfill(3)
    markdown = find_lab(lang, lab_id)
    destination = output_root / lang
    destination.mkdir(parents=True, exist_ok=True)
    stem = f"lab-{lab_id}-kit-{lang}"
    pdf_path = destination / f"{stem}.pdf"
    zip_path = destination / f"{stem}.zip"
    pdf_path.write_bytes(pdf_bytes(markdown_text(markdown)))

    support_dir = markdown.parent / f"lab-{lab_id}"
    metadata = {
        "lab_id": lab_id,
        "language": lang,
        "priority": lab["priority"],
        "kind": lab["kind"],
        "source": markdown.name,
    }
    with zipfile.ZipFile(zip_path, "w") as archive:
        zip_add(archive, markdown, f"guide/{markdown.name}")
        if support_dir.exists():
            for path in sorted(item for item in support_dir.rglob("*") if item.is_file()):
                zip_add(archive, path, f"exercise/{path.relative_to(support_dir).as_posix()}")
        info = zipfile.ZipInfo("kit.json", ZIP_TIMESTAMP)
        info.compress_type = zipfile.ZIP_DEFLATED
        info.external_attr = 0o644 << 16
        archive.writestr(info, json.dumps(metadata, indent=2, sort_keys=True) + "\n")
    return {
        **metadata,
        "pdf": pdf_path.relative_to(ROOT).as_posix(),
        "zip": zip_path.relative_to(ROOT).as_posix(),
        "pdf_sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
        "zip_sha256": hashlib.sha256(zip_path.read_bytes()).hexdigest(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    manifest = load_manifest()
    output_root = args.output or ROOT / manifest["output"]
    records = [
        build_kit(lang, lab, output_root)
        for lab in manifest["labs"]
        for lang in LANGS
    ]
    index_path = output_root / "index.json"
    index_path.parent.mkdir(parents=True, exist_ok=True)
    index_path.write_text(json.dumps(records, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    expected = len(manifest["labs"]) * len(LANGS)
    if len(records) != expected:
        raise SystemExit(f"Expected {expected} kits, generated {len(records)}")
    if args.check:
        for record in records:
            if not (ROOT / record["pdf"]).exists() or not (ROOT / record["zip"]).exists():
                raise SystemExit(f"Missing artifact for Lab {record['lab_id']} {record['language']}")
    print(f"Generated {len(records)} deterministic PDF/ZIP kits in {output_root}")


if __name__ == "__main__":
    main()
