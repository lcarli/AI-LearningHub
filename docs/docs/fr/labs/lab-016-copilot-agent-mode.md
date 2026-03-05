---
tags: [github-copilot, free, vscode]
---
# Lab 016 : GitHub Copilot Agent Mode

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/copilot/">🤖 GitHub Copilot</a></span>
  <span><strong>Durée :</strong> ~30 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-github">GitHub Free</span> — Compte GitHub gratuit (le niveau gratuit inclut le mode agent)</span>
</div>

## Ce que vous allez apprendre

- Ce qui distingue le **mode agent** du Copilot Chat classique
- Comment activer et utiliser le mode agent dans VS Code
- Comment l'agent lit votre code source, planifie et exécute des tâches en plusieurs étapes
- Comment connecter des **serveurs MCP** pour étendre les capacités de l'agent
- Bonnes pratiques et limitations

---

## Introduction

GitHub Copilot dans VS Code dispose de trois modes :

| Mode | Ce qu'il fait |
|------|---------------|
| **Ask** | Répond aux questions sur le code ; lecture seule |
| **Edit** | Effectue des modifications sur les fichiers que vous spécifiez |
| **Agent** ⭐ | Explore de manière autonome votre code source, exécute des commandes, utilise des outils et accomplit des tâches en plusieurs étapes |

Le **mode agent** est le plus récent et le plus puissant. Vous décrivez un objectif, et Copilot agit comme un développeur junior : il lit les fichiers, écrit du code, exécute les tests et itère jusqu'à ce que ce soit terminé — en vous demandant votre approbation aux points de décision clés.

!!! info "Disponible dans VS Code 1.99+"
    Le mode agent nécessite VS Code 1.99 ou une version ultérieure et l'extension GitHub Copilot. Vérifiez les mises à jour si vous ne voyez pas le sélecteur de mode.

---

## Configuration des prérequis

