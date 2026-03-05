---
tags: [github-copilot, free, foundations]
---
# Lab 010 : GitHub Copilot — Premiers pas

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/copilot/">🤖 GitHub Copilot</a></span>
  <span><strong>Durée :</strong> ~45 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-github">GitHub Free</span> — Niveau gratuit (2 000 complétions + 50 chats/mois)</span>
</div>

## Ce que vous apprendrez

- Utiliser la **complétion de code en ligne** pour écrire du code à partir de commentaires
- Utiliser **Copilot Chat `/fix`** pour trouver et comprendre de vrais bugs
- Utiliser **Copilot Edits** pour refactoriser un fichier entier en langage naturel
- Utiliser le **chat en ligne** pour étendre le code sans quitter l'éditeur
- Écrire des prompts qui donnent de meilleurs résultats

Ce lab utilise des **exercices pratiques** — vous ouvrirez des fichiers contenant de vrais bugs et du code incomplet, puis vous utiliserez Copilot pour les corriger et les étendre.

---

## Prérequis

### 1. Activer GitHub Copilot Free

1. Rendez-vous sur [github.com/features/copilot](https://github.com/features/copilot) → **« Commencer gratuitement »**
2. Connectez-vous et suivez l'assistant de configuration

!!! tip "Les étudiants obtiennent Copilot Pro gratuitement"
    → [GitHub Student Developer Pack](https://education.github.com/pack)

### 2. Installer VS Code + l'extension Copilot

1. Installez [VS Code](https://code.visualstudio.com)
2. Extensions (`Ctrl+Shift+X`) → recherchez **« GitHub Copilot »** → Installez les deux :
   - **GitHub Copilot** (complétions)
   - **GitHub Copilot Chat** (panneau de chat)
3. Connectez-vous lorsque vous y êtes invité — vous verrez l'icône Copilot dans la barre d'état

### 3. Télécharger les fichiers d'exercices

Clonez ou téléchargez les fichiers d'exercices pour ce lab :

```bash
git clone https://github.com/lcarli/AI-LearningHub.git
cd AI-LearningHub/docs/docs/en/labs/lab-010
```

Ou copiez chaque fichier directement depuis les sections ci-dessous.

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-010/` de votre répertoire de travail.

| Fichier | Description | Téléchargement |
|---------|-------------|----------------|
| `exercise1_fibonacci.py` | Script d'exercice interactif | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-010/exercise1_fibonacci.py) |
| `exercise2_shopping_cart.py` | Script d'exercice interactif | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-010/exercise2_shopping_cart.py) |
| `exercise3_product_search.py` | Script d'exercice interactif | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-010/exercise3_product_search.py) |
| `exercise4_refactor_me.py` | Script d'exercice interactif | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-010/exercise4_refactor_me.py) |

---

## Exercice 1 — Complétion en ligne : Écrire du code à partir de commentaires

**Objectif :** Apprendre comment Copilot complète le code au fur et à mesure que vous tapez.

Créez un nouveau fichier `practice.py` et tapez chaque commentaire ci-dessous. Après chaque commentaire, **arrêtez de taper** et attendez la suggestion de Copilot. Appuyez sur `Tab` pour accepter, vous pouvez continuer à appuyer sur Tab jusqu'à ce que Copilot arrête de proposer des complétions.

!!! tip "Nous n'exécuterons pas ce code, donc ne vous inquiétez pas des erreurs de syntaxe ou des imports manquants — concentrez-vous uniquement sur les suggestions que Copilot vous donne en fonction des commentaires."

```python
# Function that takes a list of prices and returns the average:

# Function that reads a CSV file and returns rows as a list of dicts:

# Async function that fetches JSON from a URL using httpx:

# Class OutdoorProduct with name, price, category attributes and a discount() method:
```

!!! tip "Raccourcis clavier"
    | Touche | Action |
    |--------|--------|
    | `Tab` | Accepter la suggestion |
    | `Esc` | Ignorer |
    | `Alt+]` / `Alt+[` | Suggestion suivante / précédente |
    | `Ctrl+Enter` | Ouvrir le panneau de toutes les suggestions |

**Essayez des prompts meilleurs et moins bons :**

| ❌ Vague | ✅ Spécifique |
|---------|-------------|
| `# sort this` | `# Sort list of dicts by 'price' descending, then 'name' ascending` |
| `# connect to db` | `# Connect to PostgreSQL using asyncpg, return a connection pool` |
| `# handle error` | `# Retry 3 times with exponential backoff if requests.Timeout is raised` |

---

## Exercice 2 — Copilot `/fix` : Chasse aux bugs 🐛

**Objectif :** Utiliser Copilot Chat pour trouver, comprendre et corriger de vrais bugs.

### Fichier : [📥 `exercise1_fibonacci.py`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-010/exercise1_fibonacci.py)

```python title="exercise1_fibonacci.py — 3 bugs cachés à l'intérieur"
--8<-- "labs/lab-010/exercise1_fibonacci.py"
```

**Étapes :**

1. Copiez le code ci-dessus dans un nouveau fichier (ou ouvrez-le à partir des exercices téléchargés)
2. Ouvrez **Copilot Chat** (`Ctrl+Shift+I`)
3. Sélectionnez **tout le code** (`Ctrl+A`)
4. Tapez : `/fix`

Copilot devrait identifier les 3 bugs et expliquer chacun d'entre eux. Avant d'accepter, **lisez l'explication** — comprendre *pourquoi* le code était incorrect, c'est tout l'intérêt.

**Sortie attendue après correction :**
```python
fibonacci(0)  # → []
fibonacci(1)  # → [0]
fibonacci(8)  # → [0, 1, 1, 2, 3, 5, 8, 13]
```

Exécutez `python exercise1_fibonacci.py` — vous devriez voir : `✅ All tests passed!`

---

### Fichier : [📥 `exercise2_shopping_cart.py`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-010/exercise2_shopping_cart.py)

```python title="exercise2_shopping_cart.py — 4 bugs cachés à l'intérieur"
--8<-- "labs/lab-010/exercise2_shopping_cart.py"
```

Ce fichier contient **4 bugs** dans la classe `ShoppingCart`. Cette fois, avant d'utiliser `/fix` :

1. **Essayez d'abord de repérer les bugs vous-même** — passez 2 minutes à lire le code
2. Puis utilisez Copilot Chat : sélectionnez tout → `/fix`
3. Copilot a-t-il trouvé des bugs que vous avez manqués ?

**Demandez à Copilot d'expliquer un bug en profondeur :**
```
Why is iterating with "for item in self.items" wrong here? What does it actually iterate over?
```

**Sortie attendue après correction :**
```
TrailBlazer X200 x2 @ $189.99 = $379.98
Summit Pro Tent x1 @ $349.00 = $349.00

Total: $656.08
Unique items: 2
✅ All tests passed!
```

---

## Exercice 3 — Chat en ligne : Corriger + Étendre

**Objectif :** Corriger des bugs ET ajouter une nouvelle fonctionnalité en utilisant le chat en ligne (`Ctrl+I`).

### Fichier : [📥 `exercise3_product_search.py`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-010/exercise3_product_search.py)

```python title="exercise3_product_search.py — 2 bugs + 1 fonctionnalité manquante"
--8<-- "labs/lab-010/exercise3_product_search.py"
```

**Partie A — Correction (2 bugs) :**

1. Ouvrez le fichier dans VS Code
2. Sélectionnez tout (`Ctrl+A`) → Copilot Chat → `/fix`
3. Vérifiez : `python exercise3_product_search.py` — les tests 1 à 4 devraient passer

**Partie B — Extension (1 fonctionnalité manquante) :**

Le fichier mentionne une fonction `sort_by_price()` qui n'existe pas encore.

1. Placez votre curseur à la fin du fichier (avant la section des tests)
2. Appuyez sur `Ctrl+I` (chat en ligne)
3. Tapez exactement :
   ```
   Add a sort_by_price(products, ascending=True) function that returns
   the products list sorted by price
   ```
4. Examinez la suggestion et appuyez sur **Accepter** (`Ctrl+Enter`)
5. Relancez les tests — les 5 devraient maintenant passer

---

## Exercice 4 — Copilot Edits : Refactoriser un fichier entier

**Objectif :** Utiliser Copilot Edits pour améliorer la qualité du code avec des instructions en langage naturel — sans changer le comportement.

### Fichier : [📥 `exercise4_refactor_me.py`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-010/exercise4_refactor_me.py)

```python title="exercise4_refactor_me.py — fonctionne, mais nécessite des améliorations"
--8<-- "labs/lab-010/exercise4_refactor_me.py"
```

Ce code **fonctionne correctement** mais est difficile à lire et à maintenir. Utilisez **Copilot Edits** pour l'améliorer étape par étape :

1. Ouvrez le panneau Copilot Edits : `Ctrl+Shift+I` → cliquez sur **« Ouvrir Copilot Edits »** (icône crayon)
2. Cliquez sur **« Ajouter des fichiers »** et ajoutez `exercise4_refactor_me.py`
3. Exécutez chacun de ces prompts **un à la fois**, en examinant les modifications avant de continuer :

**Prompt 1 :**
```
Add type hints to all function parameters and return values
```

**Prompt 2 :**
```
Add docstrings following Google style to every function
```

**Prompt 3 :**
```
Refactor calculate_shipping to use early return instead of nested if/else
```

**Prompt 4 :**
```
Add input validation: raise ValueError if price or quantity is negative
```

Après chaque prompt, vérifiez que le test en bas du fichier passe toujours :
```bash
python exercise4_refactor_me.py
# Should still print: ✅ Refactoring complete — behavior unchanged!
```

!!! warning "N'acceptez pas tout aveuglément"
    Parfois Copilot ajoute de la complexité superflue. Si une suggestion rend le code plus difficile à lire, appuyez sur **Annuler** (`Ctrl+Backspace`) et reformulez.

---

## Bonus : Demandez à Copilot d'expliquer, pas seulement de corriger

Utilisez ces prompts sur n'importe quel fichier d'exercice pour approfondir votre compréhension :

```
/explain
```
```
What tests should I write for this function? Generate them.
```
```
What edge cases does this code not handle?
```
```
Is there a more Pythonic way to write this?
```

---

## Ce que vous avez pratiqué

| Fonctionnalité Copilot | Exercice | Cas d'utilisation |
|------------------------|----------|-------------------|
| Complétion en ligne | Exercice 1 | Écrire du nouveau code à partir de commentaires |
| Chat `/fix` | Exercice 2 | Comprendre et corriger des bugs |
| Chat en ligne `Ctrl+I` | Exercice 3 | Corriger + étendre sur place |
| Copilot Edits | Exercice 4 | Refactoriser des fichiers entiers |

---

## Prochaines étapes

- **Construire un agent sans code pour Teams :** → [Lab 011 — Copilot Studio](lab-011-copilot-studio-first-agent.md)
- **Utiliser le mode Agent pour construire une fonctionnalité complète :** → [Lab 016 — Copilot Agent Mode](lab-016-copilot-agent-mode.md)
- **Utiliser des LLM gratuits dans votre code :** → [Lab 013 — GitHub Models](lab-013-github-models.md)
