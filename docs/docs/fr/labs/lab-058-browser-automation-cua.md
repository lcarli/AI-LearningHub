---
tags: [browser-automation, cua, openai, playwright, python, safety]
---
# Lab 058 : Agents d'automatisation de navigateur avec OpenAI CUA

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/pro-code/">⚙️ Pro Code</a></span>
  <span><strong>Durée :</strong> ~90 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Utilise un jeu de données de benchmark ; API OpenAI optionnelle</span>
</div>

## Ce que vous apprendrez

- Ce qu'est **OpenAI CUA** (Computer-Using Agent) — GPT-4o vision pilotant un vrai navigateur cloud via des captures d'écran
- La différence architecturale entre **CUA** (basé sur les captures d'écran) et **Playwright** (basé sur des sélecteurs de code)
- Quand utiliser CUA vs Playwright — sites dynamiques sans sélecteurs stables vs pages structurées et bien connues
- Concevoir des **limites de sécurité** — listes blanches d'URL, limites de durée de session et confirmation d'action
- Analyser des **benchmarks d'automatisation web** comparant CUA et Playwright selon les niveaux de difficulté

## Introduction

**OpenAI CUA** opère un vrai navigateur via des captures d'écran. L'agent voit la page rendue comme une image, raisonne sur l'action suivante et envoie des actions structurées (coordonnées de clic, saisie de texte, défilement). C'est fondamentalement différent de **Playwright**, qui interagit avec la page via du code — sélecteurs CSS, requêtes XPath et appels API programmatiques.

| Approche | Comment il « voit » la page | Méthode d'interaction | Fragilité |
|----------|----------------------|-------------------|-------------|
| **CUA** | Captures d'écran (pixels) | Coordonnées de clic, saisie clavier | Résistant aux changements du DOM ; peine avec les SPA dynamiques |
| **Playwright** | DOM / structure HTML | Sélecteurs CSS, XPath, appels API | Casse quand les sélecteurs changent ; rapide et précis |

### Le scénario

Vous êtes **ingénieur en automatisation web** chez OutdoorGear Inc. L'équipe doit automatiser des tâches sur plusieurs propriétés web — la boutique e-commerce, les partenaires de réservation de voyages, le portail de support et les tableaux de bord d'analyse internes. Certains sites ont un HTML stable et bien structuré ; d'autres sont des applications monopage dynamiques avec des sélecteurs en constante évolution.

Votre mission est d'évaluer **CUA vs Playwright** en utilisant un jeu de données de benchmark de **10 tâches** tentées par les deux méthodes, et de recommander quelle approche utiliser pour chaque scénario.

!!! info "Aucun agent en direct requis"
    Ce lab analyse un **jeu de données de benchmark pré-enregistré** comparant les résultats de CUA et Playwright. Vous n'avez pas besoin d'une clé API OpenAI ni d'une installation de Playwright — toute l'analyse se fait localement avec pandas. Si vous avez accès à l'API, vous pouvez optionnellement étendre le lab pour exécuter des tâches CUA en direct.

## Prérequis

| Exigence | Pourquoi |
|---|---|
| Python 3.10+ | Exécuter les scripts d'analyse |
| Bibliothèque `pandas` | Opérations sur les DataFrames |
| (Optionnel) Clé API OpenAI | Pour des expériences CUA en direct |
| (Optionnel) Playwright | Pour la comparaison d'automatisation de navigateur en direct |

```bash
pip install pandas
```

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-058/` dans votre répertoire de travail.

| Fichier | Description | Télécharger |
|------|-------------|----------|
| `broken_cua.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-058/broken_cua.py) |
| `browser_tasks.csv` | Jeu de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-058/browser_tasks.csv) |

---

## Étape 1 : Comprendre CUA vs Playwright

### Architecture CUA

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Browser     │────▶│  GPT-4o      │────▶│  Browser     │
│  Screenshot  │     │  Vision      │     │  Action      │
│  (pixels)    │     │  (reason)    │     │  (click/type)│
└─────────────┘     └──────────────┘     └──────────────┘
       ▲                                        │
       └────────────────────────────────────────┘
                    repeat until done
