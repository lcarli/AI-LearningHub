---
tags: [rag, pgvector, python, free, github-models]
---
# Lab 022: RAG Pipeline with GitHub Models + pgvector

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Path:</strong> <a href="../paths/rag/">RAG</a></span>
  <span><strong>Time:</strong> ~50 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-github">GitHub Free</span> + <span class="level-badge cost-free">Docker (local)</span></span>
</div>

!!! info "Traduction en cours"
    Ce lab est en cours de traduction. Le contenu ci-dessous est en anglais.



## What You'll Learn

- Spin up **pgvector** (PostgreSQL + vectors) locally via Docker
- Generate embeddings with **GitHub Models** (`text-embedding-3-small`) — free
- **Ingest** documents: chunk, embed, store in pgvector
- **Query** with semantic similarity search (`<=>` cosine operator)
- Build a full **RAG answer pipeline** (retrieve → augment → generate)

---

## Introduction

In [Lab 006](lab-006-what-is-rag.md) you learned RAG theory. Here you build the real thing — a working RAG system using only free tools: GitHub Models for embeddings + generation, and pgvector running locally in Docker.

!!! tip "Pre-built dataset included"
    This lab uses the **OutdoorGear sample dataset** — 25 products, FAQs, and company policies, ready to ingest.  
    📥 [`data/products.csv`](https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/products.csv) · [`data/knowledge-base.json`](https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/knowledge-base.json)

    ```bash
    # Download the sample data
    curl -O https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/products.csv
    curl -O https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/knowledge-base.json
    ```

---

## Prerequisites

- Docker Desktop — free: https://www.docker.com/products/docker-desktop
- Python 3.11+
- `GITHUB_TOKEN` set (from [Lab 013](lab-013-github-models.md))

```bash
pip install openai psycopg2-binary python-dotenv
```

---

## Lab Exercise

### Step 1: Start pgvector with Docker

```bash
docker run -d \
  --name pgvector-rag \
  -e POSTGRES_PASSWORD=ragpass \
  -e POSTGRES_DB=ragdb \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

Verify it's running:
```bash
docker ps | grep pgvector-rag
```

### Step 2: Create the database schema

```python
# setup_db.py
import psycopg2

conn = psycopg2.connect(
    host="localhost", port=5432,
    dbname="ragdb", user="postgres", password="ragpass"
)
cur = conn.cursor()

cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
cur.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id          SERIAL PRIMARY KEY,
        title       TEXT NOT NULL,
        content     TEXT NOT NULL,
        embedding   vector(1536),   -- text-embedding-3-small dimension
        source      TEXT
    );
""")
cur.execute("""
    CREATE INDEX IF NOT EXISTS documents_embedding_idx
    ON documents USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 10);
