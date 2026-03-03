---
tags: [free, beginner, no-account-needed, awareness]
---
# Lab 002: AI Agent Landscape 2025

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-50">L50</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~20 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — No account needed</span>
</div>

## What You'll Learn

- The Microsoft AI agent ecosystem at a glance
- When to use each platform: Copilot Studio, Microsoft Foundry, Semantic Kernel, Teams AI Library, AutoGen
- How MCP fits into all of them
- The spectrum from no-code to pro-code

---

## Introduction

The Microsoft ecosystem offers multiple overlapping ways to build AI agents. This can be confusing — should you use Copilot Studio or Foundry? Semantic Kernel or LangChain? MCP or direct API calls?

This lab gives you a **map of the landscape** so you can make informed choices.

---

## The Spectrum: No-Code → Pro-Code

```
No-Code ─────────────────────────────────────── Pro-Code
   │                                                 │
   ▼                                                 ▼
Copilot      Copilot Studio    Foundry         Semantic Kernel
Studio       + Custom Conn.    Agent Svc       AutoGen / LangChain
(GUI only)   (some config)     (SDK + portal)  (full code control)
```

There's no "better" end — it depends on your use case, team skills, and governance requirements.

---

## Platform Comparison

### 🤖 GitHub Copilot

| | |
|---|---|
| **What it is** | AI coding assistant embedded in your IDE and GitHub |
| **Best for** | Individual developers, coding productivity |
| **Agent capability** | Copilot Chat, GitHub Models, Copilot Extensions |
| **Skill needed** | Low (chat) to High (extensions) |
| **Cost** | Free tier available |

### 🎨 Copilot Studio (Low-Code)

| | |
|---|---|
| **What it is** | Microsoft's no-code/low-code agent builder |
| **Best for** | Business analysts, M365 users, Teams agents |
| **Agent capability** | Topic flows, connectors, custom actions, Azure OpenAI |
| **Skill needed** | Low — no coding required |
| **Cost** | Included with many M365 licenses; free trial available |

### 🏭 Microsoft Foundry Agent Service

| | |
|---|---|
| **What it is** | Managed agent runtime on Azure |
| **Best for** | Production agents, enterprise scale |
| **Agent capability** | Tool calling, Code Interpreter, MCP servers, evaluation |
| **Skill needed** | Medium — Python or C# SDK |
| **Cost** | Azure subscription (free tier for prototyping) |

### 🧠 Semantic Kernel

| | |
|---|---|
| **What it is** | Open-source agent SDK (Python / C# / Java) |
| **Best for** | Developers who want code control with Microsoft stack |
| **Agent capability** | Plugins, vector memory, planners, multi-agent |
| **Skill needed** | Medium — Python or C# experience |
| **Cost** | Free (open-source); LLM costs depend on backend |

### ⚙️ AutoGen

| | |
|---|---|
| **What it is** | Open-source multi-agent framework by Microsoft Research |
| **Best for** | Complex multi-agent workflows, research, orchestration |
| **Agent capability** | Nested conversations, human-in-the-loop, code execution |
| **Skill needed** | High — Python, advanced agent concepts |
| **Cost** | Free (open-source); LLM costs |

### 👥 Teams AI Library

| | |
|---|---|
| **What it is** | SDK for building AI-powered Teams bots |
| **Best for** | Teams-native apps, enterprise collaboration |
| **Agent capability** | Conversational AI inside Teams channels, M365 data access |
| **Skill needed** | Medium — Node.js or C# |
| **Cost** | Free SDK; requires M365 tenant |

---

## Where Does MCP Fit?

**Model Context Protocol (MCP)** is not a platform — it's a **connector standard**. Think of it as the USB-C of AI tools: one standard interface that any agent can use to plug in to any data source or tool.

```
┌─────────────────────────────────────────────────┐
│              Any AI Agent                        │
│  (Foundry / SK / Copilot / Claude / ChatGPT)    │
└──────────────────┬──────────────────────────────┘
                   │  MCP Protocol
         ┌─────────▼──────────┐
         │    MCP Server      │
         │  (your tool)       │
         └─────────┬──────────┘
                   │
    ┌──────────────▼──────────────┐
    │  PostgreSQL / REST API /    │
    │  File System / IoT / etc.   │
    └─────────────────────────────┘
```

MCP works with **all the platforms above** — and also with Claude Desktop, OpenAI, and any other MCP-compatible host.

---

## Decision Cheat Sheet

| Situation | Recommended tool |
|-----------|-----------------|
| "I want an agent in Teams for my team, no coding" | Copilot Studio |
| "I want to add AI to my VS Code extension" | VS Code Chat Participant API |
| "I want a production agent backed by Azure, with monitoring" | Microsoft Foundry Agent Service |
| "I want to write Python/C# code to build a sophisticated agent" | Semantic Kernel |
| "I want multiple AI agents collaborating on complex tasks" | AutoGen |
| "I want to connect my existing tool/API to any AI agent" | Build an MCP Server |
| "I just want to experiment with LLMs for free" | GitHub Models |

---

## 🧠 Knowledge Check

??? question "1. Which Microsoft tool is best for building a no-code agent in Teams, with no coding required?"
    **Copilot Studio.** It provides a GUI-based builder for agents that live inside Microsoft 365 / Teams, using natural language to define behavior, knowledge sources, and actions — no code needed.

??? question "2. What does MCP stand for, and what is its role in the ecosystem?"
    **Model Context Protocol.** MCP is a universal standard (like USB-C for AI tools) that lets *any* agent connect to *any* data source or tool via a common interface. It works across Copilot Studio, Foundry, Semantic Kernel, Claude, and others.

??? question "3. What is the key difference between Semantic Kernel and AutoGen?"
    **Semantic Kernel** is an SDK for building a **single sophisticated agent** — with plugins, memory, and planners. **AutoGen** is for **multi-agent orchestration** — multiple specialized agents collaborating, each doing a part of a complex task. SK focuses on depth; AutoGen focuses on breadth across agents.

---

## Summary

The Microsoft ecosystem has tools for **every skill level and use case**— from no-code Copilot Studio to pro-code AutoGen. MCP is the universal connector that works across all of them. In the next lab, we'll help you choose the right tool for your specific situation.

---

## Next Steps

→ **[Lab 003: Choosing the Right Tool](lab-003-choosing-the-right-tool.md)**