```

CUA envoie des captures d'écran à GPT-4o, qui renvoie des actions structurées. Le navigateur exécute l'action, prend une nouvelle capture d'écran, et la boucle continue jusqu'à ce que la tâche soit terminée.

### Architecture Playwright

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Test Script │────▶│  Browser     │────▶│  DOM / HTML  │
│  (code)      │     │  Engine      │     │  (selectors) │
└─────────────┘     └──────────────┘     └──────────────┘
```

Playwright exécute du code pré-écrit qui cible des éléments HTML spécifiques en utilisant des sélecteurs CSS, XPath ou des rôles ARIA. C'est rapide, précis et déterministe — mais casse quand la structure de la page change.

### Quand utiliser chaque approche

| Scénario | Meilleure approche | Pourquoi |
|----------|--------------|-----|
| Site stable et bien structuré | **Playwright** | Les sélecteurs sont fiables ; plus rapide et moins coûteux |
| SPA dynamique avec sélecteurs changeants | **CUA** | Basé sur la vision ; ne dépend pas de la structure du DOM |
| Pages protégées par CAPTCHA | **CUA** | Peut « voir » et raisonner sur les CAPTCHAs |
| Tâches répétitives à haut volume | **Playwright** | Exécution plus rapide ; pas de coût API par action |
| Exploration de site inconnu/nouveau | **CUA** | Pas de sélecteurs pré-écrits nécessaires |

!!! tip "Différence clé"
    CUA utilise la **vision et les captures d'écran** pour comprendre la page — comme un humain regardant un écran. Playwright utilise du **code et des sélecteurs** — comme un développeur inspectant le code source HTML. CUA est plus flexible ; Playwright est plus fiable sur les pages connues.

---

## Étape 2 : Charger le jeu de données de benchmark

Le jeu de données contient **10 tâches**, chacune tentée par CUA et Playwright :

```python
import pandas as pd

tasks = pd.read_csv("lab-058/browser_tasks.csv")
print(f"Total rows: {len(tasks)}")
print(f"Unique tasks: {tasks['task_id'].nunique()}")
print(f"Website types: {sorted(tasks['website_type'].unique())}")
print(f"Difficulty levels: {sorted(tasks['difficulty'].unique())}")
print(f"\nDataset preview:")
print(tasks[["task_id", "task_description", "difficulty",
             "cua_completed", "playwright_completed"]].to_string(index=False))
```

**Sortie attendue :**

```
Total rows: 10
Unique tasks: 10
Website types: ['auth', 'data', 'e-commerce', 'support', 'travel', 'webapp']
Difficulty levels: ['easy', 'hard', 'medium']
```

| task_id | task_description | difficulty | cua | playwright |
|---------|-----------------|------------|-----|------------|
| T01 | Search for hiking boots and filter by price | easy | ✓ | ✓ |
| T02 | Add a product to cart and view cart total | easy | ✓ | ✓ |
| T03 | Fill out a shipping address form | medium | ✓ | ✓ |
| ... | ... | ... | ... | ... |
| T10 | Navigate a dynamic SPA with client-side routing | hard | ✗ | ✓ |

---

## Étape 3 : Comparer les taux de réussite CUA vs Playwright

Calculez et comparez les taux de complétion des deux méthodes :

```python
cua_completed = tasks["cua_completed"].sum()
pw_completed = tasks["playwright_completed"].sum()
total = len(tasks)

cua_rate = (cua_completed / total) * 100
pw_rate = (pw_completed / total) * 100

print(f"CUA:        {cua_completed}/{total} = {cua_rate:.0f}%")
print(f"Playwright: {pw_completed}/{total} = {pw_rate:.0f}%")
print(f"Difference: {pw_rate - cua_rate:.0f} percentage points in Playwright's favor")
```

**Sortie attendue :**

```
CUA:        7/10 = 70%
Playwright: 8/10 = 80%
Difference: 10 percentage points in Playwright's favor
```

### Là où chaque méthode excelle

