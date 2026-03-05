---
tags: [ag-ui, protocol, frontend, copilotkit, events, python, persona-developer, persona-architect]
---
# Lab 077: AG-UI Protocol — Connect Agents to User Interfaces

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~60 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Uses mock event data</span>
</div>

## What You'll Learn

- What the **AG-UI Protocol** is and how it connects agents to frontend user interfaces
- How AG-UI completes the **interoperability trilogy**: MCP (tools) + A2A (agents) + AG-UI (users)
- Analyze **12 event types** and their directions (agent→frontend vs. frontend→agent)
- Understand event categories: lifecycle, text, tool, state, and input
- Build an **event flow diagram** from a real interaction trace

## Introduction

The **AG-UI (Agent–User Interface) Protocol** is an event-based protocol that standardizes how AI agents communicate with frontend applications. While **MCP** connects agents to tools and **A2A** connects agents to other agents, **AG-UI** closes the loop by connecting agents to **users** through their UIs.

### The Interoperability Trilogy

| Protocol | Connects | Purpose |
|----------|----------|---------|
| **MCP** | Agent ↔ Tools | Standardized tool/resource access |
| **A2A** | Agent ↔ Agent | Multi-agent collaboration |
| **AG-UI** | Agent ↔ User | Real-time UI streaming and interaction |

### How It Works

AG-UI uses a **streaming event model**. Instead of request/response, the agent and frontend exchange a continuous stream of typed events:

```
Frontend                          Agent
   │                                │
   │── RunAgent (start) ──────────►│
   │                                │
   │◄──── LifecycleStarted ────────│
   │◄──── TextMessageStart ────────│
   │◄──── TextMessageContent ──────│
   │◄──── TextMessageEnd ──────────│
   │◄──── ToolCallStart ──────────│
   │◄──── ToolCallArgs ───────────│
   │◄──── ToolCallEnd ────────────│
   │                                │
   │── ToolResult (response) ─────►│
   │                                │
   │◄──── StateUpdate ─────────────│
   │◄──── LifecycleCompleted ──────│
   │                                │
```

### The Scenario

You are a **Frontend Engineer** integrating an AI agent into a CopilotKit-powered UI. You have a dataset of **12 event types** (`agui_events.csv`) that defines every event in the AG-UI protocol. Your job: analyze the events, understand their directions and categories, and map out the event flow for a typical agent interaction.

!!! info "Mock Data"
    This lab uses a mock event type dataset. The event names, directions, and categories mirror the AG-UI protocol specification as defined by CopilotKit.

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Run the analysis scripts |
| `pandas` library | Data manipulation |

```bash
pip install pandas
```

---

!!! tip "Quick Start with GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    All dependencies are pre-installed in the devcontainer.


## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-077/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_agui.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-077/broken_agui.py) |
| `agui_events.csv` | 12 AG-UI event types with directions and categories | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-077/agui_events.csv) |

---

## Step 1: Understand the Event Model

AG-UI events are organized by **direction** and **category**:

| Direction | Meaning |
|-----------|---------|
| **agent→frontend** | Agent sends data to the UI (streaming text, tool calls, state updates) |
| **frontend→agent** | User/UI sends input to the agent (run command, tool results) |

| Category | Examples |
|----------|---------|
| **lifecycle** | `LifecycleStarted`, `LifecycleCompleted` — marks agent run boundaries |
| **text** | `TextMessageStart`, `TextMessageContent`, `TextMessageEnd` — streaming text output |
| **tool** | `ToolCallStart`, `ToolCallArgs`, `ToolCallEnd`, `ToolResult` — tool execution |
| **state** | `StateUpdate`, `StateSnapshot` — shared state synchronization |
| **input** | `RunAgent` — frontend initiates an agent run |

---

## Step 2: Load and Explore the Events

```python
import pandas as pd

df = pd.read_csv("lab-077/agui_events.csv")

print(f"Total event types: {len(df)}")
print(f"Directions: {df['direction'].value_counts().to_dict()}")
print(f"Categories: {df['category'].value_counts().to_dict()}")
print(f"\nAll events:")
print(df[["event_name", "direction", "category"]].to_string(index=False))
```

**Expected output:**

