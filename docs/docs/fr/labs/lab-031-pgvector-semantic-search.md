---
tags: [pgvector, rag, azure, azure-required]
---
# Lab 031: pgvector Semantic Search on Azure

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Path:</strong> <a href="../paths/rag/">RAG</a></span>
  <span><strong>Time:</strong> ~60 min</span>
  <span><strong>💰 Cost:</strong> ~$15/month (PostgreSQL Flexible Server Burstable B1ms)</span>
</div>

!!! info "Traduction en cours"
    Ce lab est en cours de traduction. Le contenu ci-dessous est en anglais.



!!! warning "Azure subscription required"
    This lab deploys Azure PostgreSQL Flexible Server. → [Prerequisites guide](../prerequisites.md)

## What You'll Learn

- Deploy **Azure PostgreSQL Flexible Server** with pgvector enabled via one click
- Connect securely with SSL and firewall rules
- Migrate the RAG pipeline from [Lab 022](lab-022-rag-github-models-pgvector.md) to Azure
- Use **Azure AI Services** for embeddings (or keep using GitHub Models — free)
- Expose the vector store as an **MCP tool** for agents

---

## Deploy Infrastructure

### Option A — Deploy to Azure (one click)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Flcarli%2FAI-LearningHub%2Fmain%2Finfra%2Flab-031-pgvector%2Fazuredeploy.json)

This deploys:
- PostgreSQL Flexible Server (Burstable B1ms, ~$15/month)
- pgvector extension enabled
- Database `ragdb` pre-created
- Azure services firewall rule

**Parameters you'll set:**
- `administratorLoginPassword` — your database password (note it down!)
- `location` — choose a region close to you

### Option B — Azure CLI (Bicep)

```bash
# Clone the repo (if you haven't)
git clone https://github.com/lcarli/AI-LearningHub.git && cd AI-LearningHub

# Create resource group
az group create --name rg-ai-labs-rag --location eastus

# Deploy (replace the password)
az deployment group create \
  --resource-group rg-ai-labs-rag \
  --template-file infra/lab-031-pgvector/main.bicep \
  --parameters administratorLoginPassword="YourP@ssw0rd!"

# Get the server hostname from outputs
az deployment group show \
  --resource-group rg-ai-labs-rag \
  --name main \
  --query properties.outputs.serverFqdn.value -o tsv
```

---

## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-031/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `migrations` | Database migration files | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-031/migrations) |

---

## Lab Exercise

### Step 1: Set connection environment variables

After deployment, save your connection details:

```bash
# From the Azure portal: PostgreSQL server → Connection strings
export PG_HOST="your-server.postgres.database.azure.com"
export PG_USER="pgadmin"
export PG_PASSWORD="YourP@ssw0rd!"
export PG_DATABASE="ragdb"
```

### Step 2: Connect and verify pgvector

```python
import os, psycopg2

conn = psycopg2.connect(
    host=os.environ["PG_HOST"],
    port=5432,
    dbname=os.environ["PG_DATABASE"],
    user=os.environ["PG_USER"],
    password=os.environ["PG_PASSWORD"],
    sslmode="require",          # ← Required for Azure PostgreSQL
)
cur = conn.cursor()

# Verify pgvector is installed
cur.execute("SELECT extversion FROM pg_extension WHERE extname = 'vector';")
version = cur.fetchone()
print(f"pgvector version: {version[0] if version else 'NOT INSTALLED'}")
# pgvector version: 0.7.0

cur.close()
conn.close()
```

### Step 3: Create schema

```python
# setup_db.py
import os, psycopg2

def get_conn():
    return psycopg2.connect(
        host=os.environ["PG_HOST"], port=5432,
        dbname=os.environ["PG_DATABASE"],
        user=os.environ["PG_USER"],
        password=os.environ["PG_PASSWORD"],
        sslmode="require",
    )

conn = get_conn()
cur = conn.cursor()

cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
cur.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id          SERIAL PRIMARY KEY,
        title       TEXT NOT NULL,
        content     TEXT NOT NULL,
        embedding   vector(1536),
        source      TEXT,
        created_at  TIMESTAMPTZ DEFAULT NOW()
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
print("Schema ready on Azure PostgreSQL!")
```

### Step 4: Ingest the sample dataset

Download and ingest the OutdoorGear sample data:

```bash
curl -O https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/products.csv
curl -O https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/knowledge-base.json
```

