# Lab 001: What are AI Agents?

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-50">L50</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~15 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — No account needed</span>
</div>

## What You'll Learn

- What an AI agent is (and isn't)
- The four core properties of an agent: **perception, memory, reasoning, action**
- How agents differ from simple chatbots and from traditional software
- Real-world examples of AI agents

---

## Introduction

The word "agent" is everywhere in AI right now — but what does it actually mean?

An **AI agent** is software that uses a Large Language Model (LLM) as its reasoning engine to **autonomously pursue a goal**, deciding *what to do* and *which tools to call* at each step — without you pre-programming every possible path.

The key word is **autonomous**: the agent doesn't just answer a question. It plans, acts, observes the result, and adjusts.

---

## The Four Properties of an Agent

### 1. 🔍 Perception
The agent receives input — a user message, a file, an API response, an event.

### 2. 🧠 Memory
The agent stores information across turns:
- **Short-term (context window):** the current conversation
- **Long-term (vector store / DB):** facts, history, retrieved documents

### 3. 💡 Reasoning
The LLM decides *what to do next*: answer directly, call a tool, ask a clarifying question, or break the goal into sub-steps.

### 4. ⚡ Action
The agent *does something*: calls an API, queries a database, writes a file, sends an email, triggers another agent.

```
User Goal
    │
    ▼
┌──────────────────────────────────┐
│          AI Agent Loop           │
│                                  │
│  Perceive → Reason → Act         │
│      ▲                 │         │
│      └─── Observe ◄────┘         │
│                                  │
└──────────────────────────────────┘
    │
    ▼
Goal Achieved
```

---

## Agent vs. Chatbot vs. Traditional Software

| | Traditional Software | Chatbot | AI Agent |
|---|---|---|---|
| **Logic defined by** | Developer | Developer | LLM (at runtime) |
| **Handles new situations** | ❌ Only what's coded | ⚠️ Within trained patterns | ✅ Adapts dynamically |
| **Uses tools** | ✅ Hardcoded | ⚠️ Limited | ✅ Discovers and calls tools |
| **Multi-step reasoning** | ❌ | ❌ | ✅ |
| **Predictability** | ✅ Very predictable | ✅ Mostly predictable | ⚠️ Less predictable |

!!! tip "When NOT to use an agent"
    Agents are powerful but complex. Use a **simple LLM call** for single-turn Q&A. Use an **agent** only when the task requires multi-step reasoning, tool use, or dynamic decision-making.

---

## Real-World Examples

| Agent | What it does |
|-------|-------------|
| **GitHub Copilot** | Reads your code, suggests completions, chats, runs commands |
| **Zava Sales Agent** *(this repo's workshop)* | Queries PostgreSQL, generates charts, interprets sales trends |
| **Microsoft 365 Copilot** | Reads emails, calendar, files, drafts replies, summarizes meetings |
| **AutoGen research agent** | Spawns sub-agents to search, synthesize, and write a report |

---

## Key Terms

| Term | Definition |
|------|-----------|
| **LLM** | Large Language Model — the AI brain (e.g., GPT-4o, Phi-4) |
| **Tool / Function** | A function the LLM can call (e.g., `search_database`, `send_email`) |
| **Context window** | The "working memory" of the LLM — everything it can see at once |
| **Prompt** | The instructions + context sent to the LLM |
| **Token** | The unit LLMs process — roughly ¾ of a word |
| **Grounding** | Connecting agent responses to real, verified data |

---

## Summary

An AI agent is an LLM-powered system that **perceives, remembers, reasons, and acts** to achieve a goal. It differs from traditional software because the logic is not hardcoded — the LLM decides at runtime. This flexibility is powerful, but requires careful design of instructions and tools.

---

## Next Steps

→ **[Lab 002: AI Agent Landscape 2025](lab-002-agent-landscape.md)** — Compare all the tools and platforms available today.
