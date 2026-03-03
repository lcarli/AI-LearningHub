# Lab 006: What is RAG?

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-50">L50</span></span>
  <span><strong>Path:</strong> <a href="../paths/rag/">📚 RAG</a></span>
  <span><strong>Time:</strong> ~20 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — No account needed</span>
</div>

## What You'll Learn

- Why LLMs need external knowledge (and why training data alone isn't enough)
- The complete RAG pipeline: ingest → chunk → embed → store → retrieve → generate
- The difference between **keyword search**, **semantic search**, and **hybrid search**
- When to use RAG vs. fine-tuning vs. just a bigger context window
- Real-world RAG architectures

---

## Introduction

Imagine you've built an AI agent for your company. It answers questions beautifully — until a user asks about a product launched last month, or a policy updated last week.

The LLM doesn't know. Its training data has a cutoff date. And even if the information existed in training data, the model may not have memorized it accurately.

**RAG (Retrieval-Augmented Generation)** solves this by connecting the LLM to your own, up-to-date knowledge at query time — without retraining the model.

---

## Part 1: The Core Problem

LLMs have two knowledge limitations:

| Limitation | Description | Example |
|-----------|-------------|---------|
| **Training cutoff** | Knowledge stops at a date | "What happened last week?" |
| **Private data** | Never saw your documents | "What's our refund policy?" |
| **Hallucination risk** | May confabulate when uncertain | Invents plausible-sounding but wrong answer |

The naive solution — "just put all your documents in the prompt" — doesn't scale. A 500-page manual is ~375,000 tokens. Most LLMs cap at 128,000 tokens, and even if they didn't, you'd pay for all those tokens on every single query.

**RAG's answer:** Only retrieve the *relevant* pieces, right when you need them.

---

## Part 2: The RAG Pipeline

RAG has two distinct phases:

### Phase 1 — Ingestion (runs once, or on schedule)

```
Your documents (PDFs, Word, web pages, databases...)
         │
         ▼
    1. LOAD       ── Read content from source
         │
         ▼
    2. CHUNK      ── Split into overlapping segments (~512 tokens each)
         │
         ▼
    3. EMBED      ── Convert each chunk to a vector (list of numbers)
         │
         ▼
    4. STORE      ── Save chunks + vectors in a vector database
                     (pgvector, Azure AI Search, Chroma, Pinecone...)
```

### Phase 2 — Retrieval + Generation (runs on every query)

```
User asks: "What is the return policy for outdoor equipment?"
         │
         ▼
    5. EMBED QUERY ── Convert user question to a vector
         │
         ▼
    6. SEARCH     ── Find the most similar chunks in the vector DB
                     (cosine similarity / vector distance)
         │
         ▼
    7. AUGMENT    ── Inject retrieved chunks into the prompt:
                     "Answer based on these documents: [chunks]"
         │
         ▼
    8. GENERATE   ── LLM answers, grounded in real data
         │
         ▼
    User gets: "Our return policy for outdoor equipment allows returns
               within 30 days with original receipt..."
```

---

## Part 3: Chunking Strategies

How you split documents matters enormously.

| Strategy | How | Best for |
|----------|-----|---------|
| **Fixed-size** | Split every N tokens | Simple, fast, works for most cases |
| **Sentence/paragraph** | Split at natural boundaries | Better context preservation |
| **Semantic** | Split when topic changes | Best quality, more complex |
| **Recursive** | Try paragraph → sentence → word | Good default for mixed content |

**Overlap is important.** If you split at exactly 512 tokens, relevant information that spans a boundary gets lost. Add 50–100 token overlap between chunks.

```
Chunk 1: tokens 1–512
Chunk 2: tokens 462–974   ← 50-token overlap
Chunk 3: tokens 924–1436  ← 50-token overlap
```

---

## Part 4: Search Types

### Keyword Search (BM25)
Traditional search — matches exact words. Fast, interpretable, but misses synonyms and intent.

```
Query: "waterproof jacket"
Finds: documents containing exactly "waterproof" and "jacket"
Misses: "rain-resistant coat", "weatherproof outerwear"
```

### Semantic Search (Vector)
Compares meaning, not words. Finds conceptually similar content.

```
Query: "waterproof jacket"
Finds: "rain-resistant coat", "all-weather outerwear", "waterproof jacket"
Based on: vector similarity in embedding space
```

### Hybrid Search (BM25 + Vector)
Best of both worlds — combines keyword and semantic scores.

```
Final score = α × keyword_score + (1-α) × semantic_score
```

Most production RAG systems use hybrid search because it handles both exact lookups ("SKU-12345") and semantic queries ("something for camping in the rain").

---

## Part 5: RAG vs. Fine-tuning vs. Big Context

A common question: "Why not just fine-tune the model on my data?"

| Approach | Cost | Freshness | Best for |
|----------|------|-----------|---------|
| **RAG** | Low | ✅ Real-time | Dynamic data, documents, Q&A |
| **Fine-tuning** | High | ❌ Static | Tone, style, domain vocabulary |
| **Big context** | Medium | ✅ Per-request | Small datasets that fit in context |
| **RAG + Fine-tuning** | High | ✅ Real-time | Production systems needing both |

**Rule of thumb:** Use RAG for *knowledge* (facts, documents). Use fine-tuning for *behavior* (tone, style, format). They're complementary, not competing.

---

## Part 6: RAG Quality Metrics

A RAG system can fail in two places:

| Failure | Symptom | Fix |
|---------|---------|-----|
| **Bad retrieval** | Retrieved chunks aren't relevant | Better chunking, hybrid search, re-ranking |
| **Bad generation** | LLM ignores or misuses retrieved content | Stronger system prompt, citation enforcement |

Key metrics used in [Lab 035](lab-035-agent-evaluation.md) and [Lab 042](lab-042-enterprise-rag.md):

- **Groundedness**: Is the answer supported by retrieved documents?
- **Relevance**: Are the retrieved chunks actually relevant to the question?
- **Coherence**: Is the answer well-structured and readable?
- **Faithfulness**: Does the answer stay true to the source material?

---

## Real-World RAG Architectures

### Basic RAG
```
User → Embed query → Vector search → Augment prompt → LLM → Answer
```

### Agentic RAG (covered in Lab 026)
```
User → Agent decides: search? what query? how many chunks?
     → Multiple targeted searches
     → Agent synthesizes results
     → Answer with citations
```

### Corrective RAG
```
User → Retrieve → Grade relevance → If poor: web search fallback
     → Augment → Generate → Self-check → Answer
```

---

## Summary

| Concept | Key takeaway |
|---------|-------------|
| **Why RAG** | LLMs don't know your data or recent events — RAG fixes this |
| **Ingestion** | Load → Chunk → Embed → Store (runs once) |
| **Retrieval** | Embed query → Vector search → Top-k chunks |
| **Chunking** | Size + overlap matter; ~512 tokens with 50-token overlap |
| **Search** | Hybrid (keyword + semantic) beats either alone |
| **Evaluation** | Measure groundedness and relevance — both retrieval and generation |

---

## Next Steps

- **Understand the embedding vectors:** → [Lab 007 — What are Embeddings?](lab-007-what-are-embeddings.md)
- **Build a RAG app for free:** → [Lab 022 — RAG with GitHub Models + pgvector](lab-022-rag-github-models.md)
- **Production RAG on Azure:** → [Lab 031 — pgvector Semantic Search on Azure](lab-031-pgvector-semantic-search.md)
