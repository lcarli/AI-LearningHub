---
tags: [security, postgresql, python, free]
---
# Lab 032 : Sécurité au niveau des lignes pour les agents

<div class="lab-meta">
  <span><strong>Niveau :</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Parcours :</strong> <a href="../paths/foundry/">Foundry + Sécurité</a></span>
  <span><strong>Durée :</strong> ~45 min</span>
  <span><strong>💰 Coût :</strong> <span class="level-badge cost-free">Gratuit (Docker local)</span> ou Azure PostgreSQL (~15 $/mois)</span>
</div>

## Ce que vous apprendrez

- Pourquoi les agents ont besoin d'**isolation des données** (risque multi-locataire)
- Implémenter la **sécurité au niveau des lignes PostgreSQL (RLS)** — la base de données applique l'accès, pas votre application
- Créer des **rôles de base de données** pour les identités d'agents
- Tester qu'un agent ne peut littéralement pas voir les données d'un autre utilisateur — même avec des attaques par injection
- Appliquer le RLS au jeu de données exemple `orders.csv`

---

## Introduction

Lorsque votre agent interroge la base de données, il peut servir le Client A — mais la requête SQL qu'il génère pourrait accidentellement retourner les commandes du Client B. Les attaques par injection de prompt exploitent exactement cela.

La **sécurité au niveau des lignes** déplace le contrôle d'accès dans la base de données elle-même. Même si l'agent génère `SELECT * FROM orders`, PostgreSQL ajoute automatiquement `WHERE customer_id = current_user_id` en fonction du rôle de la session. L'agent ne peut pas y échapper.

---

## Prérequis

- Docker Desktop (gratuit) OU Azure PostgreSQL du [Lab 031](lab-031-pgvector-semantic-search.md)
- Python 3.11+, `pip install psycopg2-binary openai`
- `GITHUB_TOKEN` configuré

---

## 📦 Fichiers de support

!!! note "Téléchargez ces fichiers avant de commencer le lab"
    Enregistrez tous les fichiers dans un dossier `lab-032/` dans votre répertoire de travail.

| Fichier | Description | Téléchargement |
|---------|-------------|----------------|
| `migrations` | Fichiers de migration de base de données | [📥 Télécharger](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-032/migrations) |

---

## Exercice du lab

### Étape 1 : Démarrer PostgreSQL avec Docker

```bash
docker run -d \
  --name pg-rls-demo \
  -e POSTGRES_PASSWORD=adminpass \
  -e POSTGRES_DB=storedb \
  -p 5433:5432 \
  postgres:16
```

### Étape 2 : Charger les commandes exemple et configurer le RLS

```python
# setup_rls.py
import psycopg2

ADMIN_CONN = dict(
    host="localhost", port=5433, dbname="storedb",
    user="postgres", password="adminpass"
)

conn = psycopg2.connect(**ADMIN_CONN)
conn.autocommit = True
cur = conn.cursor()

# Create orders table
cur.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        order_id        TEXT PRIMARY KEY,
        customer_id     TEXT NOT NULL,
        customer_name   TEXT NOT NULL,
        product_name    TEXT NOT NULL,
        total           NUMERIC(10,2),
        status          TEXT,
        order_date      DATE
    );
""")

# Load sample data from the repo's orders.csv
import csv, urllib.request, io
url = "https://raw.githubusercontent.com/lcarli/AI-LearningHub/main/data/orders.csv"
with urllib.request.urlopen(url) as r:
    rows = list(csv.DictReader(io.StringIO(r.read().decode())))

for row in rows:
    cur.execute("""
        INSERT INTO orders (order_id, customer_id, customer_name, product_name, total, status, order_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
    """, (row['order_id'], row['customer_id'], row['customer_name'],
          row['product_name'], float(row['total']), row['status'], row['order_date']))

# Create per-customer roles
customers = {row['customer_id'] for row in rows}
for cid in customers:
    cur.execute(f"DROP ROLE IF EXISTS {cid};")
    cur.execute(f"CREATE ROLE {cid} LOGIN PASSWORD 'userpass';")
    cur.execute(f"GRANT SELECT ON orders TO {cid};")
    print(f"  Created role: {cid}")

# Create a generic agent role
cur.execute("DROP ROLE IF EXISTS agent_role; CREATE ROLE agent_role;")
cur.execute("GRANT SELECT ON orders TO agent_role;")

print(f"\nLoaded {len(rows)} orders for {len(customers)} customers.")
cur.close()
conn.close()
```

```bash
python setup_rls.py
```

### Étape 3 : Activer la sécurité au niveau des lignes

