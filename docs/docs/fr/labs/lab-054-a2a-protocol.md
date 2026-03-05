---
tags: [a2a, protocol, multi-agent, interoperability, python, free]
---
# Lab 054: A2A Protocol — Build Interoperable Multi-Agent Systems

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~75 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Uses local JSON data only</span>
</div>

!!! info "Traduction en cours"
    Ce lab est en cours de traduction. Le contenu ci-dessous est en anglais.



!!! tip "The Three Agentic Protocols"
    A2A is one of three open protocols for the agentic era: **MCP** (agent↔tools, [Lab 012](lab-012-what-is-mcp.md)), **A2A** (agent↔agent, this lab), and **AG-UI** (agent↔user, [Lab 077](lab-077-agui-protocol.md)). Together they form the complete interoperability stack.

## What You'll Learn

- What the **A2A (Agent-to-Agent) protocol** is — JSON-RPC 2.0 over HTTPS, governed by the Linux Foundation
- How **Agent Cards** work as the discovery mechanism for agent capabilities
- How to programmatically parse Agent Cards and inspect **skills**, **streaming**, and **pushNotifications**
- The key differences between **A2A** (peer-to-peer agent communication) and **MCP** (agent-to-tool access)

## Introduction

Modern AI systems rarely consist of a single agent. Real-world solutions require **multiple specialized agents** that discover each other, negotiate capabilities, and collaborate on tasks. The **Agent-to-Agent (A2A) protocol** standardizes this communication.

A2A and MCP solve different problems:

| Protocol | Purpose | Direction |
|----------|---------|-----------|
| **A2A** | Agent ↔ Agent communication | Peer-to-peer — agents delegate tasks to other agents |
| **MCP** | Agent → Tool access | Client-server — agents call tools, databases, APIs |

Think of A2A as agents *talking to each other*, and MCP as agents *using tools*. A complete multi-agent system typically uses **both** protocols.

### The Scenario

You are an **Integration Architect** at OutdoorGear Inc. The company operates **3 specialized agents**:

1. **ProductSearchAgent** — searches the product catalog by category, price, and availability
2. **OrderManagementAgent** — manages orders, returns, and shipping updates
3. **CustomerSupportAgent** — handles inquiries, complaints, and FAQ responses

Each agent publishes an **Agent Card** — a JSON document describing its identity, capabilities, skills, and authentication requirements. Your job is to load these cards, analyze what each agent can do, and understand how A2A enables them to discover and collaborate with each other.

!!! info "A2A Protocol Essentials"
    A2A uses **JSON-RPC 2.0 over HTTPS** as its transport layer. Each agent publishes an Agent Card at a well-known URL (typically `/.well-known/agent.json`). Client agents discover available agents by fetching these cards, inspecting their skills, and sending task requests using the JSON-RPC protocol.

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Parse and analyze Agent Cards |
| `json` (built-in) | Load agent card data |

No external packages are required — this lab uses only the Python standard library.

---

!!! tip "Quick Start with GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    All dependencies are pre-installed in the devcontainer.


## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-054/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `agent_cards.json` | Configuration / data file | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-054/agent_cards.json) |
| `broken_a2a.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-054/broken_a2a.py) |

---

## Step 1: Understanding the A2A Protocol

A2A defines a standard for **peer-to-peer agent communication**. The protocol specifies:

| Concept | Description |
|---------|-------------|
| **Agent Card** | JSON document advertising an agent's identity, URL, capabilities, skills, and auth |
| **Skills** | Named operations an agent can perform (e.g., `search_products`, `track_order`) |
| **Capabilities** | Feature flags: `streaming`, `pushNotifications`, `stateTransitionHistory` |
| **Task** | A unit of work sent from one agent to another via JSON-RPC 2.0 |
| **Artifact** | The result returned by an agent after completing a task |

### Agent Card Structure

```json
{
  "name": "ProductSearchAgent",
  "description": "Searches the OutdoorGear product catalog",
  "url": "https://agents.outdoorgear.com/product-search",
  "version": "1.0.0",
  "provider": "OutdoorGear Inc.",
  "capabilities": {
    "streaming": true,
    "pushNotifications": false,
    "stateTransitionHistory": false
  },
  "skills": [
    {"id": "search_products", "name": "Search Products", "description": "Search by category, price, and stock"}
  ],
  "authentication": {"type": "bearer", "required": true}
}
```

### A2A Communication Flow

```
┌─────────────┐   1. Fetch Agent Card    ┌─────────────────┐
│  Client     │ ───────────────────────►  │  Remote Agent   │
│  Agent      │   2. Inspect skills      │  (Agent Card)   │
│             │ ◄───────────────────────  │                 │
│             │   3. Send JSON-RPC task   │                 │
│             │ ───────────────────────►  │                 │
│             │   4. Receive artifact     │                 │
│             │ ◄───────────────────────  │                 │
└─────────────┘                           └─────────────────┘
```

---

## Step 2: Load Agent Cards

Load the three OutdoorGear agent cards from the JSON file:

```python
import json

