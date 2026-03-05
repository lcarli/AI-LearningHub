---
tags: [deep-research, multi-agent, synthesis, citations, python]
---
# Lab 079 : Agents de recherche approfondie — Synthèse de connaissances multi-étapes

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~90 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Utilise des données de trace de recherche simulées</span>
</div>

## Ce que vous apprendrez

- Comment les **agents de recherche approfondie** utilisent un pipeline multi-agents pour la synthèse de connaissances
- L'architecture **Planificateur → Chercheur → Rédacteur → Réviseur** et les responsabilités de chaque rôle
- Comment le **suivi des citations** garantit que chaque affirmation est reliée à une source
- Analyser une **trace de recherche en 14 étapes** avec les rôles d'agents, l'utilisation de tokens et les scores de qualité
- Identifier les goulots d'étranglement, la distribution des tokens et les schémas de qualité dans le pipeline

## Introduction

Les **agents de recherche approfondie** implémentent un pipeline multi-étapes pour produire des rapports de recherche complets et bien sourcés. Au lieu qu'un seul LLM génère un rapport entier, le travail est réparti entre des agents spécialisés :

### Le pipeline

```
  ┌──────────┐     ┌────────────┐     ┌──────────┐     ┌──────────┐
  │ Planner  │────►│ Researcher │────►│  Writer  │────►│ Reviewer │
  └──────────┘     └────────────┘     └──────────┘     └──────────┘
       │                 │                  │                │
  Décompose         Collecte les      Synthétise les    Révise et
  la requête        informations      résultats en      fournit un
  en sous-          des sources       rapport en        retour
  questions         avec citations    prose             d'information
```

| Agent | Rôle | Sortie clé |
|-------|------|-----------|
| **Planner** | Décompose la question de recherche en sous-questions et crée un plan de recherche | Sous-questions, stratégie de recherche |
| **Researcher** | Exécute les recherches, lit les sources, extrait les résultats clés avec citations | Résultats avec citations de sources |
| **Writer** | Synthétise les résultats en un rapport cohérent et bien structuré | Brouillon de rapport avec citations en ligne |
| **Reviewer** | Révise le brouillon pour la précision, l'exhaustivité et la qualité des citations | Retour d'information, score de qualité, approbation/révision |

### Suivi des citations

Chaque affirmation du rapport final doit être reliée à une source. Le pipeline suit :

- **sources_cited** : Nombre de sources uniques citées à chaque étape
- **quality_score** : Auto-évaluation de la qualité de la sortie par l'agent (0.0–1.0)

### Le scénario

Vous êtes un **responsable d'équipe de recherche** évaluant un système d'agent de recherche approfondie. Vous disposez d'une **trace de recherche en 14 étapes** (`research_trace.csv`) provenant d'une exécution de recherche terminée. Votre mission : analyser la trace pour comprendre le comportement des agents, l'utilisation des tokens, les schémas de qualité et identifier les opportunités d'optimisation.

!!! info "Données simulées"
    Ce lab utilise un fichier CSV de trace de recherche simulé. Les données représentent une exécution de recherche approfondie réaliste avec 14 étapes réparties sur 4 rôles d'agents, incluant la planification, la recherche multi-sources, la rédaction et la révision itérative.

## Prérequis

| Exigence | Pourquoi |
|---|---|
| Python 3.10+ | Exécuter les scripts d'analyse |
| Bibliothèque `pandas` | Manipulation des données |

```bash
pip install pandas
```

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-079/` de votre répertoire de travail.

| Fichier | Description | Téléchargement |
|------|-------------|----------|
| `broken_research.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-079/broken_research.py) |
| `research_trace.csv` | Trace de recherche en 14 étapes avec rôles d'agents, tokens et qualité | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-079/research_trace.csv) |

---

## Étape 1 : Comprendre le format de la trace

Chaque ligne de la trace représente une étape du pipeline de recherche :

