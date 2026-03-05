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
  <span class="path-badge">Todos os caminhos</span>
  <span class="time-badge">~75 min</span>
  <span class="cost-badge cost-free">Gratuito — Usa SQLite localmente (capacidade do Fabric opcional)</span>
</div>

## O Que Você Vai Aprender

- Como os **Microsoft Fabric Data Agents** traduzem perguntas em linguagem natural para consultas SQL, DAX ou KQL
- O fluxo de ponta a ponta da geração, execução e apresentação de resultados **NL → SQL**
- Como o acesso de **menor privilégio** e a vinculação de identidade **Entra ID** mantêm os dados seguros em cada etapa
- Por que a **transparência de consultas** e o **registro de auditoria** são críticos para confiança em consultas geradas por IA
- Como habilitar **análises de autoatendimento** para usuários não técnicos sem expor acesso direto ao banco de dados

## Introdução

![Fluxo NL para SQL](../../assets/diagrams/fabric-nl-to-sql.svg)

Um **Fabric Data Agent** permite que usuários de negócios façam perguntas sobre dados em linguagem natural. Nos bastidores, o agente inspeciona o esquema do banco de dados, gera uma consulta SQL (ou DAX / KQL), a executa sob a própria identidade Entra do chamador e retorna uma resposta formatada — tudo sem o usuário escrever uma única linha de código.

Neste lab, você construirá uma simulação local desse pipeline usando **SQLite** e **Python**. O cenário é a **OutdoorGear**, uma varejista fictícia de equipamentos outdoor. O banco de dados contém duas tabelas:

| Tabela | Descrição |
|-------|-------------|
| `products` | Catálogo de produtos — 10 itens em categorias como Tents, Backpacks, Sleeping Bags e Accessories |
| `orders` | Histórico de pedidos — 15 pedidos referenciando produtos por `product_id` |

Usuários não técnicos — gerentes de loja, analistas de marketing, planejadores de cadeia de suprimentos — precisam fazer perguntas como *"Quantas barracas estão em estoque?"* ou *"Qual é a receita total?"* sem aprender SQL. Ao final deste lab, você entenderá exatamente como um Fabric Data Agent responde essas perguntas e por que o modelo de segurança é importante.

## Pré-requisitos

| Requisito | Notas |
|-------------|-------|
| **Python 3.10+** | [python.org/downloads](https://www.python.org/downloads/){:target="_blank"} |
| **pandas** | `pip install pandas` — usado para carregar arquivos CSV no SQLite |
| **sqlite3** | Parte da biblioteca padrão do Python — nenhuma instalação necessária |

!!! tip "Nenhuma capacidade do Fabric necessária"
    Este lab roda inteiramente na sua máquina local usando SQLite. Uma capacidade do Fabric é necessária apenas se você quiser implantar um Data Agent real depois.

---

!!! tip "Início Rápido com GitHub Codespaces"
    [![Abrir no GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    Todas as dependências estão pré-instaladas no devcontainer.


## 📦 Arquivos de Apoio

!!! note "Baixe estes arquivos antes de iniciar o lab"
    Salve todos os arquivos em uma pasta `lab-052/` no seu diretório de trabalho.

| Arquivo | Descrição | Download |
|------|-------------|----------|
| `broken_query_gen.py` | Exercício de correção de bugs (3 bugs + auto-testes) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-052/broken_query_gen.py) |
| `orders.csv` | Conjunto de dados | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-052/orders.csv) |
| `products.csv` | Conjunto de dados | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-052/products.csv) |

---

## Etapa 1: Entendendo os Fabric Data Agents

Um Fabric Data Agent fica entre o usuário e os dados. Quando um usuário digita uma pergunta, o agente:

1. **Analisa** a entrada em linguagem natural e identifica intenção, entidades e filtros.
2. **Inspeciona** o esquema da fonte de dados conectada (tabelas, colunas, relacionamentos).
3. **Gera** uma consulta na linguagem apropriada — SQL para warehouses e endpoints SQL, DAX para modelos semânticos, KQL para bancos de dados KQL.
4. **Executa** a consulta sob o **próprio Entra ID do usuário**. O agente nunca usa uma conta de serviço com privilégios elevados; ele delega para a identidade do chamador para que Row-Level Security (RLS) e permissões em nível de objeto sejam aplicadas automaticamente.
5. **Retorna** o resultado junto com a consulta gerada para que o usuário (ou um auditor) possa inspecionar exatamente o que foi executado.

