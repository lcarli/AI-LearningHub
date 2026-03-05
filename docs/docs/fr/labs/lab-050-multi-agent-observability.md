---
tags: [observability, opentelemetry, multi-agent, genai-conventions, azure-monitor, foundry, python]
---
# Lab 050: Multi-Agent Observability with GenAI Semantic Conventions

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-400">L400</span></span>
  <span><strong>Path:</strong> <a href="../paths/foundry/">🏭 Microsoft Foundry</a></span>
  <span><strong>Time:</strong> ~120 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Offline trace analysis with provided dataset (Azure Monitor optional)</span>
</div>

!!! info "Traduction en cours"
    Ce lab est en cours de traduction. Le contenu ci-dessous est en anglais.



## What You'll Learn

- Apply **GenAI semantic conventions** to multi-agent systems: agent spans, model spans, tool spans
- Trace **agent-to-agent handoffs**, routing decisions, and retry patterns
- Distinguish `INTERNAL` (agent logic) vs `CLIENT` (LLM/tool calls) span kinds
- Analyze **quality scores**, **token costs**, and **latency** across a multi-agent pipeline
- Build observability **dashboard metrics** from raw span data
- Understand how conventions standardize telemetry across **Foundry, Semantic Kernel, LangChain, AutoGen**

!!! abstract "Prerequisite"
    Complete **[Lab 049: Foundry IQ — Agent Tracing](lab-049-foundry-iq-agent-tracing.md)** first. This lab assumes familiarity with OpenTelemetry spans, attributes, and GenAI conventions.

## Introduction

![Multi-Agent Tracing](../../assets/diagrams/multi-agent-tracing.svg)

Single-agent tracing is hard. **Multi-agent** tracing is exponentially harder. When a Router hands off to a Specialist, who calls tools, who passes results to a Reviewer — you need a standard way to capture every step so you can reconstruct the full execution flow.

The **OpenTelemetry GenAI semantic conventions** solve this with three span types:

| Span Type | Kind | Key Attributes | Example |
|-----------|------|----------------|---------|
| **Agent span** | `INTERNAL` | `gen_ai.agent.name`, `gen_ai.agent.id` | Router, ProductSpec, Reviewer |
| **Model span** | `CLIENT` | `gen_ai.request.model`, `gen_ai.usage.*_tokens` | `chat gpt-4o` |
| **Tool span** | `CLIENT` | `gen_ai.tool.name` | `search_products` |

### The Scenario

OutdoorGear Inc. has upgraded to a **multi-agent system** with 4 specialist agents orchestrated by a Router:

1. **Router Agent** — classifies incoming queries and dispatches to the right specialist
2. **Product Specialist** — handles product search and recommendations
3. **Order Specialist** — processes order status and shipping queries
4. **Support Specialist** — handles complaints and sensitive issues
5. **Reviewer Agent** — checks every response for quality and policy compliance

You have **5 complex traces** with 46 spans showing the full agent pipeline, including a trace with a **failed review and retry**.

---

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Run analysis scripts |
| `pandas` | Analyze span data |
| Lab 049 completed | Understanding of OpenTelemetry basics |

```bash
pip install pandas
```

---

!!! tip "Quick Start with GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    All dependencies are pre-installed in the devcontainer.


## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-050/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_conventions.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-050/broken_conventions.py) |
| `dashboard_builder.py` | Starter script with TODOs | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-050/dashboard_builder.py) |
| `multi_agent_spans.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-050/multi_agent_spans.csv) |

---

## Step 1: Understanding Multi-Agent Trace Structure

In a multi-agent system, the trace forms a **tree**:

```
root: router_agent (INTERNAL)
├── classify_query (CLIENT, gpt-4o-mini)
├── product_specialist (INTERNAL)
│   ├── search_reasoning (CLIENT, gpt-4o)
│   ├── search_products (CLIENT, tool)
│   └── format_response (CLIENT, gpt-4o)
└── reviewer (INTERNAL)
    └── quality_check (CLIENT, gpt-4o-mini)
```

Key conventions:

- **Agent spans** are `INTERNAL` — they represent the agent's own logic and orchestration
- **LLM calls** are `CLIENT` — outgoing requests to model endpoints
- **Tool calls** are `CLIENT` — outgoing requests to tools/APIs
- **Parent-child** relationships show the handoff chain
- **`gen_ai.agent.name`** is set ONLY on agent spans, not on LLM/tool spans

!!! tip "Why `INTERNAL` for Agents?"
    An agent's decision-making happens locally (routing, planning, memory retrieval). It doesn't cross a network boundary — so it's `INTERNAL`. The LLM call that the agent *makes* is `CLIENT` because it goes over the network to an API.

---

## Step 2: Load and Explore the Trace Data

The dataset has **46 spans** across **5 traces**:

```python
import pandas as pd

