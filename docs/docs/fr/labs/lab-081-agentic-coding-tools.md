---
tags: [claude-code, copilot-cli, coding-tools, developer-experience, comparison]
---
# Lab 081 : Outils de codage agentiques — Claude Code vs Copilot CLI

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~45 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span></span>
</div>

## Ce que vous apprendrez

- Ce que sont les **outils de codage agentiques** — des assistants IA qui opèrent directement dans votre terminal avec un contexte complet du code
- Comparer **Claude Code** et **GitHub Copilot CLI** sur 10 tâches de développement réelles
- Comprendre comment chaque outil gère la **compréhension du code**, la **génération**, le **débogage** et les **workflows git**
- Mesurer le **gain de temps** par rapport aux approches manuelles pour les tâches de développement courantes
- Déboguer un script d'analyse de comparaison cassé en corrigeant 3 bugs

## Introduction

Une nouvelle catégorie d'outils pour développeurs a émergé : les **assistants de codage agentiques** qui s'exécutent dans votre terminal, lisent l'intégralité de votre base de code et exécutent des tâches multi-étapes de manière autonome. Contrairement aux copilotes basés sur l'IDE qui suggèrent des lignes ou blocs individuels, ces outils peuvent rechercher dans les bases de code, écrire des tests, créer des commits, refactorer des modules et déboguer des pipelines défaillants — le tout à partir d'une seule instruction en langage naturel.

Deux outils de premier plan dans ce domaine sont :

| Outil | Éditeur | Fonctionnement |
|------|--------|-------------|
| **Claude Code** | Anthropic | Agent terminal qui lit votre base de code, exécute des commandes et édite les fichiers directement |
| **GitHub Copilot CLI** | GitHub | Agent terminal intégré à l'écosystème GitHub, exécute des commandes et édite les fichiers |

Les deux outils partagent un modèle commun : ils acceptent une tâche en langage naturel, analysent votre base de code pour le contexte, planifient une approche et l'exécutent — souvent en une seule interaction.

### Le scénario

Vous êtes un **responsable technique** chez OutdoorGear Inc. évaluant des assistants de codage basés sur le terminal pour votre équipe d'ingénierie. Vous avez effectué un benchmark des deux outils sur **10 tâches de développement représentatives** et devez maintenant analyser les résultats pour faire une recommandation.

!!! info "Aucune installation d'outil requise"
    Ce lab analyse un **jeu de données de benchmark pré-enregistré** comparant les temps d'exécution et les taux de réussite. Vous n'avez pas besoin d'installer Claude Code ou Copilot CLI — toute l'analyse est faite localement avec pandas.

## Prérequis

| Exigence | Pourquoi |
|---|---|
| Python 3.10+ | Exécuter les scripts d'analyse |
| Bibliothèque `pandas` | Opérations sur les DataFrames |

```bash
pip install pandas
```

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-081/` de votre répertoire de travail.

| Fichier | Description | Téléchargement |
|------|-------------|----------|
| `broken_tools.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-081/broken_tools.py) |
| `coding_tools_comparison.csv` | Jeu de données — 10 tâches comparées entre les outils | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-081/coding_tools_comparison.csv) |

---

## Étape 1 : Comprendre les outils de codage agentiques

Claude Code et Copilot CLI suivent tous deux une boucle d'agent similaire :

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  User Prompt │────▶│  Codebase    │────▶│  Plan &      │
│  (terminal)  │     │  Analysis    │     │  Execute     │
└──────────────┘     └──────────────┘     └──────────────┘
                                                │
                     ┌──────────────┐            │
                     │  Edit files, │◀───────────┘
                     │  run commands│
                     └──────────────┘
```

Capacités clés partagées par les deux outils :

| Capacité | Description |
|-----------|-------------|
| **Compréhension du code** | Lire et raisonner sur la structure du projet, les dépendances et les patterns |
| **Génération de code** | Écrire du nouveau code (fonctions, tests, modules) aligné sur les conventions du projet |
| **Débogage** | Analyser les erreurs, tracer les problèmes et appliquer les correctifs |
| **Workflows git** | Indexer les changements, créer des commits avec des messages conventionnels, gérer les branches |
| **Refactoring** | Restructurer le code tout en préservant le comportement |
| **Revue de code** | Examiner les changements et suggérer des améliorations |

---

## Étape 2 : Charger le jeu de données de benchmark

Le jeu de données contient **10 tâches** benchmarkées sur les deux outils et la complétion manuelle :

```python
import pandas as pd

