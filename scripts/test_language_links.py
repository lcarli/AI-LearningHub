import tempfile
import unittest
from pathlib import Path

from docs.hooks.fix_language_links import rewrite_site_language_links
from scripts.validate_site_links import validate

LANGUAGES = ("en", "pt", "fr")


def selector() -> str:
    links = "".join(
        f'<a href="/wrong/{lang}/" hreflang="{lang}" class="md-select__link">{lang}</a>'
        for lang in LANGUAGES
    )
    return f"<html><body>{links}</body></html>"


class LanguageLinkTests(unittest.TestCase):
    def test_all_directions_preserve_equivalent_root_and_nested_pages(self):
        with tempfile.TemporaryDirectory() as temporary:
            site = Path(temporary)
            for language in LANGUAGES:
                prefix = Path() if language == "en" else Path(language)
                for route in ("", "labs/lab-004/"):
                    page = site / prefix / route / "index.html"
                    page.parent.mkdir(parents=True, exist_ok=True)
                    page.write_text(selector(), encoding="utf-8")

            rewrite_site_language_links(
                site, "https://example.github.io/AI-LearningHub/"
            )

            for source in LANGUAGES:
                prefix = Path() if source == "en" else Path(source)
                for route in ("", "labs/lab-004/"):
                    text = (site / prefix / route / "index.html").read_text(
                        encoding="utf-8"
                    )
                    for target in LANGUAGES:
                        target_prefix = "" if target == "en" else f"{target}/"
                        self.assertIn(
                            f'href="/AI-LearningHub/{target_prefix}{route}" '
                            f'hreflang="{target}"',
                            text,
                            (source, target, route),
                        )

    def test_missing_translation_falls_back_to_language_home(self):
        with tempfile.TemporaryDirectory() as temporary:
            site = Path(temporary)
            for language in LANGUAGES:
                prefix = Path() if language == "en" else Path(language)
                home = site / prefix / "index.html"
                home.parent.mkdir(parents=True, exist_ok=True)
                home.write_text(selector(), encoding="utf-8")
            nested = site / "labs" / "lab-004" / "index.html"
            nested.parent.mkdir(parents=True)
            nested.write_text(selector(), encoding="utf-8")

            rewrite_site_language_links(
                site, "https://example.github.io/AI-LearningHub/"
            )
            text = nested.read_text(encoding="utf-8")

            self.assertIn(
                'href="/AI-LearningHub/labs/lab-004/" hreflang="en"',
                text,
            )
            self.assertIn('href="/AI-LearningHub/pt/" hreflang="pt"', text)
            self.assertIn('href="/AI-LearningHub/fr/" hreflang="fr"', text)

    def test_rendered_site_validator_checks_language_targets(self):
        with tempfile.TemporaryDirectory() as temporary:
            site = Path(temporary)
            for language in LANGUAGES:
                prefix = Path() if language == "en" else Path(language)
                home = site / prefix / "index.html"
                home.parent.mkdir(parents=True, exist_ok=True)
                home.write_text(selector(), encoding="utf-8")

            rewrite_site_language_links(site, "https://docs.example/")
            self.assertEqual(validate(site), [])


if __name__ == "__main__":
    unittest.main()
