#!/usr/bin/env python3
"""Mark pages that still contain archived GitHub Models instructions."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "docs"

NOTICES = {
    "en": """!!! warning "Backend update (October 2026)"
    GitHub Models inference was retired on July 30, 2026. Any references below are retained only for historical context while this lab is migrated. Use [Lab 013 — Free LLM backends](../labs/lab-013-github-models.md) to configure Foundry Local or Ollama before continuing.

""",
    "pt": """!!! warning "Atualização de backend (outubro de 2026)"
    A inferência do GitHub Models foi descontinuada em 30 de julho de 2026. As referências abaixo são mantidas apenas como contexto histórico enquanto este lab é migrado. Use o [Lab 013 — Backends de LLM gratuitos](../labs/lab-013-github-models.md) para configurar o Foundry Local ou o Ollama antes de continuar.

""",
    "fr": """!!! warning "Mise à jour du backend (octobre 2026)"
    L'inférence GitHub Models a été retirée le 30 juillet 2026. Les références ci-dessous sont conservées uniquement comme contexte historique pendant la migration de ce lab. Utilisez le [Lab 013 — Backends LLM gratuits](../labs/lab-013-github-models.md) pour configurer Foundry Local ou Ollama avant de continuer.

""",
}

LEGACY = re.compile(
    r"GitHub Models|models\.inference\.ai\.azure\.com|github\.com/marketplace/models",
    re.IGNORECASE,
)
NOTICE_BLOCK = re.compile(
    r'^!!! warning "(?:Backend update \(October 2026\)|'
    r'Atualização de backend \(outubro de 2026\)|'
    r'Mise à jour du backend \(octobre 2026\))"\n'
    r'(?:    .*\n)+\n?',
    re.MULTILINE,
)


def insert_notice(text: str, notice: str) -> str:
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            split = end + len("\n---\n")
            return text[:split] + notice + text[split:]
    return notice + text


def main() -> None:
    updated = 0
    for lang, notice in NOTICES.items():
        for path in sorted((DOCS / lang).rglob("*.md")):
            text = path.read_text(encoding="utf-8")
            if path.parent.name != "labs":
                cleaned = NOTICE_BLOCK.sub("", text)
                if cleaned != text:
                    path.write_text(cleaned, encoding="utf-8")
                continue
            if path.name.startswith("lab-013-"):
                cleaned = NOTICE_BLOCK.sub("", text)
                if cleaned != text:
                    path.write_text(cleaned, encoding="utf-8")
                continue
            if LEGACY.search(text) and notice.splitlines()[0] not in text:
                path.write_text(insert_notice(text, notice), encoding="utf-8")
                updated += 1
    print(f"Added backend retirement notices to {updated} pages.")


if __name__ == "__main__":
    main()