Re-use the `ingest.py` from [Lab 022](lab-022-rag-github-models-pgvector.md#step-3-ingest-documents-from-the-sample-dataset), but update the connection to use Azure:

```python
# Use environment variables instead of hardcoded local values
conn = psycopg2.connect(
    host=os.environ["PG_HOST"], port=5432,
    dbname=os.environ["PG_DATABASE"],
    user=os.environ["PG_USER"],
    password=os.environ["PG_PASSWORD"],
    sslmode="require",          # ← Only change needed
)
```

### Step 5: Expose as an MCP tool

Wrap the search function as an MCP tool so any agent can query your knowledge base:

```python
# mcp_search_server.py
import os, asyncio, psycopg2
from mcp.server.fastmcp import FastMCP
from openai import OpenAI

mcp = FastMCP("OutdoorGear Search")
client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

def get_pg_conn():
    return psycopg2.connect(
        host=os.environ["PG_HOST"], port=5432,
        dbname=os.environ["PG_DATABASE"],
        user=os.environ["PG_USER"],
        password=os.environ["PG_PASSWORD"],
        sslmode="require",
    )

def embed(text: str) -> list[float]:
    return client.embeddings.create(
        model="text-embedding-3-small", input=text
    ).data[0].embedding

@mcp.tool()
def semantic_search(query: str, top_k: int = 3, source_filter: str = "") -> str:
    """Search the OutdoorGear knowledge base using semantic similarity."""
    query_vec = embed(query)
    conn = get_pg_conn()
    cur = conn.cursor()

    if source_filter:
        cur.execute("""
            SELECT title, content, source, 1 - (embedding <=> %s::vector) AS sim
            FROM documents WHERE source = %s
            ORDER BY embedding <=> %s::vector LIMIT %s
        """, (query_vec, source_filter, query_vec, top_k))
    else:
        cur.execute("""
            SELECT title, content, source, 1 - (embedding <=> %s::vector) AS sim
            FROM documents
            ORDER BY embedding <=> %s::vector LIMIT %s
        """, (query_vec, query_vec, top_k))

    rows = cur.fetchall()
    cur.close()
    conn.close()

    if not rows:
        return "No results found."

    return "\n\n".join([
        f"[{r[3]:.2f}] **{r[0]}** ({r[2]})\n{r[1][:300]}"
        for r in rows
    ])

if __name__ == "__main__":
    mcp.run(transport="stdio")
```

Add to `.vscode/mcp.json`:
```json
{
  "servers": {
    "outdoorgear-search": {
      "type": "stdio",
      "command": "python",
      "args": ["mcp_search_server.py"],
      "env": {
        "PG_HOST": "your-server.postgres.database.azure.com",
        "PG_USER": "pgadmin",
        "PG_PASSWORD": "YourP@ssw0rd!",
        "PG_DATABASE": "ragdb",
        "GITHUB_TOKEN": "${env:GITHUB_TOKEN}"
      }
    }
  }
}
```

---

## Cleanup

```bash
# Stop charges immediately
az group delete --name rg-ai-labs-rag --yes --no-wait
```

---


## 🧠 Knowledge Check

??? question "**Q1 (Run the Lab):** After running `001_init.sql` against your database, how many rows are in the `products` table? Run `SELECT COUNT(*) FROM products;` to verify."

    Run the migration then query the table.

    ??? success "✅ Reveal Answer"
        **7 rows**

        The migration seeds 7 OutdoorGear products: P001 (TrailBlazer Tent 2P), P002 (Summit Dome 4P), P003 (TrailBlazer Solo), P004 (ArcticDown -20°C), P005 (SummerLight +5°C), P006 (Osprey Atmos 65L), P007 (DayHiker 22L). Run `SELECT id, name, category FROM products ORDER BY id;` to see them all.

??? question "**Q2 (Run the Lab):** What type of index is created on the `product_embeddings` table, and which column does it index?"

    Open `lab-031/migrations/001_init.sql` and find the `CREATE INDEX` statement.

    ??? success "✅ Reveal Answer"
        **IVFFlat index on the `embedding` column**

        The migration creates: `CREATE INDEX ON product_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);`

        IVFFlat (Inverted File with Flat quantization) is an approximate nearest neighbor index — it's faster than exact search but sacrifices a small amount of recall. The `lists = 100` parameter defines the number of Voronoi cells for clustering. `vector_cosine_ops` means distances are computed using cosine similarity.

??? question "**Q3 (Multiple Choice):** You run `SELECT * FROM search_products_by_vector($1::vector, 3)` and get 3 results. What do the results represent?"

    - A) The 3 most recently inserted products
    - B) The 3 products with the highest price
    - C) The 3 products whose embedding vectors are most similar (closest cosine distance) to the query vector
    - D) 3 randomly selected products from the database

    ??? success "✅ Reveal Answer"
        **Correct: C**

        The `search_products_by_vector()` function performs an **approximate nearest neighbor (ANN) search** using the IVFFlat index. It computes cosine distance between the query vector and all stored product embeddings, then returns the `k` products with the smallest distance (= highest semantic similarity). The result represents the most semantically relevant products for the user's query.

---

## Next Steps

- **Row Level Security for multi-tenant agents:** → [Lab 032 — Row Level Security](lab-032-row-level-security.md)
- **Agentic RAG on top of this:** → [Lab 026 — Agentic RAG Pattern](lab-026-agentic-rag.md)
