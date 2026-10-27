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


if __name__ == "__main__":
    unittest.main()
