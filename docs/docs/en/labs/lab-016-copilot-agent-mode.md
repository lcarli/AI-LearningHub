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

## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-016/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `outdoorgear_api.py` | Python script | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-016/outdoorgear_api.py) |

---

## Lab Exercise

### Step 1: Activate agent mode

1. Open the Copilot Chat panel (`Ctrl+Shift+I`)
2. Look for the mode switcher at the top of the chat input
3. Select **"Agent"**

You'll notice the input changes — you can now describe goals, not just ask questions.

---

### Step 2: The Broken Project — Fix it with Agent Mode 🐛

This exercise gives you a **real broken Python project** to fix using agent mode. The goal is to see how the agent reads files, identifies problems, and fixes them — step by step.

**Download the project:**
```bash
cd AI-LearningHub/docs/docs/en/labs/lab-016
```

Or copy the file [📥 `outdoorgear_api.py`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-016/outdoorgear_api.py) below:

```python title="lab-016/outdoorgear_api.py — 5 bugs, 1 missing feature, no tests"
--8<-- "labs/lab-016/outdoorgear_api.py"
```

**Open the folder in VS Code** (important — the agent needs to see the whole project):
```bash
code docs/docs/en/labs/lab-016/
```

---

### Phase 1: Let the agent find and fix the bugs

Switch to **Agent mode** and type exactly this:

```
Fix all the bugs in outdoorgear_api.py so that the basic tests 
at the bottom of the file pass when I run: python outdoorgear_api.py

Don't fix the "Test 7" failure yet — that requires a missing function.
```

Watch what the agent does:

1. 🔍 It **reads the file** without you pasting anything
2. 🐛 It **identifies each bug** and explains why it's wrong
3. ✏️ It **proposes fixes** and asks your approval
4. ▶️ It **runs the file** to verify the fix worked

After accepting, run the verification:
```bash
python outdoorgear_api.py
```
Tests 1–6 should pass. Test 7 will fail (that's expected — the function is missing).

!!! tip "If the agent gets stuck"
    Try being more specific: "Run python outdoorgear_api.py and show me the error output, then fix the remaining bug"

---

### Phase 2: Add the missing feature

Now ask the agent to implement the missing `search_by_price_range` function:

```
Implement the search_by_price_range(min_price, max_price) function 
that is referenced in Test 7. 
It should return active products in that price range, sorted by price ascending.
Then run python outdoorgear_api.py to verify all 7 tests pass.
```

The agent should:
1. Read the existing code to understand the data structures
2. Implement the function
3. Run the tests to verify

---

### Phase 3: Write a test suite

Now ask the agent to create proper tests:

```
Create a tests/ folder with a file test_outdoorgear_api.py.
Write pytest tests that cover:
- get_all_products() with include_inactive=True and False
- get_product_by_id() for valid and invalid IDs
- add_to_cart() including the stock check
- calculate_cart_total() with multiple items
- apply_promo_code() with valid and invalid codes
- place_order() end-to-end

Run pytest to make sure all tests pass.
```

Watch the agent:
- Creates the `tests/` folder
- Writes comprehensive tests using pytest fixtures
- Runs `pytest` in the terminal
- Fixes any test failures it finds

---

### Phase 4: Improve code quality

```
Add type hints to all public functions in outdoorgear_api.py.
Add Google-style docstrings to each function.
Don't change any logic.
```

---

### Step 3: Codebase exploration

Try asking the agent to analyze what it just created:

```
Give me a summary of the outdoorgear_api.py module:
1. What it does
2. All public functions and their signatures
3. Any edge cases not currently handled
```

The agent reads the whole codebase and synthesizes a coherent answer — without you pasting any code.

---

### Step 4: Connect an MCP server (bonus)

Agent mode supports MCP servers. Configure VS Code to use the MCP server from [Lab 020](lab-020-mcp-server-python.md):

**`.vscode/mcp.json`:**
```json
{
  "servers": {
    "outdoorgear-products": {
      "type": "stdio",
      "command": "python",
      "args": ["server.py"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

Then ask in agent mode:
```
What camping products do we have in stock? Use the outdoorgear-products MCP tool.
```

### Step 5: Custom instructions

Create `.github/copilot-instructions.md` to make the agent always follow your project conventions:

```markdown
# Copilot Instructions

## Project
Python API project for OutdoorGear Inc.

## Code Style
- Use type hints on all functions
- Docstrings follow Google style  
- Tests use pytest with fixtures, no unittest
- All prices rounded to 2 decimal places

## Never
- Use print() for logging
- Hardcode product data outside CATALOG
- Skip ValueError validation on public functions
```

---

## Agent Mode vs. Edit Mode: When to Use Which

| Use Edit mode when | Use Agent mode when |
|-------------------|---------------------|
| You know exactly what to change | You have a goal but not a plan |
| Simple, targeted edits | Multi-file, multi-step tasks |
| You want full control of each edit | You want the agent to figure it out |
| Quick fixes, refactors | Debugging, adding features, writing tests |

---

## What the Agent Did (Behind the Scenes)

```
Your request: "Fix all bugs"
        │
        ▼
[read_file] outdoorgear_api.py        ← agent reads without you pasting
        │
        ▼
[analysis] Found 5 bugs:
  Bug 1: line 45 — = instead of ==
  Bug 2: line 57 — =+ instead of +=
  ...
        │
        ▼
[replace_in_file] × 5 targeted fixes  ← surgical edits, not rewriting whole file
        │
        ▼
[run_terminal] python outdoorgear_api.py
        │
        ▼
✅ All 6 tests pass
```

---

## Summary

- ✅ **Reads your codebase** — no copying/pasting code into chat
- ✅ **Multi-step execution** — plans and completes complex tasks
- ✅ **Terminal access** — runs tests, verifies fixes
- ✅ **MCP integration** — connect custom tools
- ✅ **Approvals at every step** — you stay in control

---

## Next Steps

- **Build an MCP server to extend agent mode:** → [Lab 020 — MCP Server in Python](lab-020-mcp-server-python.md)
- **Build a VS Code Chat Participant (custom @agent):** → [Lab 025 — VS Code Chat Participant](lab-025-vscode-chat-participant.md)