tasks = pd.read_csv("lab-081/coding_tools_comparison.csv")
print(f"Total tasks: {len(tasks)}")
print(f"Categories: {sorted(tasks['category'].unique())}")
print(f"\nDataset preview:")
print(tasks[["task_id", "task_description", "category"]].to_string(index=False))
```

**Sortie attendue :**

```
Total tasks: 10
Categories: ['code_generation', 'code_review', 'code_understanding', 'codebase_search', 'debugging', 'devops', 'git_workflow', 'migration', 'refactoring', 'scaffolding']
```

| task_id | task_description | category |
|---------|-----------------|----------|
| T01 | Explain a complex function in the codebase | code_understanding |
| T02 | Find all API endpoints in the project | codebase_search |
| ... | ... | ... |
| T10 | Debug a failing CI pipeline | devops |

---

## Étape 3 : Comparer les taux de réussite

Calculez les taux de réussite pour chaque outil :

```python
for col in ["claude_code_success", "copilot_cli_success"]:
    tasks[col] = tasks[col].astype(str).str.lower() == "true"

cc_success = tasks["claude_code_success"].sum()
cp_success = tasks["copilot_cli_success"].sum()
total = len(tasks)

print(f"Claude Code:  {cc_success}/{total} = {cc_success/total*100:.0f}%")
print(f"Copilot CLI:  {cp_success}/{total} = {cp_success/total*100:.0f}%")

failed_cp = tasks[tasks["copilot_cli_success"] == False]
if len(failed_cp) > 0:
    print(f"\nCopilot CLI failures:")
    print(failed_cp[["task_id", "task_description", "category"]].to_string(index=False))
```

**Sortie attendue :**

```
Claude Code:  10/10 = 100%
Copilot CLI:   9/10 =  90%

Copilot CLI failures:
 task_id                  task_description category
     T10 Debug a failing CI pipeline   devops
```

!!! tip "Observation"
    Claude Code a complété les 10 tâches avec succès (100%). Copilot CLI a complété 9 sur 10 (90%), échouant uniquement sur T10 — le débogage d'un pipeline CI défaillant, qui nécessite un contexte approfondi sur la configuration CI, les variables d'environnement et les systèmes de build.

---

## Étape 4 : Comparer les temps de complétion

Analysez la rapidité de chaque outil pour compléter les tâches :

```python
cc_avg = tasks["claude_code_time_sec"].mean()
cp_avg = tasks["copilot_cli_time_sec"].mean()
manual_avg = tasks["manual_time_sec"].mean()

print(f"Average completion time:")
print(f"  Claude Code:  {cc_avg:.1f}s")
print(f"  Copilot CLI:  {cp_avg:.1f}s")
print(f"  Manual:       {manual_avg:.1f}s")

print(f"\nSpeedup over manual:")
print(f"  Claude Code:  {manual_avg/cc_avg:.0f}x faster")
print(f"  Copilot CLI:  {manual_avg/cp_avg:.0f}x faster")
```

**Sortie attendue :**

```
Average completion time:
  Claude Code:  20.5s
  Copilot CLI:  24.5s
  Manual:       1005.0s

Speedup over manual:
  Claude Code:  49x faster
  Copilot CLI:  41x faster
```

```python
print("\nPer-task comparison:")
for _, t in tasks.iterrows():
    faster = "Claude Code" if t["claude_code_time_sec"] < t["copilot_cli_time_sec"] else "Copilot CLI"
    print(f"  {t['task_id']} ({t['category']:>20}): CC={t['claude_code_time_sec']:>3}s  "
          f"CP={t['copilot_cli_time_sec']:>3}s  → {faster}")
