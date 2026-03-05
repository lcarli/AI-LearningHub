---
tags: [agent-framework, semantic-kernel, autogen, migration, python, dotnet]
---
# Lab 076 : Microsoft Agent Framework — De SK à MAF

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~75 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Utilise des données de migration simulées</span>
</div>

## Ce que vous apprendrez

- Comment **Semantic Kernel** et **AutoGen** sont unifiés dans le **Microsoft Agent Framework (MAF)**
- Ce que sont les **Agent Skills** (packages de compétences portables `.md`) et comment ils permettent la réutilisation
- Comment les **Graph Workflows** (DAG avec points de contrôle) remplacent les pipelines linéaires
- Analyser une **matrice de migration** comparant 15 fonctionnalités entre SK, AutoGen et MAF
- Identifier les niveaux d'effort de migration et les fonctionnalités exclusives à MAF

## Introduction

Le **Microsoft Agent Framework (MAF)** unifie Semantic Kernel et AutoGen en une seule plateforme cohérente pour la création d'agents IA. Publié en tant que **Release Candidate en février 2026**, MAF réunit le meilleur des deux mondes :

- Le système de plugins, les planificateurs et les connecteurs d'entreprise de **Semantic Kernel**
- Les conversations multi-agents, l'exécution de code et les modèles de discussion de groupe d'**AutoGen**

### Installation

```bash
pip install agent-framework
```

### Concepts clés

| Concept | Description |
|---------|------------|
| **Agent Skills** | Packages de compétences portables `.md` qui définissent les capacités, entrées, sorties et dépendances d'un agent — partageables entre équipes et projets |
| **Graph Workflows** | Orchestration basée sur des DAG avec points de contrôle, réessais et embranchements — remplaçant les pipelines linéaires |
| **DevUI** | Interface de développement intégrée pour déboguer les conversations d'agents, inspecter l'exécution des compétences et visualiser les workflows |
| **Unified API** | Surface d'API unique qui remplace le `Kernel` de SK et l'`AssistantAgent` d'AutoGen par une classe commune `Agent` |

### Le scénario

Vous êtes un **ingénieur de plateforme** dans une entreprise qui a créé des agents avec Semantic Kernel et AutoGen. La direction a décidé de migrer vers MAF. Vous disposez d'une **matrice de migration** (`migration_matrix.csv`) qui associe 15 fonctionnalités entre les trois frameworks — en suivant la disponibilité, l'effort de migration et les fonctionnalités exclusives à MAF.

Votre mission : analyser la matrice, identifier les gains rapides, signaler les défis et construire un plan de migration.

!!! info "Données simulées"
    Ce lab utilise un fichier CSV de matrice de migration simulé. Les données reflètent la correspondance réelle des fonctionnalités entre Semantic Kernel, AutoGen et MAF, telle que documentée dans les guides de migration.

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
    Enregistrez tous les fichiers dans un dossier `lab-076/` de votre répertoire de travail.

| Fichier | Description | Téléchargement |
|------|-------------|----------|
| `broken_migration.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-076/broken_migration.py) |
| `migration_matrix.csv` | Comparaison de 15 fonctionnalités : SK vs AutoGen vs MAF | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-076/migration_matrix.csv) |

---

## Étape 1 : Comprendre la matrice de migration

La matrice de migration associe 15 fonctionnalités entre trois frameworks. Chaque ligne représente une capacité :

| Colonne | Description |
|--------|-----------|
| **feature** | La capacité comparée (ex. : `plugins`, `multi_agent_chat`) |
| **sk_support** | Si Semantic Kernel prend en charge cette fonctionnalité : `yes`, `partial` ou `no` |
| **autogen_support** | Si AutoGen prend en charge cette fonctionnalité : `yes`, `partial` ou `no` |
| **maf_support** | Si MAF prend en charge cette fonctionnalité : `yes`, `partial` ou `no` |
| **migration_effort** | Effort de migration de SK/AutoGen vers MAF : `low`, `medium` ou `high` |
| **category** | Catégorie de la fonctionnalité : `core`, `orchestration`, `tooling` ou `integration` |

---

## Étape 2 : Charger et explorer la matrice

```python
import pandas as pd

df = pd.read_csv("lab-076/migration_matrix.csv")

print(f"Total features: {len(df)}")
print(f"Categories: {df['category'].value_counts().to_dict()}")
print(f"Migration effort: {df['migration_effort'].value_counts().to_dict()}")
print(f"\nFull matrix:")
print(df[["feature", "sk_support", "autogen_support", "maf_support", "migration_effort"]].to_string(index=False))
```

**Sortie attendue :**

```
Total features: 15
Categories: {'core': 5, 'orchestration': 4, 'tooling': 3, 'integration': 3}
Migration effort: {'low': 7, 'medium': 5, 'high': 3}
```

---

## Étape 3 : Identifier les gains rapides (effort de migration faible)

Les fonctionnalités avec un effort de migration `low` sont vos gains rapides — commencez par celles-ci :

```python
low_effort = df[df["migration_effort"] == "low"]
print(f"Quick wins (low effort): {len(low_effort)} features\n")
for _, row in low_effort.iterrows():
    print(f"  {row['feature']:>25s}  SK={row['sk_support']:<8s} AutoGen={row['autogen_support']:<8s} MAF={row['maf_support']}")