Este design entrega três garantias:

| Garantia | Como |
|-----------|-----|
| **Menor privilégio** | Consultas rodam como o usuário autenticado — sem super-usuário compartilhado |
| **Transparência** | O SQL/DAX/KQL gerado é sempre mostrado ao chamador |
| **Auditabilidade** | Toda consulta é registrada com a identidade do usuário e timestamp |

!!! info "Por que a transparência importa"
    Se o agente gerar uma consulta incorreta, o usuário pode ver — e reportar — o erro. Esse ciclo de feedback é essencial para construir confiança em análises geradas por IA.

---

## Etapa 2: Configurar o Banco de Dados

Nesta etapa, você criará um banco de dados SQLite local a partir de dois arquivos CSV que acompanham o lab.

### 2.1 Carregar os arquivos CSV no SQLite

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect("lab-052/outdoor_gear.db")

pd.read_csv("lab-052/products.csv").to_sql("products", conn, if_exists="replace", index=False)
pd.read_csv("lab-052/orders.csv").to_sql("orders", conn, if_exists="replace", index=False)

print("✅ Database created: lab-052/outdoor_gear.db")
```

### 2.2 Explorar o esquema

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

Saída esperada:

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

### 2.3 Contagem rápida de linhas

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

## Etapa 3: Construir Padrões de Consulta NL → SQL

Um Fabric Data Agent mapeia perguntas em linguagem natural para consultas SQL. Abaixo estão cinco padrões representativos que cobrem os tipos de perguntas mais comuns: contagem, agregação, filtragem, junção e média.

### Padrão 1 — Contagem com filtro

> **Usuário pergunta:** *"Quantas barracas estão em estoque?"*

```sql
SELECT COUNT(*)
FROM   products
WHERE  category = 'Tents'
  AND  stock > 0;
```

**Resultado esperado:** `2`

!!! warning "O filtro `stock > 0` importa"
    Sem a cláusula `stock > 0`, a consulta contaria produtos que existem no catálogo mesmo se estiverem sem estoque. Um agente bem projetado sempre aplica o filtro de em estoque quando o usuário diz *"em estoque."*

---

### Padrão 2 — Agregação de soma

> **Usuário pergunta:** *"Qual é a receita total?"*

```sql
SELECT SUM(total)
FROM   orders;
```

**Resultado esperado:** `3209.74`

A receita vem da tabela **orders** — não de multiplicar `price × stock` na tabela products. Este é um erro comum em sistemas NL → SQL.

---

### Padrão 3 — Filtro simples / SELECT *

> **Usuário pergunta:** *"Mostrar todas as mochilas"*

```sql
SELECT *
FROM   products
WHERE  category = 'Backpacks';
```

Isso retorna todas as colunas para produtos na categoria Backpacks.

---

### Padrão 4 — JOIN + GROUP BY + ORDER BY

> **Usuário pergunta:** *"Qual produto tem mais pedidos?"*

```sql
SELECT   p.product_name,
         COUNT(*) AS order_count
