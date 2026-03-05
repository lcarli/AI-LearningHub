---
tags: [reasoning, o3, deepseek-r1, chain-of-thought, benchmark, python]
---
# Lab 060 : Modèles de raisonnement — Chain-of-Thought avec o3 et DeepSeek R1

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~75 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Utilise un jeu de données de benchmark (Azure OpenAI optionnel)</span>
</div>

## Ce que vous apprendrez

- Comment les **modèles de raisonnement** (o3, DeepSeek R1) diffèrent des modèles standard (GPT-4o) — réflexion étendue, chaîne de pensée
- Ce qu'est un **budget de réflexion** et comment il contrôle la profondeur du raisonnement du modèle
- Comparer la **précision, la vitesse et le coût en tokens** de 3 modèles sur 12 problèmes de benchmark
- Identifier quelles **catégories de problèmes et niveaux de difficulté** bénéficient le plus du raisonnement
- Appliquer un cadre décisionnel : **quand utiliser les modèles de raisonnement** vs les modèles standard
- Comprendre les **compromis coût-performance** pour les déploiements en production

---

## Introduction

Les LLM standard comme GPT-4o génèrent des réponses en une seule passe — rapidement, mais ils peuvent trébucher sur des problèmes qui nécessitent un raisonnement logique en plusieurs étapes. Les **modèles de raisonnement** comme o3 et DeepSeek R1 adoptent une approche différente : ils utilisent la **réflexion étendue** (chaîne de pensée) pour décomposer les problèmes complexes en étapes, vérifier les résultats intermédiaires et revenir en arrière lorsqu'ils détectent des erreurs.

Le compromis est clair : les modèles de raisonnement sont plus lents et utilisent plus de tokens, mais ils atteignent une précision considérablement plus élevée sur les problèmes difficiles.

### Le benchmark

Vous comparerez **3 modèles** sur **12 problèmes** répartis en 4 catégories :

| Catégorie | Facile | Moyen | Difficile |
|-----------|--------|-------|-----------|
| **Maths** | Intérêts composés | Système d'équations | Prouver que √2 est irrationnel |
| **Code** | Inverser une chaîne | Recherche binaire | Cache LRU thread-safe |
| **Logique** | Syllogisme | Puzzle des trois boîtes | Loup-chèvre-chou |
| **Planification** | Itinéraire de randonnée | Itinéraire de livraison | Migration vers les microservices |

---

## Prérequis

```bash
pip install pandas
```

Ce lab analyse des résultats de benchmark pré-calculés — aucune clé API ni abonnement Azure requis. Pour exécuter des benchmarks en direct, vous auriez besoin d'un accès à GPT-4o, o3 et DeepSeek R1 via Azure OpenAI ou les API respectives.

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-060/` dans votre répertoire de travail.

| Fichier | Description | Télécharger |
|---------|-------------|-------------|
| `broken_reasoning.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-060/broken_reasoning.py) |
| `reasoning_benchmark.csv` | Jeu de données de benchmark | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-060/reasoning_benchmark.csv) |

---

## Partie 1 : Comprendre les modèles de raisonnement

### Étape 1 : Comment fonctionnent les modèles de raisonnement

Les modèles standard génèrent des tokens de gauche à droite sans s'arrêter pour « réfléchir ». Les modèles de raisonnement ajoutent une phase de délibération interne :

```
Standard (GPT-4o):
  Input → [Generate tokens] → Output

Reasoning (o3 / DeepSeek R1):
  Input → [Think: break into steps] → [Verify each step] → [Backtrack if needed] → Output
```

Concepts clés :

| Concept | Description |
|---------|-------------|
| **Chaîne de pensée** | Le modèle raisonne explicitement à travers des étapes intermédiaires avant de répondre |
| **Budget de réflexion** | Contrôle la quantité de raisonnement effectuée par le modèle (plus de budget = plus approfondi = plus lent) |
| **Réflexion étendue** | La délibération interne du modèle — visible dans certaines API sous forme de « tokens de réflexion » |
| **Auto-vérification** | Le modèle vérifie ses propres résultats intermédiaires et corrige les erreurs |

