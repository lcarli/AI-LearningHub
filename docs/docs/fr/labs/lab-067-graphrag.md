---
tags: [graphrag, knowledge-graph, rag, python]
---
# Lab 067 : GraphRAG — Graphes de connaissances pour la recherche inter-documents

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Parcours :</strong> Tous les parcours</span>
  <span><strong>Durée :</strong> ~90 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit</span> — Données simulées (aucun Azure OpenAI ni base de données graphe requis)</span>
</div>

## Ce que vous apprendrez

- Ce qu'est **GraphRAG** et en quoi il diffère du RAG traditionnel basé uniquement sur les vecteurs
- Construire un **graphe de connaissances** à partir de l'extraction d'entités et de relations
- Détecter des **communautés** à l'aide d'algorithmes de clustering de graphes
- Exécuter des **requêtes globales** qui synthétisent l'information à travers tous les documents
- Exécuter des **requêtes locales** qui suivent des sous-graphes centrés sur les entités
- Évaluer la qualité de la recherche à l'aide du **score d'importance** et de la couverture des communautés

!!! abstract "Prérequis"
    Complétez d'abord le **[Lab 009 : Génération augmentée par la recherche](lab-009-rag-basic.md)**. Ce lab suppose une familiarité avec les concepts de base du RAG, notamment le découpage, l'embedding et la recherche vectorielle.

## Introduction

Le RAG traditionnel récupère des segments individuels par similarité sémantique. Cela fonctionne bien pour les **requêtes locales** (« Quelle est la politique de retour ? ») mais échoue pour les **requêtes globales** qui nécessitent la synthèse d'informations provenant de nombreux documents (« Quels sont les thèmes majeurs des résultats du T3 pour toutes les entreprises du portefeuille ? »).

**GraphRAG** résout ce problème en construisant un **graphe de connaissances** à partir d'entités et de relations extraites, puis en regroupant le graphe en **communautés** qui représentent des groupes thématiques :

| Approche | Méthode de recherche | Idéal pour | Faiblesse |
|----------|---------------------|------------|-----------|
| **Vector RAG** | Similarité cosinus sur les embeddings | Requêtes locales et spécifiques | Ne peut pas synthétiser entre documents |
| **GraphRAG Local** | Parcours de sous-graphe centré sur les entités | Requêtes sur des entités spécifiques | Manque les thèmes globaux |
| **GraphRAG Global** | Résumés de communautés + map-reduce | Requêtes larges et inter-documents | Latence et coût plus élevés |

### Le scénario

Vous construisez un **système de veille de marché** pour une entreprise d'équipement outdoor. Votre corpus contient des avis produits, des rapports fournisseurs et des documents d'analyse concurrentielle. Vous allez extraire des entités, construire un graphe de connaissances, détecter des communautés et comparer les performances des requêtes locales et globales.

Le graphe de connaissances contient **15 entités** organisées en **8 communautés**.

---

## Prérequis

| Exigence | Pourquoi |
|---|---|
| Python 3.10+ | Exécuter les scripts d'analyse |
| `pandas` | Analyser les données du graphe de connaissances |

```bash
pip install pandas
```

---

!!! tip "Démarrage rapide avec GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Toutes les dépendances sont pré-installées dans le devcontainer.


## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-067/` de votre répertoire de travail.

| Fichier | Description | Téléchargement |
|---------|-------------|----------------|
| `broken_graphrag.py` | Exercice de correction de bugs (3 bugs + auto-tests) | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-067/broken_graphrag.py) |
| `knowledge_graph.csv` | Jeu de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-067/knowledge_graph.csv) |

---

## Étape 1 : Comprendre l'architecture GraphRAG

GraphRAG étend le pipeline RAG avec la construction de graphes et la détection de communautés :

```
Documents → [Entity Extraction] → [Relationship Extraction] → Knowledge Graph
                                                                     ↓
Query → [Community Detection] → [Community Summaries] → [Map-Reduce Answer]
                                        ↓
                              [Local Subgraph] → [Entity-Centric Answer]
```

Concepts clés :

1. **Entités** — Personnes, organisations, produits et concepts extraits du texte
2. **Relations** — Connexions entre entités (ex. : « EntrepriseA *fournit* EntrepriseB »)
3. **Communautés** — Groupes d'entités densément connectées découvertes par des algorithmes de graphes
4. **Résumés de communautés** — Descriptions générées par le LLM du thème de chaque communauté
5. **Score d'importance** — Métrique de centralité (0–1) indiquant la signification d'une entité

!!! info "Pourquoi les communautés sont importantes"
    Les communautés regroupent des entités liées qui co-apparaissent fréquemment. Une requête globale comme « Quelles sont les tendances du marché ? » peut être répondue en synthétisant les résumés de communautés plutôt qu'en parcourant chaque segment de document — réduisant drastiquement l'utilisation de tokens tout en améliorant la couverture.

---