| Colonne | Description |
|--------|-----------|
| **step_id** | Numéro séquentiel de l'étape (1–14) |
| **agent_role** | Quel agent a exécuté cette étape : `planner`, `researcher`, `writer`, `reviewer` |
| **action** | Ce que l'agent a fait (ex. : `decompose_query`, `search_sources`, `write_section`) |
| **tokens_used** | Nombre de tokens consommés à cette étape |
| **sources_cited** | Nombre de sources citées dans la sortie de cette étape |
| **quality_score** | Évaluation de la qualité de la sortie de cette étape (0.0–1.0) |
| **duration_sec** | Temps pris pour cette étape en secondes |

---

## Étape 2 : Charger et explorer la trace

```python
import pandas as pd

df = pd.read_csv("lab-079/research_trace.csv")

print(f"Total steps: {len(df)}")
print(f"Agent roles: {df['agent_role'].value_counts().to_dict()}")
print(f"Total tokens: {df['tokens_used'].sum():,}")
print(f"Total sources cited: {df['sources_cited'].sum()}")
print(f"\nFull trace:")
print(df[["step_id", "agent_role", "action", "tokens_used", "sources_cited", "quality_score"]].to_string(index=False))
```

**Sortie attendue :**

```
Total steps: 14
Agent roles: {'researcher': 6, 'writer': 4, 'reviewer': 2, 'planner': 2}
Total tokens: varies
Total sources cited: 10
```

---

## Étape 3 : Analyser l'utilisation des tokens par agent

```python
print("Token usage by agent role:\n")
for role, group in df.groupby("agent_role"):
    total_tokens = group["tokens_used"].sum()
    avg_tokens = group["tokens_used"].mean()
    steps = len(group)
    print(f"  {role:>12s}: {total_tokens:>7,} tokens across {steps} steps (avg {avg_tokens:,.0f}/step)")

print(f"\nTotal tokens: {df['tokens_used'].sum():,}")
```

```python
# Token share by agent
total_tokens = df["tokens_used"].sum()
print("\nToken distribution:")
for role, group in df.groupby("agent_role"):
    share = group["tokens_used"].sum() / total_tokens * 100
    bar = "█" * int(share / 2)
    print(f"  {role:>12s}: {share:>5.1f}% {bar}")
```

!!! tip "Piste d'optimisation"
    Le **Researcher** consomme généralement le plus de tokens car il traite plusieurs sources par sous-question. Pour réduire les coûts, envisagez de mettre en cache les extractions de sources et de limiter le nombre de sources par sous-question.

---

## Étape 4 : Analyser le flux de citations

```python
print("Citation flow through the pipeline:\n")
for _, row in df.iterrows():
    cited = "📚" * row["sources_cited"] if row["sources_cited"] > 0 else "—"
    print(f"  Step {row['step_id']:>2}: [{row['agent_role']:>10s}] {row['action']:<25s} sources={row['sources_cited']}  {cited}")

total_sources = df["sources_cited"].sum()
print(f"\nTotal sources cited across all steps: {total_sources}")

# Sources by agent role
print("\nSources cited by role:")
for role, group in df.groupby("agent_role"):
    print(f"  {role:>12s}: {group['sources_cited'].sum()} sources")
```

---

## Étape 5 : Analyse de la qualité

```python
print("Quality scores by agent role:\n")
for role, group in df.groupby("agent_role"):
    avg_q = group["quality_score"].mean()
    min_q = group["quality_score"].min()
    max_q = group["quality_score"].max()
    print(f"  {role:>12s}: avg={avg_q:.2f}  min={min_q:.2f}  max={max_q:.2f}")

# Find the lowest-quality step
worst_step = df.loc[df["quality_score"].idxmin()]
print(f"\nLowest quality step:")
print(f"  Step {worst_step['step_id']}: [{worst_step['agent_role']}] {worst_step['action']}")
print(f"  Quality: {worst_step['quality_score']}")
print(f"  Tokens: {worst_step['tokens_used']}")

# Find the highest-quality step
best_step = df.loc[df["quality_score"].idxmax()]
print(f"\nHighest quality step:")
print(f"  Step {best_step['step_id']}: [{best_step['agent_role']}] {best_step['action']}")
print(f"  Quality: {best_step['quality_score']}")
```