spans = pd.read_csv("lab-050/multi_agent_spans.csv")
print(f"Total spans: {len(spans)}")
print(f"Traces: {spans['trace_id'].nunique()}")
print(f"\nSpans per trace:")
print(spans.groupby("trace_id")["span_id"].count())
```

**Expected:**

| Trace | Spans | Scenario |
|-------|-------|----------|
| A001 | 8 | Product search (simple) |
| A002 | 10 | Complex order query |
| A003 | 9 | Complaint handling |
| A004 | 5 | FAQ (no reviewer) |
| A005 | 14 | Refund with failed review + retry |

---

## Step 3: Agent Span Analysis

Extract and analyze agent spans:

```python
agent_spans = spans[(spans["kind"] == "INTERNAL") & (spans["agent_name"].notna())]
print(f"Total agent spans: {len(agent_spans)}")
print(f"Unique agents: {sorted(agent_spans['agent_name'].unique())}")
print(f"\nSpans per agent:")
print(agent_spans["agent_name"].value_counts().sort_index())
```

**Expected:**

```
Total agent spans: 16
Unique agents: ['FAQSpec', 'OrderSpec', 'ProductSpec', 'RefundSpec', 'Reviewer', 'Router', 'SupportSpec']

Reviewer     5
Router       5
RefundSpec   2
...
```

!!! tip "Insight"
    **Router appears in all 5 traces** — it's the entry point. **Reviewer appears in 4 traces** (not A004, the simple FAQ). **RefundSpec appears twice** in trace A005 because the first attempt failed review and was retried.

---

## Step 4: LLM Token Usage Analysis

Analyze token consumption across all model calls:

```python
llm_spans = spans[spans["model"].notna()]
print(f"Total LLM calls: {len(llm_spans)}")

by_model = llm_spans.groupby("model").agg(
    calls=("span_id", "count"),
    total_input=("input_tokens", "sum"),
    total_output=("output_tokens", "sum"),
).reset_index()
by_model["total_tokens"] = by_model["total_input"] + by_model["total_output"]
print(by_model.to_string(index=False))

total_tokens = int(llm_spans["input_tokens"].sum() + llm_spans["output_tokens"].sum())
print(f"\nGrand total: {total_tokens:,} tokens")
```

**Expected:**

| Model | Calls | Input | Output | Total |
|-------|-------|-------|--------|-------|
| gpt-4o | 12 | 3,830 | 1,890 | 5,720 |
| gpt-4o-mini | 10 | 1,045 | 177 | 1,222 |
| **Total** | **22** | **4,875** | **2,067** | **6,942** |

!!! tip "Cost Insight"
    gpt-4o handles the heavy reasoning (82% of tokens) while gpt-4o-mini does lightweight classification and quality checks (18%). This is a cost-efficient pattern — use expensive models only for complex reasoning.

---

## Step 5: Tool Call Analysis

```python
tool_spans = spans[spans["tool_name"].notna()]
print(f"Total tool calls: {len(tool_spans)}")
print(f"\nTools used:")
print(tool_spans["tool_name"].value_counts())

trace_tools = tool_spans.groupby("trace_id").size()
print(f"\nTrace with most tool calls: {trace_tools.idxmax()} ({trace_tools.max()} calls)")
```

**Expected:**

```
Total tool calls: 8

search_products         1
get_order_status        1
get_shipping_info       1
calculate_eta           1
get_customer_history    1
search_faq              1
get_order_details       1
check_refund_policy     1

Trace with most tool calls: A002 (3 calls)
```

---

## Step 6: Quality Score Analysis

Reviewer agents assign quality scores. Analyze them:

```python
quality_spans = spans[spans["quality_score"].notna()]
print(f"Quality assessments: {len(quality_spans)}")
print(f"Average quality:     {quality_spans['quality_score'].mean():.3f}")
print(f"Min quality:         {quality_spans['quality_score'].min():.2f}")
print(f"Max quality:         {quality_spans['quality_score'].max():.2f}")

# Traces that fell below the quality threshold
below_threshold = quality_spans[quality_spans["quality_score"] < 0.8]
print(f"\nTraces below 0.8 threshold: {below_threshold['trace_id'].unique().tolist()}")
```

**Expected:**

```
Quality assessments: 5
Average quality:     0.790
Min quality:         0.45
Max quality:         0.95

Traces below 0.8 threshold: ['A003', 'A005']
```

### Investigating the Failed Review (Trace A005)

```python
a005 = spans[spans["trace_id"] == "A005"].sort_values("span_id")
print(a005[["span_id", "span_name", "agent_name", "kind", "quality_score", "status"]]
      .to_string(index=False))
```

This shows the **retry pattern**: the first reviewer check (s40) scored 0.45 with status ERROR. The Refund Specialist was re-invoked (s42), produced a revised response, and the second reviewer check (s45) passed at 0.85.

---

## Step 7: Build Dashboard Metrics

Combine everything into a dashboard summary:

```python
# Overall metrics
total_traces = spans["trace_id"].nunique()
total_spans = len(spans)
total_agent_spans = len(agent_spans)
total_llm_calls = len(llm_spans)
total_tools = len(tool_spans)
error_spans = spans[spans["status"] == "ERROR"]
avg_quality = quality_spans["quality_score"].mean()