## Étape 2 : Charger et explorer le graphe de connaissances

Le jeu de données contient **15 entités** avec des relations et des affectations de communautés :

```python
import pandas as pd

kg = pd.read_csv("lab-067/knowledge_graph.csv")
print(f"Total entities: {len(kg)}")
print(f"Entity types: {sorted(kg['entity_type'].unique())}")
print(f"Communities: {sorted(kg['community_id'].unique())}")
print(f"Number of communities: {kg['community_id'].nunique()}")
print(f"\nEntities per community:")
print(kg.groupby("community_id")["entity_id"].count().sort_values(ascending=False))
```

**Résultat attendu :**

```
Total entities: 15
Communities: [0, 1, 2, 3, 4, 5, 6, 7]
Number of communities: 8
```

---

## Étape 3 : Analyse de l'importance des entités

Analysez les scores d'importance des entités pour identifier les nœuds clés du graphe :

```python
print("Top entities by importance score:")
top_entities = kg.sort_values("importance_score", ascending=False).head(5)
print(top_entities[["entity_id", "entity_name", "entity_type", "importance_score", "community_id"]]
      .to_string(index=False))

print(f"\nHighest importance entity: {kg.loc[kg['importance_score'].idxmax(), 'entity_name']} "
      f"({kg['importance_score'].max():.2f})")
print(f"Average importance score: {kg['importance_score'].mean():.2f}")
```

**Résultat attendu :**

```
Highest importance entity: OutdoorGear Inc (0.98)
```

!!! tip "Centralité et importance"
    Le score d'importance reflète le degré de centralité d'une entité dans le graphe de connaissances. Les entités avec des scores élevés (comme OutdoorGear Inc à 0,98) connectent de nombreuses autres entités et communautés. Les requêtes impliquant ces entités pivots parcourront davantage le graphe, fournissant un contexte plus riche.

---

## Étape 4 : Analyse de la structure des communautés

Examinez la structure et les thèmes des communautés :

```python
print(f"Total communities: {kg['community_id'].nunique()}")
print(f"\nCommunity sizes:")
community_sizes = kg.groupby("community_id").agg(
    entity_count=("entity_id", "count"),
    avg_importance=("importance_score", "mean"),
    entities=("entity_name", lambda x: ", ".join(x))
).sort_values("entity_count", ascending=False)
print(community_sizes.to_string())
```

**Résultat attendu :**

```
Total communities: 8
```

!!! info "Détection de communautés"
    Les communautés sont détectées à l'aide de l'algorithme de Leiden, qui identifie les sous-graphes densément connectés. Chaque communauté représente un groupe thématique — par exemple, une communauté peut contenir des entités liées aux fournisseurs tandis qu'une autre regroupe les entités concurrentes. Le nombre et la taille des communautés dépendent de la structure de connectivité du graphe.

---

## Étape 5 : Simulation de requêtes locales vs globales

Simulez la manière dont les requêtes locales et globales parcourent le graphe différemment :

```python
# Local query: find entities related to a specific entity
target_entity = kg.loc[kg["importance_score"].idxmax(), "entity_name"]
target_community = kg.loc[kg["importance_score"].idxmax(), "community_id"]
local_results = kg[kg["community_id"] == target_community]
print(f"Local query for '{target_entity}':")
print(f"  Community {target_community} has {len(local_results)} entities")
print(f"  Entities: {', '.join(local_results['entity_name'].tolist())}")

# Global query: summarize across all communities
print(f"\nGlobal query — all communities:")
for cid in sorted(kg["community_id"].unique()):
    community = kg[kg["community_id"] == cid]
    print(f"  Community {cid}: {len(community)} entities — "
          f"{', '.join(community['entity_name'].tolist())}")
```

---

## Étape 6 : Métriques de qualité du graphe

Évaluez la qualité du graphe de connaissances :

```python
total_entities = len(kg)
total_communities = kg["community_id"].nunique()
avg_community_size = total_entities / total_communities
max_importance = kg["importance_score"].max()
min_importance = kg["importance_score"].min()

report = f"""
╔════════════════════════════════════════════════════════╗
║     GraphRAG — Knowledge Graph Quality Report          ║
╠════════════════════════════════════════════════════════╣
║ Total Entities:              {total_entities:>5}                     ║
║ Total Communities:           {total_communities:>5}                     ║
║ Avg Community Size:          {avg_community_size:>5.1f}                     ║
║ Max Importance Score:        {max_importance:>5.2f}                     ║
║ Min Importance Score:        {min_importance:>5.2f}                     ║
║ Entity Types:                {kg['entity_type'].nunique():>5}                     ║
╚════════════════════════════════════════════════════════╝
"""
print(report)
```

---

## 🐛 Exercice de correction de bugs

Le fichier `lab-067/broken_graphrag.py` contient **3 bugs** dans la manière dont il traite le graphe de connaissances :

```bash
python lab-067/broken_graphrag.py
```