!!! info "Budget de réflexion"
    Le budget de réflexion contrôle la quantité de raisonnement effectuée par le modèle avant de produire une réponse finale. Un budget plus élevé permet au modèle d'explorer davantage de pistes de solution et de vérifier plus minutieusement — mais coûte plus de tokens et prend plus de temps. Pour les questions simples, un budget faible suffit ; pour les preuves complexes, vous voulez le budget maximal.

---

## Partie 2 : Charger les données du benchmark

### Étape 2 : Charger [📥 `reasoning_benchmark.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-060/reasoning_benchmark.csv)

Le jeu de données de benchmark contient les résultats de l'exécution des 12 problèmes à travers chaque modèle :

```python
# reasoning_analysis.py
import pandas as pd

bench = pd.read_csv("lab-060/reasoning_benchmark.csv")

# Convert boolean columns
for model in ["gpt4o", "o3", "deepseek_r1"]:
    bench[f"{model}_correct"] = bench[f"{model}_correct"].astype(str).str.lower() == "true"

print(f"Problems: {len(bench)}")
print(f"Categories: {bench['category'].unique().tolist()}")
print(f"Difficulties: {bench['difficulty'].unique().tolist()}")
print(bench[["problem_id", "category", "difficulty"]].to_string(index=False))
```

**Sortie attendue :**

```
Problems: 12
Categories: ['math', 'code', 'logic', 'planning']
Difficulties: ['easy', 'medium', 'hard']

problem_id category difficulty
       P01     math       easy
       P02     math     medium
       P03     math       hard
       P04     code       easy
       P05     code     medium
       P06     code       hard
       P07    logic       easy
       P08    logic     medium
       P09    logic       hard
       P10 planning       easy
       P11 planning     medium
       P12 planning       hard
```

---

## Partie 3 : Comparaison globale de la précision

### Étape 3 : Calculer la précision pour chaque modèle

```python
# Overall accuracy
for model in ["gpt4o", "o3", "deepseek_r1"]:
    correct = bench[f"{model}_correct"].sum()
    total = len(bench)
    print(f"{model:>12}: {correct}/{total} = {correct/total*100:.1f}%")
```

**Sortie attendue :**

```
      gpt4o: 6/12 = 50.0%
          o3: 12/12 = 100.0%
 deepseek_r1: 11/12 = 91.7%
```

!!! warning "Constat clé"
    GPT-4o ne résout que la moitié des problèmes, tandis que o3 obtient un score parfait. DeepSeek R1 échoue sur un seul problème (P12 — le problème de planification le plus difficile). L'écart est considérable sur les problèmes difficiles.

```python
# Which problems does GPT-4o get wrong?
gpt4o_fails = bench[bench["gpt4o_correct"] == False]
print("GPT-4o failures:")
print(gpt4o_fails[["problem_id", "category", "difficulty", "description"]].to_string(index=False))
```

**Sortie attendue :**

```
GPT-4o failures:
problem_id category difficulty                                       description
       P03     math       hard                    Prove that sqrt(2) is irrational
       P06     code       hard          Design a thread-safe LRU cache in Python
       P08    logic     medium  Three boxes puzzle: one has gold - find the optimal strategy
       P09    logic       hard  River crossing puzzle with wolf-goat-cabbage constraints
       P11 planning     medium  Optimize a delivery route for 5 stops minimizing distance
       P12 planning       hard  Design a microservices migration plan for a monolith app
```

GPT-4o échoue sur **tous les problèmes difficiles** plus deux problèmes de difficulté moyenne (P08, P11) qui nécessitent un raisonnement en plusieurs étapes.

```python
# What does DeepSeek R1 get wrong?
r1_fails = bench[bench["deepseek_r1_correct"] == False]
print("DeepSeek R1 failures:")
print(r1_fails[["problem_id", "category", "difficulty", "description"]].to_string(index=False))
```

**Sortie attendue :**

```
DeepSeek R1 failures:
problem_id  category difficulty                                          description
       P12  planning       hard  Design a microservices migration plan for a monolith app
```

DeepSeek R1 échoue uniquement sur P12 — le problème de planification le plus complexe nécessitant à la fois des connaissances techniques et une planification de projet en plusieurs étapes.

---

## Partie 4 : Précision par catégorie et difficulté

### Étape 4 : Décomposer la précision par catégorie

