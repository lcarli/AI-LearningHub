---
tags: [vector-db, rag, azure, production, L300]
---
# Lab 039: Vector Database Comparison

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Path:</strong> <a href="../paths/rag/">📚 RAG</a></span>
  <span><strong>Time:</strong> ~50 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — All options have free tiers or local mode</span>
</div>

## What You'll Learn

- Understand the key differences between major vector databases
- Compare **pgvector**, **Chroma**, **Qdrant**, and **Azure AI Search** on the same task
- Evaluate each on: setup complexity, query speed, filtering, cloud integration
- Choose the right vector database for your agent's requirements

---

## Introduction

Choosing a vector database is one of the most consequential architecture decisions for a RAG-based agent. The "best" choice depends on your team's existing stack, scale requirements, filtering needs, and cloud strategy.

**The candidates:**

| Database | Type | Free option | Best for |
|----------|------|-------------|---------|
| **pgvector** | PostgreSQL extension | Azure free tier / local | Teams already using PostgreSQL |
| **Chroma** | Embedded / server | Fully open-source | Local development, small projects |
| **Qdrant** | Dedicated vector DB | Qdrant Cloud free tier | High-scale production, advanced filtering |
| **Azure AI Search** | Azure service | Free tier (1 index) | Azure-native, hybrid search, enterprise |

---

## Prerequisites

```bash
# Install all clients
pip install chromadb qdrant-client openai

# For Azure AI Search (optional)
pip install azure-search-documents
```

No API keys needed for Chroma (local) and Qdrant (local mode).
GitHub Token required for embeddings:
```bash
export GITHUB_TOKEN=<your PAT>
```

---

## Setup: Shared Embedding Function

All four tests use the same OutdoorGear product data and the same embedding model:

```python
# shared.py
import os
import math
from openai import OpenAI

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

PRODUCTS = [
    {"id": "P001", "name": "TrailBlazer Tent 2P",          "category": "Tents",         "price": 249.99, "weight": 1800},
    {"id": "P002", "name": "Summit Dome 4P",                "category": "Tents",         "price": 549.99, "weight": 3200},
    {"id": "P003", "name": "TrailBlazer Solo",              "category": "Tents",         "price": 299.99, "weight":  850},
    {"id": "P004", "name": "ArcticDown -20°C Sleeping Bag", "category": "Sleeping Bags", "price": 389.99, "weight": 1400},
    {"id": "P005", "name": "SummerLight +5°C Sleeping Bag", "category": "Sleeping Bags", "price": 149.99, "weight":  700},
    {"id": "P006", "name": "Osprey Atmos 65L Backpack",     "category": "Backpacks",     "price": 289.99, "weight": 1980},
    {"id": "P007", "name": "DayHiker 22L Daypack",          "category": "Backpacks",     "price":  89.99, "weight":  580},
]

def embed(text: str) -> list[float]:
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return response.data[0].embedding

def product_text(p: dict) -> str:
    return f"{p['name']}: {p['category']} product, ${p['price']:.2f}, {p['weight']}g"
```

---

## Option A: Chroma (Local, No Setup)

Chroma is the easiest way to get started — pure Python, runs in-memory or on-disk:

```python
# option_a_chroma.py
import chromadb
from shared import PRODUCTS, embed, product_text
import time

print("=== Option A: ChromaDB (Local) ===\n")

# In-memory collection (no persistence — great for prototyping)
chroma = chromadb.Client()
collection = chroma.create_collection("outdoorgear_products")

# Ingest
start = time.time()
collection.add(
    ids=[p["id"] for p in PRODUCTS],
    embeddings=[embed(product_text(p)) for p in PRODUCTS],
    documents=[product_text(p) for p in PRODUCTS],
    metadatas=[{"category": p["category"], "price": p["price"]} for p in PRODUCTS],
)
ingest_ms = (time.time() - start) * 1000

# Query
query = "lightweight tent for solo backpacking"
start = time.time()
results = collection.query(
    query_embeddings=[embed(query)],
    n_results=3,
)
query_ms = (time.time() - start) * 1000

print(f"Ingest: {ingest_ms:.0f}ms | Query: {query_ms:.0f}ms")
print(f"\nTop 3 results for '{query}':")
for doc, dist in zip(results["documents"][0], results["distances"][0]):
    similarity = 1 - dist  # Chroma returns distance, not similarity
    print(f"  {similarity:.3f} | {doc}")

# Filtered query (Chroma supports simple metadata filtering)
start = time.time()
filtered = collection.query(
    query_embeddings=[embed(query)],
    n_results=3,
    where={"category": "Tents"},   # ← metadata filter
)
filtered_ms = (time.time() - start) * 1000

print(f"\nFiltered to 'Tents' only ({filtered_ms:.0f}ms):")
for doc in filtered["documents"][0]:
    print(f"  {doc}")
```