""")

conn.commit()
cur.close()
conn.close()
print("Database ready.")
```

```bash
python setup_db.py
```

### Step 3: Ingest documents from the sample dataset

The sample dataset lives in the repo. Download it (or use the URL directly):

```bash
curl -O https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/products.csv
curl -O https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/knowledge-base.json
```

```python
# ingest.py
import os, csv, json, psycopg2
from openai import OpenAI

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

def build_documents() -> list[dict]:
    """Load products.csv and knowledge-base.json into a flat list of documents."""
    docs = []

    # --- Products from CSV ---
    with open("products.csv") as f:
        for p in csv.DictReader(f):
            docs.append({
                "title": f"{p['name']} — Product Info",
                "content": (
                    f"{p['name']} ({p['category']}/{p['subcategory']}). "
                    f"SKU: {p['sku']}. Price: ${p['price']}. "
                    f"In stock: {p['in_stock']}. Weight: {p['weight_kg']}kg. "
                    f"Rating: {p['rating']}/5. {p['description']}"
                ),
                "source": "product-catalog",
            })

    # --- Policies, FAQs, and guides from JSON ---
    with open("knowledge-base.json") as f:
        kb = json.load(f)

    for section in kb["sections"].values():
        docs.append({
            "title": section["title"],
            "content": section["content"],
            "source": "policies",
        })

    for faq in kb["faqs"]:
        docs.append({
            "title": f"FAQ: {faq['question']}",
            "content": f"Q: {faq['question']}\nA: {faq['answer']}",
            "source": "faq",
        })

    for guide in kb["product_guides"]:
        docs.append({
            "title": guide["title"],
            "content": guide["content"],
            "source": "guide",
        })

    return docs

def get_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding

documents = build_documents()
print(f"Prepared {len(documents)} documents to ingest")

conn = psycopg2.connect(
    host="localhost", port=5432,
    dbname="ragdb", user="postgres", password="ragpass"
)
cur = conn.cursor()

for doc in documents:
    print(f"  Embedding: {doc['title'][:60]}")
    embedding = get_embedding(doc["content"])
    cur.execute(
        "INSERT INTO documents (title, content, embedding, source) VALUES (%s, %s, %s, %s)",
        (doc["title"], doc["content"], embedding, doc["source"])
    )

conn.commit()
cur.close()
conn.close()
print(f"\n✅ Ingested {len(documents)} documents.")
```

```bash
python ingest.py
# Prepared 42 documents to ingest
# ✅ Ingested 42 documents.
```

### Step 4: Query with semantic search

```python
# search.py
import os, psycopg2
from openai import OpenAI

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

def search(query: str, top_k: int = 3) -> list[dict]:
    # Embed the query
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query,
    )
    query_embedding = response.data[0].embedding

    # Cosine similarity search in pgvector
    conn = psycopg2.connect(
        host="localhost", port=5432,
        dbname="ragdb", user="postgres", password="ragpass"
    )
    cur = conn.cursor()
    cur.execute("""
        SELECT title, content, source,
               1 - (embedding <=> %s::vector) AS similarity
        FROM documents
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """, (query_embedding, query_embedding, top_k))

    results = [
        {"title": row[0], "content": row[1], "source": row[2], "similarity": row[3]}
        for row in cur.fetchall()
    ]
    cur.close()
    conn.close()
    return results

# Test
results = search("how waterproof are the boots?")
for r in results:
    print(f"[{r['similarity']:.3f}] {r['title']}")
```

### Step 5: The RAG answer pipeline

```python
# rag.py
import os
from openai import OpenAI
from search import search

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

def answer(question: str) -> str:
    # 1. Retrieve
    docs = search(question, top_k=3)

    # 2. Augment — build context
    context = "\n\n".join([
        f"**{d['title']}** (similarity: {d['similarity']:.2f})\n{d['content']}"
        for d in docs
    ])

    # 3. Generate
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful outdoor gear assistant. "
                    "Answer questions using ONLY the provided context. "
                    "If the context doesn't contain the answer, say so honestly. "
                    "Always cite which document your answer comes from."
                )
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {question}"
            }
        ],
    )
    return response.choices[0].message.content

# Test the full pipeline
questions = [
    "Can I return hiking boots I've already worn?",
    "How much does express shipping cost?",
    "What certification does the harness have?",
    "What are the tent dimensions?",
]

for q in questions:
    print(f"\n❓ {q}")
    print(f"💬 {answer(q)}")
    print("—" * 60)
```

```bash
python rag.py
```

---

## Understanding the Results

!!! tip "Similarity scores"
    - **> 0.85** — very strong match (the document directly answers the question)
    - **0.70–0.85** — related (might be relevant)  
    - **< 0.70** — weak match (probably not helpful, consider filtering)

Add a threshold filter to avoid using low-confidence documents:

```python
docs = [d for d in search(question, top_k=5) if d["similarity"] > 0.75]
if not docs:
    return "I don't have information about that in my knowledge base."
```

---

## Cleanup

```bash
docker stop pgvector-rag && docker rm pgvector-rag
```

---

## Next Steps

- **Agentic RAG** (query rewriting, multi-hop): → [Lab 026 — Agentic RAG Pattern](lab-026-agentic-rag.md)
- **RAG with Semantic Kernel**: → [Lab 023 — SK Plugins, Memory & Planners](lab-023-sk-plugins-memory.md)
- **Production pgvector on Azure**: → [Lab 031 — pgvector on Azure](lab-031-pgvector-semantic-search.md)
