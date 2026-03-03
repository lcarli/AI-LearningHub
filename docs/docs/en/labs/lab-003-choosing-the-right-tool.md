# Lab 003: Choosing the Right Tool

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-50">L50</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~15 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — No account needed</span>
</div>

## What You'll Learn

- A practical decision framework for choosing your AI agent tool
- Understanding the key trade-offs (control vs. simplicity, cost vs. power)
- Suggested learning routes based on your role and goals

---

## Introduction

After reviewing the landscape in [Lab 002](lab-002-agent-landscape.md), the natural question is: **where should I start?**

Use the decision flowchart and role-based guides below to find your path.

---

## Decision Flowchart

```
START: What's your primary goal?
         │
         ├── "Build an agent for Microsoft Teams"
         │      └── Copilot Studio (no-code) or Teams AI Library (code)
         │
         ├── "Add AI to my VS Code extension or GitHub workflow"
         │      └── VS Code Chat Participant API / GitHub Copilot Extensions
         │
         ├── "Production AI agent on Azure with monitoring & security"
         │      └── Microsoft Foundry Agent Service
         │
         ├── "Build a sophisticated agent in Python/C# with full control"
         │      └── Semantic Kernel
         │
         ├── "Orchestrate multiple AI agents for complex tasks"
         │      └── AutoGen (+ Semantic Kernel for agent logic)
         │
         ├── "Connect my existing tool/database/API to AI agents"
         │      └── Build an MCP Server
         │
         └── "Just experiment / learn for free"
                └── GitHub Models + Semantic Kernel
```

---

## By Role

### 🎯 Business Analyst / Power User
**Goal:** Automate workflows, create agents without writing code.

Recommended path:
1. [Lab 001](lab-001-what-are-ai-agents.md) → [Lab 011](lab-011-copilot-studio-first-agent.md) → [Lab 024](lab-024-teams-ai-library.md)

**Tools:** Copilot Studio, Power Automate, M365 Copilot

---

### 👨‍💻 Developer (Python / C#)
**Goal:** Write agents in code, integrate with existing systems.

Recommended path:
1. [Lab 013](lab-013-github-models.md) → [Lab 014](lab-014-sk-hello-agent.md) → [Lab 020](lab-020-mcp-server-python.md) → [Lab 030](lab-030-foundry-agent-mcp.md)

**Tools:** Semantic Kernel, Microsoft Foundry, MCP

---

### 🔌 Integration / Platform Engineer
**Goal:** Expose existing systems (databases, APIs) to AI agents.

Recommended path:
1. [Lab 012](lab-012-what-is-mcp.md) → [Lab 020](lab-020-mcp-server-python.md) → [Lab 031](lab-031-pgvector-semantic-search.md) → [Lab 032](lab-032-row-level-security.md)

**Tools:** MCP, PostgreSQL + pgvector, Row Level Security

---

### 🏗️ Solution Architect / Senior Engineer
**Goal:** Design production multi-agent systems with governance and observability.

Recommended path:
1. [Lab 030](lab-030-foundry-agent-mcp.md) → [Lab 033](lab-033-agent-observability.md) → [Lab 034](lab-034-multi-agent-sk.md) → [Lab 040](lab-040-autogen-multi-agent.md)

**Tools:** Foundry, Semantic Kernel, AutoGen, App Insights

---

### 🎓 Student / Learner
**Goal:** Understand AI agents and build something real, for free.

Recommended path:
1. [Lab 001](lab-001-what-are-ai-agents.md) → [Lab 002](lab-002-agent-landscape.md) → [Lab 013](lab-013-github-models.md) → [Lab 014](lab-014-sk-hello-agent.md) → [Lab 022](lab-022-rag-github-models.md)

**Tools:** GitHub Models, Semantic Kernel — everything free!

---

## The Two Key Trade-offs

### 1. Control vs. Simplicity

```
More control                           More simplicity
     │                                        │
     ▼                                        ▼
AutoGen          SK         Foundry    Copilot Studio
LangChain    (SDK)       (managed)    (no-code GUI)
```

More control = more flexibility + more responsibility.  
More simplicity = faster to build + less customizable.

### 2. Free vs. Paid

```
Always free:         GitHub free:         Azure sub needed:
─────────────        ────────────         ─────────────────
L50 labs             GitHub Models        Foundry Agent Svc
(conceptual)         SK with free LLMs    Azure PostgreSQL
                     Local MCP servers    App Insights
                     VS Code extensions   L300+ labs
```

---

## Summary

There's no single "right" tool — it depends on your role, goals, and constraints. The good news: **everything in this hub starts free**, and you can always level up. The decision framework above points you to the most efficient path.

---

## Next Steps

Pick your path and dive in!

- **No-code route:** → [Lab 011 — Copilot Studio](lab-011-copilot-studio-first-agent.md)
- **Developer route (free):** → [Lab 013 — GitHub Models](lab-013-github-models.md)
- **MCP route:** → [Lab 012 — What is MCP?](lab-012-what-is-mcp.md)
- **Full Azure route:** → [Lab 030 — Foundry + MCP](lab-030-foundry-agent-mcp.md)
