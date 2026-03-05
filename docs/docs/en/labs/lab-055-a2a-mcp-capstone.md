---
tags: [a2a, mcp, multi-agent, architecture, capstone, python]
---
# Lab 055: A2A + MCP Full Stack — Agent Interoperability Capstone

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-400">L400</span></span>
  <span><strong>Path:</strong> <a href="../paths/pro-code/">⚙️ Pro Code</a></span>
  <span><strong>Time:</strong> ~120 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Uses mock trace data (no cloud resources required)</span>
</div>

!!! tip "The Three Agentic Protocols"
    This capstone covers A2A + MCP. The third protocol — **AG-UI** (agent↔user interaction) — is covered in **[Lab 077](lab-077-agui-protocol.md)**.

## What You'll Learn

- How **A2A + MCP** work together in a full-stack multi-agent architecture
- Analyze a **travel planner system** with 3 specialized agents using delegation traces
- Distinguish **A2A calls** (agent-to-agent delegation) from **MCP calls** (agent-to-tool access)
- Perform **token cost analysis** across a distributed agent system
- Understand **error handling and retry patterns** in multi-agent workflows
- Apply **design principles** for building production-grade agent architectures

## Introduction

A2A and MCP are **complementary protocols** that serve different roles in a multi-agent system:

| Protocol | Role | Example |
|----------|------|---------|
| **A2A** | Agent-to-agent task delegation | Coordinator asks FlightAgent to find flights |
| **MCP** | Agent-to-tool access | FlightAgent calls a booking API via MCP server |

In this capstone lab, you'll analyze a **travel planner system** that uses both protocols. The Coordinator agent receives a customer request and delegates sub-tasks to specialized agents via A2A. Each specialized agent then uses MCP to access its back-end tools and APIs.

### The Architecture

```
                        Customer Request
                              │
                              ▼
                    ┌──────────────────┐
                    │   Coordinator    │
                    │   Agent          │
                    └──────┬───────────┘
                           │ A2A
           ┌───────────────┼───────────────┐
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌──────────────┐
    │ FlightAgent │ │ HotelAgent  │ │ Itinerary    │
    │             │ │             │ │ Agent        │
    └──────┬──────┘ └──────┬──────┘ └──────┬───────┘
      MCP  │          MCP  │          MCP  │
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌──────────────┐
    │ booking_api │ │ booking_api │ │ maps_api     │
    │ pricing_api │ │ reviews_api │ │ calendar_api │
    │ payment_api │ │             │ │ weather_api  │
    └─────────────┘ └─────────────┘ └──────────────┘
```

The delegation traces dataset (`delegation_traces.csv`) captures **20 events** from a complete travel planning session — 8 A2A calls between agents and 12 MCP calls from agents to tools.

!!! info "Why Two Protocols?"
    A2A handles the *social* layer — agents discovering, negotiating, and delegating tasks to peers. MCP handles the *tool* layer — agents accessing databases, APIs, and external services. Separating these concerns enables independent scaling, security boundaries, and protocol evolution.

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Analyze delegation traces |
| `pandas` library | DataFrame operations on trace data |

```bash
pip install pandas
```

---

!!! tip "Quick Start with GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    All dependencies are pre-installed in the devcontainer.


## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-055/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_delegation.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-055/broken_delegation.py) |
| `delegation_traces.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-055/delegation_traces.csv) |

---

## Step 1: Understanding the Architecture

Before diving into data, understand what each component does:

### Agent Roles

| Agent | A2A Role | MCP Tools |
|-------|----------|-----------|
| **Coordinator** | Receives customer request, delegates to specialists | None (orchestration only) |
| **FlightAgent** | Finds and books flights | `booking_api`, `pricing_api`, `payment_api` |
| **HotelAgent** | Finds and books hotels | `booking_api`, `reviews_api` |
| **ItineraryAgent** | Plans and updates itineraries | `maps_api`, `calendar_api`, `weather_api` |

### Call Flow

1. Customer sends a travel request to the **Coordinator**
2. Coordinator uses **A2A** to delegate sub-tasks (find flights, find hotels, plan itinerary)
3. Each specialist uses **MCP** to call its back-end tools
4. Results flow back through A2A to the Coordinator
5. Coordinator assembles the final response

### Protocol Boundaries

| Boundary | Protocol | Auth |
|----------|----------|------|
| Customer → Coordinator | HTTP/API | API key |
| Coordinator → Specialists | **A2A** | OAuth 2.0 |
| Specialists → Tools | **MCP** | Service-to-service tokens |

!!! tip "OAuth Across A2A Boundaries"
    When the Coordinator delegates to FlightAgent via A2A, it must pass an OAuth token scoped to the customer's permissions. The FlightAgent then uses a *separate* service token for its MCP calls to the booking API. This two-layer auth model prevents privilege escalation.

---

## Step 2: Load and Explore Delegation Traces

Load the trace data containing all 20 events from the travel planning session:

```python
import pandas as pd

