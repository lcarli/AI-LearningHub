---
tags:
  - fabric
  - data-agent
  - nl-to-sql
  - sqlite
  - python
  - entra-id
---

# Lab 052: Fabric IQ — Conversational Data Agent (NL → SQL)

<div class="lab-meta">
  <span class="level-badge level-200">L200</span>
  <span class="path-badge">All paths</span>
  <span class="time-badge">~75 min</span>
  <span class="cost-badge cost-free">Free — Uses SQLite locally (Fabric capacity optional)</span>
</div>

!!! info "Tradução em andamento"
    Este lab ainda está sendo traduzido. O conteúdo abaixo está em inglês.



## What You'll Learn

- How **Microsoft Fabric Data Agents** translate natural-language questions into SQL, DAX, or KQL queries
- The end-to-end flow of **NL → SQL** generation, execution, and result presentation
- How **least-privilege** access and **Entra ID** identity binding keep data secure at every step
- Why **query transparency** and **audit logging** are critical for trust in AI-generated queries
- How to enable **self-serve analytics** for non-technical users without exposing raw database access

## Introduction

![NL to SQL Flow](../../assets/diagrams/fabric-nl-to-sql.svg)

A **Fabric Data Agent** lets business users ask data questions in plain English. Behind the scenes the agent inspects the database schema, generates a SQL (or DAX / KQL) query, executes it under the caller's own Entra identity, and returns a formatted answer — all without the user writing a single line of code.

In this lab you will build a local simulation of that pipeline using **SQLite** and **Python**. The scenario is **OutdoorGear**, a fictitious outdoor-equipment retailer. The database contains two tables:

| Table | Description |
|-------|-------------|
| `products` | Product catalog — 10 items across categories such as Tents, Backpacks, Sleeping Bags, and Accessories |
| `orders` | Order history — 15 orders referencing products by `product_id` |

Non-technical users — store managers, marketing analysts, supply-chain planners — need to ask questions like *"How many tents are in stock?"* or *"What is the total revenue?"* without learning SQL. By the end of this lab you will understand exactly how a Fabric Data Agent answers those questions and why the security model matters.

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| **Python 3.10+** | [python.org/downloads](https://www.python.org/downloads/){:target="_blank"} |
| **pandas** | `pip install pandas` — used to load CSV files into SQLite |
| **sqlite3** | Part of the Python standard library — no installation required |

!!! tip "No Fabric capacity needed"
    This lab runs entirely on your local machine using SQLite. A Fabric capacity is only needed if you want to deploy a real Data Agent afterward.

---

!!! tip "Quick Start with GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    All dependencies are pre-installed in the devcontainer.


## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-052/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_query_gen.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-052/broken_query_gen.py) |
| `orders.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-052/orders.csv) |
| `products.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-052/products.csv) |

---

## Step 1: Understanding Fabric Data Agents

A Fabric Data Agent sits between the user and the data. When a user types a question the agent:

1. **Parses** the natural-language input and identifies intent, entities, and filters.
2. **Inspects** the connected data-source schema (tables, columns, relationships).
3. **Generates** a query in the appropriate language — SQL for warehouses and SQL endpoints, DAX for semantic models, KQL for KQL databases.
4. **Executes** the query under the **user's own Entra ID**. The agent never uses a service account with elevated privileges; it delegates to the caller's identity so that Row-Level Security (RLS) and object-level permissions are enforced automatically.
5. **Returns** the result along with the generated query so the user (or an auditor) can inspect exactly what ran.

This design delivers three guarantees:

| Guarantee | How |
|-----------|-----|
| **Least-privilege** | Queries run as the authenticated user — no shared super-user |
| **Transparency** | The generated SQL/DAX/KQL is always shown to the caller |
| **Auditability** | Every query is logged with the user's identity and timestamp |

!!! info "Why transparency matters"
    If the agent generates an incorrect query the user can see — and report — the mistake. This feedback loop is essential for building trust in AI-generated analytics.

---

## Step 2: Set Up the Database

In this step you will create a local SQLite database from two CSV files that ship with the lab.

### 2.1 Load the CSV files into SQLite

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect("lab-052/outdoor_gear.db")

pd.read_csv("lab-052/products.csv").to_sql("products", conn, if_exists="replace", index=False)
pd.read_csv("lab-052/orders.csv").to_sql("orders", conn, if_exists="replace", index=False)

print("✅ Database created: lab-052/outdoor_gear.db")
```

### 2.2 Explore the schema

```python
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables:", tables)

for table in tables:
    print(f"\n--- {table} ---")
    info = conn.execute(f"PRAGMA table_info({table})").fetchall()
    for col in info:
        print(f"  {col[1]:20s} {col[2]}")
```

Expected output:

```
Tables: ['products', 'orders']

