---
tags: [graphrag, knowledge-graph, rag, python, persona-developer, persona-architect]
---
# Lab 067: GraphRAG — Knowledge Graphs for Cross-Document Retrieval

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~90 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Mock data (no Azure OpenAI or graph DB required)</span>
</div>

## What You'll Learn

- What **GraphRAG** is and how it differs from traditional vector-only RAG
- Build a **knowledge graph** from entity and relationship extraction
- Detect **communities** using graph clustering algorithms
- Execute **global queries** that synthesize across all documents
- Execute **local queries** that follow entity-centric subgraphs
- Evaluate retrieval quality using **importance scoring** and community coverage

!!! abstract "Prerequisite"
    Complete **[Lab 009: Retrieval-Augmented Generation](lab-009-rag-basic.md)** first. This lab assumes familiarity with basic RAG concepts including chunking, embedding, and vector search.

## Introduction

Traditional RAG retrieves individual chunks by semantic similarity. This works well for **local queries** ("What is the return policy?") but fails for **global queries** that require synthesizing information across many documents ("What are the major themes in Q3 earnings across all portfolio companies?").

**GraphRAG** solves this by building a **knowledge graph** from extracted entities and relationships, then clustering the graph into **communities** that represent thematic groups:

| Approach | Retrieval Method | Best For | Weakness |
|----------|-----------------|----------|----------|
| **Vector RAG** | Cosine similarity on embeddings | Local, specific queries | Cannot synthesize across documents |
| **GraphRAG Local** | Entity-centric subgraph traversal | Queries about specific entities | Misses global themes |
| **GraphRAG Global** | Community summaries + map-reduce | Broad, cross-document queries | Higher latency and cost |

### The Scenario

You are building a **market intelligence system** for an outdoor gear company. Your corpus contains product reviews, supplier reports, and competitor analysis documents. You will extract entities, build a knowledge graph, detect communities, and compare local vs global query performance.

The knowledge graph contains **15 entities** organized into **8 communities**.

---

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Run analysis scripts |
| `pandas` | Analyze knowledge graph data |

```bash
pip install pandas
```

---

!!! tip "Quick Start with GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    All dependencies are pre-installed in the devcontainer.


## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-067/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_graphrag.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-067/broken_graphrag.py) |
| `knowledge_graph.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-067/knowledge_graph.csv) |

---

## Step 1: Understanding GraphRAG Architecture

GraphRAG extends the RAG pipeline with graph construction and community detection:

```
Documents → [Entity Extraction] → [Relationship Extraction] → Knowledge Graph
                                                                     ↓
Query → [Community Detection] → [Community Summaries] → [Map-Reduce Answer]
                                        ↓
                              [Local Subgraph] → [Entity-Centric Answer]
```

Key concepts:

1. **Entities** — People, organizations, products, and concepts extracted from text
2. **Relationships** — Connections between entities (e.g., "CompanyA *supplies* CompanyB")
3. **Communities** — Clusters of densely connected entities discovered by graph algorithms
4. **Community Summaries** — LLM-generated descriptions of each community's theme
5. **Importance Score** — Centrality metric (0–1) indicating an entity's significance

!!! info "Why Communities Matter"
    Communities group related entities that frequently co-occur. A global query like "What are the market trends?" can be answered by synthesizing community summaries rather than scanning every document chunk — dramatically reducing token usage while improving coverage.

---

## Step 2: Load and Explore the Knowledge Graph

The dataset contains **15 entities** with relationships and community assignments:

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

**Expected:**

```
Total entities: 15
Communities: [0, 1, 2, 3, 4, 5, 6, 7]
Number of communities: 8
```

---

## Step 3: Entity Importance Analysis

Analyze entity importance scores to identify key nodes in the graph:

```python
print("Top entities by importance score:")
top_entities = kg.sort_values("importance_score", ascending=False).head(5)
print(top_entities[["entity_id", "entity_name", "entity_type", "importance_score", "community_id"]]
      .to_string(index=False))

print(f"\nHighest importance entity: {kg.loc[kg['importance_score'].idxmax(), 'entity_name']} "
      f"({kg['importance_score'].max():.2f})")