with open("lab-054/agent_cards.json") as f:
    cards = json.load(f)

print(f"Total agents: {len(cards)}")
for card in cards:
    print(f"  • {card['name']} (v{card['version']}) — {card['description']}")
```

**Expected output:**

```
Total agents: 3
  • ProductSearchAgent (v1.0.0) — Searches the OutdoorGear product catalog by category, price range, and availability
  • OrderManagementAgent (v2.1.0) — Manages customer orders including status tracking, returns, and shipping updates
  • CustomerSupportAgent (v1.3.0) — Handles customer inquiries, complaints, and FAQ responses with sentiment awareness
```

---

## Step 3: Analyze Agent Capabilities

Parse each agent's capabilities, skills, and authentication to build a discovery summary:

### 3a — Skills Inventory

```python
total_skills = 0
for card in cards:
    skills = card["skills"]
    total_skills += len(skills)
    print(f"\n{card['name']} — {len(skills)} skill(s):")
    for skill in skills:
        print(f"  • {skill['name']}: {skill['description']}")

print(f"\nTotal skills across all agents: {total_skills}")
```

**Expected output:**

```
ProductSearchAgent — 2 skill(s):
  • Search Products: Search by category, price, and stock
  • Get Product Details: Retrieve full specs for a product ID

OrderManagementAgent — 3 skill(s):
  • Track Order: Get real-time order status
  • Process Return: Initiate a product return
  • Update Shipping: Change shipping address or speed

CustomerSupportAgent — 2 skill(s):
  • Answer FAQ: Respond to common questions
  • Handle Complaint: Process and resolve complaints

Total skills across all agents: 7
```

### 3b — Capability Flags

```python
print("Agent Capabilities Matrix:")
print(f"{'Agent':<25} {'Streaming':<12} {'Push':<12} {'History':<12}")
print("-" * 61)
for card in cards:
    caps = card["capabilities"]
    print(f"{card['name']:<25} {str(caps['streaming']):<12} "
          f"{str(caps['pushNotifications']):<12} "
          f"{str(caps['stateTransitionHistory']):<12}")

push_count = sum(1 for c in cards if c["capabilities"]["pushNotifications"])
print(f"\nAgents supporting pushNotifications: {push_count}")
```

**Expected output:**

```
Agent Capabilities Matrix:
Agent                     Streaming    Push         History
-------------------------------------------------------------
ProductSearchAgent        True         False        False
OrderManagementAgent      False        True         True
CustomerSupportAgent      True         True         False

Agents supporting pushNotifications: 2
```

### 3c — Authentication Types

```python
auth_types = sorted(set(c["authentication"]["type"] for c in cards))
print(f"Authentication types used: {auth_types}")

for card in cards:
    auth = card["authentication"]
    print(f"  {card['name']}: {auth['type']} (required={auth['required']})")
```

**Expected output:**

```
Authentication types used: ['bearer', 'oauth2']
  ProductSearchAgent: bearer (required=True)
  OrderManagementAgent: bearer (required=True)
  CustomerSupportAgent: oauth2 (required=True)
