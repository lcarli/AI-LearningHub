---
tags: [connectors, mcp, m365, copilot, federation, enterprise]
---
# Lab 056: Federated M365 Copilot Connectors with MCP

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~90 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Uses mock comparison data (no M365 tenant required)</span>
</div>

!!! info "Tradução em andamento"
    Este lab ainda está sendo traduzido. O conteúdo abaixo está em inglês.



## What You'll Learn

- The difference between **synced (indexed) connectors** and **federated (real-time) connectors** in Microsoft 365 Copilot
- How **MCP can act as a federated connector** — providing real-time data access without indexing
- How **citations** work in federated vs synced connectors
- **OAuth and compliance considerations** for regulated data (healthcare, legal, finance)
- When to choose each connector type based on latency, freshness, and compliance requirements

## Introduction

Microsoft 365 Copilot uses **connectors** to bring external data into the Copilot experience. There are two fundamental architectures:

| Connector Type | How It Works | Data Location |
|----------------|-------------|---------------|
| **Synced (Indexed)** | Crawls and copies data into the Microsoft Search index | Data stored on Microsoft servers |
| **Federated (Real-Time)** | Queries the source system at runtime — no data is copied | Data stays in the source system |

Each approach has trade-offs:

| Dimension | Federated | Synced |
|-----------|-----------|--------|
| **Latency** | Higher (real-time query) | Lower (pre-indexed) |
| **Data Freshness** | Always current (0 sec) | Depends on crawl schedule |
| **Compliance** | Data never leaves source | Data copied to Microsoft servers |
| **Offline Access** | Requires source availability | Works even if source is down |

### The Scenario

OutdoorGear Inc. needs to connect **multiple data sources** to Microsoft 365 Copilot:

- **Product catalog** and **order history** — can be indexed (synced) for fast search
- **Patient medical records**, **employee salary data**, and **legal contracts** — regulated data that must **never** leave the source system (federated only)
- **Real-time stock prices** and **shipping tracking** — need the freshest data possible

Your job is to analyze a comparison dataset of 20 queries (10 federated, 10 synced) and determine when each connector type is the right choice.

!!! info "MCP as a Federated Connector"
    An MCP server can serve as a federated connector for M365 Copilot. The MCP server queries the source system in real-time and returns results with citations — no data is ever indexed or stored on Microsoft servers. This makes MCP ideal for regulated data that must comply with HIPAA, GDPR, or SOX requirements.

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Analyze connector comparison data |
| `pandas` library | DataFrame operations |

```bash
pip install pandas
```

---

!!! tip "Quick Start with GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    All dependencies are pre-installed in the devcontainer.


## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-056/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_connector.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-056/broken_connector.py) |
| `connector_comparison.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-056/connector_comparison.csv) |

---

## Step 1: Understanding Connector Types

### Synced (Indexed) Connectors

Synced connectors **crawl** a data source on a schedule and **copy** the content into the Microsoft Search index:

```
┌─────────────┐    Crawl     ┌──────────────┐    Index    ┌─────────────┐
│  Source      │ ──────────► │  Microsoft   │ ─────────► │  Copilot    │
│  System      │  (schedule) │  Graph       │  (fast)    │  Search     │
│             │             │  Connector    │            │             │
└─────────────┘             └──────────────┘            └─────────────┘
```

- ✅ **Fast queries** — data is pre-indexed
- ✅ **Works offline** — source system can be down
- ❌ **Stale data** — depends on crawl frequency
- ❌ **Compliance risk** — data is copied to Microsoft servers

### Federated (Real-Time) Connectors

Federated connectors query the source system **at runtime** — no data is ever copied:

```
┌─────────────┐   Real-time   ┌──────────────┐   Results   ┌─────────────┐
│  Source      │ ◄──────────► │  Federated   │ ──────────► │  Copilot    │
│  System      │    query      │  Connector   │  + citation │  Search     │
│             │              │  (MCP Server) │             │             │
└─────────────┘              └──────────────┘             └─────────────┘
```

- ✅ **Always fresh** — queries live data
- ✅ **Compliant** — data never leaves the source
- ✅ **Citations** — responses include source links
- ❌ **Higher latency** — real-time query overhead
- ❌ **Source dependency** — requires source system availability

---

## Step 2: Load the Comparison Dataset

The dataset contains **20 queries** — each query was run through both a federated and a synced connector:

```python
import pandas as pd

df = pd.read_csv("lab-056/connector_comparison.csv")
print(f"Total queries: {len(df)}")
print(f"Connector types: {df['connector_type'].unique().tolist()}")
print(f"Columns: {list(df.columns)}")
print(f"\nFirst 6 rows:")
print(df.head(6).to_string(index=False))
```

**Expected output:**

```
Total queries: 20
Connector types: ['federated', 'synced']
Columns: ['query_id', 'query_text', 'connector_type', 'latency_ms', 'results_count',
           'data_freshness_sec', 'data_size_kb', 'compliant']

