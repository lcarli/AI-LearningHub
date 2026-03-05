---
tags: [slm, phi-4, onnx, privacy, local-inference, python]
---
# Lab 061 : SLM — Phi-4 Mini pour des compétences d'agent à faible coût

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~60 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Utilise des données de benchmark simulées (aucune clé API requise)</span>
</div>

## Ce que vous apprendrez

- Comment les **Small Language Models (SLM)** comme Phi-4 Mini se comparent aux modèles de pointe comme GPT-4o
- Quand les SLM offrent un meilleur compromis : **faible latence, confidentialité et zéro coût cloud**
- Exécuter une inférence **ONNX Runtime** localement pour des compétences d'agent (classifier, extraire, résumer, router, rédiger)
- Analyser un **benchmark de 15 tâches** comparant Phi-4 Mini vs GPT-4o sur la précision, la latence et le coût
- Identifier quels types de tâches les SLM gèrent bien — et où ils échouent
- Appliquer une stratégie d'**inférence axée sur la confidentialité** pour les charges de travail sensibles

---

## Introduction

Les modèles de pointe comme GPT-4o offrent une qualité exceptionnelle, mais ils impliquent des compromis en termes de latence, de coût et de confidentialité. Les **Small Language Models (SLM)** comme Phi-4 Mini s'exécutent localement via ONNX Runtime, offrant une latence considérablement plus faible, zéro coût cloud et une confidentialité totale des données — vos données ne quittent jamais l'appareil.

La question n'est pas « quel modèle est meilleur » — mais « quelles tâches un SLM peut-il gérer tout aussi bien ? » Ce lab utilise un benchmark de 15 tâches pour trouver la réponse.

### Le benchmark

Vous comparerez **Phi-4 Mini (local)** vs **GPT-4o (cloud)** sur **15 tâches** réparties en 5 catégories :

| Catégorie | Nombre | Exemple |
|-----------|--------|---------|
| **Classifier** | 3 | Analyse de sentiment, détection d'intention, étiquetage de sujet |
| **Extraire** | 3 | Extraction d'entités, analyse clé-valeur, normalisation de dates |
| **Résumer** | 3 | Notes de réunion, résumé d'article, résumé de ticket de support |
| **Router** | 3 | Routage de tickets, décision d'escalade, attribution de file d'attente |
| **Rédiger** | 3 | Réponse par e-mail, paragraphe de rapport, description de produit |

---

## Prérequis

```bash
pip install pandas
```

Ce lab analyse des résultats de benchmark pré-calculés — aucune clé API, GPU ou installation d'ONNX Runtime requise. Pour exécuter une inférence en direct, vous auriez besoin d'ONNX Runtime et du modèle Phi-4 Mini ONNX.

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-061/` dans votre répertoire de travail.

| Fichier | Description | Télécharger |
|---------|-------------|-------------|
| `broken_slm.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-061/broken_slm.py) |
| `slm_benchmark.csv` | Jeu de données de benchmark | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-061/slm_benchmark.csv) |

---

## Partie 1 : Comprendre les SLM

### Étape 1 : SLM vs modèles de pointe

Les SLM sont des modèles compacts (généralement 1 à 4 milliards de paramètres) optimisés pour des modèles de tâches spécifiques. Ils échangent la polyvalence contre l'efficacité :

```
Frontier Model (GPT-4o):
  Cloud API → [Large model] → High accuracy, high latency, per-token cost

Small Language Model (Phi-4 Mini):
  Local ONNX → [Compact model] → Good accuracy, very low latency, zero cost
```

Concepts clés :

| Concept | Description |
|---------|-------------|
| **SLM** | Small Language Model — modèle compact optimisé pour des tâches spécifiques |
| **ONNX Runtime** | Moteur d'inférence multiplateforme pour exécuter des modèles localement |
| **Inférence axée sur la confidentialité** | Les données ne quittent jamais l'appareil — essentiel pour les données personnelles, la santé, la finance |
| **Routage de tâches** | Diriger les tâches simples vers les SLM et les tâches complexes vers les modèles de pointe |

!!! info "Quand envisager les SLM"
    Les SLM excellent dans les tâches bien définies et contraintes comme la classification, l'extraction et le routage. Ils peinent avec les tâches créatives ouvertes qui nécessitent une large connaissance du monde. L'architecture idéale route chaque tâche vers le modèle de la bonne taille.

---

## Partie 2 : Charger les données du benchmark