--- products ---
  product_id           TEXT
  product_name         TEXT
  category             TEXT
  price                REAL
  stock                INTEGER

--- orders ---
  order_id             TEXT
  product_id           TEXT
  customer_name        TEXT
  quantity             INTEGER
  total                REAL
  order_date           TEXT
```

### 2.3 Quick row counts

```python
for table in tables:
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    print(f"{table}: {count} rows")
```

```
products: 10 rows
orders: 15 rows
```

---

## Step 3: Build NL → SQL Query Patterns

A Fabric Data Agent maps natural-language questions to SQL queries. Below are five representative patterns that cover the most common question types: counting, aggregation, filtering, joining, and averaging.

### Pattern 1 — Counting with a filter

> **User asks:** *"How many tents are in stock?"*

```sql
SELECT COUNT(*)
FROM   products
WHERE  category = 'Tents'
  AND  stock > 0;
```

**Expected result:** `2`

!!! warning "The `stock > 0` filter matters"
    Without the `stock > 0` clause the query would count products that exist in the catalog even if they are out of stock. A well-designed agent always applies the in-stock filter when the user says *"in stock."*

---

### Pattern 2 — Sum aggregation

> **User asks:** *"What is the total revenue?"*

```sql
SELECT SUM(total)
FROM   orders;
```

**Expected result:** `3209.74`

Revenue comes from the **orders** table — not from multiplying `price × stock` in the products table. This is a common mistake in NL → SQL systems.

---

### Pattern 3 — Simple filter / SELECT *

> **User asks:** *"Show all backpacks"*

```sql
SELECT *
FROM   products
WHERE  category = 'Backpacks';
```

This returns all columns for products in the Backpacks category.

---

### Pattern 4 — JOIN + GROUP BY + ORDER BY

> **User asks:** *"Which product has the most orders?"*

```sql
SELECT   p.product_name,
         COUNT(*) AS order_count
FROM     orders o
JOIN     products p ON o.product_id = p.product_id
GROUP BY p.product_name
ORDER BY order_count DESC
LIMIT    1;
```

**Expected result:** `Alpine Explorer Tent` — 3 orders

!!! note "COUNT(*) vs SUM(quantity)"
    *"Most orders"* means the highest **number of order rows**, not the highest total quantity. The correct aggregate is `COUNT(*)`, not `SUM(quantity)`.

---

### Pattern 5 — Average aggregation

> **User asks:** *"Average order value?"*

```sql
SELECT AVG(total)
FROM   orders;
```

**Expected result:** `213.98`

Verification: total revenue is 3,209.74 and there are 15 orders → 3,209.74 ÷ 15 = **213.9827 ≈ 213.98**.

---

## Step 4: Run Queries and Verify

Execute every pattern against the local SQLite database and confirm the results match the expected values.

```python
queries = {
    "How many tents are in stock?": (
        "SELECT COUNT(*) FROM products WHERE category='Tents' AND stock > 0",
        "2",
    ),
    "What is the total revenue?": (
        "SELECT SUM(total) FROM orders",
        "3209.74",
    ),
    "Show all backpacks": (
        "SELECT * FROM products WHERE category='Backpacks'",
        None,  # tabular result — just display
    ),
    "Which product has the most orders?": (
        "SELECT p.product_name, COUNT(*) AS order_count "
        "FROM orders o JOIN products p ON o.product_id=p.product_id "
        "GROUP BY p.product_name ORDER BY order_count DESC LIMIT 1",
        "Alpine Explorer Tent|3",
    ),
    "Average order value?": (
        "SELECT AVG(total) FROM orders",
        "213.98",
    ),
}

print("=" * 60)
for question, (sql, expected) in queries.items():
    print(f"\n❓ {question}")
    print(f"   SQL ➜ {sql}")
    result = conn.execute(sql).fetchall()
    print(f"   Result: {result}")
    if expected:
        print(f"   Expected: {expected}")