```python
# Accuracy by category
for category in bench["category"].unique():
    cat_data = bench[bench["category"] == category]
    print(f"\n{category.upper()}:")
    for model in ["gpt4o", "o3", "deepseek_r1"]:
        correct = cat_data[f"{model}_correct"].sum()
        total = len(cat_data)
        print(f"  {model:>12}: {correct}/{total}")
```

**Sortie attendue :**

```
MATH:
        gpt4o: 2/3
            o3: 3/3
   deepseek_r1: 3/3

CODE:
        gpt4o: 2/3
            o3: 3/3
   deepseek_r1: 3/3

LOGIC:
        gpt4o: 1/3
            o3: 3/3
   deepseek_r1: 3/3

PLANNING:
        gpt4o: 1/3
            o3: 3/3
   deepseek_r1: 2/3
```

```python
# Accuracy by difficulty
for diff in ["easy", "medium", "hard"]:
    diff_data = bench[bench["difficulty"] == diff]
    print(f"\n{diff.upper()}:")
    for model in ["gpt4o", "o3", "deepseek_r1"]:
        correct = diff_data[f"{model}_correct"].sum()
        total = len(diff_data)
        print(f"  {model:>12}: {correct}/{total} = {correct/total*100:.0f}%")
```

**Sortie attendue :**

```
EASY:
        gpt4o: 4/4 = 100%
            o3: 4/4 = 100%
   deepseek_r1: 4/4 = 100%

MEDIUM:
        gpt4o: 2/4 = 50%
            o3: 4/4 = 100%
   deepseek_r1: 4/4 = 100%

HARD:
        gpt4o: 0/4 = 0%
            o3: 4/4 = 100%
   deepseek_r1: 3/4 = 75%
```

!!! info "Aperçu par difficulté"
    Les trois modèles réussissent parfaitement les problèmes faciles. L'écart apparaît à la difficulté moyenne (GPT-4o chute à 50 %) et devient considérable sur les problèmes difficiles (GPT-4o : 0 %, DeepSeek R1 : 75 %, o3 : 100 %). Les modèles de raisonnement prouvent leur valeur sur les problèmes difficiles.

---

## Partie 5 : Compromis vitesse vs précision

### Étape 5 : Analyser le temps de réponse par modèle

```python
# Average time per model
for model in ["gpt4o", "o3", "deepseek_r1"]:
    avg_time = bench[f"{model}_time_sec"].mean()
    print(f"{model:>12}: {avg_time:.1f}s average")

# Time vs accuracy scatter
print("\nProblem-level detail:")
for _, row in bench.iterrows():
    print(f"  {row['problem_id']} ({row['difficulty']:>6}): "
          f"GPT-4o={row['gpt4o_time_sec']:.1f}s "
          f"o3={row['o3_time_sec']:.1f}s "
          f"R1={row['deepseek_r1_time_sec']:.1f}s")
```

**Sortie attendue :**

```
      gpt4o: 2.1s average
          o3: 7.1s average
 deepseek_r1: 5.4s average

Problem-level detail:
  P01 (  easy): GPT-4o=1.2s o3=3.5s R1=2.8s
  P02 (medium): GPT-4o=1.8s o3=4.2s R1=3.5s
  P03 (  hard): GPT-4o=2.5s o3=8.1s R1=6.5s
  ...
  P12 (  hard): GPT-4o=4.0s o3=15.0s R1=11.0s
```

!!! warning "Compromis de vitesse"
    o3 est **3,4× plus lent** que GPT-4o en moyenne (7,1s vs 2,1s). Sur le problème le plus difficile (P12), o3 prend 15 secondes — acceptable pour des tâches complexes, mais trop lent pour le chat en temps réel. Choisissez votre modèle en fonction de la complexité du problème, pas pour un déploiement universel.

---

## Partie 6 : Analyse du coût en tokens

### Étape 6 : Comparer l'utilisation des tokens

```python
# Average tokens per model
for model in ["gpt4o", "o3", "deepseek_r1"]:
    avg_tokens = bench[f"{model}_tokens"].mean()
    total_tokens = bench[f"{model}_tokens"].sum()
    print(f"{model:>12}: {avg_tokens:.0f} avg tokens, {total_tokens:,} total")

# Cost ratio (relative to GPT-4o)
gpt4o_total = bench["gpt4o_tokens"].sum()
for model in ["o3", "deepseek_r1"]:
    model_total = bench[f"{model}_tokens"].sum()
    ratio = model_total / gpt4o_total
    print(f"\n{model} uses {ratio:.1f}× more tokens than GPT-4o")
```