dashboard = f"""
╔══════════════════════════════════════════════════╗
║         Multi-Agent Observability Dashboard      ║
╠══════════════════════════════════════════════════╣
║ Traces:           {total_traces:>5}                          ║
║ Total Spans:      {total_spans:>5}                          ║
║ Agent Spans:      {total_agent_spans:>5}  (INTERNAL)                ║
║ LLM Calls:        {total_llm_calls:>5}  (CLIENT)                  ║
║ Tool Calls:       {total_tools:>5}  (CLIENT)                  ║
║ Error Spans:      {len(error_spans):>5}                          ║
║ Total Tokens:     {total_tokens:>5,}                        ║
║ Avg Quality:      {avg_quality:>5.3f}                        ║
║ Below Threshold:  {len(below_threshold):>5}  traces                  ║
╚══════════════════════════════════════════════════╝
"""
print(dashboard)
```

---

## 🐛 Bug-Fix Exercise

The file `lab-050/broken_conventions.py` has **3 bugs** in how it interprets GenAI semantic conventions:

```bash
python lab-050/broken_conventions.py
```

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Agent names come from `agent_name`, not `span_name` | Which column has the agent identity? |
| Test 2 | Agent spans must be `INTERNAL` kind AND have an `agent_name` | Don't count LLM/tool spans |
| Test 3 | Total tokens = input + output | Don't forget output_tokens |

---


## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** In GenAI semantic conventions, which span kind should be used for an agent's internal routing/planning logic?"

    - A) CLIENT — because the agent is a client of the LLM
    - B) SERVER — because the agent serves user requests
    - C) INTERNAL — because routing happens locally, not over the network
    - D) PRODUCER — because the agent produces responses

    ??? success "✅ Reveal Answer"
        **Correct: C) INTERNAL**

        Agent decision-making (routing, planning, memory retrieval) happens within the process — it doesn't cross a network boundary. `CLIENT` is used for outgoing calls to LLMs and tools. The convention is: agent logic = `INTERNAL`, external calls = `CLIENT`.

??? question "**Q2 (Multiple Choice):** Why does trace A005 have 14 spans while A001 has only 8?"

    - A) A005 uses a larger model
    - B) A005 had a failed quality review and required a retry loop
    - C) A005 has more user input tokens
    - D) A005 uses a different routing algorithm

    ??? success "✅ Reveal Answer"
        **Correct: B) A005 had a failed quality review and required a retry loop**

        The Reviewer scored A005's first response at 0.45 (ERROR). The system re-invoked the Refund Specialist to revise the response, then the Reviewer checked again (score: 0.85, OK). This retry added extra spans: second specialist (2 LLM calls) + second reviewer (1 LLM call) = 5 additional spans.

??? question "**Q3 (Run the Lab):** How many total agent spans (kind=INTERNAL with an agent_name) are there across all 5 traces?"

    Filter the spans DataFrame for `kind == "INTERNAL"` and `agent_name` not null.

    ??? success "✅ Reveal Answer"
        **16 agent spans**

        Across 5 traces: A001(3) + A002(3) + A003(3) + A004(2) + A005(5) = **16**. A004 has fewer because it skips the Reviewer. A005 has more because of the retry (RefundSpec×2 + Reviewer×2).

??? question "**Q4 (Run the Lab):** Which trace has the most tool calls, and how many?"

    Group tool spans by `trace_id` and find the maximum.

    ??? success "✅ Reveal Answer"
        **Trace A002 — 3 tool calls**

        A002 (complex order query) called: `get_order_status`, `get_shipping_info`, and `calculate_eta`. This is the most tool-intensive trace. A005 has 2 tool calls, and the rest have 1 each.

??? question "**Q5 (Run the Lab):** What is the average quality score across all reviewer assessments?"

    Filter for spans with a non-null `quality_score` and calculate the mean.

    ??? success "✅ Reveal Answer"
        **0.790**

        Quality scores from reviewer spans: A001 (0.95), A002 (0.92), A003 (0.78), A005-first (0.45), A005-retry (0.85). A004 (FAQ) has no reviewer. The data has 5 quality_score entries. Average = (0.95 + 0.92 + 0.78 + 0.45 + 0.85) / 5 = **0.790**. Two traces (A003 and A005) fell below the 0.8 quality threshold.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| GenAI Conventions | Standard attributes: agent.name, request.model, usage.tokens |
| Span Kinds | INTERNAL (agent logic) vs CLIENT (LLM/tool calls) |
| Trace Hierarchy | Parent-child spans showing agent handoffs |
| Retry Patterns | Failed reviews trigger retry loops (visible in traces) |
| Dashboard Metrics | Agent counts, token usage, tool calls, quality scores |
| Cross-Framework | Same conventions work across Foundry, SK, LangChain, AutoGen |

---

## Next Steps

- **[Lab 033](lab-033-agent-observability.md)** — Agent Observability with Application Insights (complementary Azure-native approach)
- **[Lab 034](lab-034-multi-agent-sk.md)** — Multi-Agent Orchestration with Semantic Kernel (build the agents this lab traces)
- **[Lab 035](lab-035-agent-evaluation.md)** — Agent Evaluation with Azure AI Eval SDK (quality scoring that feeds the Reviewer)