```python
# Tasks where CUA succeeded but Playwright failed
cua_only = tasks[(tasks["cua_completed"] == True) & (tasks["playwright_completed"] == False)]
print(f"CUA succeeded, Playwright failed ({len(cua_only)}):")
print(cua_only[["task_id", "task_description"]].to_string(index=False))

# Tasks where Playwright succeeded but CUA failed
pw_only = tasks[(tasks["playwright_completed"] == True) & (tasks["cua_completed"] == False)]
print(f"\nPlaywright succeeded, CUA failed ({len(pw_only)}):")
print(pw_only[["task_id", "task_description"]].to_string(index=False))
```

**Attendu :**

- **CUA uniquement** : T07 (Soumettre un ticket de support avec pièce jointe de capture d'écran) — formulaire dynamique avec téléchargement de fichier difficile à scripter avec des sélecteurs
- **Playwright uniquement** : T06 (Comparer les prix d'hôtels sur 3 onglets), T10 (Naviguer dans une SPA dynamique) — tâches structurées où la navigation basée sur le code est plus fiable

!!! tip "Observation"
    Playwright a un taux de réussite global plus élevé (80% vs 70%), mais CUA gagne sur les tâches impliquant du **contenu dynamique** ou du **raisonnement visuel** (comme joindre des captures d'écran aux tickets de support). Playwright excelle dans les flux de travail **structurés, multi-onglets** où une navigation précise basée sur les sélecteurs est nécessaire.

---

## Étape 4 : Analyser par difficulté

Détaillez les taux de réussite par niveau de difficulté :

```python
print("Success rates by difficulty:\n")
for diff in ["easy", "medium", "hard"]:
    subset = tasks[tasks["difficulty"] == diff]
    cua_r = (subset["cua_completed"].sum() / len(subset)) * 100
    pw_r = (subset["playwright_completed"].sum() / len(subset)) * 100
    print(f"  {diff.upper()} ({len(subset)} tasks):")
    print(f"    CUA:        {subset['cua_completed'].sum()}/{len(subset)} = {cua_r:.0f}%")
    print(f"    Playwright: {subset['playwright_completed'].sum()}/{len(subset)} = {pw_r:.0f}%")
    print()
```

**Sortie attendue :**

```
Success rates by difficulty:

  EASY (2 tasks):
    CUA:        2/2 = 100%
    Playwright: 2/2 = 100%

  MEDIUM (3 tasks):
    CUA:        3/3 = 100%
    Playwright: 3/3 = 100%

  HARD (5 tasks):
    CUA:        2/5 = 40%
    Playwright: 3/5 = 60%
```

!!! tip "Observation"
    Les deux méthodes gèrent parfaitement les tâches **faciles et moyennes** (100%). L'écart apparaît dans les **tâches difficiles** où l'approche basée sur les sélecteurs de Playwright a un léger avantage (60% vs 40%). Cependant, les tâches où CUA gagne (T07) sont précisément celles où les sélecteurs de Playwright ne peuvent pas gérer le contenu dynamique et visuel.

---

## Étape 5 : Analyse des captures d'écran

CUA prend des captures d'écran à chaque étape — plus de captures d'écran signifie généralement une tâche plus difficile ou plus longue :

```python
total_screenshots = tasks["cua_screenshots"].sum()
print(f"Total CUA screenshots across all tasks: {total_screenshots}")

print(f"\nScreenshots per task:")
print(tasks[["task_id", "task_description", "difficulty",
             "cua_screenshots", "cua_completed"]].to_string(index=False))

avg_by_diff = tasks.groupby("difficulty")["cua_screenshots"].mean()
print(f"\nAverage screenshots by difficulty:")
print(avg_by_diff.to_string())
```

**Sortie attendue :**

```
Total CUA screenshots across all tasks: 122
```

| task_id | difficulty | screenshots | completed |
|---------|-----------|-------------|-----------|
| T01 | easy | 3 | True |
| T02 | easy | 5 | True |
| T03 | medium | 8 | True |
| T04 | medium | 6 | True |
| T05 | medium | 10 | True |
| T06 | hard | 18 | False |
| T07 | hard | 14 | True |
| T08 | hard | 16 | False |
| T09 | hard | 22 | True |
| T10 | hard | 20 | False |

```
Average screenshots by difficulty:
easy       4.0
medium     8.0
hard      18.0
```

!!! tip "Coût des captures d'écran"
    Chaque capture d'écran est envoyée à GPT-4o sous forme de tokens d'image — à environ 765 tokens par capture d'écran (page web typique), 122 captures d'écran ≈ 93 000 tokens. Au tarif de GPT-4o, cela représente environ **0,47 $ en tokens d'entrée** pour l'ensemble du benchmark. CUA est économique pour des charges de travail modérées mais peut s'accumuler pour des tâches à haut volume.

---

## Étape 6 : Considérations de sécurité

### Liste blanche d'URL

Restreignez CUA aux domaines approuvés :

```python
# Analyze domain patterns in the dataset
print("URL patterns in tasks:")
print(tasks["url_pattern"].value_counts().to_string())

internal = tasks[tasks["url_pattern"] != "external"]
external = tasks[tasks["url_pattern"] == "external"]
print(f"\nInternal domains: {len(internal)} tasks")
print(f"External domains: {len(external)} tasks")

high_risk = tasks[tasks["safety_risk"] == "high"]
print(f"\nHigh-risk tasks: {len(high_risk)}")
print(high_risk[["task_id", "task_description", "safety_risk", "url_pattern"]].to_string(index=False))
```

### Limites de sécurité recommandées

| Limite | Objectif | Implémentation |
|----------|---------|----------------|
| **Liste blanche d'URL** | Restreindre les sites que CUA peut visiter | `allowed_domains = ["*.outdoorgear.com"]` |
| **Limite de durée de session** | Empêcher les agents incontrôlés | Arrêter la session après 5 minutes d'inactivité |
| **Confirmation d'action** | Approbation humaine pour les actions risquées | Demander confirmation avant les soumissions de formulaires sur les pages de paiement |
| **Conservation des captures d'écran** | Piste d'audit | Enregistrer toutes les captures d'écran avec horodatage pour révision |
| **Gestion des identifiants** | Ne jamais exposer les mots de passe dans les captures d'écran | Utiliser le remplissage automatique du navigateur ; garder les mots de passe hors des champs visibles |

!!! warning "Sites externes"
    La tâche T10 cible un domaine externe (`external`). En production, CUA ne devrait **jamais** être dirigé vers des sites externes sans liste blanche explicite. Un agent non contraint pourrait naviguer vers des sites de phishing, télécharger des logiciels malveillants ou divulguer des données sensibles via des soumissions de formulaires sur des domaines non fiables.

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-058/broken_cua.py` contient **3 bugs** dans les fonctions d'analyse CUA. Pouvez-vous les trouver et les corriger tous ?

Exécutez les auto-tests pour voir lesquels échouent :

```bash
python lab-058/broken_cua.py
```

Vous devriez voir **3 tests échoués**. Chaque test correspond à un bug :

| Test | Ce qu'il vérifie | Indice |
|------|---------------|------|
| Test 1 | Taux de réussite CUA | Devrait utiliser la colonne `cua_completed`, pas `playwright_completed` |
| Test 2 | Total des captures d'écran CUA | Devrait utiliser `sum()`, pas `max()` |
| Test 3 | Taux de réussite CUA par difficulté | Doit filtrer par le paramètre `difficulty` avant de calculer le taux |

Corrigez les 3 bugs, puis relancez. Quand vous voyez `🎉 All 3 tests passed`, c'est terminé !

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Quelle est la différence clé entre CUA et Playwright pour l'automatisation de navigateur ?"

    - A) CUA est plus rapide car il ignore le rendu de la page
    - B) CUA utilise la vision/captures d'écran pour comprendre les pages, tandis que Playwright utilise des sélecteurs CSS basés sur le code
    - C) Playwright peut gérer les CAPTCHAs mais pas CUA
    - D) CUA nécessite l'accès au code source HTML de la page

    ??? success "✅ Révéler la réponse"
        **Correct : B) CUA utilise la vision/captures d'écran pour comprendre les pages, tandis que Playwright utilise des sélecteurs CSS basés sur le code**

        CUA envoie des captures d'écran à un modèle de vision-langage (GPT-4o) et reçoit des actions de clic/saisie basées sur ce qu'il « voit » — tout comme un humain regardant un écran. Playwright interagit directement avec le DOM en utilisant des sélecteurs CSS, XPath ou des rôles ARIA. Cette différence fondamentale signifie que CUA est plus flexible (fonctionne sur n'importe quelle interface visuelle) tandis que Playwright est plus précis (accès direct au DOM).

??? question "**Q2 (Choix multiple) :** Quand CUA est-il un meilleur choix que Playwright ?"

    - A) Pour les tâches répétitives à haut volume sur des pages stables
    - B) Pour les sites dynamiques sans sélecteurs CSS stables
    - C) Quand vous avez besoin de résultats de tests déterministes et reproductibles
    - D) Quand la page a une API bien documentée

    ??? success "✅ Révéler la réponse"
        **Correct : B) Pour les sites dynamiques sans sélecteurs CSS stables**

        CUA excelle sur les sites où la structure du DOM change fréquemment — SPA dynamiques, sites avec tests A/B ou pages avec des identifiants d'éléments aléatoires. Parce que CUA « voit » la page visuellement, il ne dépend pas des sélecteurs CSS qui pourraient casser à chaque déploiement. Playwright est meilleur pour les sites stables et bien structurés où les sélecteurs sont fiables.

??? question "**Q3 (Exécuter le lab) :** Quel est le taux de réussite de CUA ?"

    Comptez les tâches où `cua_completed == True` et divisez par le nombre total de tâches.

    ??? success "✅ Révéler la réponse"
        **70%**

        7 tâches sur 10 ont été complétées avec succès par CUA. Les 3 échecs (T06, T08, T10) étaient tous des tâches de difficulté **difficile** impliquant la comparaison multi-onglets, la gestion de CAPTCHA et la navigation dans une SPA dynamique.

??? question "**Q4 (Exécuter le lab) :** Quel est le taux de réussite de Playwright ?"

    Comptez les tâches où `playwright_completed == True` et divisez par le nombre total de tâches.

    ??? success "✅ Révéler la réponse"
        **80%**

        8 tâches sur 10 ont été complétées avec succès par Playwright. Les 2 échecs (T07, T08) impliquaient un téléchargement de pièce jointe de capture d'écran (qui nécessite un raisonnement visuel au-delà des sélecteurs) et un formulaire protégé par CAPTCHA (qu'aucune des deux méthodes n'a pu gérer).

??? question "**Q5 (Exécuter le lab) :** Quel est le nombre total de captures d'écran CUA sur l'ensemble des tâches ?"

    Calculez `tasks["cua_screenshots"].sum()`.

    ??? success "✅ Révéler la réponse"
        **122**

        Somme de toutes les captures d'écran : 3 + 5 + 8 + 6 + 10 + 18 + 14 + 16 + 22 + 20 = **122 captures d'écran**. Les tâches difficiles nécessitaient significativement plus de captures d'écran (moy. 18) par rapport aux tâches faciles (moy. 4), reflétant les étapes de raisonnement supplémentaires nécessaires pour les flux de travail complexes.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|-----------------|
| Architecture CUA | La vision GPT-4o pilote un navigateur cloud via une boucle capture d'écran → action |
| Architecture Playwright | Des sélecteurs basés sur le code interagissent directement avec le DOM |
| CUA vs Playwright | CUA : 70% de réussite, flexible ; Playwright : 80% de réussite, précis |
| Impact de la difficulté | Les deux méthodes réussissent les tâches faciles/moyennes ; les tâches difficiles révèlent leurs différences |
| Surcoût des captures d'écran | 122 captures d'écran au total ; les tâches difficiles en nécessitent 4× plus que les faciles |
| Conception de la sécurité | Listes blanches d'URL, limites de session, isolation des identifiants, pistes d'audit |

---

## Prochaines étapes

- **[Lab 057](lab-057-computer-use-agents.md)** — Agents utilisant l'ordinateur pour l'automatisation du bureau
- Explorez la [documentation CUA](https://platform.openai.com/docs/guides/computer-using-agent) d'OpenAI pour la configuration d'un agent en direct
- Essayez [Playwright](https://playwright.dev/) pour l'automatisation de navigateur basée sur le code
