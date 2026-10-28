import re
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "docs"
LANGS = ("en", "pt", "fr")
KIT_HEADINGS = {
    "en": "Supporting kit",
    "pt": "Kit de apoio",
    "fr": "Kit d'accompagnement",
}
RAW_REPOSITORY_URL = re.compile(
    r"https://github\.com/lcarli/AI-LearningHub/raw/main/([^\s)]+)"
)


def local_home_target(lang: str, href: str) -> Path:
    target = (DOCS / lang / unquote(urlsplit(href).path)).resolve()
    if href.endswith("/"):
        index = target / "index.md"
        return index if index.exists() else target.with_suffix(".md")
    return target


class ContentLinkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = yaml.safe_load(
            (ROOT / "kits" / "manifest.yml").read_text(encoding="utf-8")
        )
        cls.materials = yaml.safe_load(
            (ROOT / "kits" / "materials.yml").read_text(encoding="utf-8")
        )

    def test_home_ctas_are_subpath_safe_and_resolve(self):
        for lang in LANGS:
            home = (DOCS / lang / "index.md").read_text(encoding="utf-8")
            hrefs = re.findall(r'<a class="(?:hub-button|journey-card|persona-card)[^"]*" href="([^"]+)"', home)
            self.assertEqual(len(hrefs), 9, lang)
            self.assertEqual(
                hrefs[0],
                "labs/lab-097-tokens-sampling-context/",
                lang,
            )
            for href in hrefs:
                self.assertFalse(href.startswith("/"), (lang, href))
                self.assertNotIn(".md", href, (lang, href))
                self.assertTrue(local_home_target(lang, href).exists(), (lang, href))

    def test_raw_html_links_do_not_target_markdown_or_site_root(self):
        for path in DOCS.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            for href in re.findall(r'href=["\']([^"\']+)["\']', text):
                parsed = urlsplit(href)
                if parsed.scheme or parsed.netloc or href.startswith("#"):
                    continue
                self.assertFalse(parsed.path.startswith("/"), (path, href))
                self.assertFalse(parsed.path.endswith(".md"), (path, href))

    def test_lab_downloads_use_local_files(self):
        for lang in LANGS:
            for path in (DOCS / lang / "labs").glob("lab-*.md"):
                text = path.read_text(encoding="utf-8")
                self.assertNotRegex(
                    text,
                    r"https://github\.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/",
                    str(path),
                )

    def test_repository_raw_links_point_to_existing_files(self):
        for path in DOCS.rglob("*.md"):
            text = path.read_text(encoding="utf-8")
            for target in RAW_REPOSITORY_URL.findall(text):
                self.assertTrue((ROOT / unquote(target)).is_file(), (path, target))

    def test_every_kit_promise_has_pdf_and_zip_destinations(self):
        manifest_ids = {
            str(item["id"]).zfill(3) for item in self.manifest["labs"]
        }
        for lang in LANGS:
            heading = KIT_HEADINGS[lang]
            kit_pages = 0
            for path in sorted((DOCS / lang / "labs").glob("lab-*.md")):
                text = path.read_text(encoding="utf-8")
                marker = f"## {heading}\n"
                if marker not in text:
                    continue
                kit_pages += 1
                lab_id = re.search(r"lab-(\d+)", path.name).group(1)
                self.assertIn(lab_id, manifest_ids, str(path))
                section = text.split(marker, 1)[1].split("\n## ", 1)[0]
                self.assertIn(
                    f"../downloads/kits/lab-{lab_id}-kit-{lang}.pdf",
                    section,
                    str(path),
                )
                self.assertIn(
                    f"../downloads/kits/lab-{lab_id}-kit-{lang}.zip",
                    section,
                    str(path),
                )
                support = DOCS / lang / "labs" / f"lab-{lab_id}"
                self.assertTrue(support.is_dir(), str(support))
                self.assertTrue(any(item.is_file() for item in support.rglob("*")), str(support))
            self.assertEqual(kit_pages, len(manifest_ids), lang)

    def test_roadmap_material_manifest_is_complete(self):
        kit_ids = {str(item["id"]).zfill(3) for item in self.manifest["labs"]}
        required = set(self.materials["priority_scope"]["required"])
        retired = set(self.materials["priority_scope"]["excluded_retired"])
        self.assertTrue(required <= kit_ids)
        self.assertTrue(retired.isdisjoint(kit_ids))
        for lab_id, spec in self.materials["labs"].items():
            self.assertIn(lab_id, kit_ids)
            for lang in LANGS:
                support = DOCS / lang / "labs" / f"lab-{lab_id}"
                for relative in spec["required"]:
                    self.assertTrue((support / relative).is_file(), (lang, lab_id, relative))


if __name__ == "__main__":
    unittest.main()