print("\n" + "=" * 60)
```

!!! tip "Compare carefully"
    If any result does not match, re-check the CSV data and the query. Mismatches usually come from an incorrect filter or the wrong aggregation function.

---

## Step 5: Security and Audit

In a production Fabric deployment the same queries you ran locally would be executed through the Data Agent with full enterprise security. This section explains the key safeguards.

### Entra ID identity binding

Every query is executed under the **calling user's Entra ID token**. The Data Agent does not have its own database credentials — it delegates authentication to the identity provider. This means:

- A store manager sees only their store's data (if RLS is configured).
- A marketing analyst can query aggregate revenue but cannot see individual customer records.
- An external auditor can review query logs tied to specific user identities.

### Row-Level Security (RLS)

Fabric supports RLS on SQL endpoints and semantic models. When the Data Agent generates a query, the database engine automatically applies RLS filters based on the authenticated user's identity. The agent itself never modifies or strips these filters.

### Query logging and audit

Every generated query — along with the user identity, timestamp, and result row count — is recorded in the Fabric activity log. This enables:

| Capability | Benefit |
|------------|---------|
| **Compliance reporting** | Prove who accessed what data and when |
| **Anomaly detection** | Flag unusual query patterns (e.g., bulk exports) |
| **Agent improvement** | Identify frequently failed queries and improve the NL → SQL model |

!!! info "Local simulation"
    In this lab you are running queries directly against SQLite, so there is no Entra binding or RLS. In a real Fabric deployment these controls are enforced automatically.

---

## Bug-Fix Exercise

The file `lab-052/broken_query_gen.py` contains a simplified NL → SQL generator with **three bugs**. Your task is to find and fix each one.

### Run the broken script

```bash
python lab-052/broken_query_gen.py
```

### Bug 1 — Missing `stock > 0` filter

```python
# ❌ BUG: counts all products in the category, including out-of-stock
def count_in_stock(category):
    return f"SELECT COUNT(*) FROM products WHERE category='{category}'"
```

**Fix:** Add `AND stock > 0` to the WHERE clause.

```python
# ✅ FIXED
def count_in_stock(category):
    return f"SELECT COUNT(*) FROM products WHERE category='{category}' AND stock > 0"
```

### Bug 2 — Revenue uses `price × stock` instead of order totals

```python
# ❌ BUG: calculates potential inventory value, not actual revenue
def total_revenue():
    return "SELECT SUM(price * stock) FROM products"
```

**Fix:** Query the `orders` table instead.

```python
# ✅ FIXED
def total_revenue():
    return "SELECT SUM(total) FROM orders"
```

### Bug 3 — Most ordered uses `quantity DESC` instead of `COUNT(*)`

```python
# ❌ BUG: returns the order with the highest single-order quantity,
#          not the product with the most orders
def most_ordered_product():
    return (
        "SELECT p.product_name, o.quantity "
        "FROM orders o JOIN products p ON o.product_id=p.product_id "
        "ORDER BY o.quantity DESC LIMIT 1"
    )
```

**Fix:** Group by product and count order rows.

```python
# ✅ FIXED
def most_ordered_product():
    return (
        "SELECT p.product_name, COUNT(*) AS order_count "
        "FROM orders o JOIN products p ON o.product_id=p.product_id "
        "GROUP BY p.product_name ORDER BY order_count DESC LIMIT 1"
    )
```

---

## Supporting Files

The following files are provided in the `lab-052/` directory.

### `lab-052/products.csv`

```csv
product_id,product_name,category,price,stock
P001,Alpine Explorer Tent,Tents,349.99,5
P002,TrailMaster 2P Tent,Tents,199.99,8
P003,Summit Backpack 65L,Backpacks,189.99,12
P004,DayHiker 30L Pack,Backpacks,79.99,20
P005,Arctic Dream Sleeping Bag,Sleeping Bags,299.99,3
P006,Summer Lite Sleeping Bag,Sleeping Bags,89.99,15
P007,Trekking Poles Carbon,Accessories,59.99,25
P008,Headlamp ProBeam 400,Accessories,34.99,30
P009,Portable Water Filter,Accessories,34.92,18
P010,Camping Cookset Titanium,Accessories,124.99,7
```

### `lab-052/orders.csv`

```csv
order_id,product_id,customer_name,quantity,total,order_date
O001,P001,Alice Martin,1,349.99,2025-01-05
O002,P003,Bob Chen,1,189.99,2025-01-08
O003,P005,Carla Diaz,1,299.99,2025-01-10
O004,P002,David Kim,2,399.98,2025-01-12
O005,P007,Eva Novak,3,179.97,2025-01-15
O006,P001,Frank Osei,1,349.99,2025-01-17
O007,P004,Grace Liu,1,79.99,2025-01-20
O008,P008,Hiro Tanaka,2,69.98,2025-01-22
O009,P006,Isabelle Roy,1,89.99,2025-01-24
O010,P001,Jake Wilson,1,349.99,2025-01-27
O011,P009,Karen Patel,1,34.92,2025-01-29
O012,P003,Liam Murphy,1,189.99,2025-02-01
O013,P010,Mia Santos,1,124.99,2025-02-04
O014,P002,Noah Berg,1,199.99,2025-02-06
O015,P005,Olivia Park,1,299.99,2025-02-09
```

### `lab-052/broken_query_gen.py`

```python
"""Broken NL → SQL generator — fix the three bugs!"""

import sqlite3

DB_PATH = "lab-052/outdoor_gear.db"

# ❌ BUG 1: Missing stock > 0 filter
def count_in_stock(category):
    return f"SELECT COUNT(*) FROM products WHERE category='{category}'"

