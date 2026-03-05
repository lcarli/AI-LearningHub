---
tags: [pgvector, rag, azure, azure-required]
---
# Lab 031 : Recherche sémantique pgvector sur Azure

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/rag/">RAG</a></span>
  <span><strong>Durée :</strong> ~60 min</span>
  <span><strong>💰 Coût :</strong> ~15 $/mois (PostgreSQL Flexible Server Burstable B1ms)</span>
</div>

!!! warning "Abonnement Azure requis"
    Ce lab déploie Azure PostgreSQL Flexible Server. → [Guide des prérequis](../prerequisites.md)

## Ce que vous apprendrez

- Déployer **Azure PostgreSQL Flexible Server** avec pgvector activé en un clic
- Se connecter de manière sécurisée avec SSL et les règles de pare-feu
- Migrer le pipeline RAG du [Lab 022](lab-022-rag-github-models-pgvector.md) vers Azure
- Utiliser **Azure AI Services** pour les embeddings (ou continuer à utiliser GitHub Models — gratuit)
- Exposer le magasin de vecteurs comme un **outil MCP** pour les agents

---

## Déployer l'infrastructure

### Option A — Déployer sur Azure (un clic)

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2Flcarli%2FAI-LearningHub%2Fmain%2Finfra%2Flab-031-pgvector%2Fazuredeploy.json)

Ceci déploie :
- PostgreSQL Flexible Server (Burstable B1ms, ~15 $/mois)
- Extension pgvector activée
- Base de données `ragdb` pré-créée
- Règle de pare-feu pour les services Azure

**Paramètres que vous définirez :**
- `administratorLoginPassword` — votre mot de passe de base de données (notez-le !)
- `location` — choisissez une région proche de vous

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

## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-031/` dans votre répertoire de travail.

| Fichier | Description | Téléchargement |
|---------|-------------|----------------|
| `migrations` | Fichiers de migration de base de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-031/migrations) |

---

## Exercice du lab

### Étape 1 : Définir les variables d'environnement de connexion

Après le déploiement, enregistrez vos détails de connexion :

```bash
# From the Azure portal: PostgreSQL server → Connection strings
export PG_HOST="your-server.postgres.database.azure.com"
export PG_USER="pgadmin"
export PG_PASSWORD="YourP@ssw0rd!"
export PG_DATABASE="ragdb"
```

### Étape 2 : Se connecter et vérifier pgvector

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

### Étape 3 : Créer le schéma

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

### Étape 4 : Ingérer le jeu de données exemple

Téléchargez et ingérez les données exemple OutdoorGear :

```bash
curl -O https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/products.csv
curl -O https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/knowledge-base.json
```

Réutilisez le `ingest.py` du [Lab 022](lab-022-rag-github-models-pgvector.md#step-3-ingest-documents-from-the-sample-dataset), mais mettez à jour la connexion pour utiliser Azure :

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

### Étape 5 : Exposer comme outil MCP

Encapsulez la fonction de recherche comme outil MCP pour que tout agent puisse interroger votre base de connaissances :

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

Ajoutez à `.vscode/mcp.json` :
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

## Nettoyage

```bash
# Stop charges immediately
az group delete --name rg-ai-labs-rag --yes --no-wait
```

---


## 🧠 Vérification des connaissances

??? question "**Q1 (Exécuter le lab) :** Après avoir exécuté `001_init.sql` sur votre base de données, combien de lignes y a-t-il dans la table `products` ? Exécutez `SELECT COUNT(*) FROM products;` pour vérifier."

    Exécutez la migration puis interrogez la table.

    ??? success "✅ Révéler la réponse"
        **7 lignes**

        La migration insère 7 produits OutdoorGear : P001 (TrailBlazer Tent 2P), P002 (Summit Dome 4P), P003 (TrailBlazer Solo), P004 (ArcticDown -20°C), P005 (SummerLight +5°C), P006 (Osprey Atmos 65L), P007 (DayHiker 22L). Exécutez `SELECT id, name, category FROM products ORDER BY id;` pour les voir tous.

??? question "**Q2 (Exécuter le lab) :** Quel type d'index est créé sur la table `product_embeddings`, et quelle colonne indexe-t-il ?"

    Ouvrez `lab-031/migrations/001_init.sql` et trouvez l'instruction `CREATE INDEX`.

    ??? success "✅ Révéler la réponse"
        **Index IVFFlat sur la colonne `embedding`**

        La migration crée : `CREATE INDEX ON product_embeddings USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);`

        IVFFlat (Inverted File with Flat quantization) est un index de plus proche voisin approximatif — il est plus rapide que la recherche exacte mais sacrifie une petite quantité de rappel. Le paramètre `lists = 100` définit le nombre de cellules de Voronoi pour le regroupement. `vector_cosine_ops` signifie que les distances sont calculées en utilisant la similarité cosinus.

??? question "**Q3 (Choix multiple) :** Vous exécutez `SELECT * FROM search_products_by_vector($1::vector, 3)` et obtenez 3 résultats. Que représentent les résultats ?"

    - A) Les 3 produits les plus récemment insérés
    - B) Les 3 produits avec le prix le plus élevé
    - C) Les 3 produits dont les vecteurs d'embedding sont les plus similaires (distance cosinus la plus proche) au vecteur de requête
    - D) 3 produits sélectionnés aléatoirement dans la base de données

    ??? success "✅ Révéler la réponse"
        **Correct : C**

        La fonction `search_products_by_vector()` effectue une **recherche de plus proche voisin approximatif (ANN)** en utilisant l'index IVFFlat. Elle calcule la distance cosinus entre le vecteur de requête et tous les embeddings de produits stockés, puis retourne les `k` produits avec la plus petite distance (= similarité sémantique la plus élevée). Le résultat représente les produits les plus sémantiquement pertinents pour la requête de l'utilisateur.

---

## Prochaines étapes

- **Sécurité au niveau des lignes pour les agents multi-locataires :** → [Lab 032 — Sécurité au niveau des lignes](lab-032-row-level-security.md)
- **RAG agentique par-dessus :** → [Lab 026 — Pattern RAG agentique](lab-026-agentic-rag.md)