```

!!! tip "Observation"
    Claude Code est plus rapide en moyenne (20.5s vs 24.5s). La seule tâche où Copilot CLI est plus rapide est **T06 (workflow git)** — créer un message de commit conventionnel — probablement grâce à une intégration GitHub plus étroite.

---

## Étape 5 : Analyser par catégorie de tâche

Comparez les performances des outils selon les différents types de tâches :

```python
print("Performance by category:")
for _, row in tasks.iterrows():
    cc_status = "✅" if row["claude_code_success"] else "❌"
    cp_status = "✅" if row["copilot_cli_success"] else "❌"
    print(f"  {row['category']:>20}: CC {cc_status} ({row['claude_code_time_sec']:>3}s)  "
          f"CP {cp_status} ({row['copilot_cli_time_sec']:>3}s)  "
          f"Advantage: {row['tool_advantage']}")
```

**Sortie attendue :**

```
  code_understanding: CC ✅ ( 8s)  CP ✅ (12s)  Advantage: 10x faster
     codebase_search: CC ✅ ( 5s)  CP ✅ ( 8s)  Advantage: 40x faster
     code_generation: CC ✅ (25s)  CP ✅ (30s)  Advantage: 20x faster
           debugging: CC ✅ (18s)  CP ✅ (22s)  Advantage: 45x faster
         refactoring: CC ✅ (35s)  CP ✅ (40s)  Advantage: 30x faster
        git_workflow: CC ✅ ( 4s)  CP ✅ ( 3s)  Advantage: 8x faster
         code_review: CC ✅ (15s)  CP ✅ (20s)  Advantage: 35x faster
         scaffolding: CC ✅ (45s)  CP ✅ (50s)  Advantage: 75x faster
           migration: CC ✅ (30s)  CP ✅ (35s)  Advantage: 55x faster
              devops: CC ✅ (20s)  CP ❌ (25s)  Advantage: 45x faster
```

Les deux outils offrent des **gains de vitesse considérables** par rapport au travail manuel (8x à 75x plus rapide), avec les plus grands gains sur les tâches de scaffolding et de recherche dans la base de code.

---

## Étape 6 : Formuler une recommandation

Résumez la comparaison :

```python
print("=== Tool Comparison Summary ===\n")
print(f"{'Metric':<30} {'Claude Code':>12} {'Copilot CLI':>12}")
print("-" * 56)
print(f"{'Success Rate':<30} {'100%':>12} {'90%':>12}")
print(f"{'Avg Time (s)':<30} {cc_avg:>12.1f} {cp_avg:>12.1f}")
print(f"{'Tasks Won (speed)':<30} {'9':>12} {'1':>12}")
print(f"{'Manual Speedup':<30} {f'{manual_avg/cc_avg:.0f}x':>12} {f'{manual_avg/cp_avg:.0f}x':>12}")
```

!!! tip "Recommandation"
    Les deux outils offrent des gains de productivité exceptionnels. **Claude Code** prend l'avantage dans ce benchmark avec un taux de réussite parfait et des temps moyens plus rapides. **Copilot CLI** excelle dans les workflows git et offre une intégration GitHub plus étroite. Pour les équipes déjà dans l'écosystème GitHub, Copilot CLI est un choix naturel ; pour une fiabilité maximale sur des tâches diverses, Claude Code est l'option la plus robuste.

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-081/broken_tools.py` contient **3 bugs** dans les fonctions d'analyse. Pouvez-vous les trouver et les corriger tous ?

Exécutez les auto-tests pour voir lesquels échouent :

```bash
python lab-081/broken_tools.py
```

Vous devriez voir **3 tests échoués**. Chaque test correspond à un bug :

| Test | Ce qu'il vérifie | Indice |
|------|---------------|------|
| Test 1 | Calcul de l'accélération moyenne | Devrait calculer l'accélération à partir des temps de Claude Code, pas Copilot CLI |
| Test 2 | Taux de réussite des deux outils | Devrait utiliser ET (`&`) pas OU (`|`) pour « les deux ont réussi » |
| Test 3 | Détection de l'outil le plus rapide | L'opérateur de comparaison est inversé |

Corrigez les 3 bugs, puis relancez. Quand vous voyez `All passed!`, c'est terminé !

---

## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Qu'est-ce qui distingue les outils de codage agentiques des copilotes classiques basés sur l'IDE ?"

    - A) Ils ne fonctionnent qu'avec du code Python
    - B) Ils opèrent dans le terminal, lisent des bases de code entières et exécutent des tâches multi-étapes de manière autonome
    - C) Ils nécessitent un GPU pour fonctionner localement
    - D) Ils ne suggèrent que des complétions ligne par ligne

    ??? success "✅ Révéler la réponse"
        **Correct : B) Ils opèrent dans le terminal, lisent des bases de code entières et exécutent des tâches multi-étapes de manière autonome**

        Contrairement aux copilotes basés sur l'IDE qui suggèrent des complétions de code dans un éditeur, les outils de codage agentiques comme Claude Code et Copilot CLI s'exécutent dans le terminal, analysent la structure complète de votre projet et peuvent effectuer des tâches multi-étapes complexes — recherche dans les bases de code, écriture de tests, création de commits et débogage de pipelines — le tout à partir d'une seule instruction en langage naturel.

??? question "**Q2 (Choix multiple) :** Quel est le principal avantage des outils de codage agentiques par rapport au développement manuel ?"

    - A) Ils produisent du code sans bugs à chaque fois
    - B) Ils éliminent le besoin de revue de code
    - C) Ils réduisent considérablement le temps pour les tâches courantes (souvent 10x–75x plus rapide)
    - D) Ils remplacent le besoin de contrôle de version

    ??? success "✅ Révéler la réponse"
        **Correct : C) Ils réduisent considérablement le temps pour les tâches courantes (souvent 10x–75x plus rapide)**

        Le benchmark montre des accélérations allant de 8x (workflows git) à 75x (scaffolding) par rapport à la complétion manuelle. Bien que les outils ne produisent pas du code parfait à chaque fois et que la revue de code reste importante, les gains de temps pour les tâches routinières sont substantiels.

??? question "**Q3 (Exécutez le lab) :** Quel est le taux de réussite de Claude Code sur les 10 tâches ?"

    Chargez [📥 `coding_tools_comparison.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-081/coding_tools_comparison.csv) et comptez `claude_code_success == True`.

    ??? success "✅ Révéler la réponse"
        **100% (10/10)**

        Claude Code a complété avec succès les 10 tâches du benchmark, incluant la compréhension du code, la génération, le débogage, le refactoring, les workflows git, la revue de code, le scaffolding, la migration et les tâches DevOps.

??? question "**Q4 (Exécutez le lab) :** Quel est le taux de réussite de Copilot CLI, et quelle tâche a échoué ?"

    Comptez `copilot_cli_success == True` et identifiez la tâche échouée.

    ??? success "✅ Révéler la réponse"
        **90% (9/10) — échec sur T10 (Debug a failing CI pipeline)**

        Copilot CLI a réussi 9 tâches sur 10. Le seul échec était T10 — le débogage d'un pipeline CI défaillant — qui nécessite un contexte approfondi sur la configuration CI, les variables d'environnement et les interactions du système de build.

??? question "**Q5 (Exécutez le lab) :** Quel outil est le plus rapide globalement selon le temps de complétion moyen ?"

    Calculez `claude_code_time_sec.mean()` et `copilot_cli_time_sec.mean()`.

    ??? success "✅ Révéler la réponse"
        **Claude Code (20.5s en moyenne vs 24.5s en moyenne)**

        Le temps de complétion moyen de Claude Code est de 20.5 secondes contre 24.5 secondes pour Copilot CLI. Claude Code était plus rapide sur 9 des 10 tâches ; Copilot CLI n'était plus rapide que sur T06 (workflow git, 3s vs 4s).

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|-----------------|
| Outils de codage agentiques | Assistants IA basés sur le terminal qui lisent les bases de code et exécutent des tâches multi-étapes |
| Claude Code | Taux de réussite de 100%, 20.5s en moyenne, meilleur sur les tâches complexes |
| Copilot CLI | Taux de réussite de 90%, 24.5s en moyenne, excelle dans les workflows git |
| Gain de temps | Les deux outils offrent une accélération de 8x–75x par rapport au développement manuel |
| Catégories de tâches | Les deux gèrent bien la compréhension, la génération, la revue et le refactoring du code |
| Recommandation | Claude Code pour la fiabilité ; Copilot CLI pour l'intégration GitHub |

---

## Prochaines étapes

- **[Lab 082](lab-082-agent-guardrails.md)** — Garde-fous des agents : NeMo et Azure Content Safety
- Essayez les deux outils sur votre propre base de code pour voir lequel correspond le mieux à votre workflow
