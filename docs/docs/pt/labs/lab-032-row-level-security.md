---
tags: [security, postgresql, python, free]
---
# Lab 032: Row Level Security para Agentes

<div class="lab-meta">
  <span><strong>Nível:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Trilha:</strong> <a href="../paths/foundry/">Foundry + Security</a></span>
  <span><strong>Tempo:</strong> ~45 min</span>
  <span><strong>💰 Custo:</strong> <span class="level-badge cost-free">Gratuito (Docker local)</span> ou Azure PostgreSQL (~$15/mês)</span>
</div>

## O que Você Vai Aprender

- Por que agentes precisam de **isolamento de dados** (risco multi-tenant)
- Implementar **PostgreSQL Row Level Security (RLS)** — o banco de dados impõe o acesso, não sua aplicação
- Criar **roles de banco de dados** para identidades de agentes
- Testar que um agente literalmente não consegue ver os dados de outro usuário — mesmo com ataques de injeção
- Aplicar RLS ao conjunto de dados de exemplo `orders.csv`

---

## Introdução

Quando seu agente consulta o banco de dados, ele pode estar atendendo o Cliente A — mas a consulta SQL que ele gera pode acidentalmente retornar os pedidos do Cliente B. Ataques de injeção de prompt exploram exatamente isso.

**Row Level Security** move o controle de acesso para dentro do próprio banco de dados. Mesmo que o agente gere `SELECT * FROM orders`, o PostgreSQL adiciona automaticamente `WHERE customer_id = current_user_id` com base no role da sessão. O agente não pode escapar disso.

---

## Pré-requisitos

- Docker Desktop (gratuito) OU Azure PostgreSQL do [Lab 031](lab-031-pgvector-semantic-search.md)
- Python 3.11+, `pip install psycopg2-binary openai`
- `GITHUB_TOKEN` configurado

---

## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-032/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|---------|-----------|----------|
| `migrations` | Arquivos de migração do banco de dados | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-032/migrations) |

---

## Exercício do Lab

### Passo 1: Iniciar o PostgreSQL com Docker

```bash
docker run -d \
  --name pg-rls-demo \
  -e POSTGRES_PASSWORD=adminpass \
  -e POSTGRES_DB=storedb \
  -p 5433:5432 \
  postgres:16
```

### Passo 2: Carregar pedidos de exemplo e configurar RLS

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

### Passo 3: Habilitar Row Level Security

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

### Passo 4: Testar isolamento — agentes não conseguem cruzar limites

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

Saída esperada:
```
Alex sees 4 orders
Jordan sees 4 orders

⚠️  Injection attempt: SELECT * FROM orders (no WHERE clause)
Alex's injection returned 4 rows (should only be Alex's)

✅ C002 rows visible to C001: 0
```

### Passo 5: Construir um agente com suporte a RLS

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

## Por que Isso Importa

| Sem RLS | Com RLS |
|---------|---------|
| A aplicação deve filtrar: `WHERE customer_id = ?` | O banco de dados filtra automaticamente |
| Injeção de prompt pode contornar filtros da aplicação | Política no nível do banco — não pode ser contornada |
| Bug no agente = vazamento de dados | Bug no agente = ainda vê apenas seus próprios dados |
| Precisa confiar em toda consulta que o agente gera | A confiança está no role do banco de dados |

---

## Limpeza

```bash
docker stop pg-rls-demo && docker rm pg-rls-demo
```

---


## Próximos Passos

- **Observabilidade de Agentes:** → [Lab 033 — App Insights Tracing](lab-033-agent-observability.md)
- **RLS no Azure PostgreSQL:** → [Lab 031 — pgvector on Azure](lab-031-pgvector-semantic-search.md)