traces = pd.read_csv("lab-055/delegation_traces.csv")
print(f"Total events: {len(traces)}")
print(f"Unique request IDs: {traces['request_id'].nunique()}")
print(f"Protocols: {traces['protocol'].unique().tolist()}")
print(f"Statuses: {traces['status'].unique().tolist()}")
print(f"\nFirst 5 events:")
print(traces.head().to_string(index=False))
```

**Expected output:**

```
Total events: 20
Unique request IDs: 8
Protocols: ['A2A', 'MCP']
Statuses: ['OK', 'ERROR']

First 5 events:
request_id source_agent target_agent protocol        action  duration_ms  tokens_used status
      R001  Coordinator  FlightAgent      A2A  find_flights         2500          450     OK
      R001  FlightAgent  booking_api      MCP search_flights        1800            0     OK
      R001  FlightAgent  pricing_api      MCP    get_prices          600            0     OK
      R002  Coordinator   HotelAgent      A2A   find_hotels         3200          520     OK
      R002   HotelAgent  booking_api      MCP search_hotels         2400            0     OK
```

---

## Step 3: Analyze A2A vs MCP Call Patterns

Separate the traces by protocol to understand the delegation structure:

### 3a — Call Counts by Protocol

```python
a2a_calls = traces[traces["protocol"] == "A2A"]
mcp_calls = traces[traces["protocol"] == "MCP"]

print(f"A2A calls (agent → agent): {len(a2a_calls)}")
print(f"MCP calls (agent → tool):  {len(mcp_calls)}")
print(f"Total calls:               {len(traces)}")
```

**Expected output:**

```
A2A calls (agent → agent): 8
MCP calls (agent → tool):  12
Total calls:               20
```

### 3b — A2A Delegation Breakdown

```python
print("A2A Delegations (Coordinator → Specialists):")
print(a2a_calls[["request_id", "source_agent", "target_agent", "action", "status"]].to_string(index=False))
```

**Expected output:**

```
A2A Delegations (Coordinator → Specialists):
request_id source_agent   target_agent           action status
      R001  Coordinator    FlightAgent     find_flights     OK
      R002  Coordinator     HotelAgent      find_hotels     OK
      R003  Coordinator ItineraryAgent   plan_itinerary     OK
      R004  Coordinator    FlightAgent     book_flight      OK
      R005  Coordinator     HotelAgent      book_hotel      OK
      R006  Coordinator    FlightAgent     find_flights  ERROR
      R007  Coordinator ItineraryAgent update_itinerary     OK
      R008  Coordinator     HotelAgent     cancel_hotel     OK
```

### 3c — MCP Tool Usage by Agent

```python
print("MCP tool calls per agent:")
print(mcp_calls.groupby("source_agent")["action"].count().to_string())
print(f"\nUnique MCP tools used: {mcp_calls['target_agent'].nunique()}")
```

**Expected output:**

```
MCP tool calls per agent:
source_agent
FlightAgent       5
HotelAgent        3
ItineraryAgent    4

Unique MCP tools used: 7
```

### 3d — Error Analysis

```python
errors = traces[traces["status"] == "ERROR"]
print(f"Total errors: {len(errors)}")
print(f"\nFailed events:")
print(errors[["request_id", "source_agent", "target_agent", "protocol", "action"]].to_string(index=False))
```

**Expected output:**

```
Total errors: 2

Failed events:
request_id source_agent target_agent protocol         action
      R006  Coordinator  FlightAgent      A2A   find_flights
      R006  FlightAgent  booking_api      MCP search_flights