FROM     orders o
JOIN     products p ON o.product_id = p.product_id
GROUP BY p.product_name
ORDER BY order_count DESC
LIMIT    1;
```

**Resultado esperado:** `Alpine Explorer Tent` — 3 pedidos

!!! note "COUNT(*) vs SUM(quantity)"
    *"Mais pedidos"* significa o maior **número de linhas de pedidos**, não a maior quantidade total. O agregado correto é `COUNT(*)`, não `SUM(quantity)`.

---

### Padrão 5 — Agregação de média

> **Usuário pergunta:** *"Valor médio do pedido?"*

```sql
SELECT AVG(total)
FROM   orders;
```

**Resultado esperado:** `213.98`

Verificação: a receita total é 3.209,74 e há 15 pedidos → 3.209,74 ÷ 15 = **213,9827 ≈ 213,98**.

---

## Etapa 4: Executar Consultas e Verificar

Execute cada padrão contra o banco de dados SQLite local e confirme que os resultados correspondem aos valores esperados.

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

!!! tip "Compare com cuidado"
    Se algum resultado não corresponder, verifique novamente os dados CSV e a consulta. Divergências geralmente vêm de um filtro incorreto ou da função de agregação errada.

---

## Etapa 5: Segurança e Auditoria

Em uma implantação Fabric em produção, as mesmas consultas que você executou localmente seriam executadas através do Data Agent com segurança empresarial completa. Esta seção explica as principais salvaguardas.

### Vinculação de identidade Entra ID

Toda consulta é executada sob o **token Entra ID do usuário chamador**. O Data Agent não tem suas próprias credenciais de banco de dados — ele delega a autenticação ao provedor de identidade. Isso significa:

- Um gerente de loja vê apenas os dados da sua loja (se RLS estiver configurado).
- Um analista de marketing pode consultar receita agregada, mas não pode ver registros individuais de clientes.
- Um auditor externo pode revisar logs de consultas vinculados a identidades de usuários específicos.

### Row-Level Security (RLS)

O Fabric suporta RLS em endpoints SQL e modelos semânticos. Quando o Data Agent gera uma consulta, o motor do banco de dados aplica automaticamente filtros RLS com base na identidade do usuário autenticado. O agente em si nunca modifica ou remove esses filtros.

### Log de consultas e auditoria

Toda consulta gerada — junto com a identidade do usuário, timestamp e contagem de linhas do resultado — é registrada no log de atividades do Fabric. Isso permite:

| Capacidade | Benefício |
|------------|---------|
| **Relatórios de conformidade** | Provar quem acessou quais dados e quando |
| **Detecção de anomalias** | Sinalizar padrões de consulta incomuns (ex.: exportações em massa) |
| **Melhoria do agente** | Identificar consultas frequentemente falhas e melhorar o modelo NL → SQL |

!!! info "Simulação local"
    Neste lab, você está executando consultas diretamente contra o SQLite, então não há vinculação Entra ou RLS. Em uma implantação Fabric real, esses controles são aplicados automaticamente.

---

## Exercício de Correção de Bugs

O arquivo `lab-052/broken_query_gen.py` contém um gerador NL → SQL simplificado com **três bugs**. Sua tarefa é encontrar e corrigir cada um.

### Executar o script com bugs

```bash
python lab-052/broken_query_gen.py
```

### Bug 1 — Filtro `stock > 0` ausente

```python
# ❌ BUG: counts all products in the category, including out-of-stock
def count_in_stock(category):
    return f"SELECT COUNT(*) FROM products WHERE category='{category}'"
```

**Correção:** Adicione `AND stock > 0` à cláusula WHERE.

```python
# ✅ FIXED
def count_in_stock(category):
    return f"SELECT COUNT(*) FROM products WHERE category='{category}' AND stock > 0"
```

### Bug 2 — Receita usa `price × stock` em vez de totais de pedidos

```python
# ❌ BUG: calculates potential inventory value, not actual revenue
def total_revenue():
    return "SELECT SUM(price * stock) FROM products"
```

**Correção:** Consulte a tabela `orders` em vez disso.

```python
# ✅ FIXED
def total_revenue():
    return "SELECT SUM(total) FROM orders"
