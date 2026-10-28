#!/usr/bin/env python3
"""Validate local navigation and assets in the rendered MkDocs site."""

from __future__ import annotations

import argparse
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from mkdocs.config import load_config

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SITE = ROOT / "docs" / "site"
MKDOCS_CONFIG = ROOT / "docs" / "mkdocs.yml"
LINK_ATTRIBUTES = {
    "a": ("href",),
    "img": ("src",),
    "link": ("href",),
    "script": ("src",),
    "source": ("src",),
}


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[tuple[str, str]] = []
        self.language_links: dict[str, str] = {}
        self.is_material_page = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        classes = (values.get("class") or "").split()
        if tag == "header" and "md-header" in classes:
            self.is_material_page = True
        if tag == "a" and "md-select__link" in (values.get("class") or "").split():
            language = values.get("hreflang")
            href = values.get("href")
            if language and href:
                self.language_links[language] = href
        expected = LINK_ATTRIBUTES.get(tag)
        if not expected:
            return
        for attribute in expected:
            value = values.get(attribute)
            if value:
                self.links.append((attribute, value))


def candidate_paths(page: Path, value: str, site: Path, site_prefix: str) -> list[Path]:
    parsed = urlsplit(value)
    path = unquote(parsed.path)
    if path.startswith("/"):
        relative = path.removeprefix(site_prefix).lstrip("/")
        target = (site / relative).resolve()
    else:
        target = (page.parent / path).resolve()
    if path.endswith("/"):
        return [target / "index.html"]
    if target.suffix:
        return [target]
    return [target, target.with_suffix(".html"), target / "index.html"]


def validate(site: Path) -> list[str]:
    errors: list[str] = []
    site = site.resolve()
    if not site.is_dir():
        return [f"{site}: rendered site directory does not exist"]

    html_files = sorted(site.rglob("*.html"))
    if not html_files:
        return [f"{site}: no rendered HTML files found"]

    config = load_config(config_file=str(MKDOCS_CONFIG))
    site_prefix = urlsplit(config.site_url).path.rstrip("/")

    for page in html_files:
        parser = LinkParser()
        parser.feed(page.read_text(encoding="utf-8"))
        if page.name != "404.html" and parser.is_material_page:
            languages = set(parser.language_links)
            expected_languages = {"en", "pt", "fr"}
            if languages != expected_languages:
                errors.append(
                    f"{page.relative_to(site)}: language selector has {sorted(languages)}, "
                    f"expected {sorted(expected_languages)}"
                )
            for language, href in parser.language_links.items():
                candidates = candidate_paths(page, href, site, site_prefix)
                if not any(candidate.exists() for candidate in candidates):
                    errors.append(
                        f"{page.relative_to(site)}: language {language!r} target {href!r} does not exist"
                    )
        for attribute, value in parser.links:
            parsed = urlsplit(value)
            if (
                parsed.scheme
                or parsed.netloc
                or value.startswith(("#", "mailto:", "tel:", "data:", "javascript:"))
            ):
                continue
            if parsed.path.startswith("/"):
                if parsed.path != site_prefix and not parsed.path.startswith(site_prefix + "/"):
                    errors.append(
                        f"{page.relative_to(site)}: {attribute}={value!r} is outside site_url path {site_prefix!r}"
                    )
                    continue
            if parsed.path.endswith(".md"):
                errors.append(
                    f"{page.relative_to(site)}: {attribute}={value!r} exposes a Markdown source URL"
                )
                continue
            candidates = candidate_paths(page, value, site, site_prefix)
            if not any(candidate.exists() for candidate in candidates):
                expected = ", ".join(str(path.relative_to(site)) for path in candidates)
                errors.append(
                    f"{page.relative_to(site)}: {attribute}={value!r} has no target ({expected})"
                )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("site", nargs="?", type=Path, default=DEFAULT_SITE)
    args = parser.parse_args()
    errors = validate(args.site)
    if errors:
        print("Rendered site link validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    html_count = len(list(args.site.rglob("*.html")))
    print(f"Rendered site link validation passed for {html_count} HTML pages.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
