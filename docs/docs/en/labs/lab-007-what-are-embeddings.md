---
tags: [free, beginner, no-account-needed, embeddings, rag]
---
# Lab 007: What are Embeddings?

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-50">L50</span></span>
  <span><strong>Path:</strong> <a href="../paths/rag/">📚 RAG</a> · <a href="../paths/semantic-kernel/">🧠 Semantic Kernel</a></span>
  <span><strong>Time:</strong> ~15 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — No account needed</span>
</div>

## What You'll Learn

- What an embedding is (a vector / list of numbers)
- How text is mapped to a high-dimensional space
- What **cosine similarity** means and why it matters
- Why embeddings power semantic search, RAG, and agent memory
- Which embedding models to use and when

---

## Introduction

Embeddings are the engine behind semantic search, RAG, and vector memory in AI agents. Once you understand what they are, a lot of "magic" in AI systems becomes obvious.

The key idea is simple: **convert any piece of text into a list of numbers (a vector) such that similar texts produce similar vectors.**

---

## Part 1: Text as a Point in Space

Imagine a 2D map where every word is placed based on its meaning:

```
                    Science
                      │
              Physics  │  Biology
                    \  │  /
Tech ───────────────────────────── Nature
                    /  │  \
               Code    │   Animals
                      AI
                      │
```

Words with similar meanings cluster together. "Dog" is near "Cat" and "Pet". "Python" clusters near "Code" and "Programming" — not near "Snake" (in a code-focused corpus).

Real embedding models don't use 2 dimensions — they use **1,536** (OpenAI) or **3,072** dimensions. But the principle is the same: similar meaning = nearby point in space.

---

## Part 2: What an Embedding Actually Looks Like

When you embed the text `"waterproof hiking boots"`, you get back something like:

```python
[0.023, -0.157, 0.842, 0.001, -0.334, 0.711, ..., 0.089]
# ↑ 1,536 numbers for text-embedding-3-small
```

Each number encodes some aspect of meaning — but there's no human-readable interpretation of individual dimensions. The meaning lives in the *relationships* between vectors.

---

## Part 3: Measuring Similarity — Cosine Distance

To compare two vectors, we use **cosine similarity**: the angle between them.

```
Vector A ("waterproof hiking boots")
      ↗

Vector B ("weatherproof trekking shoes")  ← small angle → very similar
      ↗ (almost same direction)

Vector C ("chocolate birthday cake")      ← large angle → very different
→  (completely different direction)
```

Cosine similarity ranges from **-1 to 1**:
- `1.0` = identical meaning
- `0.0` = unrelated
- `-1.0` = opposite meaning

In practice, most similar documents score between **0.7 and 0.95**.

```python
# Simplified cosine similarity
import numpy as np

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# "king" - "man" + "woman" ≈ "queen"  (the famous word2vec example)
similarity = cosine_similarity(embed("king"), embed("queen"))
# → ~0.89 (very similar)

similarity = cosine_similarity(embed("king"), embed("pizza"))
# → ~0.12 (unrelated)
```

---

## Part 4: Where Embeddings Are Used in Agent Systems

### 1. Semantic Search (RAG)
```
User query: "something to keep rain out while hiking"
         ↓ embed
[0.023, -0.157, ...]
         ↓ compare with all document vectors
Matches: "waterproof hiking jacket" (0.91)
         "rain-resistant trekking gear" (0.88)
         "chocolate cake recipe" (0.08) ← filtered out
```

### 2. Agent Memory (Semantic Kernel / LangChain)
Long-term agent memory stores past interactions as embeddings. When the user mentions a topic, the agent retrieves semantically relevant memories:

```
User: "Let's continue our discussion about the camping budget"
         ↓ embed query
Retrieves: previous conversation about camping (0.87 similarity)
Not: unrelated conversation about software (0.12 similarity)
```

### 3. Duplicate Detection
```
"How do I return a product?" (0.94 similarity)
"What's your return policy?"
→ Detected as duplicates → merge/deduplicate FAQs
```

### 4. Clustering / Categorization
Group documents automatically by meaning without predefined categories.

---

## Part 5: Embedding Models