# ❌ BUG 2: Uses price * stock instead of order totals
def total_revenue():
    return "SELECT SUM(price * stock) FROM products"

# ❌ BUG 3: Uses quantity DESC instead of COUNT(*)
def most_ordered_product():
    return (
        "SELECT p.product_name, o.quantity "
        "FROM orders o JOIN products p ON o.product_id=p.product_id "
        "ORDER BY o.quantity DESC LIMIT 1"
    )

def run(query_fn, *args):
    conn = sqlite3.connect(DB_PATH)
    sql = query_fn(*args)
    print(f"SQL: {sql}")
    result = conn.execute(sql).fetchall()
    print(f"Result: {result}\n")
    conn.close()

if __name__ == "__main__":
    print("--- Tents in stock ---")
    run(count_in_stock, "Tents")

    print("--- Total revenue ---")
    run(total_revenue)

    print("--- Most ordered product ---")
    run(most_ordered_product)
```

---

## Knowledge Check

??? question "**Q1 (Multiple Choice):** What security model does a Fabric Data Agent use for query execution?"

    - A) A shared service account with full database access
    - B) The user's own Entra ID with least-privilege permissions
    - C) An API key embedded in the agent configuration
    - D) Anonymous access with IP-based restrictions

    ??? success "✅ Reveal Answer"
        **Correct: B) The user's own Entra ID with least-privilege permissions**

        Fabric Data Agents execute every query under the calling user's Entra identity. This ensures that Row-Level Security, object permissions, and conditional-access policies are enforced automatically — the agent never elevates privileges beyond what the user already has.

??? question "**Q2 (Multiple Choice):** Why is it important that generated SQL is inspectable by the user?"

    - A) So users can copy the SQL and run it faster next time
    - B) To enable transparency, auditability, and trust in AI-generated queries
    - C) Because SQL syntax highlighting looks better in the UI
    - D) To allow users to manually optimize query performance

    ??? success "✅ Reveal Answer"
        **Correct: B) To enable transparency, auditability, and trust in AI-generated queries**

        When users can see the exact SQL that was generated and executed, they can verify correctness, report mistakes, and auditors can review data-access patterns. This transparency is a foundational requirement for trustworthy AI-assisted analytics.

??? question "**Q3 (Run the query):** How many tents are currently in stock (stock > 0)?"

    Run this query against the lab database:

    ```sql
    SELECT COUNT(*) FROM products WHERE category='Tents' AND stock > 0;
    ```

    ??? success "✅ Reveal Answer"
        **Answer: 2**

        Both the Alpine Explorer Tent (P001, stock=5) and the TrailMaster 2P Tent (P002, stock=8) have stock greater than zero. The query correctly filters on both `category='Tents'` and `stock > 0`.

??? question "**Q4 (Run the query):** What is the total revenue from all orders?"

    Run this query against the lab database:

    ```sql
    SELECT SUM(total) FROM orders;
    ```

    ??? success "✅ Reveal Answer"
        **Answer: $3,209.74**

        The `total` column in the orders table contains the actual revenue for each order (price × quantity). Summing all 15 order totals gives 3,209.74. A common mistake is to calculate `SUM(price * stock)` from the products table, which gives inventory value — not revenue.

??? question "**Q5 (Run the query):** Which product has the most orders?"

    Run this query against the lab database:

    ```sql
    SELECT p.product_name, COUNT(*) AS order_count
    FROM   orders o
    JOIN   products p ON o.product_id = p.product_id
    GROUP BY p.product_name
    ORDER BY order_count DESC
    LIMIT 1;
    ```

    ??? success "✅ Reveal Answer"
        **Answer: Alpine Explorer Tent (P001) — 3 orders**

        Product P001 appears in orders O001, O006, and O010. The query joins orders to products, groups by product name, counts the number of order rows per product, and returns the one with the highest count. Note that `COUNT(*)` counts order rows — not total quantity shipped.

---

## Summary

| Topic | Key Takeaway |
|-------|-------------|
| **Fabric Data Agents** | Translate natural-language questions into SQL, DAX, or KQL and execute them on behalf of the user |
| **NL → SQL pipeline** | Parse intent → inspect schema → generate query → execute → return results |
| **Identity & security** | Queries run under the user's Entra ID — least-privilege by default |
| **Row-Level Security** | RLS filters are applied by the database engine, not the agent |
| **Query transparency** | The generated query is always shown so users can verify and auditors can review |
| **Audit logging** | Every query is recorded with user identity, timestamp, and result metadata |
| **Common NL → SQL bugs** | Missing filters, wrong table for aggregation, incorrect aggregate function |

---

## Next Steps

- [← Lab 051: Previous Lab](lab-051-previous-lab.md) — continue your learning path
- [→ Lab 053: Next Lab](lab-053-next-lab.md) — advance to the next topic
