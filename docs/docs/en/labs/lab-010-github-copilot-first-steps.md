# Lab 010: GitHub Copilot — First Steps

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Path:</strong> <a href="../paths/copilot/">🤖 GitHub Copilot</a></span>
  <span><strong>Time:</strong> ~30 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-github">GitHub Free</span> — Free tier (2,000 completions + 50 chat/month)</span>
</div>

## What You'll Learn

- How to install and configure GitHub Copilot in VS Code
- Use **inline code completion** effectively
- Use **Copilot Chat** for Q&A and code generation
- Use **Copilot Edits** for multi-file changes
- Best practices for writing good prompts

---

## Prerequisites Setup

### 1. Enable GitHub Copilot Free

1. Go to [github.com/features/copilot](https://github.com/features/copilot) and click **"Start for free"**
2. Sign in with your GitHub account
3. Follow the setup wizard

!!! tip "Students get Copilot Pro for free"
    → [GitHub Student Developer Pack](https://education.github.com/pack)

### 2. Install VS Code and the Copilot extension

1. Install [VS Code](https://code.visualstudio.com) if you haven't already
2. Open VS Code → Extensions (`Ctrl+Shift+X`) → Search **"GitHub Copilot"** → Install
3. Sign in when prompted

---

## Lab Exercise

### Step 1: Code Completion

Create a new file `lab010.py` and type the following comment — then pause after the colon:

```python
# Function to calculate the fibonacci sequence up to n terms:
```

Copilot should suggest a completion. Press `Tab` to accept it.

**Try these prompts:**
- `# Parse a CSV file and return a list of dictionaries:`
- `# Send an HTTP POST request with JSON body and return the response:`

!!! tip "Keyboard shortcuts"
    - `Tab` — Accept suggestion
    - `Esc` — Dismiss suggestion
    - `Alt+]` — Next suggestion
    - `Alt+[` — Previous suggestion

### Step 2: Copilot Chat

Open Copilot Chat with `Ctrl+Shift+I` (or click the chat icon in the sidebar).

Try these prompts:

1. **Explain code:** Select a function and type `/explain`
2. **Fix a bug:** Write intentionally broken code, select it, type `/fix`
3. **Write tests:** Select a function and type `/tests`
4. **Ask anything:** `"What's the difference between asyncio and threading in Python?"`

### Step 3: Copilot Edits (multi-file changes)

1. Open the Copilot Edits panel (Ctrl+Shift+I → "Open Copilot Edits")
2. Add your `lab010.py` file to the working set
3. Type: `"Add type hints to all functions and add docstrings"`
4. Review and accept the changes

### Step 4: Inline Chat

Place your cursor inside a function and press `Ctrl+I`:
- Type `"add error handling for invalid inputs"`
- Review the suggestion and press `Accept`

---

## Tips for Better Copilot Prompts

| ❌ Vague | ✅ Specific |
|---------|-----------|
| `# sort this` | `# Sort list of dicts by 'price' descending, then by 'name' ascending` |
| `# connect to db` | `# Connect to PostgreSQL using asyncpg, return connection pool` |
| `# handle error` | `# Retry 3 times with exponential backoff if requests.exceptions.Timeout` |

---

## Summary

GitHub Copilot transforms how you write code. You're now using:
- ✅ **Inline completion** — code as you type
- ✅ **Copilot Chat** — Q&A and slash commands
- ✅ **Copilot Edits** — multi-file AI-assisted refactoring

---

## Next Steps

- **Build a no-code agent:** → [Lab 011 — Copilot Studio](lab-011-copilot-studio-first-agent.md)
- **Use free LLMs in your code:** → [Lab 013 — GitHub Models](lab-013-github-models.md)