### Étape 2 : Charger [📥 `slm_benchmark.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-061/slm_benchmark.csv)

Le jeu de données de benchmark contient les résultats de l'exécution des 15 tâches à travers les deux modèles :

```python
# slm_analysis.py
import pandas as pd

bench = pd.read_csv("lab-061/slm_benchmark.csv")

print(f"Tasks: {len(bench)}")
print(f"Categories: {bench['category'].unique().tolist()}")
print(bench[["task_id", "category", "description"]].to_string(index=False))
```

**Sortie attendue :**

```
Tasks: 15
Categories: ['classify', 'extract', 'summarize', 'route', 'draft']

task_id  category                          description
    T01  classify                   Sentiment analysis
    T02  classify                     Intent detection
    T03  classify                        Topic tagging
    T04   extract                  Entity extraction
    T05   extract                  Key-value parsing
    T06   extract                Date normalization
    T07 summarize                     Meeting notes
    T08 summarize                    Article digest
    T09 summarize            Support ticket summary
    T10     draft                       Email reply
    T11     draft                  Report paragraph
    T12     draft              Product description
    T13     route                   Ticket routing
    T14 summarize       Compliance document summary
    T15     route              Escalation decision
```

---

## Partie 3 : Comparaison de la précision

### Étape 3 : Calculer la précision pour chaque modèle

```python
# Overall accuracy
for model in ["phi4_mini", "gpt4o"]:
    correct = bench[f"{model}_correct"].sum()
    total = len(bench)
    print(f"{model:>10}: {correct}/{total} = {correct/total*100:.0f}%")
```

**Sortie attendue :**

```
 phi4_mini: 12/15 = 80%
     gpt4o: 15/15 = 100%
```

!!! warning "Constat clé"
    Phi-4 Mini atteint 80 % de précision — solide pour la plupart des tâches d'agent. GPT-4o réussit tout, mais avec une latence et un coût bien plus élevés. Les 3 tâches échouées par Phi-4 Mini révèlent les limites des SLM.

```python
# Which tasks does Phi-4 Mini get wrong?
phi4_fails = bench[bench["phi4_mini_correct"] == False]
print("Phi-4 Mini failures:")
print(phi4_fails[["task_id", "category", "description"]].to_string(index=False))
```

**Sortie attendue :**

```
Phi-4 Mini failures:
task_id  category                    description
    T10     draft                     Email reply
    T11     draft                Report paragraph
    T14 summarize  Compliance document summary
```

Phi-4 Mini échoue sur **2 tâches de rédaction** (T10, T11) et **1 tâche de résumé** (T14). Les tâches de rédaction nécessitent une écriture créative et nuancée — exactement là où les SLM peinent. T14 est un document de conformité complexe qui dépasse la capacité de contexte du modèle.

---

## Partie 4 : Comparaison de la latence

### Étape 4 : Comparer la latence d'inférence

```python
# Average latency per model
for model in ["phi4_mini", "gpt4o"]:
    avg_ms = bench[f"{model}_latency_ms"].mean()
    print(f"{model:>10}: {avg_ms:.1f}ms average")

# Speedup
phi4_avg = bench["phi4_mini_latency_ms"].mean()
gpt4o_avg = bench["gpt4o_latency_ms"].mean()
speedup = gpt4o_avg / phi4_avg
print(f"\nPhi-4 Mini is {speedup:.0f}× faster than GPT-4o")
```

**Sortie attendue :**

```
 phi4_mini: 82.3ms average
     gpt4o: 996.7ms average

Phi-4 Mini is 12× faster than GPT-4o
```

!!! info "Avantage de latence"
    Phi-4 Mini s'exécute localement via ONNX Runtime à 82,3ms en moyenne — **12× plus rapide** que l'aller-retour cloud de GPT-4o d'environ 1 seconde. Pour les compétences d'agent qui s'exécutent de manière répétée (classification, routage), cette différence de latence se compose de façon considérable.

```python
# Per-task latency comparison
print("\nPer-task latency:")
for _, row in bench.iterrows():
    print(f"  {row['task_id']} ({row['category']:>9}): "
          f"Phi-4={row['phi4_mini_latency_ms']:.0f}ms  "
          f"GPT-4o={row['gpt4o_latency_ms']:.0f}ms")
```

---

## Partie 5 : Analyse des coûts

### Étape 5 : Calculer le coût cloud évité

