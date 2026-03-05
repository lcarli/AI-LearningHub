---
tags: [search, rag, bm25, vector, semantic-ranker, python]
---
# Lab 068: Hybrid Search — Vector + BM25 + Semantic Ranker

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~60 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Pre-computed search results (no Azure AI Search required)</span>
</div>

!!! info "Tradução em andamento"
    Este lab ainda está sendo traduzido. O conteúdo abaixo está em inglês.



## What You'll Learn

- The differences between **BM25** (keyword), **vector** (semantic), and **hybrid** search
- How **Reciprocal Rank Fusion (RRF)** combines BM25 and vector scores
- How a **semantic ranker** (cross-encoder reranker) improves precision
- Measure retrieval quality with **recall** and **precision** metrics
- Compare search strategies using a **benchmark dataset**
- Identify which query types benefit most from hybrid + reranking

!!! abstract "Prerequisite"
    Complete **[Lab 009: Retrieval-Augmented Generation](lab-009-rag-basic.md)** first. This lab assumes familiarity with embedding-based retrieval and basic search concepts.

## Introduction

RAG pipelines depend on retrieval quality — if you retrieve the wrong chunks, even the best LLM will produce wrong answers. Modern search combines multiple strategies to maximize recall and precision:

| Strategy | How It Works | Strengths | Weaknesses |
|----------|-------------|-----------|------------|
| **BM25** | TF-IDF keyword matching | Exact matches, rare terms | No semantic understanding |
| **Vector** | Cosine similarity on embeddings | Semantic similarity, synonyms | Misses exact keywords |
| **Hybrid (RRF)** | Combines BM25 + vector via rank fusion | Best of both worlds | Higher latency |
| **Hybrid + Rerank** | Hybrid + cross-encoder reranking | Highest quality results | Highest latency and cost |

### The Scenario

You have **20 search queries** with known relevant documents (ground truth). Each query has been executed against all four strategies, with recall and precision recorded. Your job: analyze which strategy delivers the best retrieval quality and understand when each approach shines.

---

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Run analysis scripts |
| `pandas` | Analyze search comparison data |

```bash
pip install pandas
```

---

!!! tip "Quick Start with GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    All dependencies are pre-installed in the devcontainer.


## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-068/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_search.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-068/broken_search.py) |
| `search_comparison.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-068/search_comparison.csv) |

---

## Step 1: Understanding Search Strategies

Each search strategy processes queries differently:

```
Query → ┬─ [BM25 Index]      → keyword matches   ─┐
        │                                          ├─ [RRF Fusion] → Hybrid Results
        └─ [Vector Index]     → semantic matches   ─┘                      ↓
                                                                  [Semantic Ranker]
                                                                         ↓
                                                               Hybrid + Rerank Results
```

Key metrics:

1. **Recall** — What fraction of relevant documents were retrieved? (higher = fewer misses)
2. **Precision** — What fraction of retrieved documents are relevant? (higher = less noise)
3. **RRF Score** — Reciprocal Rank Fusion combines rankings: `1/(k + rank)` summed across strategies
4. **Rerank Score** — Cross-encoder relevance score applied to hybrid results

!!! info "Why Hybrid Beats Both"
    BM25 excels at exact keyword matches ("error code 0x8004") while vector search excels at semantic meaning ("application crashes on startup"). Hybrid search fuses both — capturing exact matches that vector search misses AND semantic matches that BM25 misses. The semantic ranker then reorders results using a more expensive but more accurate cross-encoder model.

---

## Step 2: Load and Explore Search Results

The dataset contains **20 queries** with results from all four strategies:

```python
import pandas as pd

results = pd.read_csv("lab-068/search_comparison.csv")
print(f"Total queries: {len(results)}")
print(f"Search strategies: {sorted(results.columns)}")
print(f"\nFirst 5 queries:")
print(results[["query_id", "query_text", "bm25_recall", "vector_recall",
               "hybrid_recall", "hybrid_rerank_recall"]].head().to_string(index=False))