```

!!! tip "Stratégie de migration"
    **Commencez par les fonctionnalités à faible effort** pour renforcer la confiance de l'équipe et démontrer l'API unifiée de MAF. Celles-ci ont généralement des équivalents directs dans SK ou AutoGen, ce qui rend la migration simple.

---

## Étape 4 : Trouver les fonctionnalités exclusives à MAF

Quelles fonctionnalités existent dans MAF mais pas dans Semantic Kernel ?

```python
maf_only_vs_sk = df[(df["maf_support"] == "yes") & (df["sk_support"] == "no")]
print(f"Features in MAF but NOT in SK: {len(maf_only_vs_sk)}\n")
for _, row in maf_only_vs_sk.iterrows():
    print(f"  {row['feature']:>25s}  category={row['category']}")
```

```python
# Features exclusive to MAF (not in SK AND not in AutoGen)
maf_exclusive = df[(df["maf_support"] == "yes") & (df["sk_support"] == "no") & (df["autogen_support"] == "no")]
print(f"\nMAF-exclusive features (not in SK or AutoGen): {len(maf_exclusive)}")
for _, row in maf_exclusive.iterrows():
    print(f"  {row['feature']}: {row['category']}")
```

---

## Étape 5 : Analyser les migrations à effort élevé

Ces fonctionnalités nécessitent le plus de planification :

```python
high_effort = df[df["migration_effort"] == "high"]
print(f"High-effort migrations: {len(high_effort)}\n")
for _, row in high_effort.iterrows():
    print(f"  {row['feature']}")
    print(f"    SK: {row['sk_support']}, AutoGen: {row['autogen_support']}, MAF: {row['maf_support']}")
    print(f"    Category: {row['category']}")
    print()
```

!!! warning "Risque de migration"
    Les fonctionnalités à effort élevé impliquent souvent des **changements architecturaux** — par exemple, remplacer l'orchestration personnalisée par des Graph Workflows ou convertir des plugins propriétaires en Agent Skills. Prévoyez 2 à 4 semaines par fonctionnalité à effort élevé.

---

## Étape 6 : Construire le plan de migration

```python
report = f"""# 📋 MAF Migration Plan

## Matrix Summary
| Metric | Value |
|--------|-------|
| Total Features | {len(df)} |
| Low Effort | {len(df[df['migration_effort'] == 'low'])} |
| Medium Effort | {len(df[df['migration_effort'] == 'medium'])} |
| High Effort | {len(df[df['migration_effort'] == 'high'])} |
| MAF-only (vs SK) | {len(maf_only_vs_sk)} |

## Phase 1: Quick Wins (Weeks 1–2)
Migrate {len(low_effort)} low-effort features:
"""
for _, row in low_effort.iterrows():
    report += f"- {row['feature']} ({row['category']})\n"

report += f"""
## Phase 2: Medium Effort (Weeks 3–5)
Migrate {len(df[df['migration_effort'] == 'medium'])} medium-effort features with dedicated sprint time.

## Phase 3: High Effort (Weeks 6–10)
Migrate {len(high_effort)} high-effort features requiring architectural changes.

## New Capabilities Unlocked
MAF-exclusive features not available in SK or AutoGen:
"""
for _, row in maf_exclusive.iterrows():
    report += f"- **{row['feature']}** ({row['category']})\n"

print(report)

with open("lab-076/migration_plan.md", "w") as f:
    f.write(report)
print("💾 Saved to lab-076/migration_plan.md")
```

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-076/broken_migration.py` contient **3 bugs** qui produisent une analyse de migration incorrecte. Pouvez-vous les trouver et les corriger tous ?

Exécutez les auto-tests pour voir lesquels échouent :

```bash
python lab-076/broken_migration.py
```

Vous devriez voir **3 tests échoués**. Chaque test correspond à un bug :

| Test | Ce qu'il vérifie | Indice |
|------|---------------|------|
| Test 1 | Nombre de fonctionnalités à faible effort | Devrait filtrer `migration_effort == "low"`, pas `"high"` |
| Test 2 | Nombre de fonctionnalités MAF uniquement vs SK | Devrait vérifier `sk_support == "no"`, pas `"yes"` |
| Test 3 | Nombre total de fonctionnalités | Devrait utiliser `len(df)`, pas `len(df.columns)` |