1. **VS Code 1.99+** avec l'extension GitHub Copilot installée
2. **Compte GitHub gratuit** avec Copilot activé ([github.com/features/copilot](https://github.com/features/copilot))
3. Un projet sur lequel travailler (nous utiliserons un projet Python simple)

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-016/` dans votre répertoire de travail.

| Fichier | Description | Téléchargement |
|---------|-------------|----------------|
| `outdoorgear_api.py` | Script Python | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-016/outdoorgear_api.py) |

---

## Exercice du lab

### Étape 1 : Activer le mode agent

1. Ouvrez le panneau Copilot Chat (`Ctrl+Shift+I`)
2. Cherchez le sélecteur de mode en haut de la zone de saisie du chat
3. Sélectionnez **« Agent »**

Vous remarquerez que la zone de saisie change — vous pouvez maintenant décrire des objectifs, pas seulement poser des questions.

---

### Étape 2 : Le projet cassé — Corrigez-le avec le mode agent 🐛

Cet exercice vous donne un **vrai projet Python cassé** à corriger en utilisant le mode agent. L'objectif est de voir comment l'agent lit les fichiers, identifie les problèmes et les corrige — étape par étape.

**Téléchargez le projet :**
```bash
cd AI-LearningHub/docs/docs/en/labs/lab-016
```

Ou copiez le fichier [📥 `outdoorgear_api.py`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-016/outdoorgear_api.py) ci-dessous :

```python title="lab-016/outdoorgear_api.py — 5 bugs, 1 missing feature, no tests"
--8<-- "labs/lab-016/outdoorgear_api.py"
```

**Ouvrez le dossier dans VS Code** (important — l'agent a besoin de voir l'ensemble du projet) :
```bash
code docs/docs/en/labs/lab-016/
```

---

### Phase 1 : Laissez l'agent trouver et corriger les bugs

Passez en **mode agent** et tapez exactement ceci :

```
Fix all the bugs in outdoorgear_api.py so that the basic tests 
at the bottom of the file pass when I run: python outdoorgear_api.py

Don't fix the "Test 7" failure yet — that requires a missing function.
```

Observez ce que fait l'agent :

1. 🔍 Il **lit le fichier** sans que vous ayez à coller quoi que ce soit
2. 🐛 Il **identifie chaque bug** et explique pourquoi c'est incorrect
3. ✏️ Il **propose des correctifs** et vous demande votre approbation
4. ▶️ Il **exécute le fichier** pour vérifier que la correction fonctionne

Après avoir accepté, lancez la vérification :
```bash
python outdoorgear_api.py
```
Les tests 1 à 6 devraient passer. Le test 7 échouera (c'est attendu — la fonction est manquante).

!!! tip "Si l'agent se bloque"
    Essayez d'être plus précis : « Exécute python outdoorgear_api.py et montre-moi la sortie d'erreur, puis corrige le bug restant »

---

### Phase 2 : Ajouter la fonctionnalité manquante

Demandez maintenant à l'agent d'implémenter la fonction `search_by_price_range` manquante :

```
Implement the search_by_price_range(min_price, max_price) function 
that is referenced in Test 7. 
It should return active products in that price range, sorted by price ascending.
Then run python outdoorgear_api.py to verify all 7 tests pass.
```

L'agent devrait :
1. Lire le code existant pour comprendre les structures de données
2. Implémenter la fonction
3. Exécuter les tests pour vérifier

---

### Phase 3 : Écrire une suite de tests

Demandez maintenant à l'agent de créer des tests appropriés :

```
Create a tests/ folder with a file test_outdoorgear_api.py.
Write pytest tests that cover:
- get_all_products() with include_inactive=True and False
- get_product_by_id() for valid and invalid IDs
- add_to_cart() including the stock check
- calculate_cart_total() with multiple items
- apply_promo_code() with valid and invalid codes
- place_order() end-to-end

Run pytest to make sure all tests pass.
```

Observez l'agent :
- Il crée le dossier `tests/`
- Il écrit des tests complets en utilisant des fixtures pytest
- Il exécute `pytest` dans le terminal
- Il corrige toutes les erreurs de test qu'il trouve

---

### Phase 4 : Améliorer la qualité du code

```
Add type hints to all public functions in outdoorgear_api.py.
Add Google-style docstrings to each function.
Don't change any logic.
```

---

### Étape 3 : Exploration du code source

Essayez de demander à l'agent d'analyser ce qu'il vient de créer :

```
Give me a summary of the outdoorgear_api.py module:
1. What it does
2. All public functions and their signatures
3. Any edge cases not currently handled
```

L'agent lit l'ensemble du code source et synthétise une réponse cohérente — sans que vous ayez à coller du code.

---

### Étape 4 : Connecter un serveur MCP (bonus)

Le mode agent prend en charge les serveurs MCP. Configurez VS Code pour utiliser le serveur MCP du [Lab 020](lab-020-mcp-server-python.md) :

**`.vscode/mcp.json` :**
```json
{
  "servers": {
    "outdoorgear-products": {
      "type": "stdio",
      "command": "python",
      "args": ["server.py"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

Puis demandez en mode agent :
```
What camping products do we have in stock? Use the outdoorgear-products MCP tool.
```

### Étape 5 : Instructions personnalisées

Créez `.github/copilot-instructions.md` pour que l'agent suive toujours les conventions de votre projet :

```markdown
# Copilot Instructions

## Project
Python API project for OutdoorGear Inc.

## Code Style
- Use type hints on all functions
- Docstrings follow Google style  
- Tests use pytest with fixtures, no unittest
- All prices rounded to 2 decimal places

## Never
- Use print() for logging
- Hardcode product data outside CATALOG
- Skip ValueError validation on public functions
```

---

## Mode agent vs. mode édition : quand utiliser lequel

| Utilisez le mode édition quand | Utilisez le mode agent quand |
|--------------------------------|------------------------------|
| Vous savez exactement quoi modifier | Vous avez un objectif mais pas de plan |
| Modifications simples et ciblées | Tâches multi-fichiers et multi-étapes |
| Vous voulez un contrôle total sur chaque modification | Vous voulez que l'agent trouve la solution |
| Corrections rapides, refactorisations | Débogage, ajout de fonctionnalités, écriture de tests |

---

## Ce que l'agent a fait (en coulisses)

```
Your request: "Fix all bugs"
        │
        ▼
[read_file] outdoorgear_api.py        ← agent reads without you pasting
        │
        ▼
[analysis] Found 5 bugs:
  Bug 1: line 45 — = instead of ==
  Bug 2: line 57 — =+ instead of +=
  ...
        │
        ▼
[replace_in_file] × 5 targeted fixes  ← surgical edits, not rewriting whole file
        │
        ▼
[run_terminal] python outdoorgear_api.py
        │
        ▼
✅ All 6 tests pass
```

---

## Résumé

- ✅ **Lit votre code source** — pas besoin de copier/coller du code dans le chat
- ✅ **Exécution en plusieurs étapes** — planifie et accomplit des tâches complexes
- ✅ **Accès au terminal** — exécute les tests, vérifie les corrections
- ✅ **Intégration MCP** — connecte des outils personnalisés
- ✅ **Approbation à chaque étape** — vous gardez le contrôle

---

## Prochaines étapes

- **Créer un serveur MCP pour étendre le mode agent :** → [Lab 020 — Serveur MCP en Python](lab-020-mcp-server-python.md)
- **Créer un Chat Participant VS Code (@agent personnalisé) :** → [Lab 025 — VS Code Chat Participant](lab-025-vscode-chat-participant.md)
