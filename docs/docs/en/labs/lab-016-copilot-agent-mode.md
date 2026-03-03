---
tags: [github-copilot, free, vscode]
---
# Lab 016: GitHub Copilot Agent Mode

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Path:</strong> <a href="../paths/copilot/">🤖 GitHub Copilot</a></span>
  <span><strong>Time:</strong> ~30 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-github">GitHub Free</span> — Free GitHub account (free tier includes agent mode)</span>
</div>

## What You'll Learn

- What makes **agent mode** different from regular Copilot Chat
- How to activate and use agent mode in VS Code
- How the agent reads your codebase, plans, and executes multi-step tasks
- How to connect **MCP servers** to expand agent capabilities
- Best practices and limitations

---

## Introduction

GitHub Copilot in VS Code has three modes:

| Mode | What it does |
|------|-------------|
| **Ask** | Answers questions about code; read-only |
| **Edit** | Makes changes to files you specify |
| **Agent** ⭐ | Autonomously explores your codebase, runs commands, uses tools, and completes multi-step tasks |

**Agent mode** is the newest and most powerful. You describe a goal, and Copilot acts like a junior developer: it reads files, writes code, runs tests, and iterates until done — asking for your approval at key decision points.

!!! info "Available in VS Code 1.99+"
    Agent mode requires VS Code 1.99 or later and GitHub Copilot extension. Check for updates if you don't see the mode switcher.

---

## Prerequisites Setup

1. **VS Code 1.99+** with GitHub Copilot extension installed
2. **Free GitHub account** with Copilot enabled ([github.com/features/copilot](https://github.com/features/copilot))
3. A project to work with (we'll use a simple Python project)

---

## Lab Exercise

### Step 1: Activate agent mode

1. Open the Copilot Chat panel (`Ctrl+Shift+I`)
2. Look for the mode switcher at the top of the chat input (dropdown showing "Ask", "Edit", "Agent")
3. Select **"Agent"**

You'll notice the input changes — you can now describe goals, not just ask questions.

### Step 2: Explore codebase exploration

Create a simple project (or use any existing one). In agent mode, ask:

```
Analyze this codebase and give me a summary of:
1. What it does
2. The main files and their responsibilities
3. Any potential issues you see
```

Watch what Copilot does:
- It reads multiple files autonomously
- It references specific line numbers
- It synthesizes a coherent summary

This is fundamentally different from "Ask" mode — the agent *searches* your codebase, it doesn't wait for you to paste code.

### Step 3: Multi-step code task

Try a task that requires multiple steps:

```
Add a unit test suite for this project:
1. Create a tests/ folder
2. Write tests for the main functions
3. Make sure they pass (run them)
```

Observe the agent:
- Creates files
- Writes test code
- Runs the tests via terminal
- Fixes failures it discovers
- Reports when done

!!! tip "You stay in control"
    The agent asks for confirmation before running terminal commands. You can review and approve/reject each action.

### Step 4: Use built-in tools

Agent mode has built-in tools it uses automatically:

| Tool | What it does |
|------|-------------|
| `read_file` | Reads any file in your workspace |
| `list_directory` | Explores folder structure |
| `run_terminal_command` | Runs shell commands (with your approval) |
| `create_file` | Creates new files |
| `replace_in_file` | Makes targeted edits |
| `search_web` | (If enabled) Searches the internet |

You don't invoke these directly — the agent decides when to use them.

### Step 5: Connect an MCP server

Agent mode supports MCP servers, dramatically expanding what it can do. Let's connect the products server from [Lab 020](lab-020-mcp-server-python.md):

**1. Start the MCP server (from Lab 020):**
```bash
cd products-mcp-server
python server.py  # stdio mode
```

**2. Configure VS Code to use it (`.vscode/mcp.json`):**
```json
{
  "servers": {
    "products": {
      "type": "stdio",
      "command": "python",
      "args": ["server.py"],
      "cwd": "${workspaceFolder}/products-mcp-server"
    }
  }
}
```

**3. Restart VS Code and ask in agent mode:**
```
What product categories are available in our catalog?
Find all camping products under $100.
```

The agent now has access to your custom tools alongside its built-in ones!

### Step 6: Advanced — custom instructions

Create `.github/copilot-instructions.md` to customize agent behavior for your project:

```markdown
# Copilot Instructions

## Project
This is a Python FastAPI project. Always use async/await.

## Code style
- Use type hints on all functions
- Docstrings follow Google style
- Tests use pytest with fixtures

## Never
- Use print() for logging (use loguru)
- Commit secrets or API keys
- Skip error handling
```

The agent reads this file and applies these rules automatically.

---

## Agent Mode vs. Edit Mode: When to Use Which

| Use Edit mode when | Use Agent mode when |
|-------------------|---------------------|
| You know exactly what to change | You have a goal but not a plan |
| Simple, targeted edits | Multi-file, multi-step tasks |
| You want full control of each edit | You want the agent to figure it out |
| Quick fixes, refactors | Adding features, writing tests, debugging |

---

## Limitations

- **Approval required** for terminal commands (by design — security)
- **Context limit** applies — very large codebases may require guidance on where to look
- **Non-deterministic** — same prompt may produce slightly different approaches
- **Review everything** — agent mode is fast but not infallible; always review generated code

---

## Summary

GitHub Copilot agent mode transforms your editor into an autonomous coding assistant:

- ✅ **Reads your codebase** — understands context without you pasting code
- ✅ **Multi-step execution** — plans and completes complex tasks
- ✅ **Terminal access** — runs tests, installs packages, executes scripts
- ✅ **MCP integration** — connect any tool or data source
- ✅ **Stays in VS Code** — no context switching

---

## Next Steps

- **Build an MCP server to extend agent mode:** → [Lab 020 — MCP Server in Python](lab-020-mcp-server-python.md)
- **Build a VS Code Chat Participant (custom @agent):** → [Lab 025 — VS Code Chat Participant](lab-025-vscode-chat-participant.md)