```
Total event types: 12
Directions: {'agent_to_frontend': 9, 'frontend_to_agent': 3}
Categories: {'tool': 4, 'text': 3, 'lifecycle': 2, 'state': 2, 'input': 1}
```

---

## Step 3: Analyze Event Directions

Which events flow from agent to frontend, and which go the other way?

```python
agent_to_ui = df[df["direction"] == "agent_to_frontend"]
ui_to_agent = df[df["direction"] == "frontend_to_agent"]

print(f"Agent → Frontend events: {len(agent_to_ui)}")
for _, row in agent_to_ui.iterrows():
    print(f"  {row['event_name']:>25s}  [{row['category']}]")

print(f"\nFrontend → Agent events: {len(ui_to_agent)}")
for _, row in ui_to_agent.iterrows():
    print(f"  {row['event_name']:>25s}  [{row['category']}]")
```

!!! tip "Design Insight"
    The protocol is **heavily asymmetric**: **9 events** flow from agent to frontend, but only **3** from frontend to agent. This reflects the reality that agents produce most of the data (streaming text, tool calls, state updates) while frontends primarily send commands and tool results.

---

## Step 4: Map the Event Flow

Build a timeline of events for a typical agent interaction:

```python
# Define a typical interaction sequence
sequence = [
    "RunAgent",
    "LifecycleStarted",
    "TextMessageStart",
    "TextMessageContent",
    "TextMessageEnd",
    "ToolCallStart",
    "ToolCallArgs",
    "ToolCallEnd",
    "ToolResult",
    "StateUpdate",
    "TextMessageStart",
    "TextMessageContent",
    "TextMessageEnd",
    "LifecycleCompleted"
]

print("Typical AG-UI Event Flow:")
print("=" * 60)
for i, event_name in enumerate(sequence, 1):
    match = df[df["event_name"] == event_name]
    if not match.empty:
        row = match.iloc[0]
        direction = "►" if row["direction"] == "frontend_to_agent" else "◄"
        side = "Frontend" if row["direction"] == "frontend_to_agent" else "Agent   "
        print(f"  {i:>2}. {side} {direction} {event_name:<25s} [{row['category']}]")
```

---

## Step 5: Analyze Categories in Depth

```python
print("Events by category:\n")
for category, group in df.groupby("category"):
    print(f"  {category.upper()} ({len(group)} events):")
    for _, row in group.iterrows():
        arrow = "→" if row["direction"] == "agent_to_frontend" else "←"
        print(f"    {arrow} {row['event_name']}")
    print()

# Summary statistics
print("Category × Direction matrix:")
pivot = df.groupby(["category", "direction"]).size().unstack(fill_value=0)
print(pivot.to_string())
```

!!! warning "Frontend Responsibility"
    When the agent emits a `ToolCallEnd` event, the **frontend is responsible** for executing the tool and sending back a `ToolResult` event. If the frontend doesn't respond, the agent will wait indefinitely. Always implement timeout handling for tool execution.

---

## Step 6: Build the Protocol Summary

```python
report = f"""# 📋 AG-UI Protocol Summary

## Overview
| Metric | Value |
|--------|-------|
| Total Event Types | {len(df)} |
| Agent → Frontend | {len(agent_to_ui)} |
| Frontend → Agent | {len(ui_to_agent)} |
| Categories | {df['category'].nunique()} |

## Event Catalog
"""

for _, row in df.iterrows():
    arrow = "→ Frontend" if row["direction"] == "agent_to_frontend" else "→ Agent"
    report += f"| `{row['event_name']}` | {row['category']} | {arrow} |\n"

report += f"""
## Protocol Trilogy
| Protocol | Connection | Events |
|----------|-----------|--------|
| MCP | Agent ↔ Tools | Request/Response |
| A2A | Agent ↔ Agent | Task-based |
| AG-UI | Agent ↔ User | {len(df)} streaming events |
"""

print(report)

with open("lab-077/protocol_summary.md", "w") as f:
    f.write(report)
print("💾 Saved to lab-077/protocol_summary.md")
```

---

## 🐛 Bug-Fix Exercise

The file `lab-077/broken_agui.py` contains **3 bugs** that produce incorrect event analysis. Can you find and fix them all?