```

### Bug 3 — Mais pedidos usa `quantity DESC` em vez de `COUNT(*)`

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

**Correção:** Agrupe por produto e conte as linhas de pedidos.

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

## Arquivos de Apoio

Os seguintes arquivos são fornecidos no diretório `lab-052/`.

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

## Verificação de Conhecimento

??? question "**Q1 (Múltipla Escolha):** Qual modelo de segurança um Fabric Data Agent usa para execução de consultas?"

    - A) Uma conta de serviço compartilhada com acesso total ao banco de dados
    - B) O próprio Entra ID do usuário com permissões de menor privilégio
    - C) Uma chave de API embutida na configuração do agente
    - D) Acesso anônimo com restrições baseadas em IP

    ??? success "✅ Revelar Resposta"
        **Correto: B) O próprio Entra ID do usuário com permissões de menor privilégio**

        Os Fabric Data Agents executam toda consulta sob a identidade Entra do usuário chamador. Isso garante que Row-Level Security, permissões de objeto e políticas de acesso condicional sejam aplicadas automaticamente — o agente nunca eleva privilégios além do que o usuário já possui.

??? question "**Q2 (Múltipla Escolha):** Por que é importante que o SQL gerado seja inspecionável pelo usuário?"

    - A) Para que os usuários possam copiar o SQL e executá-lo mais rápido na próxima vez
    - B) Para permitir transparência, auditabilidade e confiança em consultas geradas por IA
    - C) Porque o destaque de sintaxe SQL fica melhor na interface
    - D) Para permitir que os usuários otimizem manualmente o desempenho da consulta

    ??? success "✅ Revelar Resposta"
        **Correto: B) Para permitir transparência, auditabilidade e confiança em consultas geradas por IA**

        Quando os usuários podem ver o SQL exato que foi gerado e executado, eles podem verificar a correção, reportar erros e auditores podem revisar padrões de acesso a dados. Essa transparência é um requisito fundamental para análises confiáveis assistidas por IA.

??? question "**Q3 (Execute a consulta):** Quantas barracas estão atualmente em estoque (stock > 0)?"

    Execute esta consulta contra o banco de dados do lab:

    ```sql
    SELECT COUNT(*) FROM products WHERE category='Tents' AND stock > 0;
    ```

    ??? success "✅ Revelar Resposta"
        **Resposta: 2**

        Tanto a Alpine Explorer Tent (P001, stock=5) quanto a TrailMaster 2P Tent (P002, stock=8) têm estoque maior que zero. A consulta filtra corretamente tanto por `category='Tents'` quanto por `stock > 0`.

??? question "**Q4 (Execute a consulta):** Qual é a receita total de todos os pedidos?"

    Execute esta consulta contra o banco de dados do lab:

    ```sql
    SELECT SUM(total) FROM orders;
    ```

    ??? success "✅ Revelar Resposta"
        **Resposta: $3.209,74**

        A coluna `total` na tabela orders contém a receita real de cada pedido (preço × quantidade). Somando todos os 15 totais de pedidos resulta em 3.209,74. Um erro comum é calcular `SUM(price * stock)` da tabela products, que dá o valor do inventário — não a receita.

??? question "**Q5 (Execute a consulta):** Qual produto tem mais pedidos?"

    Execute esta consulta contra o banco de dados do lab:

    ```sql
    SELECT p.product_name, COUNT(*) AS order_count
    FROM   orders o
    JOIN   products p ON o.product_id = p.product_id
    GROUP BY p.product_name
    ORDER BY order_count DESC
    LIMIT 1;
    ```

    ??? success "✅ Revelar Resposta"
        **Resposta: Alpine Explorer Tent (P001) — 3 pedidos**

        O produto P001 aparece nos pedidos O001, O006 e O010. A consulta junta pedidos com produtos, agrupa por nome do produto, conta o número de linhas de pedidos por produto e retorna o que tem a maior contagem. Note que `COUNT(*)` conta linhas de pedidos — não a quantidade total expedida.

---

## Resumo

| Tópico | Conclusão Principal |
|-------|-------------|
| **Fabric Data Agents** | Traduzem perguntas em linguagem natural para SQL, DAX ou KQL e as executam em nome do usuário |
| **Pipeline NL → SQL** | Analisar intenção → inspecionar esquema → gerar consulta → executar → retornar resultados |
| **Identidade & segurança** | Consultas rodam sob o Entra ID do usuário — menor privilégio por padrão |
| **Row-Level Security** | Filtros RLS são aplicados pelo motor do banco de dados, não pelo agente |
| **Transparência de consultas** | A consulta gerada é sempre mostrada para que usuários possam verificar e auditores possam revisar |
| **Log de auditoria** | Toda consulta é registrada com identidade do usuário, timestamp e metadados do resultado |
| **Bugs comuns NL → SQL** | Filtros ausentes, tabela errada para agregação, função de agregação incorreta |

---

## Próximos Passos

- [← Lab 051: Lab Anterior](lab-051-previous-lab.md) — continue seu caminho de aprendizado
- [→ Lab 053: Próximo Lab](lab-053-next-lab.md) — avance para o próximo tópico