Corrigez les 3 bugs, puis relancez. Quand vous voyez `All passed!`, c'est terminé !

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Qu'est-ce que le Microsoft Agent Framework (MAF) ?"

    - A) Une nouvelle version d'AutoGen avec un nom différent
    - B) Un framework unifié combinant Semantic Kernel et AutoGen en une seule plateforme
    - C) Un service cloud uniquement pour exécuter des agents sur Azure
    - D) Un remplacement de LangChain

    ??? success "✅ Révéler la réponse"
        **Correct : B) Un framework unifié combinant Semantic Kernel et AutoGen en une seule plateforme**

        MAF fusionne les forces des deux frameworks : le système de plugins d'entreprise et les planificateurs de SK avec les conversations multi-agents et l'exécution de code d'AutoGen. Il fournit une classe unique `Agent`, des Agent Skills portables et des Graph Workflows basés sur des DAG.

??? question "**Q2 (Choix multiple) :** Que sont les Agent Skills dans MAF ?"

    - A) Des fonctions Python décorées avec `@skill`
    - B) Des packages de compétences portables `.md` qui définissent les capacités, entrées, sorties et dépendances
    - C) Des poids de modèle pré-entraînés pour des tâches spécifiques
    - D) Des Azure Functions que les agents peuvent appeler

    ??? success "✅ Révéler la réponse"
        **Correct : B) Des packages de compétences portables `.md` qui définissent les capacités, entrées, sorties et dépendances**

        Les Agent Skills sont des packages basés sur Markdown qui décrivent ce qu'un agent peut faire, les entrées dont il a besoin, les sorties qu'il produit et les dépendances requises. Ils sont partageables entre équipes et projets, permettant un marketplace de capacités d'agents réutilisables.

??? question "**Q3 (Exécutez le lab) :** Combien de fonctionnalités ont un effort de migration « low » ?"

    Exécutez l'analyse de l'étape 3 sur [📥 `migration_matrix.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-076/migration_matrix.csv) et comptez les fonctionnalités à faible effort.

    ??? success "✅ Révéler la réponse"
        **7 fonctionnalités**

        Sur les 15 fonctionnalités de la matrice de migration, **7 ont `migration_effort = "low"`**. Ce sont les gains rapides de la phase 1 de la migration — généralement des fonctionnalités avec des équivalents directs entre SK/AutoGen et MAF.

??? question "**Q4 (Exécutez le lab) :** Combien de fonctionnalités sont disponibles dans MAF mais PAS dans Semantic Kernel ?"

    Exécutez l'analyse de l'étape 4 pour trouver les fonctionnalités où `maf_support = "yes"` et `sk_support = "no"`.

    ??? success "✅ Révéler la réponse"
        **Le nombre de fonctionnalités où MAF a le support `yes` mais SK a le support `no`.**

        Celles-ci représentent les capacités que les équipes gagnent en migrant de SK vers MAF — comme les modèles de discussion multi-agents, les bacs à sable d'exécution de code et d'autres fonctionnalités issues d'AutoGen désormais disponibles dans le framework unifié.

??? question "**Q5 (Exécutez le lab) :** Combien de fonctionnalités au total sont suivies dans la matrice de migration ?"

    Chargez le CSV et vérifiez le nombre total de lignes.

    ??? success "✅ Révéler la réponse"
        **15 fonctionnalités**

        La matrice de migration suit **15 fonctionnalités** réparties en 4 catégories : core (5), orchestration (4), tooling (3) et integration (3). Chaque fonctionnalité est évaluée pour le support dans SK, AutoGen et MAF, ainsi que l'effort de migration.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|-----------------|
| Microsoft Agent Framework | Plateforme unifiée fusionnant Semantic Kernel et AutoGen (RC fév. 2026) |
| Agent Skills | Packages de compétences portables `.md` pour des capacités d'agents réutilisables |
| Graph Workflows | Orchestration basée sur des DAG avec points de contrôle, remplaçant les pipelines linéaires |
| Matrice de migration | 15 fonctionnalités comparées entre SK, AutoGen et MAF |
| Stratégie de migration | Commencer par le faible effort (7 fonctionnalités), planifier l'effort élevé (3 fonctionnalités) |
| DevUI | Interface de développement intégrée pour déboguer et visualiser les workflows d'agents |

---

## Prochaines étapes

- **[Lab 034](lab-034-multi-agent-sk.md)** — Multi-Agent avec Semantic Kernel (comprendre ce que vous migrez)
- **[Lab 036](lab-036-autogen-basics.md)** — Bases d'AutoGen (comprendre les modèles AutoGen avant MAF)
- **[Lab 074](lab-074-foundry-agent-service.md)** — Foundry Agent Service (déployer des agents MAF en production)
- **[Lab 073](lab-073-swe-bench.md)** — SWE-Bench (évaluer les agents MAF sur des tâches de codage réelles)