```

---

## Step 4: A2A vs MCP — Protocol Comparison

Understanding when to use each protocol is essential for multi-agent architecture:

| Dimension | A2A | MCP |
|-----------|-----|-----|
| **Purpose** | Agent-to-agent task delegation | Agent-to-tool access |
| **Transport** | JSON-RPC 2.0 over HTTPS | JSON-RPC 2.0 over stdio/SSE |
| **Discovery** | Agent Cards at `/.well-known/agent.json` | Tool manifests in MCP server |
| **Direction** | Peer-to-peer (bidirectional) | Client → Server (unidirectional) |
| **Auth** | OAuth 2.0, bearer tokens | Server-defined (API keys, OAuth) |
| **Governance** | Linux Foundation | Anthropic (open standard) |
| **Use case** | "Ask another agent to do something" | "Call a tool / read a resource" |

### When to Use Which

```
Customer asks: "Find me a waterproof tent under $200 and track my last order"

                    ┌──────────────────┐
                    │  Coordinator     │
                    │  Agent           │
                    └──────┬───────────┘
                           │
              ┌────────────┼────────────┐
         A2A  │       A2A  │            │ A2A
              ▼            ▼            ▼
    ┌──────────────┐ ┌──────────┐ ┌──────────────┐
    │ ProductSearch │ │ Order    │ │ Customer     │
    │ Agent        │ │ Mgmt     │ │ Support      │
    └──────┬───────┘ └────┬─────┘ └──────┬───────┘
      MCP  │         MCP  │         MCP  │
           ▼              ▼              ▼
    ┌──────────────┐ ┌──────────┐ ┌──────────────┐
    │ Catalog DB   │ │ Order DB │ │ FAQ KB       │
    │ (MCP Server) │ │ (MCP)    │ │ (MCP Server) │
    └──────────────┘ └──────────┘ └──────────────┘
```

- **A2A** connects the Coordinator to specialized agents (peer-to-peer delegation)
- **MCP** connects each agent to its back-end tools and data sources

---

## Step 5: Build a Mock A2A Request/Response Flow

Simulate how a client agent discovers and communicates with a remote agent using A2A:

```python
import json

def discover_agent(cards, skill_id):
    """Find an agent that has the requested skill."""
    for card in cards:
        for skill in card["skills"]:
            if skill["id"] == skill_id:
                return card
    return None

def build_a2a_request(card, skill_id, params):
    """Build a JSON-RPC 2.0 request for an A2A task."""
    return {
        "jsonrpc": "2.0",
        "method": "tasks/send",
        "id": "req-001",
        "params": {
            "id": "task-001",
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": json.dumps(params)}]
            },
            "metadata": {
                "target_agent": card["name"],
                "skill": skill_id
            }
        }
    }

def mock_a2a_response(request):
    """Simulate an A2A response."""
    return {
        "jsonrpc": "2.0",
        "id": request["id"],
        "result": {
            "id": request["params"]["id"],
            "status": {"state": "completed"},
            "artifacts": [
                {
                    "parts": [{"type": "text", "text": "Found 3 matching products"}]
                }
            ]
        }
    }

# Discovery: find who can search products
agent = discover_agent(cards, "search_products")
print(f"Discovered agent: {agent['name']} at {agent['url']}")

# Build request
request = build_a2a_request(agent, "search_products", {"category": "tents", "max_price": 200})
print(f"\nA2A Request:\n{json.dumps(request, indent=2)}")

# Get response
response = mock_a2a_response(request)
print(f"\nA2A Response:\n{json.dumps(response, indent=2)}")
```

**Expected output:**

```
Discovered agent: ProductSearchAgent at https://agents.outdoorgear.com/product-search

A2A Request:
{
  "jsonrpc": "2.0",
  "method": "tasks/send",
  "id": "req-001",
  "params": {
    "id": "task-001",
    "message": {
      "role": "user",
      "parts": [{"type": "text", "text": "{\"category\": \"tents\", \"max_price\": 200}"}]
    },
    "metadata": {
      "target_agent": "ProductSearchAgent",
      "skill": "search_products"
    }
  }
}