Run the self-tests to see which ones fail:

```bash
python lab-077/broken_agui.py
```

You should see **3 failed tests**. Each test corresponds to one bug:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Agent→frontend event count | Should filter `agent_to_frontend`, not `frontend_to_agent` |
| Test 2 | Total event types | Should use `len(df)`, not `df['category'].nunique()` |
| Test 3 | Frontend→agent event count | Should count `frontend_to_agent` direction, not `input` category |

Fix all 3 bugs, then re-run. When you see `All passed!`, you're done!

---


## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What role does AG-UI play in the interoperability trilogy?"

    - A) It connects agents to external tools and APIs
    - B) It connects agents to other agents for collaboration
    - C) It connects agents to frontend user interfaces via streaming events
    - D) It connects agents to databases for storage

    ??? success "✅ Reveal Answer"
        **Correct: C) It connects agents to frontend user interfaces via streaming events**

        The interoperability trilogy consists of MCP (agent↔tools), A2A (agent↔agents), and AG-UI (agent↔users). AG-UI uses a streaming event model to enable real-time communication between AI agents and frontend applications like CopilotKit.

??? question "**Q2 (Multiple Choice):** Why is the AG-UI protocol asymmetric (more agent→frontend events than frontend→agent)?"

    - A) The frontend is too slow to send many events
    - B) Agents produce most data (text, tool calls, state) while frontends mainly send commands and tool results
    - C) The protocol limits frontend events for security reasons
    - D) Frontend events are batched into fewer messages

    ??? success "✅ Reveal Answer"
        **Correct: B) Agents produce most data (text, tool calls, state) while frontends mainly send commands and tool results**

        In a typical interaction, the agent streams text tokens, emits tool call events, and pushes state updates — all flowing to the frontend. The frontend's role is primarily to initiate runs (`RunAgent`) and return tool execution results (`ToolResult`).

??? question "**Q3 (Run the Lab):** How many event types flow from agent to frontend?"

    Run the Step 3 analysis on [📥 `agui_events.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-077/agui_events.csv) and count `agent_to_frontend` events.

    ??? success "✅ Reveal Answer"
        **9 events**

        The following events flow from agent to frontend: `LifecycleStarted`, `LifecycleCompleted`, `TextMessageStart`, `TextMessageContent`, `TextMessageEnd`, `ToolCallStart`, `ToolCallArgs`, `ToolCallEnd`, and `StateUpdate`. That's **9** out of 12 total event types.

??? question "**Q4 (Run the Lab):** How many event types flow from frontend to agent?"

    Count the events with `frontend_to_agent` direction.

    ??? success "✅ Reveal Answer"
        **3 events**

        Only **3 events** flow from frontend to agent: `RunAgent` (input), `ToolResult` (tool), and `StateSnapshot` (state). The protocol is heavily asymmetric — agents send 3× more event types than frontends.

??? question "**Q5 (Run the Lab):** What is the total number of event types in the AG-UI protocol?"

    Load the CSV and check the total row count.

    ??? success "✅ Reveal Answer"
        **12 event types**

        The AG-UI protocol defines exactly **12 event types** across 5 categories: tool (4), text (3), lifecycle (2), state (2), and input (1).

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| AG-UI Protocol | Event-based protocol connecting agents to frontend UIs |
| Interoperability Trilogy | MCP (tools) + A2A (agents) + AG-UI (users) = complete agent ecosystem |
| Event Model | 12 event types: 9 agent→frontend, 3 frontend→agent |
| Categories | lifecycle, text, tool, state, input |
| Streaming Architecture | Continuous event stream replaces request/response pattern |
| Frontend Responsibility | UI must execute tools and return results when agent requests them |

---

## Next Steps

- **[Lab 029](lab-029-mcp-protocol.md)** — MCP Protocol (the tools leg of the trilogy)
- **[Lab 070](lab-070-agent-ux-patterns.md)** — Agent UX Patterns (design patterns for agent-powered UIs)
- **[Lab 076](lab-076-microsoft-agent-framework.md)** — Microsoft Agent Framework (build agents that speak AG-UI)
- **[Lab 034](lab-034-multi-agent-sk.md)** — Multi-Agent with Semantic Kernel (agents that collaborate via A2A)
