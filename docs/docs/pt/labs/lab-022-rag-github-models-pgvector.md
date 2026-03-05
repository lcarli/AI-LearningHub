---
tags: [rag, pgvector, python, free, github-models]
---
# Lab 022: Pipeline RAG com GitHub Models + pgvector

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/rag/">RAG</a></span>
  <span><strong>Tempo:</strong> ~50 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-github">GitHub Gratuito</span> + <span class="level-badge cost-free">Docker (local)</span></span>
</div>

## O que Você Vai Aprender

- Iniciar o **pgvector** (PostgreSQL + vetores) localmente via Docker
- Gerar embeddings com o **GitHub Models** (`text-embedding-3-small`) — gratuito
- **Ingerir** documentos: fragmentar, gerar embeddings, armazenar no pgvector
- **Consultar** com busca por similaridade semântica (operador cosseno `<=>`)
- Construir um pipeline completo de **resposta RAG** (recuperar → aumentar → gerar)

---

## Introdução

No [Lab 006](lab-006-what-is-rag.md) você aprendeu a teoria do RAG. Aqui você constrói a coisa real — um sistema RAG funcional usando apenas ferramentas gratuitas: GitHub Models para embeddings + geração, e pgvector rodando localmente no Docker.

!!! tip "Dataset pré-construído incluído"
    Este lab usa o **dataset de exemplo OutdoorGear** — 25 produtos, FAQs e políticas da empresa, prontos para ingestão.  
    📥 [`data/products.csv`](https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/products.csv) · [`data/knowledge-base.json`](https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/knowledge-base.json)

    ```bash
    # Baixar os dados de exemplo
    curl -O https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/products.csv
    curl -O https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/knowledge-base.json
    ```

---

## Pré-requisitos

- Docker Desktop — gratuito: https://www.docker.com/products/docker-desktop
- Python 3.11+
- `GITHUB_TOKEN` configurado (do [Lab 013](lab-013-github-models.md))

```bash
pip install openai psycopg2-binary python-dotenv
```

---

## Exercício do Lab

### Passo 1: Iniciar o pgvector com Docker

```bash
docker run -d   --name pgvector-rag   -e POSTGRES_PASSWORD=ragpass   -e POSTGRES_DB=ragdb   -p 5432:5432   pgvector/pgvector:pg16
```

Verifique se está rodando:
```bash
docker ps | grep pgvector-rag
```

### Passo 2: Criar o schema do banco de dados

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

### Passo 3: Ingerir documentos do dataset de exemplo

O dataset de exemplo está no repositório. Baixe-o (ou use a URL diretamente):

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
            "content": f"Q: {faq['question']}
A: {faq['answer']}",
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
print(f"
✅ Ingested {len(documents)} documents.")
```

```bash
python ingest.py
# Prepared 42 documents to ingest
# ✅ Ingested 42 documents.
```

### Passo 4: Consultar com busca semântica

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

### Passo 5: O pipeline de resposta RAG

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
    context = "

".join([
        f"**{d['title']}** (similarity: {d['similarity']:.2f})
{d['content']}"
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
                "content": f"Context:
{context}

Question: {question}"
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
    print(f"
❓ {q}")
    print(f"💬 {answer(q)}")
    print("—" * 60)
```

```bash
python rag.py
```

---

## Entendendo os Resultados

!!! tip "Scores de similaridade"
    - **> 0.85** — correspondência muito forte (o documento responde diretamente à pergunta)
    - **0.70–0.85** — relacionado (pode ser relevante)  
    - **< 0.70** — correspondência fraca (provavelmente não é útil, considere filtrar)

Adicione um filtro de limiar para evitar usar documentos de baixa confiança:

```python
docs = [d for d in search(question, top_k=5) if d["similarity"] > 0.75]
if not docs:
    return "I don't have information about that in my knowledge base."
```

---

## Limpeza

```bash
docker stop pgvector-rag && docker rm pgvector-rag
```

---

## Próximos Passos

- **RAG Agêntico** (reescrita de consulta, multi-hop): → [Lab 026 — Padrão RAG Agêntico](lab-026-agentic-rag.md)
- **RAG com Semantic Kernel**: → [Lab 023 — Plugins, Memória e Planners do SK](lab-023-sk-plugins-memory.md)
- **pgvector em produção no Azure**: → [Lab 031 — pgvector no Azure](lab-031-pgvector-semantic-search.md)
