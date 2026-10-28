"""Make rendered language-switcher links deployment-prefix aware."""

from __future__ import annotations

import re
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

NON_DEFAULT_LANGUAGES = {"pt", "fr"}
ALTERNATE_LINK = re.compile(
    r'(<(?:a|link)\b[^>]*\bhref=")[^"]+("[^>]*\bhreflang="(en|pt|fr)"[^>]*>)'
)


def page_route(page: Path, site_dir: Path) -> str | None:
    relative = page.relative_to(site_dir).as_posix()
    if relative == "404.html":
        return None
    parts = list(PurePosixPath(relative).parts)
    if parts and parts[0] in NON_DEFAULT_LANGUAGES:
        parts.pop(0)
    if parts[-1] == "index.html":
        parts.pop()
    route = "/".join(parts)
    return f"{route}/" if route else ""


def output_page(site_dir: Path, language: str, route: str) -> Path:
    prefix = "" if language == "en" else f"{language}/"
    return site_dir / prefix / route / "index.html"


def language_href(site_prefix: str, language: str, route: str, site_dir: Path) -> str:
    target_route = route if output_page(site_dir, language, route).is_file() else ""
    language_prefix = "" if language == "en" else f"{language}/"
    return f"{site_prefix}/{language_prefix}{target_route}".replace("//", "/")


def rewrite_site_language_links(site_dir: Path, site_url: str) -> None:
    site_dir = site_dir.resolve()
    site_prefix = urlsplit(site_url).path.rstrip("/")
    for page in site_dir.rglob("*.html"):
        route = page_route(page, site_dir)
        if route is None:
            continue
        text = page.read_text(encoding="utf-8")

        def replace(match: re.Match[str]) -> str:
            language = match.group(3)
            href = language_href(site_prefix, language, route, site_dir)
            return f"{match.group(1)}{href}{match.group(2)}"

        updated = ALTERNATE_LINK.sub(replace, text)
        if updated != text:
            page.write_text(updated, encoding="utf-8")


def on_post_build(config, **kwargs) -> None:
    rewrite_site_language_links(Path(config["site_dir"]), config["site_url"])
