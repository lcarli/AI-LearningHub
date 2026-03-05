---
tags: [vector-db, rag, azure, production, L300]
---
# Lab 039: Comparação de Bancos de Dados Vetoriais

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/rag/">📚 RAG</a></span>
  <span><strong>Tempo:</strong> ~50 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Free</span> — Todas as opções têm planos gratuitos ou modo local</span>
</div>

## O que Você Vai Aprender

- Entender as principais diferenças entre os grandes bancos de dados vetoriais
- Comparar **pgvector**, **Chroma**, **Qdrant** e **Azure AI Search** na mesma tarefa
- Avaliar cada um em: complexidade de configuração, velocidade de consulta, filtragem, integração com nuvem
- Escolher o banco de dados vetorial certo para os requisitos do seu agente

---

## Introdução

Escolher um banco de dados vetorial é uma das decisões arquiteturais mais consequentes para um agente baseado em RAG. A "melhor" escolha depende da stack existente da sua equipe, requisitos de escala, necessidades de filtragem e estratégia de nuvem.

**Os candidatos:**

| Banco de Dados | Tipo | Opção gratuita | Melhor para |
|----------|------|-------------|---------|
| **pgvector** | Extensão PostgreSQL | Azure free tier / local | Equipes que já usam PostgreSQL |
| **Chroma** | Embutido / servidor | Totalmente open-source | Desenvolvimento local, projetos pequenos |
| **Qdrant** | BD vetorial dedicado | Qdrant Cloud free tier | Produção em alta escala, filtragem avançada |
| **Azure AI Search** | Serviço Azure | Free tier (1 índice) | Nativo do Azure, busca híbrida, enterprise |

---

## Pré-requisitos

```bash
# Install all clients
pip install chromadb qdrant-client openai

# For Azure AI Search (optional)
pip install azure-search-documents
```

Nenhuma chave de API necessária para Chroma (local) e Qdrant (modo local).
GitHub Token necessário para embeddings:
```bash
export GITHUB_TOKEN=<your PAT>
```

---

## Configuração: Função de Embedding Compartilhada

Todos os quatro testes usam os mesmos dados de produtos OutdoorGear e o mesmo modelo de embedding:

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

## Opção A: Chroma (Local, Sem Configuração)

Chroma é a maneira mais fácil de começar — Python puro, roda em memória ou em disco:

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

## Opção B: Qdrant (Modo Servidor Local)

Qdrant oferece filtragem avançada e escala para centenas de milhões de vetores:

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

## Opção C: pgvector (Azure PostgreSQL ou Local)

Veja o [Lab 031](lab-031-pgvector-semantic-search.md) para a configuração completa do pgvector. Comparação rápida:

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

## Opção D: Azure AI Search (Busca Híbrida)

Azure AI Search suporta de forma única a **busca híbrida**: busca vetorial + busca por palavras-chave BM25 combinada com reranqueamento semântico:

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

## Framework de Decisão

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

## Tabela Comparativa

| | pgvector | Chroma | Qdrant | Azure AI Search |
|---|---|---|---|---|
| **Configuração** | Média (BD necessário) | Mínima | Fácil (Docker) | Média (Azure) |
| **Dev local** | ✅ (Docker) | ✅ (em memória) | ✅ (Docker) | ❌ (apenas Azure) |
| **Busca híbrida** | ✅ (manual) | ❌ | ✅ | ✅ (integrada) |
| **Filtragem** | SQL WHERE | Metadados básicos | Avançada | OData completo |
| **Escala** | Moderada (< 1M) | Pequena (< 100K) | Alta (> 100M) | Alta (enterprise) |
| **Integração Azure** | ✅ (PG gerenciado) | ❌ | Parcial | ✅ (nativa) |
| **Custo (plano gratuito)** | Free tier PG | Gratuito | Qdrant Cloud gratuito | 1 índice gratuito |

---

## 🧠 Verificação de Conhecimento

??? question "1. O que é busca híbrida e por que ela costuma ser melhor que busca vetorial pura?"
    **Busca híbrida** combina **busca vetorial (semântica)** com **busca por palavras-chave (BM25)** e classifica os resultados usando ambos os sinais. A busca vetorial se destaca na compreensão semântica ("abrigo quente" → saco de dormir) mas pode perder correspondências exatas (um ID de produto específico). O BM25 é excelente para correspondências exatas de palavras-chave mas perde sinônimos. Combinar ambos supera qualquer um isoladamente, especialmente para nomes de produtos, SKUs e terminologia especializada.

??? question "2. Por que você escolheria pgvector em vez de um banco de dados vetorial dedicado como o Qdrant?"
    Se você já tem **PostgreSQL como seu banco de dados principal**, o pgvector adiciona busca vetorial sem adicionar outro serviço para operar, manter e pagar. Os dados ficam junto com seus dados relacionais — você pode fazer JOIN de registros de produtos com seus embeddings em uma única consulta. Para a maioria das aplicações com menos de 1M de vetores, o desempenho do pgvector é excelente. Escolha Qdrant quando precisar de > 100M de vetores ou filtragem muito avançada.

??? question "3. O que é o índice IVFFlat no pgvector e quando você deve usar HNSW em vez dele?"
    **IVFFlat** (Inverted File Index com quantização Flat): rápido de construir, usa menos memória, bom para conjuntos de dados que não mudam frequentemente. Usa busca aproximada — o parâmetro lists controla o trade-off entre recall e velocidade. **HNSW** (Hierarchical Navigable Small World): melhor recall, consultas mais rápidas, mas maior uso de memória e mais lento para construir. Use IVFFlat para conjuntos de dados < 1M que não mudam muito; use HNSW para conjuntos de dados frequentemente atualizados ou quando o recall é crítico. Ambos requerem pgvector ≥ 0.5.0.

---

## Resumo

Para o **cenário do OutdoorGear learning hub** (< 10K produtos, infraestrutura Azure, equipe conhece SQL):

**Recomendado: pgvector** no Azure Database for PostgreSQL Flexible Server.

- Nenhum serviço novo para aprender
- SQL + vetorial em uma única consulta
- Free tier disponível
- Pronto para produção com as migrações do Lab 031

---

## Próximos Passos

- **Monte a configuração pgvector:** → [Lab 031 — Busca Semântica com pgvector](lab-031-pgvector-semantic-search.md)
- **Aplicação RAG completa:** → [Lab 022 — RAG com GitHub Models + pgvector](lab-022-rag-github-models-pgvector.md)
- **RAG Enterprise com avaliação:** → [Lab 042 — RAG Enterprise](lab-042-enterprise-rag.md)