```python
# Total cloud cost for GPT-4o
total_cost = bench["gpt4o_cost_usd"].sum()
print(f"Total GPT-4o cloud cost: ${total_cost:.4f}")
print(f"Phi-4 Mini local cost:   $0.0000")
print(f"Cost avoided by using SLM: ${total_cost:.4f}")

# Cost per category
print("\nCost by category:")
for cat in bench["category"].unique():
    cat_cost = bench[bench["category"] == cat]["gpt4o_cost_usd"].sum()
    print(f"  {cat:>9}: ${cat_cost:.4f}")
```

**Sortie attendue :**

```
Total GPT-4o cloud cost: $0.0121
Phi-4 Mini local cost:   $0.0000
Cost avoided by using SLM: $0.0121

Cost by category:
  classify: $0.0018
   extract: $0.0021
 summarize: $0.0035
     route: $0.0015
     draft: $0.0032
```

Bien que 0,0121 $ semble faible pour 15 tâches, à grande échelle (des milliers d'invocations d'agent par jour), les économies s'accumulent rapidement — et l'avantage en matière de confidentialité est inestimable pour les données sensibles.

---

## Partie 6 : Stratégie de routage des tâches

### Étape 6 : Construire une décision de routage

Sur la base du benchmark, la stratégie optimale route les tâches par catégorie :

| Catégorie | Modèle recommandé | Pourquoi |
|-----------|-------------------|----------|
| **Classifier** | Phi-4 Mini | 100 % de précision, 12× plus rapide, zéro coût |
| **Extraire** | Phi-4 Mini | 100 % de précision, 12× plus rapide, zéro coût |
| **Router** | Phi-4 Mini | 100 % de précision, 12× plus rapide, zéro coût |
| **Résumer** | Phi-4 Mini (avec repli) | 2/3 correct ; repli vers GPT-4o pour les documents complexes |
| **Rédiger** | GPT-4o | Le SLM échoue en écriture créative — utilisez un modèle de pointe |