```

**Expected:**

```
Total queries: 20
```

---

## Step 3: Recall Comparison

Compare recall across all four strategies:

```python
print("Average Recall by Strategy:")
print(f"  BM25:            {results['bm25_recall'].mean():.2f}")
print(f"  Vector:          {results['vector_recall'].mean():.2f}")
print(f"  Hybrid:          {results['hybrid_recall'].mean():.2f}")
print(f"  Hybrid + Rerank: {results['hybrid_rerank_recall'].mean():.2f}")

perfect_recall = results[results["hybrid_rerank_recall"] == 1.0]
print(f"\nQueries with perfect hybrid+rerank recall: {len(perfect_recall)} / {len(results)}")
```

**Expected:**

```
Average Recall by Strategy:
  BM25:            0.47
  Vector:          0.62
  Hybrid:          0.85
  Hybrid + Rerank: 1.00
```

!!! tip "Key Insight"
    Hybrid + Rerank achieves perfect recall (1.00) — every relevant document is retrieved for every query. BM25 alone retrieves less than half the relevant documents on average. This demonstrates why modern RAG pipelines should use hybrid search with reranking whenever possible.

---

## Step 4: Precision Analysis

Recall without precision means retrieving too much noise. Analyze precision:

```python
print("Average Precision by Strategy:")
print(f"  BM25:            {results['bm25_precision'].mean():.2f}")
print(f"  Vector:          {results['vector_precision'].mean():.2f}")
print(f"  Hybrid:          {results['hybrid_precision'].mean():.2f}")
print(f"  Hybrid + Rerank: {results['hybrid_rerank_precision'].mean():.2f}")
```

**Expected:**

```
Average Precision by Strategy:
  BM25:            0.40
  Vector:          0.48
  Hybrid:          0.52
  Hybrid + Rerank: 0.57
```

!!! warning "Precision vs Recall Trade-off"
    Even hybrid + rerank achieves only 0.57 average precision — meaning 43% of retrieved documents are not relevant. High recall ensures no relevant documents are missed, but the LLM must filter noise from the context. Consider using a stricter rerank threshold to improve precision at the cost of some recall.

---

## Step 5: Query-Level Analysis

Identify which queries benefit most from hybrid search:

```python
results["hybrid_lift"] = results["hybrid_rerank_recall"] - results["bm25_recall"]
biggest_lift = results.sort_values("hybrid_lift", ascending=False).head(5)
print("Queries with biggest recall lift (hybrid+rerank vs BM25):")
print(biggest_lift[["query_id", "query_text", "bm25_recall", "hybrid_rerank_recall", "hybrid_lift"]]
      .to_string(index=False))