| Test | Ce qu'il vérifie | Indice |
|------|-----------------|--------|
| Test 1 | Nombre d'entités | Devrait compter toutes les lignes du DataFrame, pas les ID de communauté uniques |
| Test 2 | Nombre de communautés | Devrait utiliser `nunique()` sur `community_id`, pas `count()` |
| Test 3 | Entité la plus importante | Devrait utiliser `idxmax()` sur `importance_score`, pas `idxmin()` |

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Choix multiple) :** Quel problème GraphRAG résout-il que le RAG vectoriel traditionnel ne peut pas résoudre ?"

    - A) Génération d'embeddings plus rapide
    - B) Synthèse inter-documents pour les requêtes globales en utilisant des résumés au niveau des communautés
    - C) Coûts de stockage réduits pour les embeddings
    - D) Meilleure tokenisation des documents sources

    ??? success "✅ Révéler la réponse"
        **Correct : B) Synthèse inter-documents pour les requêtes globales en utilisant des résumés au niveau des communautés**

        Le RAG vectoriel traditionnel récupère des segments individuels par similarité, ce qui fonctionne pour les requêtes locales mais échoue lorsque la réponse nécessite la synthèse d'informations dispersées dans de nombreux documents. GraphRAG construit un graphe de connaissances, détecte des communautés d'entités liées et utilise les résumés de communautés pour répondre aux requêtes globales via map-reduce.

??? question "**Q2 (Choix multiple) :** Qu'est-ce qu'une « communauté » dans le contexte de GraphRAG ?"

    - A) Un groupe d'utilisateurs partageant le même agent
    - B) Un groupe d'entités densément connectées dans le graphe de connaissances qui représentent un groupe thématique
    - C) Un type de partition d'index vectoriel
    - D) Un fil de discussion avec plusieurs participants

    ??? success "✅ Révéler la réponse"
        **Correct : B) Un groupe d'entités densément connectées dans le graphe de connaissances qui représentent un groupe thématique**

        Les communautés sont découvertes par des algorithmes de clustering de graphes comme Leiden. Les entités au sein d'une communauté sont plus densément connectées entre elles qu'aux entités extérieures à la communauté. Chaque communauté reçoit un résumé généré par le LLM qui capture son thème, permettant de répondre efficacement aux requêtes globales.

??? question "**Q3 (Exécuter le lab) :** Combien d'entités au total se trouvent dans le graphe de connaissances ?"

    Chargez le fichier CSV du graphe de connaissances et comptez le nombre total de lignes.

    ??? success "✅ Révéler la réponse"
        **15 entités**

        Le graphe de connaissances contient 15 entités couvrant plusieurs types (organisations, produits, personnes, concepts). Ces entités sont connectées par des relations extraites des documents sources.

??? question "**Q4 (Exécuter le lab) :** Combien de communautés ont été détectées dans le graphe de connaissances ?"

    Utilisez `nunique()` sur la colonne `community_id`.

    ??? success "✅ Révéler la réponse"
        **8 communautés**

        Les 15 entités sont organisées en 8 communautés par l'algorithme de clustering de Leiden. Chaque communauté représente un groupe thématique d'entités liées — par exemple, les relations fournisseurs, le paysage concurrentiel ou les catégories de produits.

??? question "**Q5 (Exécuter le lab) :** Quelle entité a le score d'importance le plus élevé, et quel est ce score ?"

    Triez par `importance_score` décroissant et vérifiez l'entité en tête.

    ??? success "✅ Révéler la réponse"
        **OutdoorGear Inc avec un score d'importance de 0,98**

        OutdoorGear Inc est l'entité la plus centrale du graphe de connaissances, connectée à des entités de plusieurs communautés. Son score d'importance élevé (0,98) reflète son rôle de pivot — les requêtes impliquant cette entité parcourront davantage le graphe et fourniront un contexte inter-documents plus riche.

---

## Résumé

| Sujet | Ce que vous avez appris |
|-------|------------------------|
| GraphRAG | Étend le RAG avec des graphes de connaissances pour la synthèse inter-documents |
| Extraction d'entités | Identifier les personnes, organisations et concepts à partir des documents |
| Détection de communautés | Regrouper les entités liées pour découvrir des groupes thématiques |
| Requêtes locales | Parcourir des sous-graphes centrés sur les entités pour des réponses spécifiques |
| Requêtes globales | Synthétiser les résumés de communautés via map-reduce pour des réponses larges |
| Score d'importance | Classer les entités par centralité dans le graphe pour identifier les nœuds clés |

---

## Prochaines étapes

- **[Lab 009](lab-009-rag-basic.md)** — Les bases du RAG (schémas fondamentaux de recherche)
- **[Lab 068](lab-068-hybrid-search.md)** — Recherche hybride (stratégies de recherche complémentaires)
- **[Lab 065](lab-065-purview-dspm-ai.md)** — Purview DSPM for AI (gouvernance pour les pipelines RAG)