First 6 rows:
query_id                      query_text connector_type  latency_ms  results_count  data_freshness_sec  data_size_kb compliant
     Q01             Show all hiking boots      federated         450              5                   0            12      true
     Q02             Show all hiking boots         synced         120              5                3600            12      true
     Q03           Find tents under $300      federated         520              3                   0             8      true
     Q04           Find tents under $300         synced          95              3                7200             8      true
     Q05  Customer order history C001      federated         680              4                   0            15      true
     Q06  Customer order history C001         synced         150              4                1800            15      true
```

---

## Step 3: Compare Latency vs Freshness

Analyze the performance trade-offs between connector types:

### 3a — Average Latency by Type

```python
fed = df[df["connector_type"] == "federated"]
syn = df[df["connector_type"] == "synced"]

avg_fed_latency = fed["latency_ms"].mean()
avg_syn_latency = syn["latency_ms"].mean()
ratio = avg_fed_latency / avg_syn_latency

print(f"Average federated latency: {avg_fed_latency:.0f} ms")
print(f"Average synced latency:    {avg_syn_latency:.1f} ms")
print(f"Federated/Synced ratio:    {ratio:.1f}×")
```

**Expected output:**

```
Average federated latency: 473 ms
Average synced latency:    109.8 ms
Federated/Synced ratio:    4.3×
```

### 3b — Freshness Comparison

```python
print("Data freshness (seconds since last update):")
print(f"  Federated average: {fed['data_freshness_sec'].mean():.0f} sec (always 0 — real-time)")
print(f"  Synced average:    {syn['data_freshness_sec'].mean():.0f} sec")
print(f"  Synced max:        {syn['data_freshness_sec'].max():.0f} sec ({syn['data_freshness_sec'].max()/3600:.1f} hours)")
```

**Expected output:**

```
Data freshness (seconds since last update):
  Federated average: 0 sec (always 0 — real-time)
  Synced average:    3660 sec
  Synced max:        14400 sec (4.0 hours)
```

### 3c — Latency Distribution

```python
print("Latency ranges:")
for ctype, group in df.groupby("connector_type"):
    print(f"  {ctype}: {group['latency_ms'].min()}–{group['latency_ms'].max()} ms "
          f"(median: {group['latency_ms'].median():.0f} ms)")
```

**Expected output:**

```
Latency ranges:
  federated: 290–680 ms (median: 465 ms)
  synced: 88–150 ms (median: 105 ms)
```

---

## Step 4: Compliance Analysis

Determine which queries involve regulated data that cannot be indexed:

### 4a — Non-Compliant Queries

```python
non_compliant = df[df["compliant"] == False]
print(f"Non-compliant queries: {len(non_compliant)}")
print(f"\nDetails:")
print(non_compliant[["query_id", "query_text", "connector_type"]].to_string(index=False))
```

**Expected output:**

```
Non-compliant queries: 3

Details:
query_id               query_text connector_type
     Q10  Patient medical records         synced
     Q12      Employee salary data         synced
     Q18    Legal contract clauses         synced
```

### 4b — Why Synced Is Non-Compliant for Regulated Data

```python
# Compare federated vs synced for the same regulated queries
regulated_queries = ["Patient medical records", "Employee salary data", "Legal contract clauses"]
for query_text in regulated_queries:
    rows = df[df["query_text"] == query_text]
    fed_row = rows[rows["connector_type"] == "federated"].iloc[0]
    syn_row = rows[rows["connector_type"] == "synced"].iloc[0]
    print(f"\n{query_text}:")
    print(f"  Federated: compliant={fed_row['compliant']}, latency={fed_row['latency_ms']}ms, freshness={fed_row['data_freshness_sec']}s")
    print(f"  Synced:    compliant={syn_row['compliant']}, latency={syn_row['latency_ms']}ms, freshness={syn_row['data_freshness_sec']}s")
```

**Expected output:**

```
Patient medical records:
  Federated: compliant=True, latency=550ms, freshness=0s
  Synced:    compliant=False, latency=130ms, freshness=3600s

Employee salary data:
  Federated: compliant=True, latency=420ms, freshness=0s
  Synced:    compliant=False, latency=105ms, freshness=1800s

Legal contract clauses:
  Federated: compliant=True, latency=480ms, freshness=0s
  Synced:    compliant=False, latency=115ms, freshness=7200s
```

!!! warning "Compliance Is Non-Negotiable"
    For regulated data (HIPAA, GDPR, SOX), the synced connector **copies data to Microsoft servers** during indexing. This violates data residency and sovereignty requirements. The federated connector (e.g., MCP server) keeps data in the source system — only query results are returned at runtime, never stored.

---

## Step 5: When to Use Each Connector Type

Based on the analysis, here are the decision criteria:

### Decision Matrix

| Criterion | Use Federated | Use Synced |
|-----------|--------------|------------|
| **Regulated data** (HIPAA, GDPR, SOX) | ✅ Required | ❌ Non-compliant |
| **Real-time freshness needed** | ✅ Always current | ❌ Stale (crawl delay) |
| **Low latency critical** | ❌ ~473ms avg | ✅ ~110ms avg |
| **Source may be offline** | ❌ Requires source | ✅ Works from index |
| **Large result sets** | ❌ Runtime cost | ✅ Pre-indexed |
| **Infrequently changing data** | ⚠️ Overkill | ✅ Crawl catches updates |

### OutdoorGear Recommendations

```python
recommendations = {
    "Product catalog": "Synced — low latency, not regulated, changes infrequently",
    "Order history": "Synced — historical data, benefits from indexing",
    "Patient medical records": "Federated — HIPAA regulated, must not leave source",
    "Employee salary data": "Federated — PII/compensation data, compliance required",
    "Real-time stock prices": "Federated — must be current, stale data is worse than slow",
    "Legal contracts": "Federated — SOX regulated, data sovereignty required",
    "Product reviews": "Synced — public data, benefits from fast search",
    "Shipping tracking": "Federated — real-time status updates needed",
}