**Sortie attendue :**

```
      gpt4o: 287 avg tokens, 3,440 total
          o3: 878 avg tokens, 10,530 total
 deepseek_r1: 725 avg tokens, 8,700 total

o3 uses 3.1× more tokens than GPT-4o
deepseek_r1 uses 2.5× more tokens than GPT-4o
```

Les tokens supplémentaires proviennent du raisonnement par chaîne de pensée — le modèle « réfléchit à voix haute » en interne. C'est le coût d'une meilleure précision.

---

## Partie 7 : Quand utiliser chaque modèle

### Étape 7 : Cadre décisionnel

Sur la base des résultats du benchmark, voici quand utiliser chaque modèle :

| Scénario | Modèle recommandé | Pourquoi |
|----------|-------------------|----------|
| Questions-réponses simples, FAQ | **GPT-4o** | 100 % de précision sur les problèmes faciles, 3× plus rapide, 3× moins cher |
| Raisonnement en plusieurs étapes | **o3** ou **DeepSeek R1** | GPT-4o chute à 0 % sur les problèmes difficiles |
| Production sensible aux coûts | **DeepSeek R1** | 91,7 % de précision à 2,5× tokens (vs 3,1× pour o3) |
| Précision maximale requise | **o3** | 100 % de précision, mais 3,4× plus lent et 3,1× plus cher |
| Conversation en temps réel | **GPT-4o** | 2,1s en moyenne — les modèles de raisonnement sont trop lents pour le chat |
| Génération de code (complexe) | **o3** | Le code thread-safe et concurrent nécessite un raisonnement minutieux |
| Preuves mathématiques | **o3** ou **DeepSeek R1** | Les deux gèrent les preuves formelles ; GPT-4o ne le peut pas |