!!! warning "Variance de qualité"
    Surveillez les **baisses de qualité dans les étapes Researcher ultérieures** — cela indique souvent un épuisement des sources (l'agent trouve des sources de moindre qualité pour les sous-questions plus difficiles). Envisagez d'ajouter un seuil de qualité qui déclenche une nouvelle recherche avec des requêtes alternatives.

---

## Étape 6 : Construire le rapport d'analyse de recherche

```python
writer_tokens = df[df["agent_role"] == "writer"]["tokens_used"].sum()
researcher_steps = len(df[df["agent_role"] == "researcher"])
total_duration = df["duration_sec"].sum()

report = f"""# 📋 Deep Research Trace Analysis

## Pipeline Summary
| Metric | Value |
|--------|-------|
| Total Steps | {len(df)} |
| Total Tokens | {df['tokens_used'].sum():,} |
| Total Sources Cited | {total_sources} |
| Total Duration | {total_duration:.0f}s ({total_duration/60:.1f} min) |
| Avg Quality | {df['quality_score'].mean():.2f} |

## Agent Breakdown
| Role | Steps | Tokens | Sources | Avg Quality |
|------|-------|--------|---------|-------------|
"""

for role in ["planner", "researcher", "writer", "reviewer"]:
    group = df[df["agent_role"] == role]
    report += f"| {role} | {len(group)} | {group['tokens_used'].sum():,} | {group['sources_cited'].sum()} | {group['quality_score'].mean():.2f} |\n"

report += f"""
## Key Findings
- **Researcher** executed {researcher_steps} steps — the most of any agent role
- **Writer** consumed {writer_tokens:,} tokens for synthesis
- **Total sources cited**: {total_sources} across the pipeline
- **Quality** {'improved' if df.iloc[-1]['quality_score'] > df.iloc[0]['quality_score'] else 'varied'} through the pipeline

## Optimization Recommendations
1. **Cache source extractions** to reduce Researcher token usage
2. **Parallelize sub-question research** — steps are independent
3. **Add quality gates** between pipeline stages
4. **Limit sources per sub-question** to top-3 most relevant
"""

print(report)

with open("lab-079/research_analysis.md", "w") as f:
    f.write(report)
print("💾 Saved to lab-079/research_analysis.md")
```

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-079/broken_research.py` contient **3 bugs** qui produisent une analyse de recherche incorrecte. Pouvez-vous les trouver et les corriger tous ?

Exécutez les auto-tests pour voir lesquels échouent :

```bash
python lab-079/broken_research.py
```

Vous devriez voir **3 tests échoués**. Chaque test correspond à un bug :

| Test | Ce qu'il vérifie | Indice |
|------|---------------|------|
| Test 1 | Total des sources citées | Devrait sommer `sources_cited`, pas compter les lignes |
| Test 2 | Nombre de tokens du Writer | Devrait filtrer `agent_role == "writer"`, pas `"researcher"` |
| Test 3 | Nombre d'étapes du Researcher | Devrait compter les lignes où `agent_role == "researcher"`, pas sommer les tokens |

Corrigez les 3 bugs, puis relancez. Quand vous voyez `All passed!`, c'est terminé !

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Quel est le principal avantage d'un pipeline multi-agents par rapport à une approche LLM unique pour la recherche ?"

    - A) Il utilise moins de tokens au total
    - B) Chaque agent se spécialise dans une tâche, permettant une meilleure qualité et traçabilité
    - C) Il ne nécessite qu'un seul déploiement de modèle
    - D) Il élimine le besoin de citations

    ??? success "✅ Révéler la réponse"
        **Correct : B) Chaque agent se spécialise dans une tâche, permettant une meilleure qualité et traçabilité**

        En divisant la recherche en planification, recherche, rédaction et révision, chaque agent peut être optimisé pour sa tâche spécifique. Le Researcher peut se concentrer sur la qualité des sources, le Writer sur la cohérence de la prose, et le Reviewer sur la précision factuelle. Cette spécialisation produit généralement une sortie de meilleure qualité qu'une génération unique de bout en bout.

??? question "**Q2 (Choix multiple) :** Pourquoi le suivi des citations est-il important dans les agents de recherche approfondie ?"

    - A) Il réduit l'utilisation des tokens
    - B) Il garantit que chaque affirmation est reliée à une source, permettant la vérification et la confiance
    - C) Il rend le rapport plus long
    - D) Il est exigé par les conditions d'utilisation du LLM

    ??? success "✅ Révéler la réponse"
        **Correct : B) Il garantit que chaque affirmation est reliée à une source, permettant la vérification et la confiance**

        Le suivi des citations crée une chaîne auditable de chaque affirmation du rapport final jusqu'à sa source. Cela permet aux réviseurs de vérifier la précision factuelle, aux utilisateurs d'explorer les sources primaires et aux organisations de maintenir l'intégrité de la recherche — critique pour les applications à enjeux élevés comme la recherche juridique, médicale ou financière.

??? question "**Q3 (Exécutez le lab) :** Quel est le nombre total de sources citées dans toutes les étapes ?"

    Exécutez l'analyse de l'étape 4 sur [📥 `research_trace.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-079/research_trace.csv) et sommez la colonne `sources_cited`.

    ??? success "✅ Révéler la réponse"
        **10 sources**

        La somme de toutes les valeurs `sources_cited` sur les 14 étapes est de **10**. La plupart des sources sont citées pendant les étapes du Researcher, avec quelques citations supplémentaires ajoutées lors de la synthèse du Writer.