```python
# Summary dashboard
print("""
╔══════════════════════════════════════════════════════╗
║     SLM Benchmark — Phi-4 Mini vs GPT-4o            ║
╠══════════════════════════════════════════════════════╣
║  Metric              Phi-4 Mini     GPT-4o          ║
║  ─────────────       ──────────     ──────          ║
║  Accuracy              80%          100%            ║
║  Avg Latency           82.3ms       996.7ms         ║
║  Speedup               12×          baseline        ║
║  Cloud Cost             $0           $0.0121        ║
║  Privacy                Full         Data leaves    ║
╠══════════════════════════════════════════════════════╣
║  Route: classify/extract/route → SLM                ║
║  Route: draft → frontier model                      ║
║  Route: summarize → SLM with fallback               ║
╚══════════════════════════════════════════════════════╝
""")
```

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-061/broken_slm.py` contient **3 bugs** dans les fonctions d'analyse SLM. Exécutez les auto-tests :

```bash
python lab-061/broken_slm.py
```

Vous devriez voir **3 tests échoués** :

| Test | Ce qu'il vérifie | Indice |
|------|-----------------|--------|
| Test 1 | Calcul de la précision | Quelle colonne représente la justesse — `_correct` ou `_latency_ms` ? |
| Test 2 | Calcul du coût | Additionnez-vous `_tokens` ou `_cost_usd` ? |
| Test 3 | Filtrage des tâches échouées | Filtrez-vous par `category == "draft"` ou manquez-vous le filtre entièrement ? |

Corrigez les 3 bugs et relancez jusqu'à voir `🎉 All 3 tests passed`.

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Quels sont les principaux avantages d'utiliser un SLM comme Phi-4 Mini par rapport à un modèle de pointe comme GPT-4o ?"

    - A) Une meilleure précision sur tous les types de tâches
    - B) Faible latence, confidentialité des données et zéro coût cloud
    - C) Meilleure écriture créative et résumé
    - D) Fenêtre de contexte plus grande et plus de paramètres

    ??? success "✅ Révéler la réponse"
        **Correct : B) Faible latence, confidentialité des données et zéro coût cloud**

        Les SLM s'exécutent localement via ONNX Runtime, offrant une latence 12× inférieure (82,3ms vs 996,7ms), gardant toutes les données sur l'appareil pour une confidentialité totale et éliminant les coûts cloud par token. Ils ne battent pas les modèles de pointe en précision (80 % vs 100 %), mais pour les tâches bien définies comme la classification, l'extraction et le routage, la précision est suffisante et les avantages opérationnels sont significatifs.

??? question "**Q2 (Choix multiple) :** Quand ne devriez-vous PAS utiliser un SLM comme Phi-4 Mini ?"

    - A) Pour la classification de sentiment
    - B) Pour l'extraction d'entités
    - C) Pour les tâches d'écriture créative complexes
    - D) Pour le routage de tickets

    ??? success "✅ Révéler la réponse"
        **Correct : C) Pour les tâches d'écriture créative complexes**

        Le benchmark montre que Phi-4 Mini échoue sur les deux tâches de rédaction (T10 : réponse par e-mail, T11 : paragraphe de rapport). L'écriture créative nécessite une génération de langage nuancée, une large connaissance du monde et une flexibilité stylistique — des domaines où les SLM manquent de la capacité des modèles de pointe. Les tâches de classification, d'extraction et de routage sont bien adaptées aux SLM.

??? question "**Q3 (Exécuter le lab) :** Quelle est la précision de Phi-4 Mini sur le benchmark de 15 tâches ?"

    Calculez `bench["phi4_mini_correct"].sum() / len(bench) * 100`.

    ??? success "✅ Révéler la réponse"
        **80 % (12/15)**

        Phi-4 Mini gère correctement 12 des 15 tâches. Il atteint 100 % de précision sur les tâches de classification (3/3), d'extraction (3/3) et de routage (3/3), mais échoue sur 2 tâches de rédaction (T10, T11) et 1 tâche de résumé complexe (T14). Cette précision de 80 % est suffisante pour une architecture de routage de tâches où seules les tâches appropriées sont envoyées au SLM.

??? question "**Q4 (Exécuter le lab) :** Combien de fois Phi-4 Mini est-il plus rapide que GPT-4o ?"

    Calculez `bench["gpt4o_latency_ms"].mean() / bench["phi4_mini_latency_ms"].mean()`.

    ??? success "✅ Révéler la réponse"
        **~12× plus rapide**

        Phi-4 Mini prend en moyenne 82,3ms par tâche via l'inférence locale ONNX Runtime, tandis que GPT-4o prend en moyenne 996,7ms incluant l'aller-retour cloud. Le ratio est 996,7 / 82,3 ≈ 12×. Pour les pipelines d'agents qui exécutent de nombreuses compétences séquentiellement, cette réduction de latence se compose — un pipeline d'agent en 10 étapes passe d'environ 10 secondes à moins d'1 seconde.

??? question "**Q5 (Exécuter le lab) :** Quel coût cloud total est évité en utilisant Phi-4 Mini pour les 15 tâches ?"

    Calculez `bench["gpt4o_cost_usd"].sum()`.

    ??? success "✅ Révéler la réponse"
        **0,0121 $**

        Le coût cloud total de GPT-4o sur les 15 tâches est de 0,0121 $. Bien que cela semble faible, cela évolue linéairement — 10 000 invocations par jour coûteraient environ 8 $/jour ou environ 240 $/mois. Avec Phi-4 Mini s'exécutant localement, le coût cloud est exactement de 0 $. La vraie valeur est souvent la confidentialité plutôt que le coût : pour les charges de travail dans la santé, la finance et le juridique, garder les données sur l'appareil peut être une exigence de conformité.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|------------------------|
| SLM | Modèles compacts optimisés pour des tâches spécifiques — rapides, privés, gratuits |
| Phi-4 Mini | 80 % de précision sur un benchmark de 15 tâches, 12× plus rapide que GPT-4o |
| ONNX Runtime | Moteur d'inférence local — pas de dépendance cloud |
| Routage de tâches | Router classifier/extraire/router vers le SLM ; rédiger vers le modèle de pointe |
| Confidentialité | L'inférence SLM garde toutes les données sur l'appareil — essentiel pour les charges de travail sensibles |
| Coût | 0,0121 $ de coût cloud évité pour 15 tâches ; se compose à grande échelle |

---

## Prochaines étapes

- **[Lab 062](lab-062-ondevice-phi-silica.md)** — Agents sur appareil avec Phi Silica (inférence sur appareil accélérée par NPU)
- **[Lab 060](lab-060-reasoning-models.md)** — Modèles de raisonnement (quand vous avez besoin d'une précision maximale plutôt que de la vitesse)
- **[Lab 044](lab-044-phi4-ollama-production.md)** — Phi-4 avec Ollama en production (déploiement local alternatif)