```python
# Summary dashboard
print("""
╔══════════════════════════════════════════════════════╗
║      Reasoning Model Benchmark — Summary             ║
╠══════════════════════════════════════════════════════╣
║  Model        Accuracy   Avg Time   Avg Tokens       ║
║  ─────────    ────────   ────────   ──────────       ║
║  GPT-4o        50.0%      2.1s        287            ║
║  o3           100.0%      7.1s        878            ║
║  DeepSeek R1   91.7%      5.4s        725            ║
╠══════════════════════════════════════════════════════╣
║  Key Insight: Use GPT-4o for simple tasks,           ║
║  reasoning models for complex multi-step problems.   ║
╚══════════════════════════════════════════════════════╝
""")
```

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-060/broken_reasoning.py` contient **3 bugs** dans les fonctions d'analyse du benchmark. Exécutez les auto-tests :

```bash
python lab-060/broken_reasoning.py
```

Vous devriez voir **3 tests échoués** :

| Test | Ce qu'il vérifie | Indice |
|------|-----------------|--------|
| Test 1 | Calcul de la précision du modèle | Quelle colonne représente la justesse — `_correct` ou `_time_sec` ? |
| Test 2 | Trouver le modèle le plus rapide | Faut-il utiliser `min` ou `max` pour trouver le plus rapide ? |
| Test 3 | Précision sur les problèmes difficiles | Quel niveau de difficulté filtrez-vous ? |

Corrigez les 3 bugs et relancez jusqu'à voir `🎉 All 3 tests passed`.

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Quand devriez-vous utiliser un modèle de raisonnement au lieu d'un modèle standard comme GPT-4o ?"

    - A) Pour toutes les tâches — les modèles de raisonnement sont toujours meilleurs
    - B) Pour les problèmes complexes en plusieurs étapes nécessitant un raisonnement logique, des preuves ou de la planification
    - C) Pour les applications de chat en temps réel où la vitesse est critique
    - D) Pour les tâches simples de FAQ et de classification

    ??? success "✅ Révéler la réponse"
        **Correct : B) Pour les problèmes complexes en plusieurs étapes nécessitant un raisonnement logique, des preuves ou de la planification**

        Les modèles de raisonnement excellent lorsque les problèmes nécessitent une décomposition en étapes, la vérification des résultats intermédiaires ou l'exploration de multiples pistes de solution. GPT-4o atteint 100 % sur les problèmes faciles — les modèles de raisonnement n'apportent aucune valeur ajoutée mais coûtent 3× plus. Réservez les modèles de raisonnement aux problèmes difficiles où l'approche en une seule passe de GPT-4o échoue.

??? question "**Q2 (Choix multiple) :** Que contrôle le « budget de réflexion » dans un modèle de raisonnement ?"

    - A) Le nombre maximum d'appels API par minute
    - B) Le coût total en dollars pour une seule requête
    - C) La quantité de raisonnement effectuée par le modèle avant de produire une réponse finale
    - D) La longueur maximale de la réponse en sortie

    ??? success "✅ Révéler la réponse"
        **Correct : C) La quantité de raisonnement effectuée par le modèle avant de produire une réponse finale**

        Le budget de réflexion contrôle la profondeur de la délibération interne du modèle. Un budget plus élevé permet au modèle d'explorer davantage de pistes de solution, de vérifier les étapes intermédiaires plus minutieusement et de revenir en arrière lorsqu'il détecte des erreurs. Cela produit des résultats plus précis mais consomme plus de tokens et prend plus de temps.

??? question "**Q3 (Exécuter le lab) :** Quelle est la précision de o3 sur le benchmark de 12 problèmes ?"

    Calculez `bench["o3_correct"].sum() / len(bench) * 100`.

    ??? success "✅ Révéler la réponse"
        **100 % (12/12)**

        o3 résout correctement les 12 problèmes dans toutes les catégories et tous les niveaux de difficulté — y compris P12 (plan de migration vers les microservices), qui est le seul problème que DeepSeek R1 échoue. Ce score parfait a un coût : o3 prend en moyenne 7,1 secondes et 878 tokens par problème.

??? question "**Q4 (Exécuter le lab) :** Quelle est la précision de GPT-4o sur le benchmark ?"

    Calculez `bench["gpt4o_correct"].sum() / len(bench) * 100`.

    ??? success "✅ Révéler la réponse"
        **50 % (6/12)**

        GPT-4o résout correctement 6 des 12 problèmes. Il réussit les 4 problèmes faciles mais échoue sur les 4 problèmes difficiles (P03, P06, P09, P12) et 2 problèmes de difficulté moyenne (P08, P11). Les échecs couvrent toutes les catégories — maths, code, logique et planification — confirmant que le problème est la profondeur du raisonnement, pas la connaissance du domaine.

??? question "**Q5 (Exécuter le lab) :** Quel modèle échoue uniquement sur le problème P12 ?"

    Vérifiez quel modèle a `_correct == False` pour exactement un problème, et ce problème est P12.

    ??? success "✅ Révéler la réponse"
        **DeepSeek R1**

        DeepSeek R1 atteint 91,7 % de précision (11/12), échouant uniquement sur P12 — « Concevoir un plan de migration vers les microservices pour une application monolithique ». C'est le problème de planification le plus difficile, nécessitant à la fois des connaissances techniques approfondies et une planification de projet complexe en plusieurs étapes. o3 le résout ; GPT-4o échoue dessus plus 5 autres problèmes.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|------------------------|
| Modèles de raisonnement | Réflexion étendue via la chaîne de pensée pour les problèmes complexes |
| Budget de réflexion | Contrôle la profondeur du raisonnement — plus de budget = plus précis mais plus lent |
| Précision | GPT-4o : 50 %, DeepSeek R1 : 91,7 %, o3 : 100 % sur un benchmark de 12 problèmes |
| Compromis de vitesse | GPT-4o : 2,1s moy., DeepSeek R1 : 5,4s, o3 : 7,1s — le raisonnement coûte du temps |
| Coût en tokens | Les modèles de raisonnement utilisent 2,5–3,1× plus de tokens que GPT-4o |
| Cadre décisionnel | Utilisez GPT-4o pour les tâches simples ; les modèles de raisonnement pour les problèmes complexes en plusieurs étapes |

---

## Prochaines étapes

- **[Lab 059](lab-059-voice-agents-realtime.md)** — Agents vocaux avec GPT Realtime API (interaction en temps réel, modalité différente)
- **[Lab 043](lab-043-multimodal-agents.md)** — Agents multimodaux avec GPT-4o Vision (une autre capacité de GPT-4o)
- **[Lab 038](lab-038-cost-optimization.md)** — Optimisation des coûts (application des compromis coût-performance de ce lab)