```

!!! warning "Cascading Failures"
    Notice that R006 has errors in *both* the A2A call and the MCP call. When the `booking_api` MCP tool fails, the FlightAgent cannot complete the A2A task — the error cascades upward. Production systems need retry logic and circuit breakers at both protocol boundaries.

---

## Step 4: Token Cost Analysis

A2A calls consume LLM tokens (agents reason about tasks), while MCP calls are typically token-free (direct API calls):

```python
total_tokens = traces["tokens_used"].sum()
a2a_tokens = a2a_calls["tokens_used"].sum()
mcp_tokens = mcp_calls["tokens_used"].sum()

print(f"Total tokens consumed: {total_tokens}")
print(f"  A2A tokens: {a2a_tokens} ({a2a_tokens/total_tokens*100:.0f}%)")
print(f"  MCP tokens: {mcp_tokens} ({mcp_tokens/total_tokens*100:.0f}%)")

print(f"\nTokens per A2A call:")
print(a2a_calls[["request_id", "action", "tokens_used"]].to_string(index=False))
```

**Expected output:**

```
Total tokens consumed: 3330
  A2A tokens: 3330 (100%)
  MCP tokens: 0 (0%)

Tokens per A2A call:
request_id           action  tokens_used
      R001     find_flights          450
      R002      find_hotels          520
      R003   plan_itinerary          680
      R004      book_flight          380
      R005       book_hotel          350
      R006     find_flights          460
      R007 update_itinerary          290
      R008     cancel_hotel          200
```

### Cost Breakdown

```python
COST_PER_1K_TOKENS = 0.005  # example: GPT-4o-mini pricing

cost = total_tokens / 1000 * COST_PER_1K_TOKENS
print(f"Estimated cost at ${COST_PER_1K_TOKENS}/1K tokens: ${cost:.4f}")
print(f"Average tokens per A2A call: {a2a_tokens / len(a2a_calls):.0f}")
print(f"Most expensive call: {a2a_calls.loc[a2a_calls['tokens_used'].idxmax(), 'action']} "
      f"({a2a_calls['tokens_used'].max()} tokens)")
```

---

## Step 5: Error Handling and Retry Patterns

Analyze how errors propagate and design retry strategies:

### 5a — Error Rate by Protocol

```python
for protocol in ["A2A", "MCP"]:
    subset = traces[traces["protocol"] == protocol]
    error_count = (subset["status"] == "ERROR").sum()
    total = len(subset)
    print(f"{protocol}: {error_count}/{total} errors ({error_count/total*100:.0f}%)")
```

**Expected output:**

```
A2A: 1/8 errors (12%)
MCP: 1/12 errors (8%)
```

### 5b — Latency Analysis

```python
print("Average latency by protocol:")
print(traces.groupby("protocol")["duration_ms"].mean().to_string())

print(f"\nSlowest call: {traces.loc[traces['duration_ms'].idxmax(), 'action']} "
      f"({traces['duration_ms'].max()} ms)")
print(f"Fastest call: {traces.loc[traces['duration_ms'].idxmin(), 'action']} "
      f"({traces['duration_ms'].min()} ms)")