```

Queries with the biggest lift are typically semantic in nature — paraphrases, synonyms, or conceptual queries where BM25's keyword matching fails but vector similarity succeeds.

---

## Step 6: Search Strategy Recommendation Engine

Build a recommendation based on the analysis:

```python
summary = f"""
╔════════════════════════════════════════════════════════╗
║     Hybrid Search — Strategy Comparison Report         ║
╠════════════════════════════════════════════════════════╣
║ Queries Evaluated:           {len(results):>5}                     ║
║ BM25 Avg Recall:             {results['bm25_recall'].mean():>5.2f}                     ║
║ Vector Avg Recall:           {results['vector_recall'].mean():>5.2f}                     ║
║ Hybrid Avg Recall:           {results['hybrid_recall'].mean():>5.2f}                     ║
║ Hybrid+Rerank Avg Recall:    {results['hybrid_rerank_recall'].mean():>5.2f}                     ║
║ Hybrid+Rerank Avg Precision: {results['hybrid_rerank_precision'].mean():>5.2f}                     ║
╚════════════════════════════════════════════════════════╝
"""
print(summary)
```

---

## 🐛 Bug-Fix Exercise

The file `lab-068/broken_search.py` has **3 bugs** in how it calculates search metrics:

```bash
python lab-068/broken_search.py
```

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Average recall calculation | Should use `mean()`, not `sum()` |
| Test 2 | Precision column name | Should use `hybrid_rerank_precision`, not `hybrid_precision` |
| Test 3 | Recall comparison | Should compare `hybrid_rerank_recall >= bm25_recall`, not `<=` |

---


## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What does Reciprocal Rank Fusion (RRF) do in hybrid search?"

    - A) Replaces the vector index with a keyword index
    - B) Combines rankings from multiple search strategies into a single unified ranking
    - C) Trains a new embedding model on the query
    - D) Reduces the number of documents in the index

    ??? success "✅ Reveal Answer"
        **Correct: B) Combines rankings from multiple search strategies into a single unified ranking**

        RRF merges result rankings from BM25 and vector search using the formula `1/(k + rank)` summed across strategies. Documents ranked highly by both strategies get boosted, while documents ranked highly by only one strategy still appear. This produces a unified ranking that captures both keyword and semantic relevance.

??? question "**Q2 (Multiple Choice):** Why does a semantic ranker (cross-encoder) improve results over hybrid search alone?"

    - A) It is faster than BM25
    - B) It re-scores each candidate by jointly encoding the query and document together, capturing deeper relevance signals
    - C) It removes all irrelevant documents perfectly
    - D) It generates new documents to fill gaps

    ??? success "✅ Reveal Answer"
        **Correct: B) It re-scores each candidate by jointly encoding the query and document together, capturing deeper relevance signals**

        A cross-encoder takes both the query and a candidate document as input and produces a relevance score. Unlike bi-encoders (used for vector search), cross-encoders capture fine-grained interactions between query and document tokens. This is more accurate but too expensive to apply to the entire index — so it is used as a reranker on the top-N hybrid results.

??? question "**Q3 (Run the Lab):** What is the average recall of the hybrid + rerank strategy?"

    Compute `results['hybrid_rerank_recall'].mean()`.

    ??? success "✅ Reveal Answer"
        **1.00 (perfect recall)**

        Hybrid + rerank achieves perfect recall across all 20 queries, meaning every relevant document is retrieved for every query. This is a significant improvement over BM25 alone (0.47) and demonstrates the value of combining keyword and semantic search with cross-encoder reranking.

??? question "**Q4 (Run the Lab):** What is the average recall of BM25 search alone?"

    Compute `results['bm25_recall'].mean()`.

    ??? success "✅ Reveal Answer"
        **0.47 average recall**

        BM25 retrieves less than half of the relevant documents on average. This is because BM25 relies on keyword matching and cannot handle synonyms, paraphrases, or conceptual queries. For example, a query about "application crashes" would miss documents that discuss "software failures" or "system instability."

??? question "**Q5 (Run the Lab):** What is the average precision of the hybrid + rerank strategy?"

    Compute `results['hybrid_rerank_precision'].mean()`.

    ??? success "✅ Reveal Answer"
        **0.57 average precision**

        While hybrid + rerank achieves perfect recall, its precision is 0.57 — meaning 43% of retrieved documents are not relevant. This is the recall-precision trade-off: maximizing recall ensures no relevant documents are missed, but includes some noise. The LLM must be robust enough to ignore irrelevant context when generating answers.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| BM25 Search | Keyword-based retrieval using TF-IDF scoring |
| Vector Search | Semantic retrieval using embedding cosine similarity |
| Hybrid Search | Combining BM25 + vector via Reciprocal Rank Fusion |
| Semantic Ranker | Cross-encoder reranking for higher-quality result ordering |
| Recall & Precision | Measuring retrieval quality with complementary metrics |
| Strategy Selection | Choosing the right search strategy based on query characteristics |

---

## Next Steps

- **[Lab 009](lab-009-rag-basic.md)** — RAG Basics (foundational retrieval patterns)
- **[Lab 067](lab-067-graphrag.md)** — GraphRAG (cross-document synthesis with knowledge graphs)
- **[Lab 065](lab-065-purview-dspm-ai.md)** — Purview DSPM for AI (governance for search pipelines)
