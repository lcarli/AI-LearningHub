---
tags: [rag, pgvector, python, free, github-models]
---
# Lab 022 : Pipeline RAG avec GitHub Models + pgvector

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/rag/">RAG</a></span>
  <span><strong>Durée :</strong> ~50 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-github">GitHub Free</span> + <span class="level-badge cost-free">Docker (local)</span></span>
</div>

## Ce que vous apprendrez

- Démarrer **pgvector** (PostgreSQL + vecteurs) localement via Docker
- Générer des embeddings avec **GitHub Models** (`text-embedding-3-small`) — gratuit
- **Ingérer** des documents : découper, vectoriser, stocker dans pgvector
- **Interroger** avec la recherche par similarité sémantique (opérateur cosinus `<=>`)
- Construire un **pipeline RAG complet** (récupérer → augmenter → générer)

---

## Introduction

Dans le [Lab 006](lab-006-what-is-rag.md) vous avez appris la théorie du RAG. Ici vous construisez la vraie chose — un système RAG fonctionnel utilisant uniquement des outils gratuits : GitHub Models pour les embeddings + la génération, et pgvector fonctionnant localement dans Docker.

!!! tip "Jeu de données pré-construit inclus"
    Ce lab utilise le **jeu de données OutdoorGear** — 25 produits, FAQs et politiques d'entreprise, prêts à être ingérés.
    📥 [`data/products.csv`](https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/products.csv) · [`data/knowledge-base.json`](https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/knowledge-base.json)

    ```bash
    # Download the sample data
    curl -O https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/products.csv
    curl -O https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/knowledge-base.json
    ```

---

## Prérequis

- Docker Desktop — gratuit : https://www.docker.com/products/docker-desktop
- Python 3.11+
- `GITHUB_TOKEN` configuré (depuis le [Lab 013](lab-013-github-models.md))

```bash
pip install openai psycopg2-binary python-dotenv
```

---

## Exercice du lab

### Étape 1 : Démarrer pgvector avec Docker

```bash
docker run -d \
  --name pgvector-rag \
  -e POSTGRES_PASSWORD=ragpass \
  -e POSTGRES_DB=ragdb \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

Vérifiez qu'il fonctionne :
```bash
docker ps | grep pgvector-rag
```

### Étape 2 : Créer le schéma de base de données

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

### Étape 3 : Ingérer les documents du jeu de données

Le jeu de données se trouve dans le dépôt. Téléchargez-le (ou utilisez l'URL directement) :

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

### Étape 4 : Interroger avec la recherche sémantique

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

### Étape 5 : Le pipeline de réponse RAG

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

## Comprendre les résultats

!!! tip "Scores de similarité"
    - **> 0.85** — correspondance très forte (le document répond directement à la question)
    - **0.70–0.85** — lié (peut être pertinent)
    - **< 0.70** — correspondance faible (probablement pas utile, envisagez de filtrer)

Ajoutez un filtre de seuil pour éviter d'utiliser des documents à faible confiance :

```python
docs = [d for d in search(question, top_k=5) if d["similarity"] > 0.75]
if not docs:
    return "I don't have information about that in my knowledge base."
```

---

## Nettoyage

```bash
docker stop pgvector-rag && docker rm pgvector-rag
```

---

## Prochaines étapes

- **RAG agentique** (réécriture de requêtes, multi-hop) : → [Lab 026 — Pattern RAG agentique](lab-026-agentic-rag.md)
- **RAG avec Semantic Kernel** : → [Lab 023 — Plugins SK, mémoire & planificateurs](lab-023-sk-plugins-memory.md)
- **pgvector en production sur Azure** : → [Lab 031 — pgvector sur Azure](lab-031-pgvector-semantic-search.md)