```

### 5c — Retry Design Patterns

| Pattern | A2A Layer | MCP Layer |
|---------|-----------|-----------|
| **Retry** | Retry the full A2A task with exponential backoff | Retry the specific tool call |
| **Fallback** | Route to an alternative agent | Use a backup API endpoint |
| **Circuit Breaker** | Stop delegating to a failing agent | Stop calling a failing tool |
| **Timeout** | Set per-task timeout in A2A request | Set per-call timeout in MCP |
| **Idempotency** | Include idempotency key in task ID | Include in tool call params |

---

## Step 6: Design Principles

Based on this analysis, here are the key principles for building A2A + MCP systems:

| Principle | Description |
|-----------|-------------|
| **Separation of Concerns** | A2A for delegation, MCP for tool access — don't mix them |
| **Token Awareness** | Only A2A calls consume LLM tokens; optimize agent prompts |
| **Auth Boundaries** | Separate OAuth scopes for A2A (user context) and MCP (service context) |
| **Error Isolation** | Handle errors at each protocol boundary independently |
| **Observability** | Trace both A2A and MCP calls with correlated request IDs |
| **Idempotency** | Design all operations to be safely retryable |

---

## 🐛 Bug-Fix Exercise

The file `lab-055/broken_delegation.py` has **3 bugs** in the trace analysis functions. Can you find and fix them all?

Run the self-tests to see which ones fail:

```bash
python lab-055/broken_delegation.py
```

You should see **3 failed tests**. Each test corresponds to one bug:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | A2A call count | Should filter by `protocol == "A2A"`, not count all rows |
| Test 2 | Average latency | Should include ALL requests (including errors), not just OK |
| Test 3 | Success rate | Should divide by total request count, not unique agent count |

Fix all 3 bugs, then re-run. When you see `🎉 All 3 tests passed`, you're done!

---


## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What is the key difference between A2A and MCP?"

    - A) A2A is faster than MCP
    - B) A2A handles agent-to-agent delegation; MCP handles agent-to-tool access
    - C) A2A uses REST; MCP uses GraphQL
    - D) A2A is for cloud agents; MCP is for local agents

    ??? success "✅ Reveal Answer"
        **Correct: B) A2A handles agent-to-agent delegation; MCP handles agent-to-tool access**

        A2A (Agent-to-Agent) is a peer-to-peer protocol for agents to discover each other and delegate tasks. MCP (Model Context Protocol) is a client-server protocol for agents to access tools, databases, and APIs. They are complementary — a multi-agent system typically uses both.

??? question "**Q2 (Multiple Choice):** Why does the architecture use separate protocols for agent communication and tool access?"

    - A) To reduce the total number of API calls
    - B) Because agents and tools use different programming languages
    - C) To enable independent scaling, security boundaries, and protocol evolution
    - D) Because A2A is proprietary and MCP is open source

    ??? success "✅ Reveal Answer"
        **Correct: C) To enable independent scaling, security boundaries, and protocol evolution**

        Separating agent-to-agent communication (A2A) from agent-to-tool access (MCP) lets you scale each layer independently, enforce different auth scopes at each boundary (user-context OAuth for A2A, service tokens for MCP), and evolve the protocols without breaking the other layer.

??? question "**Q3 (Run the Lab):** How many A2A calls are in the delegation traces?"

    Filter [📥 `delegation_traces.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-055/delegation_traces.csv) by `protocol == "A2A"` and count the rows.

    ??? success "✅ Reveal Answer"
        **8**

        There are 8 A2A calls — one for each request from the Coordinator to a specialist agent (R001–R008). The remaining 12 events are MCP calls from specialists to their back-end tools.

??? question "**Q4 (Run the Lab):** How many MCP calls are in the delegation traces?"

    Filter `delegation_traces.csv` by `protocol == "MCP"` and count the rows.

    ??? success "✅ Reveal Answer"
        **12**

        There are 12 MCP calls — FlightAgent makes 5 (search, pricing, booking, payment, search-retry), HotelAgent makes 3 (search, booking, booking), and ItineraryAgent makes 4 (directions, availability, forecast, update).

??? question "**Q5 (Run the Lab):** What is the total number of tokens consumed across all events?"

    Sum the `tokens_used` column in `delegation_traces.csv`.

    ??? success "✅ Reveal Answer"
        **3330**

        Only A2A calls consume tokens (LLM reasoning). The 8 A2A calls use: 450 + 520 + 680 + 380 + 350 + 460 + 290 + 200 = **3330 tokens**. All 12 MCP calls use 0 tokens (direct API calls).

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| Architecture | A2A for agent delegation + MCP for tool access in a unified system |
| Travel Planner | Coordinator → FlightAgent / HotelAgent / ItineraryAgent |
| Call Patterns | 8 A2A delegations triggering 12 MCP tool calls |
| Token Costs | Only A2A calls consume LLM tokens (3330 total) |
| Error Handling | Cascading failures across protocol boundaries; retry patterns |
| Design Principles | Separation of concerns, auth boundaries, observability |

---

## Next Steps

- **[Lab 054](lab-054-a2a-protocol.md)** — A2A Protocol — Build Interoperable Multi-Agent Systems
- **[Lab 056](lab-056-federated-connectors.md)** — Federated M365 Copilot Connectors with MCP
