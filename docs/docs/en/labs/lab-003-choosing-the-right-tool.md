---
tags: [free, beginner, no-account-needed, awareness, persona-student, persona-developer, persona-analyst, persona-architect, persona-admin]
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
1. [Lab 001](lab-001-what-are-ai-agents.md) → [Lab 011](lab-011-copilot-studio-first-agent.md) → [Lab 069](lab-069-declarative-agents.md) → [Lab 075](lab-075-powerbi-copilot.md)

**Tools:** Copilot Studio, Declarative Agents, Power BI Copilot, M365 Copilot

---

### 👨‍💻 Developer (Python / C#)
**Goal:** Write agents in code, integrate with existing systems.

Recommended path:
1. [Lab 013](lab-013-github-models.md) → [Lab 076](lab-076-microsoft-agent-framework.md) → [Lab 020](lab-020-mcp-server-python.md) → [Lab 082](lab-082-agent-guardrails.md) → [Lab 084](lab-084-capstone-outdoorgear-agent.md)

**Tools:** Agent Framework (SK), MCP, Guardrails, GitHub Models

---

### 🔌 Integration / Platform Engineer
**Goal:** Expose existing systems (databases, APIs) to AI agents.

Recommended path:
1. [Lab 012](lab-012-what-is-mcp.md) → [Lab 020](lab-020-mcp-server-python.md) → [Lab 031](lab-031-pgvector-semantic-search.md) → [Lab 054](lab-054-a2a-protocol.md) → [Lab 064](lab-064-securing-mcp-apim.md)

**Tools:** MCP, A2A Protocol, pgvector, Azure API Management

---

### 🏗️ Solution Architect
**Goal:** Design production multi-agent systems with governance and observability.

Recommended path:
1. [Lab 076](lab-076-microsoft-agent-framework.md) → [Lab 049](lab-049-foundry-iq-agent-tracing.md) → [Lab 050](lab-050-multi-agent-observability.md) → [Lab 074](lab-074-foundry-agent-service.md) → [Lab 084](lab-084-capstone-outdoorgear-agent.md)

**Tools:** Agent Framework, Foundry Agent Service, OpenTelemetry, A2A + MCP

---

### 📊 Data Engineer / Analyst
**Goal:** Build AI-powered analytics, data agents, and enrichment pipelines.

Recommended path:
1. [Lab 047](lab-047-work-iq-copilot-analytics.md) → [Lab 052](lab-052-fabric-conversational-agent.md) → [Lab 053](lab-053-fabric-ai-functions.md) → [Lab 067](lab-067-graphrag.md) → [Lab 075](lab-075-powerbi-copilot.md)

**Tools:** Fabric IQ, Work IQ, GraphRAG, Power BI Copilot

---

### 🔒 Enterprise Admin / IT Governance
**Goal:** Govern, secure, and monitor AI agent deployments across the organization.

Recommended path:
1. [Lab 063](lab-063-agent-identity-entra.md) → [Lab 065](lab-065-purview-dspm-ai.md) → [Lab 066](lab-066-copilot-studio-governance.md) → [Lab 064](lab-064-securing-mcp-apim.md) → [Lab 046](lab-046-agent-365.md)

**Tools:** Entra ID, Purview DSPM, Copilot Studio Governance, APIM, Agent 365

---

### 🎓 Student / Learner
**Goal:** Understand AI agents and build something real, for free.

Recommended path:
1. [Lab 001](lab-001-what-are-ai-agents.md) → [Lab 004](lab-004-how-llms-work.md) → [Lab 013](lab-013-github-models.md) → [Lab 078](lab-078-foundry-local.md) → [Lab 076](lab-076-microsoft-agent-framework.md) → [Lab 022](lab-022-rag-github-models-pgvector.md)

**Tools:** GitHub Models, Foundry Local, Agent Framework — everything free!

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
