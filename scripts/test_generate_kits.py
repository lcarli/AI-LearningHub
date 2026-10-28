import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts import generate_kits


class KitGenerationTests(unittest.TestCase):
    def test_pdf_has_valid_header(self):
        value = generate_kits.pdf_bytes(["Lab guide", "Deterministic content"])
        self.assertTrue(value.startswith(b"%PDF-1.4"))
        self.assertTrue(value.endswith(b"%%EOF\n"))

    def test_zip_timestamp_is_stable(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "source.txt"
            archive_path = Path(directory) / "kit.zip"
            source.write_text("content", encoding="utf-8")
            with zipfile.ZipFile(archive_path, "w") as archive:
                generate_kits.zip_add(archive, source, "source.txt")
            with zipfile.ZipFile(archive_path) as archive:
                self.assertEqual(archive.getinfo("source.txt").date_time, generate_kits.ZIP_TIMESTAMP)

    def test_pdf_is_reproducible(self):
        first = hashlib.sha256(generate_kits.pdf_bytes(["same"])).hexdigest()
        second = hashlib.sha256(generate_kits.pdf_bytes(["same"])).hexdigest()
        self.assertEqual(first, second)

    def test_external_output_records_absolute_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "kit.pdf"
            path.write_bytes(b"content")
            self.assertEqual(generate_kits.record_path(path), path.resolve().as_posix())

    def test_site_layout_uses_language_download_directory(self):
        with tempfile.TemporaryDirectory(dir=generate_kits.ROOT) as directory:
            output = Path(directory)
            record = generate_kits.build_kit(
                "en",
                {"id": "004", "priority": "P0", "kind": "llm-foundations"},
                output,
                site_layout=True,
            )
            self.assertIn("/en/downloads/kits/lab-004-kit-en.pdf", record["pdf"])
            self.assertTrue(
                (output / "en" / "downloads" / "kits" / "lab-004-kit-en.zip").exists()
            )

    def test_pdf_source_includes_declared_support_files(self):
        markdown = generate_kits.find_lab("en", "004")
        lines = generate_kits.kit_text(markdown, markdown.parent / "lab-004")
        self.assertIn("Supporting file: token_attention_lab.py", lines)


if __name__ == "__main__":
    unittest.main()