| Model | Dimensions | Context | Cost | Best for |
|-------|-----------|---------|------|---------|
| `text-embedding-3-small` (OpenAI) | 1,536 | 8,191 tokens | Low | Most use cases |
| `text-embedding-3-large` (OpenAI) | 3,072 | 8,191 tokens | Higher | Highest accuracy |
| `text-embedding-ada-002` (OpenAI) | 1,536 | 8,191 tokens | Low | Legacy |
| `nomic-embed-text` (Ollama) | 768 | 8,192 tokens | **Free (local)** | Offline/private |
| `mxbai-embed-large` (Ollama) | 1,024 | 512 tokens | **Free (local)** | Local production |

!!! tip "Use text-embedding-3-small via GitHub Models (free)"
    In this hub's L200 labs, we use `text-embedding-3-small` via the GitHub Models API — free, no credit card, same quality as paid Azure OpenAI.

---

## Part 6: Key Properties and Gotchas

### ✅ Embeddings capture meaning across languages
```
embed("waterproof jacket") ≈ embed("veste imperméable")  # French
```
Multilingual models work cross-language — queries in one language can find documents in another.

### ⚠️ Embeddings are model-specific
Vectors from `text-embedding-3-small` are **not comparable** to vectors from `nomic-embed-text`. Never mix models in the same vector store.

### ⚠️ Embeddings don't capture exact matches well
```
embed("SKU-12345") may not match embed("product SKU-12345")
```
For exact IDs, codes, or keywords → use keyword/BM25 search alongside embeddings (hybrid search).

### ⚠️ Long text loses detail
Embedding a 10-page document into one vector loses fine-grained meaning. That's why we **chunk** first, then embed each chunk separately.

---

## 📁 Hands-On: Embedding Explorer

This lab includes a Python script that lets you **see embeddings in action** using the GitHub Models free tier.

```
lab-007/
└── embedding_explorer.py   ← Cosine similarity demo with OutdoorGear products
```

**Prerequisites:** Python 3.9+ and a GitHub token (free)

```bash
# Install dependencies
pip install openai

# Set your GitHub token
export GITHUB_TOKEN=<your_PAT>    # Linux/macOS
set GITHUB_TOKEN=<your_PAT>       # Windows

# Run the explorer
python lab-007/embedding_explorer.py
```

**What you'll see:**

1. **Semantic search:** Find products matching "lightweight tent for solo hiking" without keyword matching
2. **Semantic vs. keyword:** Compare how keyword search misses "something to sleep in the cold" while semantic search finds the sleeping bag
3. **Similarity matrix:** See that two tent descriptions score higher similarity to each other than a tent vs. a sleeping bag

This directly illustrates why RAG works: the embedding of a *question* and the embedding of its *answer document* land close together in vector space.

---

## 🧠 Knowledge Check

??? question "1. What does a higher cosine similarity score mean?"
    The two texts are **more semantically similar** — closer in meaning. Cosine similarity ranges from -1 (opposite meaning) to 1 (identical meaning). In practice, similar product descriptions score ~0.85–0.95; unrelated texts score ~0.1–0.3.

??? question "2. Why must you always use the same embedding model for queries and documents?"
    Embeddings are **model-specific** — the numerical space is completely different for each model. Comparing a vector from `text-embedding-3-small` with one from `nomic-embed-text` is like comparing GPS coordinates in different coordinate systems. Always embed queries and documents with the same model.

??? question "3. Why do we chunk documents before embedding instead of embedding the whole document?"
    A whole-document embedding **averages out all the meaning** into one vector, losing fine-grained detail. If you embed a 50-page manual, the vector represents "a technical manual" — not specific sections. By chunking first (~512 tokens), each chunk gets its own precise vector, so retrieval finds the *exact relevant passage*, not just the *right document*.

---

## Summary

| Concept | Key takeaway |
|---------|-------------|
| **Embedding** | A list of ~1,536 numbers representing text meaning |
| **Cosine similarity** | Measures angle between vectors; closer = more similar |
| **Semantic search** | Find relevant content by meaning, not exact words |
| **Model-specific** | Never mix vectors from different embedding models |
| **Chunking first** | Embed chunks, not whole documents |
| **Free option** | `text-embedding-3-small` via GitHub Models or `nomic-embed-text` via Ollama |

---

## Next Steps

- **See embeddings in a RAG app:** → [Lab 022 — RAG with GitHub Models + pgvector](lab-022-rag-github-models-pgvector.md)
- **Run embeddings locally for free:** → [Lab 015 — Ollama Local LLMs](lab-015-ollama-local-llms.md)
- **Use embeddings in Semantic Kernel:** → [Lab 023 — SK Plugins, Memory & Planners](lab-023-sk-plugins-memory.md)
