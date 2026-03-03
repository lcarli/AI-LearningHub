# Contributing to AI Agents Learning Hub

Thank you for helping make this learning hub better! 🎉

This project thrives on community contributions — new labs, bug fixes, translations, and feedback are all welcome.

## Ways to Contribute

| Type | How |
|------|-----|
| 📝 New lab | Write a new lab following the [lab template](#lab-template) |
| 🐛 Bug fix | Fix a broken code sample, typo, or broken link |
| 🌐 Translation | Translate labs to another language (see [Translations](#translations)) |
| 💡 Suggest | Open an issue with your idea |
| ⭐ Star | Star the repo to help others find it |

## Before You Start

1. **Check existing issues** — your idea may already be tracked
2. **Open an issue first** for major changes (new labs, restructuring)
3. **Keep PRs focused** — one lab or fix per PR

## Local Setup

### Option A — GitHub Codespaces (recommended, zero setup)

Click **Code → Codespaces → New codespace**. Everything is pre-installed.

### Option B — Local

```bash
git clone https://github.com/lcarli/AI-LearningHub.git
cd AI-LearningHub

# Install Python dependencies
pip install -r .devcontainer/requirements.txt

# Preview the docs site
cd docs && python -m mkdocs serve
# Open http://localhost:8000
```

## Lab Template

Every lab follows this structure:

```markdown
# Lab NNN: Title Here

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Path:</strong> <a href="../paths/mcp/">MCP</a></span>
  <span><strong>Time:</strong> ~30 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-github">GitHub Free</span></span>
</div>

## What You'll Learn

- Bullet 1
- Bullet 2

---

## Introduction

Brief context paragraph. Link to related concepts.

---

## Prerequisites

- What accounts, tools, or prior labs are needed

---

## Lab Exercise

### Step 1: ...

[code, explanation, screenshots]

---

## Summary

Key takeaways table.

---

## Next Steps

- → [Related lab](link)
```

### Lab numbering

| Level | Number range | Description |
|-------|-------------|-------------|
| L50   | 001–009 | Awareness — no account required |
| L100  | 010–019 | Foundations — free GitHub account |
| L200  | 020–029 | Intermediate — GitHub free (no credit card) |
| L300  | 030–039 | Advanced — Azure subscription |
| L400  | 040–049 | Expert — paid Azure resources |

### Level badges

```html
<span class="level-badge level-50">L50</span>
<span class="level-badge level-100">L100</span>
<span class="level-badge level-200">L200</span>
<span class="level-badge level-300">L300</span>
<span class="level-badge level-400">L400</span>
```

### Cost badges

```html
<span class="level-badge cost-free">Free (local)</span>
<span class="level-badge cost-github">GitHub Free</span>
<span class="level-badge cost-azure-free">Azure Free Tier</span>
```

## Code Sample Guidelines

- **Always test your code** before submitting
- Use `os.environ["GITHUB_TOKEN"]` — never hardcode API keys
- Include both Python and C# where relevant
- Use the **sample dataset** from `data/` where possible:
  - `products.csv` — 25 outdoor gear products
  - `knowledge-base.json` — policies, FAQs, guides
  - `orders.csv` — 20 sample customer orders
- Always show the expected output as a comment

## Writing Style

- **Active voice**: "Create a plugin" not "A plugin should be created"
- **Short sentences**: One idea per sentence
- **Show, don't tell**: Code first, then explanation
- **Honest about costs**: Always clearly state if Azure resources are needed
- **Assume English**: Labs are in English; translations are separate files

## Translations

The i18n plugin supports additional languages. To add a language:

1. Create `docs/docs/LOCALE/` (e.g., `docs/docs/pt/` for Portuguese)
2. Copy English files and translate
3. Add the locale to `docs/mkdocs.yml` under `plugins.i18n.languages`
4. Open a PR with `[translation/pt]` in the title

## Submitting a PR

1. Fork the repo
2. Create a branch: `git checkout -b lab-NNN-topic-name`
3. Write your lab, test all code samples
4. Run `cd docs && python -m mkdocs build --strict` — must pass with no warnings
5. Open a PR using the PR template

## Code of Conduct

Be kind and constructive. We follow the [GitHub Community Code of Conduct](https://docs.github.com/en/site-policy/github-terms/github-community-code-of-conduct).

---

Questions? Open a [GitHub Discussion](https://github.com/lcarli/AI-LearningHub/discussions) or tag `@lcarli` in an issue.