??? question "**Q4 (Exécutez le lab) :** Combien de tokens au total l'agent Writer a-t-il consommé ?"

    Exécutez l'analyse de l'étape 3 et trouvez le total de tokens pour le rôle `writer`.

    ??? success "✅ Révéler la réponse"
        **Somme de `tokens_used` où `agent_role == "writer"`**

        Le total de tokens du Writer inclut toutes les étapes d'écriture et de synthèse. Filtrez la trace pour `agent_role == "writer"` et sommez la colonne `tokens_used` pour obtenir la valeur exacte.

??? question "**Q5 (Exécutez le lab) :** Combien d'étapes l'agent Researcher a-t-il exécuté ?"

    Comptez les lignes où `agent_role == "researcher"`.

    ??? success "✅ Révéler la réponse"
        **6 étapes**

        Le Researcher a exécuté **6 étapes** — le plus de tous les rôles d'agents. C'est logique car le Researcher traite plusieurs sous-questions du Planner, chaque sous-question pouvant nécessiter plusieurs étapes de recherche et d'extraction.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|-----------------|
| Agents de recherche approfondie | Pipeline multi-agents pour la synthèse de connaissances avec suivi des citations |
| Architecture du pipeline | Planner → Researcher → Writer → Reviewer avec des rôles spécialisés |
| Suivi des citations | Chaque affirmation est reliée à une source dans tout le pipeline |
| Distribution des tokens | Le Researcher utilise le plus de tokens ; le Writer synthétise ; le Reviewer valide |
| Schémas de qualité | La qualité varie selon les étapes — les étapes de recherche ultérieures peuvent montrer un épuisement des sources |
| Optimisation | Mettre en cache les sources, paralléliser la recherche, ajouter des portes de qualité |

---

## Prochaines étapes

- **[Lab 034](lab-034-multi-agent-sk.md)** — Multi-Agent avec Semantic Kernel (construire les agents eux-mêmes)
- **[Lab 067](lab-067-graphrag.md)** — GraphRAG (enrichir la recherche avec la récupération par graphe de connaissances)
- **[Lab 033](lab-033-agent-observability.md)** — Observabilité des agents (surveiller les pipelines de recherche approfondie en production)
- **[Lab 076](lab-076-microsoft-agent-framework.md)** — Microsoft Agent Framework (implémenter les pipelines avec les Graph Workflows de MAF)
