---
tags: [free, beginner, no-account-needed, awareness]
---
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

![Decision Flowchart](../../assets/diagrams/decision-flowchart.svg)

??? question "🤔 Check Your Understanding"
    According to the decision flowchart, what tool should you use if your primary goal is to connect an existing database or API to AI agents?

    ??? success "Answer"
        You should **build an MCP Server**. MCP (Model Context Protocol) provides a universal connector standard so any MCP-compatible AI agent can access your tool or data source through a common interface.

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
1. [Lab 001](lab-001-what-are-ai-agents.md) → [Lab 002](lab-002-agent-landscape.md) → [Lab 013](lab-013-github-models.md) → [Lab 014](lab-014-sk-hello-agent.md) → [Lab 022](lab-022-rag-github-models-pgvector.md)

**Tools:** GitHub Models, Semantic Kernel — everything free!

??? question "🤔 Check Your Understanding"
    A solution architect needs to design a production multi-agent system with observability and governance. Which combination of tools does this lab recommend?

    ??? success "Answer"
        **Foundry, Semantic Kernel, AutoGen, and App Insights.** The recommended learning path is: Foundry Agent MCP → Agent Observability → Multi-Agent SK → AutoGen Multi-Agent. This covers managed runtime, agent logic, multi-agent orchestration, and monitoring.

??? question "🤔 Check Your Understanding"
    What does "more control = more responsibility" mean in the control vs. simplicity trade-off?

    ??? success "Answer"
        Pro-code tools like AutoGen and Semantic Kernel give you **full flexibility** over agent logic, but you must handle more yourself — error handling, deployment, security, scaling. No-code tools like Copilot Studio are **faster to build** but less customizable. The right choice depends on your team's skills and requirements.

---

## The Two Key Trade-offs

![Control vs Simplicity, Free vs Paid](../../assets/diagrams/tradeoffs-control-cost.svg)

More control = more flexibility + more responsibility.  
More simplicity = faster to build + less customizable.

??? question "🤔 Check Your Understanding"
    Can a student with no Azure subscription and no budget still build a working AI agent using the tools in this hub?

    ??? success "Answer"
        **Yes!** GitHub Models and Semantic Kernel are completely free. The L50 conceptual labs and L100–L200 labs using GitHub Models require no Azure subscription. Students can build real agents, run MCP servers locally, and learn the full agent development lifecycle at zero cost.

### 2. Free vs. Paid

The SVG above includes the full Free vs. Paid comparison. Start free → add Azure only when you need production features.

---

## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** A developer wants to build a VS Code extension that responds to `@mybot` in GitHub Copilot Chat. Which tool/API should they use?"

    - A) Copilot Studio
    - B) VS Code Chat Participant API (Lab 025)
    - C) Microsoft Foundry Agent Service
    - D) Azure Bot Service

    ??? success "✅ Reveal Answer"
        **Correct: B — VS Code Chat Participant API**

        The Chat Participant API registers a `@yourextension` participant directly inside VS Code's Copilot Chat interface. It runs entirely inside VS Code — no Azure subscription, no server required. Copilot Studio is for Teams/M365 non-code agents. Foundry is for server-side hosted agents with full cloud scale.

??? question "**Q2 (Multiple Choice):** Which factor is MOST important when choosing between Copilot Studio and Semantic Kernel?"

    - A) The programming language you prefer (Python vs C#)
    - B) Whether you need cloud deployment or local deployment
    - C) Your role and how much code control you need — citizen developer vs. professional developer
    - D) The LLM provider (OpenAI vs Anthropic)

    ??? success "✅ Reveal Answer"
        **Correct: C**

        The primary decision axis is **code control vs. speed**. Copilot Studio targets citizen developers and IT pros who need a functional agent fast with no code. Semantic Kernel targets professional developers who need full control over logic, tool schemas, memory patterns, and production behavior. Both support multiple LLMs and cloud deployment.

??? question "**Q3 (Multiple Choice):** The 'least privilege' principle says your agent should have access to exactly what it needs — no more. Which of these violates least privilege?"

    - A) A product search agent that can call `search_products()` and `get_product_details()`
    - B) A customer service agent given read-only database access
    - C) An order-status agent given full admin credentials to the orders database
    - D) A weather agent that can only call the public weather API

    ??? success "✅ Reveal Answer"
        **Correct: C — Full admin credentials violates least privilege**

        An order-status agent only needs to *read* order records. Giving it admin credentials means a prompt injection attack or logic error could delete orders, modify prices, or access all customer data. The correct setup is a read-only database user scoped to the specific tables the agent needs. Options A, B, and D all follow least privilege correctly.

---

## Summary

There's no single "right" tool — it depends on your role, goals, and constraints.The good news: **everything in this hub starts free**, and you can always level up. The decision framework above points you to the most efficient path.

---

## Next Steps

Pick your path and dive in!

- **No-code route:** → [Lab 011 — Copilot Studio](lab-011-copilot-studio-first-agent.md)
- **Developer route (free):** → [Lab 013 — GitHub Models](lab-013-github-models.md)
- **MCP route:** → [Lab 012 — What is MCP?](lab-012-what-is-mcp.md)
- **Full Azure route:** → [Lab 030 — Foundry + MCP](lab-030-foundry-agent-mcp.md)
- **Want to understand LLMs first?** → [Lab 004 — How LLMs Work](lab-004-how-llms-work.md)