```python
# enable_rls.py
import psycopg2

conn = psycopg2.connect(
    host="localhost", port=5433, dbname="storedb",
    user="postgres", password="adminpass"
)
conn.autocommit = True
cur = conn.cursor()

# Enable RLS on the orders table
cur.execute("ALTER TABLE orders ENABLE ROW LEVEL SECURITY;")
cur.execute("ALTER TABLE orders FORCE ROW LEVEL SECURITY;")

# The policy: users can only see their own orders
cur.execute("""
    CREATE POLICY customer_isolation ON orders
    FOR SELECT
    USING (customer_id = current_user);
""")

# Allow postgres superuser to see everything (for admin)
cur.execute("""
    CREATE POLICY admin_all ON orders
    FOR ALL TO postgres
    USING (true);
""")

print("RLS enabled!")
cur.close()
conn.close()
```

```bash
python enable_rls.py
```

### Étape 4 : Tester l'isolation — les agents ne peuvent pas franchir les limites

```python
# test_isolation.py
import psycopg2

def query_as_user(customer_id: str, sql: str) -> list:
    """Simulate an agent connecting as a specific customer role."""
    conn = psycopg2.connect(
        host="localhost", port=5433, dbname="storedb",
        user=customer_id, password="userpass"
    )
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# Alex (C001) sees only their own orders
alex_orders = query_as_user("C001", "SELECT order_id, product_name, total FROM orders")
print(f"Alex sees {len(alex_orders)} orders:")
for o in alex_orders:
    print(f"  {o}")

# Jordan (C002) sees only their own orders
jordan_orders = query_as_user("C002", "SELECT order_id, product_name, total FROM orders")
print(f"\nJordan sees {len(jordan_orders)} orders:")
for o in jordan_orders:
    print(f"  {o}")

# Injection attack attempt: Alex tries to see ALL orders
print("\n⚠️  Injection attempt: SELECT * FROM orders (no WHERE clause)")
injected = query_as_user("C001", "SELECT order_id, customer_id, product_name FROM orders ORDER BY customer_id")
print(f"Alex's injection returned {len(injected)} rows (should only be Alex's):")
for o in injected[:3]:
    print(f"  {o}")

# Verify: no C002 rows in Alex's results
c002_in_c001 = [o for o in injected if o[1] == "C002"]
print(f"\n✅ C002 rows visible to C001: {len(c002_in_c001)}  ← should be 0")
```

Sortie attendue :
```
Alex sees 4 orders
Jordan sees 4 orders

⚠️  Injection attempt: SELECT * FROM orders (no WHERE clause)
Alex's injection returned 4 rows (should only be Alex's)

✅ C002 rows visible to C001: 0
```

### Étape 5 : Construire un agent compatible RLS

```python
# rls_agent.py
import os, psycopg2
from openai import OpenAI

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

def get_user_conn(customer_id: str):
    """Get a database connection scoped to a specific customer."""
    return psycopg2.connect(
        host="localhost", port=5433, dbname="storedb",
        user=customer_id, password="userpass"
    )

def run_safe_query(customer_id: str, sql: str) -> list[dict]:
    """Execute SQL as the customer's DB role — RLS enforced automatically."""
    conn = get_user_conn(customer_id)
    cur = conn.cursor()
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    cur.close()
    conn.close()
    return rows

def order_agent(customer_id: str, user_question: str) -> str:
    # Generate SQL using the LLM
    sql_response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "Generate a simple SQL SELECT query for the `orders` table. "
                    "Columns: order_id, customer_id, customer_name, product_name, total, status, order_date. "
                    "Return ONLY the SQL query, no explanation."
                )
            },
            {"role": "user", "content": user_question}
        ]
    )
    sql = sql_response.choices[0].message.content.strip().strip("```sql").strip("```")

    # Execute with customer's DB role — RLS prevents cross-customer data
    results = run_safe_query(customer_id, sql)

    # Generate natural language answer
    answer = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Answer the customer's question based on their order data. Be friendly and concise."},
            {"role": "user", "content": f"Question: {user_question}\n\nOrder data: {results}"}
        ]
    )
    return answer.choices[0].message.content

# Test
print("Alex's agent:")
print(order_agent("C001", "What have I ordered and what was the total?"))

print("\nJordan's agent:")
print(order_agent("C002", "Show me my recent orders"))
```

---

## Pourquoi c'est important

| Sans RLS | Avec RLS |
|----------|----------|
| L'application doit filtrer : `WHERE customer_id = ?` | La base de données filtre automatiquement |
| L'injection de prompt peut contourner les filtres de l'application | Politique au niveau de la base de données — impossible à contourner |
| Bug dans l'agent = fuite de données | Bug dans l'agent = ne voit toujours que ses propres données |
| Il faut faire confiance à chaque requête générée par l'agent | La confiance repose sur le rôle de la base de données |

---

## Nettoyage

```bash
docker stop pg-rls-demo && docker rm pg-rls-demo
```

---


## Prochaines étapes

- **Observabilité des agents :** → [Lab 033 — Traçage App Insights](lab-033-agent-observability.md)
- **RLS sur Azure PostgreSQL :** → [Lab 031 — pgvector sur Azure](lab-031-pgvector-semantic-search.md)