print("OutdoorGear Connector Recommendations:")
for source, rec in recommendations.items():
    connector = "🔄 Federated" if "Federated" in rec else "📦 Synced"
    print(f"  {connector}  {source}: {rec.split(' — ')[1]}")
```

---

## 🐛 Bug-Fix Exercise

The file `lab-056/broken_connector.py` has **3 bugs** in the connector analysis functions. Can you find and fix them all?

Run the self-tests to see which ones fail:

```bash
python lab-056/broken_connector.py
```

You should see **3 failed tests**. Each test corresponds to one bug:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Average freshness by type | Should return `data_freshness_sec`, not `latency_ms` |
| Test 2 | Non-compliant count | Should count `compliant == False`, not `compliant == True` |
| Test 3 | Latency ratio | Should compute `federated / synced`, not `synced / federated` |

Fix all 3 bugs, then re-run. When you see `🎉 All 3 tests passed`, you're done!

---


## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What is the primary advantage of a federated connector over a synced connector?"

    - A) Lower latency for all query types
    - B) Real-time data freshness with no indexing — data never leaves the source
    - C) Better support for offline access
    - D) Simpler authentication setup

    ??? success "✅ Reveal Answer"
        **Correct: B) Real-time data freshness with no indexing — data never leaves the source**

        Federated connectors query the source system at runtime, ensuring results are always current (0-second freshness). Because no data is copied or indexed, it remains in the source system — making it compliant with data residency requirements (HIPAA, GDPR, SOX).

??? question "**Q2 (Multiple Choice):** Why are synced connectors non-compliant for regulated data like patient medical records?"

    - A) Synced connectors don't support encryption
    - B) Data is copied to Microsoft servers during indexing, violating data residency requirements
    - C) Synced connectors cannot handle large datasets
    - D) Synced connectors don't support OAuth authentication

    ??? success "✅ Reveal Answer"
        **Correct: B) Data is copied to Microsoft servers during indexing, violating data residency requirements**

        When a synced connector crawls a data source, it **copies the content to Microsoft's search index**. For regulated data (HIPAA patient records, GDPR personal data, SOX financial data), this violates data sovereignty and residency requirements. The data must remain in the source system — only federated connectors guarantee this.

??? question "**Q3 (Run the Lab):** What is the average latency for federated connector queries?"

    Filter [📥 `connector_comparison.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-056/connector_comparison.csv) by `connector_type == "federated"` and compute `latency_ms.mean()`.

    ??? success "✅ Reveal Answer"
        **473 ms**

        The 10 federated queries have latencies: 450, 520, 680, 380, 550, 420, 610, 290, 480, 350. Sum = 4730, average = 4730 ÷ 10 = **473 ms**.

??? question "**Q4 (Run the Lab):** How many synced queries are non-compliant?"

    Filter for `connector_type == "synced"` and `compliant == False`.

    ??? success "✅ Reveal Answer"
        **3**

        Three synced queries are non-compliant: Q10 (Patient medical records), Q12 (Employee salary data), and Q18 (Legal contract clauses). These involve regulated data that must not be copied to external servers.

??? question "**Q5 (Run the Lab):** What is the approximate federated-to-synced latency ratio?"

    Divide the average federated latency by the average synced latency.

    ??? success "✅ Reveal Answer"
        **≈ 4.3×**

        Average federated latency = 473 ms. Average synced latency ≈ 110 ms. Ratio = 473 ÷ 110 ≈ **4.3×**. Federated queries are about 4.3 times slower than synced queries — the trade-off for real-time freshness and compliance.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| Connector Types | Synced (indexed, fast, stale) vs Federated (real-time, compliant, slower) |
| MCP as Connector | MCP servers can serve as federated connectors for M365 Copilot |
| Compliance | Regulated data requires federated connectors — synced copies data to Microsoft |
| Latency Trade-off | Federated ≈ 4.3× slower but always fresh; synced is fast but stale |
| Decision Criteria | Choose based on regulation, freshness needs, latency tolerance, and offline access |

---

## Next Steps

- **[Lab 054](lab-054-a2a-protocol.md)** — A2A Protocol — Build Interoperable Multi-Agent Systems
- **[Lab 055](lab-055-a2a-mcp-capstone.md)** — A2A + MCP Full Stack — Agent Interoperability Capstone
