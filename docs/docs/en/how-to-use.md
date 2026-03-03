# How to Use This Hub

This page explains how the AI Agents Learning Hub is structured so you can navigate it effectively and get the most out of every lab.

---

## 📊 The Level System

Every lab is tagged with a level from **50 to 400**, inspired by Microsoft's conference session numbering (a widely understood signal of depth).

| Level | Badge | Name | What to expect | Account needed |
|-------|-------|------|----------------|----------------|
| 50 | <span class="level-badge level-50">L50</span> | Awareness | Reading and concepts. No tools, no account. | ❌ None |
| 100 | <span class="level-badge level-100">L100</span> | Foundations | First hands-on labs. Minimal setup. | ✅ GitHub free |
| 200 | <span class="level-badge level-200">L200</span> | Intermediate | Code + free-tier cloud (GitHub Models). | ✅ GitHub free |
| 300 | <span class="level-badge level-300">L300</span> | Advanced | Cloud services, integration patterns. | ✅ Azure subscription |
| 400 | <span class="level-badge level-400">L400</span> | Expert | Production architecture, evaluations, cost. | ✅ Azure paid |

!!! tip "Start at the right level"
    Don't skip L50/L100 even if you're an experienced developer — the conceptual framing helps you make better decisions later.

---

## 🗺️ Learning Paths

Labs are grouped into **8 Learning Paths**, each focused on a tool or technology:

| Path | Best for | Entry point |
|------|----------|-------------|
| 🤖 GitHub Copilot | GitHub users, developers | L100 |
| 🏭 Microsoft Foundry | Azure developers, ML engineers | L200 |
| 🔌 MCP | Anyone building agent integrations | L100 |
| 🧠 Semantic Kernel | Python / C# developers | L100 |
| 📚 RAG | Developers working with documents/data | L100 |
| 👥 Agent Builder — Teams | M365 developers | L100 |
| 💻 Agent Builder — VS Code | Extension developers | L100 |
| ⚙️ Pro Code Agents | Senior engineers, architects | L200 |

Each path has an **index page** with the full list of labs, a recommended order, and a short overview of what you'll build.

---

## 💡 Suggested Learning Routes

### Route A — "Zero to Agent" (No account required to start)
```
Lab 001 → Lab 002 → Lab 003 → Lab 012 → Lab 020 (Python or C#)
```
Go from zero knowledge to running your own MCP server locally, no cloud account needed.

### Route B — "GitHub-only" (Free GitHub account only)
```
Lab 010 → Lab 013 → Lab 014 → Lab 022 → Lab 023
```
Use GitHub Copilot, GitHub Models, and Semantic Kernel — everything free, no credit card.

### Route C — "Full Azure Stack"
```
Lab 013 → Lab 020 → Lab 030 → Lab 031 → Lab 032 → Lab 033
```
Requires Azure subscription. Build a complete Foundry Agent with MCP, pgvector, RLS, and observability.

### Route D — "Teams Developer"
```
Lab 001 → Lab 011 → Lab 024
```
Build Copilot Studio agents and Teams bots step by step.

---

## 🔖 Reading a Lab Page

Each lab page follows this standard structure:

```
# Lab XXX: [Title]

[Info box: Level · Path · Time · Cost]

## What You'll Learn
## Introduction
## Prerequisites Setup
## Lab Exercise
  ### Step 1 ...
  ### Step 2 ...
## Summary
## Next Steps
```

- **Info box** at the top tells you everything at a glance: level, estimated time, and cost/account requirements.
- **Prerequisites Setup** tells you exactly what to install or configure — with direct links to free trial sign-ups.
- **Lab Exercise** is the step-by-step walkthrough.
- **Next Steps** links to the natural continuation of the lab.

---

## 💰 Free vs. Paid — Our Commitment

We believe the best learning resources are accessible. Our goals:

- ✅ **L50 and L100**: Zero cost, zero credit card, just a free GitHub account
- ✅ **L200**: Use [GitHub Models](https://github.com/marketplace/models) — free inference, no credit card
- ⚠️ **L300**: Azure free tier where possible; clearly marked when an Azure subscription is needed
- ⚠️ **L400**: Paid Azure resources required — estimated costs noted in each lab

→ See [Prerequisites & Accounts](prerequisites.md) for the full setup guide.