print(f"Average importance score: {kg['importance_score'].mean():.2f}")
```

**Expected:**

```
Highest importance entity: OutdoorGear Inc (0.98)
```

!!! tip "Centrality and Importance"
    The importance score reflects how central an entity is in the knowledge graph. Entities with high scores (like OutdoorGear Inc at 0.98) connect many other entities and communities. Queries that involve these hub entities will traverse more of the graph, providing richer context.

---

## Step 4: Community Structure Analysis

Examine the community structure and themes:

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

**Expected:**

```
Total communities: 8
```

!!! info "Community Detection"
    Communities are detected using the Leiden algorithm, which identifies densely connected subgraphs. Each community represents a thematic cluster — for example, one community might contain supplier-related entities while another groups competitor entities. The number and size of communities depend on the graph's connectivity structure.

---

## Step 5: Local vs Global Query Simulation

Simulate how local and global queries traverse the graph differently:

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

## Step 6: Graph Quality Metrics

Evaluate the quality of the knowledge graph:

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

## 🐛 Bug-Fix Exercise

The file `lab-067/broken_graphrag.py` has **3 bugs** in how it processes the knowledge graph:

```bash
python lab-067/broken_graphrag.py
```

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Entity count | Should count all rows in the DataFrame, not unique community IDs |
| Test 2 | Community count | Should use `nunique()` on `community_id`, not `count()` |
| Test 3 | Highest importance entity | Should use `idxmax()` on `importance_score`, not `idxmin()` |

---


## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What problem does GraphRAG solve that traditional vector RAG cannot?"

    - A) Faster embedding generation
    - B) Cross-document synthesis for global queries by using community-level summaries
    - C) Lower storage costs for embeddings
    - D) Better tokenization of source documents

    ??? success "✅ Reveal Answer"
        **Correct: B) Cross-document synthesis for global queries by using community-level summaries**

        Traditional vector RAG retrieves individual chunks by similarity, which works for local queries but fails when the answer requires synthesizing information scattered across many documents. GraphRAG builds a knowledge graph, detects communities of related entities, and uses community summaries to answer global queries via map-reduce.

??? question "**Q2 (Multiple Choice):** What is a 'community' in the context of GraphRAG?"

    - A) A group of users who share the same agent
    - B) A cluster of densely connected entities in the knowledge graph that represent a thematic group
    - C) A type of vector index partition
    - D) A chat thread with multiple participants

    ??? success "✅ Reveal Answer"
        **Correct: B) A cluster of densely connected entities in the knowledge graph that represent a thematic group**

        Communities are discovered by graph clustering algorithms like Leiden. Entities within a community are more densely connected to each other than to entities outside the community. Each community gets an LLM-generated summary that captures its theme, enabling efficient global query answering.

??? question "**Q3 (Run the Lab):** How many total entities are in the knowledge graph?"

    Load the knowledge graph CSV and count the total rows.

    ??? success "✅ Reveal Answer"
        **15 entities**

        The knowledge graph contains 15 entities spanning multiple types (organizations, products, people, concepts). These entities are connected through relationships extracted from the source documents.

??? question "**Q4 (Run the Lab):** How many communities were detected in the knowledge graph?"

    Use `nunique()` on the `community_id` column.

    ??? success "✅ Reveal Answer"
        **8 communities**

        The 15 entities are organized into 8 communities by the Leiden clustering algorithm. Each community represents a thematic group of related entities — for example, supplier relationships, competitor landscape, or product categories.

??? question "**Q5 (Run the Lab):** Which entity has the highest importance score, and what is the score?"

    Sort by `importance_score` descending and check the top entity.

    ??? success "✅ Reveal Answer"
        **OutdoorGear Inc with an importance score of 0.98**

        OutdoorGear Inc is the most central entity in the knowledge graph, connecting to entities across multiple communities. Its high importance score (0.98) reflects its role as a hub — queries involving this entity will traverse more of the graph and provide richer cross-document context.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| GraphRAG | Extends RAG with knowledge graphs for cross-document synthesis |
| Entity Extraction | Identify people, organizations, and concepts from documents |
| Community Detection | Cluster related entities to discover thematic groups |
| Local Queries | Traverse entity-centric subgraphs for specific answers |
| Global Queries | Synthesize community summaries via map-reduce for broad answers |
| Importance Scoring | Rank entities by graph centrality to identify key nodes |

---

## Next Steps

- **[Lab 009](lab-009-rag-basic.md)** — RAG Basics (foundational retrieval patterns)
- **[Lab 068](lab-068-hybrid-search.md)** — Hybrid Search (complementary retrieval strategies)
- **[Lab 065](lab-065-purview-dspm-ai.md)** — Purview DSPM for AI (governance for RAG pipelines)
