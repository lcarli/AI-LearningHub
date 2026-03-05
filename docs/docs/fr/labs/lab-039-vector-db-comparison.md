---
tags: [vector-db, rag, azure, production, L300]
---
# Lab 039 : Comparaison des bases de données vectorielles

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/rag/">📚 RAG</a></span>
  <span><strong>Durée :</strong> ~50 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Free</span> — Toutes les options ont des niveaux gratuits ou un mode local</span>
</div>

## Ce que vous apprendrez

- Comprendre les différences clés entre les principales bases de données vectorielles
- Comparer **pgvector**, **Chroma**, **Qdrant** et **Azure AI Search** sur la même tâche
- Évaluer chacune sur : complexité de mise en place, vitesse de requête, filtrage, intégration cloud
- Choisir la bonne base de données vectorielle pour les besoins de votre agent

---

## Introduction

Le choix d'une base de données vectorielle est l'une des décisions d'architecture les plus importantes pour un agent basé sur RAG. Le « meilleur » choix dépend de la stack existante de votre équipe, des exigences de mise à l'échelle, des besoins de filtrage et de la stratégie cloud.

**Les candidats :**

| Base de données | Type | Option gratuite | Idéal pour |
|----------|------|-------------|---------|
| **pgvector** | Extension PostgreSQL | Azure free tier / local | Équipes utilisant déjà PostgreSQL |
| **Chroma** | Embarqué / serveur | Entièrement open-source | Développement local, petits projets |
| **Qdrant** | BD vectorielle dédiée | Qdrant Cloud free tier | Production à grande échelle, filtrage avancé |
| **Azure AI Search** | Service Azure | Free tier (1 index) | Azure natif, recherche hybride, entreprise |

---

## Prérequis

```bash
# Install all clients
pip install chromadb qdrant-client openai

# For Azure AI Search (optional)
pip install azure-search-documents
```

Pas de clés API nécessaires pour Chroma (local) et Qdrant (mode local).
GitHub Token requis pour les embeddings :
```bash
export GITHUB_TOKEN=<your PAT>
```

---

## Configuration : Fonction d'embedding partagée

Les quatre tests utilisent les mêmes données produit OutdoorGear et le même modèle d'embedding :

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

## Option A : Chroma (local, sans configuration)

Chroma est la façon la plus simple de démarrer — pur Python, s'exécute en mémoire ou sur disque :

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

## Option B : Qdrant (mode serveur local)

Qdrant offre un filtrage avancé et passe à l'échelle à des centaines de millions de vecteurs :

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

## Option C : pgvector (Azure PostgreSQL ou local)

Voir le [Lab 031](lab-031-pgvector-semantic-search.md) pour la configuration complète de pgvector. Comparaison rapide :

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

## Option D : Azure AI Search (recherche hybride)

Azure AI Search prend en charge de manière unique la **recherche hybride** : recherche vectorielle + BM25 par mots-clés combinée avec un re-classement sémantique :

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

## Cadre de décision

```
Commencez ici :
         ↓
Utilisez-vous déjà PostgreSQL ?
  → OUI → Utilisez pgvector (Lab 031)
  → NON ↓

Besoin d'Azure natif + recherche hybride ?
  → OUI → Azure AI Search
  → NON ↓

Développement local / prototype ?
  → OUI → Chroma (zéro configuration)
  → NON ↓

Besoin de filtrage avancé + grande échelle ?
  → OUI → Qdrant
  → NON → Chroma ou pgvector
```

---

## Tableau comparatif

| | pgvector | Chroma | Qdrant | Azure AI Search |
|---|---|---|---|---|
| **Configuration** | Moyenne (BD nécessaire) | Minimale | Facile (Docker) | Moyenne (Azure) |
| **Dev local** | ✅ (Docker) | ✅ (en mémoire) | ✅ (Docker) | ❌ (Azure uniquement) |
| **Recherche hybride** | ✅ (manuelle) | ❌ | ✅ | ✅ (intégrée) |
| **Filtrage** | SQL WHERE | Métadonnées basiques | Avancé | OData complet |
| **Échelle** | Modérée (< 1M) | Petite (< 100K) | Grande (> 100M) | Grande (entreprise) |
| **Intégration Azure** | ✅ (PG managé) | ❌ | Partielle | ✅ (native) |
| **Coût (niveau gratuit)** | Free tier PG | Gratuit | Qdrant Cloud free | 1 index gratuit |

---

## 🧠 Quiz de connaissances

??? question "1. Qu'est-ce que la recherche hybride et pourquoi est-elle souvent meilleure que la recherche vectorielle pure ?"
    La **recherche hybride** combine la **recherche vectorielle (sémantique)** avec la **recherche par mots-clés (BM25)** et classe les résultats en utilisant les deux signaux. La recherche vectorielle excelle dans la compréhension sémantique (« abri chaud » → sac de couchage) mais peut manquer les correspondances exactes (un identifiant produit spécifique). BM25 est excellent pour les correspondances exactes de mots-clés mais manque les synonymes. Les combiner surpasse l'un ou l'autre seul, en particulier pour les noms de produits, les SKU et la terminologie spécialisée.

??? question "2. Pourquoi choisiriez-vous pgvector plutôt qu'une base de données vectorielle dédiée comme Qdrant ?"
    Si vous avez déjà **PostgreSQL comme base de données principale**, pgvector ajoute la recherche vectorielle sans ajouter un autre service à exploiter, maintenir et payer. Les données cohabitent avec vos données relationnelles — vous pouvez faire un JOIN entre les enregistrements produit et leurs embeddings dans une seule requête. Pour la plupart des applications de moins de 1M de vecteurs, les performances de pgvector sont excellentes. Choisissez Qdrant quand vous avez besoin de > 100M de vecteurs ou d'un filtrage très avancé.

??? question "3. Qu'est-ce que l'index IVFFlat dans pgvector et quand devriez-vous utiliser HNSW à la place ?"
    **IVFFlat** (Inverted File Index with Flat quantization) : rapide à construire, utilise moins de mémoire, bon pour les jeux de données qui ne changent pas fréquemment. Utilise une recherche approximative — le paramètre lists contrôle le compromis rappel/vitesse. **HNSW** (Hierarchical Navigable Small World) : meilleur rappel, requêtes plus rapides, mais utilisation mémoire plus élevée et construction plus lente. Utilisez IVFFlat pour les jeux de données < 1M qui ne changent pas beaucoup ; utilisez HNSW pour les jeux de données fréquemment mis à jour ou quand le rappel est critique. Les deux nécessitent pgvector ≥ 0.5.0.

---

## Résumé

Pour le **scénario du hub d'apprentissage OutdoorGear** (< 10K produits, infrastructure Azure, équipe connaissant SQL) :

**Recommandé : pgvector** sur Azure Database for PostgreSQL Flexible Server.

- Pas de nouveau service à apprendre
- SQL + vectoriel dans une seule requête
- Niveau gratuit disponible
- Prêt pour la production avec les migrations du Lab 031

---

## Prochaines étapes

- **Construire la configuration pgvector :** → [Lab 031 — Recherche sémantique pgvector](lab-031-pgvector-semantic-search.md)
- **Application RAG complète :** → [Lab 022 — RAG avec GitHub Models + pgvector](lab-022-rag-github-models-pgvector.md)
- **RAG d'entreprise avec évaluation :** → [Lab 042 — RAG d'entreprise](lab-042-enterprise-rag.md)
