# 📚 RAG Path

<span class="level-badge level-100">L100</span> <span class="level-badge level-200">L200</span> <span class="level-badge level-300">L300</span> <span class="level-badge level-400">L400</span>

**Retrieval-Augmented Generation (RAG)** is the most common pattern for grounding AI agents in your own data. Instead of relying on the LLM's training data, you retrieve relevant documents at query time and include them in the prompt.

---

## What You'll Build

- ✅ Understand the RAG pipeline end-to-end
- ✅ Load, chunk, and embed documents using **GitHub Models (free)**
- ✅ Store and query vectors with a **local pgvector** (Docker)
- ✅ Build semantic search over **Azure PostgreSQL + pgvector**
- ✅ Evaluate RAG quality with the Azure AI Evaluation SDK

---

## Path Labs (7 labs, ~355 min total)

| Lab | Title | Level | Cost |
|-----|-------|-------|------|
| [Lab 006](../../labs/lab-006-what-is-rag.md) | What is RAG? | <span class="level-badge level-50">L50</span> | ✅ Free |
| [Lab 007](../../labs/lab-007-what-are-embeddings.md) | What are Embeddings? | <span class="level-badge level-50">L50</span> | ✅ Free |
| [Lab 022](../../labs/lab-022-rag-github-models-pgvector.md) | RAG Pipeline with GitHub Models + pgvector | <span class="level-badge level-200">L200</span> | ✅ Free |
| [Lab 026](../../labs/lab-026-agentic-rag.md) | Agentic RAG Pattern | <span class="level-badge level-200">L200</span> | ✅ GitHub Free |
| [Lab 031](../../labs/lab-031-pgvector-semantic-search.md) | pgvector Semantic Search on Azure | <span class="level-badge level-300">L300</span> | Free |
| [Lab 039](../../labs/lab-039-vector-db-comparison.md) | Vector Database Comparison | <span class="level-badge level-300">L300</span> | ✅ Free |
| [Lab 042](../../labs/lab-042-enterprise-rag.md) | Enterprise RAG with Evaluations | <span class="level-badge level-400">L400</span> | ⚠️ Azure |

---

## The RAG Pipeline

```
Documents
   │
   ▼
[Chunking]  ─── split into ~512-token pieces
   │
   ▼
[Embedding] ─── text-embedding-3-small → float[]
   │
   ▼
[Vector Store] ─ pgvector / Azure AI Search
   │
   ▼  ◄──── User Query (also embedded)
[Retrieval] ─── top-k cosine similarity
   │
   ▼
[LLM + Context] ── "Answer based on these docs: ..."
   │
   ▼
Response
```

---

## External Resources

- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [Azure AI Search + RAG](https://learn.microsoft.com/azure/search/retrieval-augmented-generation-overview)
- [GitHub Models Embeddings API](https://docs.github.com/en/github-models)
- [Azure AI Evaluation SDK](https://learn.microsoft.com/azure/ai-foundry/how-to/develop/agent-evaluate-sdk)
