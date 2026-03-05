---
tags: [pgvector, rag, azure, azure-required]
---
# Lab 031: pgvector Semantic Search on Azure

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/rag/">RAG</a></span>
  <span><strong>Tempo:</strong> ~60 min</span>
  <span><strong>💰 Custo:</strong> ~$15/mês (PostgreSQL Flexible Server Burstable B1ms)</span>
</div>

!!! warning "Assinatura do Azure necessária"
    Este lab implanta o Azure PostgreSQL Flexible Server. → [Guia de pré-requisitos](../prerequisites.md)

## O que Você Vai Aprender

- Implantar o **Azure PostgreSQL Flexible Server** com pgvector habilitado em um clique
- Conectar-se com segurança usando SSL e regras de firewall
- Migrar o pipeline RAG do [Lab 022](lab-022-rag-github-models-pgvector.md) para o Azure
- Usar o **Azure AI Services** para embeddings (ou continuar usando GitHub Models — gratuito)
- Expor o banco vetorial como uma **ferramenta MCP** para agentes

---

## Implantar Infraestrutura

### Opção A — Implantar no Azure (um clique)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Flcarli%2FAI-LearningHub%2Fmain%2Finfra%2Flab-031-pgvector%2Fazuredeploy.json)

Isso implanta:
- PostgreSQL Flexible Server (Burstable B1ms, ~$15/mês)
- Extensão pgvector habilitada
- Banco de dados `ragdb` pré-criado
- Regra de firewall para serviços do Azure

**Parâmetros que você definirá:**
- `administratorLoginPassword` — sua senha do banco de dados (anote-a!)
- `location` — escolha uma região próxima a você

### Opção B — Azure CLI (Bicep)

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

## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-031/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `migrations` | Arquivos de migração do banco de dados | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-031/migrations) |

---

## Exercício do Lab

### Passo 1: Definir variáveis de ambiente de conexão

Após a implantação, salve seus detalhes de conexão:

```bash
# From the Azure portal: PostgreSQL server → Connection strings
export PG_HOST="your-server.postgres.database.azure.com"
export PG_USER="pgadmin"
export PG_PASSWORD="YourP@ssw0rd!"
export PG_DATABASE="ragdb"
```

### Passo 2: Conectar e verificar o pgvector

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

### Passo 3: Criar esquema

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

### Passo 4: Ingerir o conjunto de dados de exemplo

Baixe e ingira os dados de exemplo do OutdoorGear:

```bash
curl -O https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/products.csv
curl -O https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/knowledge-base.json
```

Reutilize o `ingest.py` do [Lab 022](lab-022-rag-github-models-pgvector.md#step-3-ingest-documents-from-the-sample-dataset), mas atualize a conexão para usar o Azure:

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

### Passo 5: Expor como ferramenta MCP

Encapsule a função de busca como uma ferramenta MCP para que qualquer agente possa consultar sua base de conhecimento:

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

Adicione ao `.vscode/mcp.json`:
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

## Limpeza

```bash
# Stop charges immediately
az group delete --name rg-ai-labs-rag --yes --no-wait
```

---


## 🧠 Verificação de Conhecimento

??? question "**Q1 (Execute o Lab):** Após executar `001_init.sql` no seu banco de dados, quantas linhas existem na tabela `products`? Execute `SELECT COUNT(*) FROM products;` para verificar."

    Execute a migração e depois consulte a tabela.

    ??? success "✅ Revelar Resposta"
        **7 linhas**

        A migração insere 7 produtos OutdoorGear: P001 (TrailBlazer Tent 2P), P002 (Summit Dome 4P), P003 (TrailBlazer Solo), P004 (ArcticDown -20°C), P005 (SummerLight +5°C), P006 (Osprey Atmos 65L), P007 (DayHiker 22L). Execute `SELECT id, name, category FROM products ORDER BY id;` para ver todos.

??? question "**Q2 (Execute o Lab):** Que tipo de índice é criado na tabela `product_embeddings`, e qual coluna ele indexa?"

    Abra `lab-031/migrations/001_init.sql` e encontre a instrução `CREATE INDEX`.

    ??? success "✅ Revelar Resposta"
        **Índice IVFFlat na coluna `embedding`**

        A migração cria: `CREATE INDEX ON product_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);`

        IVFFlat (Inverted File with Flat quantization) é um índice de vizinho mais próximo aproximado — é mais rápido que a busca exata, mas sacrifica uma pequena quantidade de recall. O parâmetro `lists = 100` define o número de células de Voronoi para agrupamento. `vector_cosine_ops` significa que as distâncias são calculadas usando similaridade de cosseno.

??? question "**Q3 (Múltipla Escolha):** Você executa `SELECT * FROM search_products_by_vector($1::vector, 3)` e obtém 3 resultados. O que os resultados representam?"

    - A) Os 3 produtos inseridos mais recentemente
    - B) Os 3 produtos com o maior preço
    - C) Os 3 produtos cujos vetores de embedding são mais similares (menor distância de cosseno) ao vetor de consulta
    - D) 3 produtos selecionados aleatoriamente do banco de dados

    ??? success "✅ Revelar Resposta"
        **Correto: C**

        A função `search_products_by_vector()` realiza uma **busca de vizinho mais próximo aproximado (ANN)** usando o índice IVFFlat. Ela calcula a distância de cosseno entre o vetor de consulta e todos os embeddings de produtos armazenados, e então retorna os `k` produtos com a menor distância (= maior similaridade semântica). O resultado representa os produtos semanticamente mais relevantes para a consulta do usuário.

---

## Próximos Passos

- **Row Level Security para agentes multi-tenant:** → [Lab 032 — Row Level Security](lab-032-row-level-security.md)
- **RAG Agêntico sobre isso:** → [Lab 026 — Agentic RAG Pattern](lab-026-agentic-rag.md)