---

## Option B: Qdrant (Local Server Mode)

Qdrant offers advanced filtering and scales to hundreds of millions of vectors:

```bash
# Run Qdrant locally with Docker (or use Qdrant Cloud free tier)
docker run -p 6333:6333 qdrant/qdrant
```

```python
# option_b_qdrant.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, Range
from shared import PRODUCTS, embed, product_text
import time

print("=== Option B: Qdrant (Local) ===\n")

client = QdrantClient("localhost", port=6333)

COLLECTION = "outdoorgear"
VECTOR_SIZE = 1536  # text-embedding-3-small

# Create collection
client.recreate_collection(
    collection_name=COLLECTION,
    vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
)

# Ingest with payload (rich metadata support)
start = time.time()
points = [
    PointStruct(
        id=int(p["id"][1:]),   # P001 → 1
        vector=embed(product_text(p)),
        payload={
            "id":       p["id"],
            "name":     p["name"],
            "category": p["category"],
            "price":    p["price"],
            "weight":   p["weight"],
        },
    )
    for p in PRODUCTS
]
client.upsert(collection_name=COLLECTION, points=points)
ingest_ms = (time.time() - start) * 1000

# Semantic search
query = "something warm for cold winter nights"
start = time.time()
results = client.search(
    collection_name=COLLECTION,
    query_vector=embed(query),
    limit=3,
)
query_ms = (time.time() - start) * 1000

print(f"Ingest: {ingest_ms:.0f}ms | Query: {query_ms:.0f}ms")
print(f"\nTop 3 for '{query}':")
for r in results:
    print(f"  {r.score:.3f} | [{r.payload['id']}] {r.payload['name']}")

# Advanced filter: Tents under $300
start = time.time()
filtered = client.search(
    collection_name=COLLECTION,
    query_vector=embed("lightweight shelter"),
    limit=3,
    query_filter=Filter(
        must=[
            FieldCondition(key="category", match=MatchValue(value="Tents")),
            FieldCondition(key="price", range=Range(lte=300.0)),
        ]
    ),
)
filtered_ms = (time.time() - start) * 1000

print(f"\nTents under $300 ({filtered_ms:.0f}ms):")
for r in filtered:
    print(f"  {r.score:.3f} | [{r.payload['id']}] {r.payload['name']} ${r.payload['price']:.2f}")
```

---

## Option C: pgvector (Azure PostgreSQL or Local)

See [Lab 031](lab-031-pgvector-semantic-search.md) for the full pgvector setup. Quick comparison:

```python
# option_c_pgvector_query.py
import psycopg2
import os
from shared import embed

# Using Azure PostgreSQL with pgvector
conn = psycopg2.connect(
    host=os.environ["PG_HOST"],
    dbname=os.environ["PG_DATABASE"],
    user=os.environ["PG_USER"],
    password=os.environ["PG_PASSWORD"],
    sslmode="require",
)
cur = conn.cursor()

query_vec = embed("lightweight tent for solo backpacking")
query_str = "[" + ",".join(str(v) for v in query_vec) + "]"

# Cosine similarity search using <=> operator
cur.execute("""
    SELECT p.name, p.category, p.price_usd,
           1 - (pe.embedding <=> %s::vector) AS similarity
    FROM product_embeddings pe
    JOIN products p ON p.id = pe.product_id
    ORDER BY pe.embedding <=> %s::vector
    LIMIT 3;
""", [query_str, query_str])

print("=== Option C: pgvector ===")
for name, category, price, sim in cur.fetchall():
    print(f"  {sim:.3f} | {name} ({category}) ${price:.2f}")
```

---

## Option D: Azure AI Search (Hybrid Search)

Azure AI Search uniquely supports **hybrid search**: vector + BM25 keyword search combined with semantic reranking:

```python
# option_d_azure_search.py
# pip install azure-search-documents
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from shared import embed
import os

client = SearchClient(
    endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
    index_name="outdoorgear-products",
    credential=AzureKeyCredential(os.environ["AZURE_SEARCH_KEY"]),
)

query = "lightweight backpacking shelter"
query_vec = embed(query)

# Hybrid search: vector + keyword + semantic reranking
results = client.search(
    search_text=query,           # BM25 keyword search
    vector_queries=[
        VectorizedQuery(
            vector=query_vec,
            k_nearest_neighbors=3,
            fields="embedding",  # the vector field in your index
        )
    ],
    query_type="semantic",       # semantic reranking (requires Semantic tier)
    semantic_configuration_name="default",
    top=3,
)

print("=== Option D: Azure AI Search (Hybrid) ===")
for r in results:
    print(f"  @score={r['@search.score']:.3f} | [{r['id']}] {r['name']}")
```

---

## Decision Framework

```
Start here:
         ↓
Already using PostgreSQL?
  → YES → Use pgvector (Lab 031)
  → NO  ↓

Need Azure-native + hybrid search?
  → YES → Azure AI Search
  → NO  ↓

Local dev / prototype?
  → YES → Chroma (zero setup)
  → NO  ↓

Need advanced filtering + high scale?
  → YES → Qdrant
  → NO  → Chroma or pgvector
```

---

## Comparison Table

| | pgvector | Chroma | Qdrant | Azure AI Search |
|---|---|---|---|---|
| **Setup** | Medium (DB needed) | Minimal | Easy (Docker) | Medium (Azure) |
| **Local dev** | ✅ (Docker) | ✅ (in-memory) | ✅ (Docker) | ❌ (Azure only) |
| **Hybrid search** | ✅ (manual) | ❌ | ✅ | ✅ (built-in) |
| **Filtering** | SQL WHERE | Basic metadata | Advanced | Full OData |
| **Scale** | Moderate (< 1M) | Small (< 100K) | High (> 100M) | High (enterprise) |
| **Azure integration** | ✅ (managed PG) | ❌ | Partial | ✅ (native) |
| **Cost (free tier)** | Free tier PG | Free | Qdrant Cloud free | 1 index free |

---

## 🧠 Knowledge Check

??? question "1. What is hybrid search, and why is it often better than pure vector search?"
    **Hybrid search** combines **vector (semantic) search** with **keyword (BM25) search** and ranks results using both signals. Vector search excels at semantic understanding ("warm shelter" → sleeping bag) but can miss exact matches (a specific product ID). BM25 is excellent for exact keyword matches but misses synonyms. Combining them outperforms either alone, especially for product names, SKUs, and specialized terminology.

??? question "2. Why would you choose pgvector over a dedicated vector database like Qdrant?"
    If you already have **PostgreSQL as your primary database**, pgvector adds vector search without adding another service to operate, maintain, and pay for. The data lives alongside your relational data — you can JOIN product records with their embeddings in a single query. For most applications under 1M vectors, pgvector's performance is excellent. Choose Qdrant when you need > 100M vectors or very advanced filtering.

??? question "3. What is the IVFFlat index in pgvector, and when should you use HNSW instead?"
    **IVFFlat** (Inverted File Index with Flat quantization): fast to build, uses less memory, good for datasets that don't change frequently. Uses approximate search — lists parameter controls recall/speed trade-off. **HNSW** (Hierarchical Navigable Small World): better recall, faster queries, but higher memory usage and slower to build. Use IVFFlat for datasets < 1M that don't change much; use HNSW for frequently updated datasets or when recall is critical. Both require pgvector ≥ 0.5.0.

---

## Summary

For the **OutdoorGear learning hub scenario** (< 10K products, Azure infrastructure, team knows SQL):

**Recommended: pgvector** on Azure Database for PostgreSQL Flexible Server.

- No new service to learn
- SQL + vector in one query
- Free tier available
- Production-ready with Lab 031 migrations

---

## Next Steps

- **Build the pgvector setup:** → [Lab 031 — pgvector Semantic Search](lab-031-pgvector-semantic-search.md)
- **Full RAG application:** → [Lab 022 — RAG with GitHub Models + pgvector](lab-022-rag-github-models-pgvector.md)
- **Enterprise RAG with evaluation:** → [Lab 042 — Enterprise RAG](lab-042-enterprise-rag.md)