A2A Response:
{
  "jsonrpc": "2.0",
  "id": "req-001",
  "result": {
    "id": "task-001",
    "status": {"state": "completed"},
    "artifacts": [
      {
        "parts": [{"type": "text", "text": "Found 3 matching products"}]
      }
    ]
  }
}
```

---

## 🐛 Bug-Fix Exercise

The file `lab-054/broken_a2a.py` has **3 bugs** in the Agent Card parser. Can you find and fix them all?

Run the self-tests to see which ones fail:

```bash
python lab-054/broken_a2a.py
```

You should see **3 failed tests**. Each test corresponds to one bug:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Total skill count across all agents | Should sum skills from *all* cards, not just the first |
| Test 2 | Agents supporting push notifications | Check `pushNotifications`, not `streaming` |
| Test 3 | Authentication types | Return the `type` field (string), not the `required` field (bool) |

Fix all 3 bugs, then re-run. When you see `🎉 All 3 tests passed`, you're done!

---


## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What transport mechanism does the A2A protocol use?"

    - A) gRPC over HTTP/2
    - B) JSON-RPC 2.0 over HTTPS
    - C) GraphQL over WebSocket
    - D) REST over HTTP with OpenAPI

    ??? success "✅ Reveal Answer"
        **Correct: B) JSON-RPC 2.0 over HTTPS**

        The A2A protocol uses **JSON-RPC 2.0 over HTTPS** as its transport layer. This provides a standardized request/response format with method names, parameters, and error codes — all transmitted securely over HTTPS.

??? question "**Q2 (Multiple Choice):** What is the primary purpose of an Agent Card in A2A?"

    - A) Storing the agent's conversation history
    - B) Capability discovery — advertising what an agent can do
    - C) Encrypting messages between agents
    - D) Rate-limiting incoming requests

    ??? success "✅ Reveal Answer"
        **Correct: B) Capability discovery — advertising what an agent can do**

        An Agent Card is a JSON document published at a well-known URL that describes an agent's identity, skills, capabilities (streaming, push notifications), and authentication requirements. Client agents fetch these cards to **discover** what remote agents can do before sending task requests.

??? question "**Q3 (Run the Lab):** How many total skills exist across all 3 OutdoorGear agents?"

    Sum the skills arrays from all agent cards in [📥 `agent_cards.json`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-054/agent_cards.json).

    ??? success "✅ Reveal Answer"
        **7**

        ProductSearchAgent has 2 skills (`search_products`, `get_details`), OrderManagementAgent has 3 skills (`track_order`, `process_return`, `update_shipping`), and CustomerSupportAgent has 2 skills (`answer_faq`, `handle_complaint`). Total: 2 + 3 + 2 = **7**.

??? question "**Q4 (Run the Lab):** How many agents support `pushNotifications`?"

    Check the `capabilities.pushNotifications` field in each agent card.

    ??? success "✅ Reveal Answer"
        **2**

        OrderManagementAgent (`pushNotifications: true`) and CustomerSupportAgent (`pushNotifications: true`) support push notifications. ProductSearchAgent does not (`pushNotifications: false`).

??? question "**Q5 (Run the Lab):** What authentication types are used across the 3 agents?"

    Inspect the `authentication.type` field in each card and collect the unique values.

    ??? success "✅ Reveal Answer"
        **bearer and oauth2**

        ProductSearchAgent and OrderManagementAgent use `bearer` token authentication. CustomerSupportAgent uses `oauth2`. The two unique auth types are **bearer** and **oauth2**.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| A2A Protocol | JSON-RPC 2.0 over HTTPS for peer-to-peer agent communication |
| Agent Cards | JSON documents for capability discovery (skills, capabilities, auth) |
| Skills & Capabilities | How agents advertise what they can do and what features they support |
| A2A vs MCP | A2A for agent↔agent delegation; MCP for agent→tool access |
| Discovery Flow | Fetch Agent Card → Inspect skills → Send task → Receive artifact |

---

## Next Steps

- **[Lab 055](lab-055-a2a-mcp-capstone.md)** — A2A + MCP Full Stack — Agent Interoperability Capstone
- **[Lab 056](lab-056-federated-connectors.md)** — Federated M365 Copilot Connectors with MCP
