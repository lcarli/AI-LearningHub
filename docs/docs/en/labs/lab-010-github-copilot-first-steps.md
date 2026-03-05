---
tags: [github-copilot, free, foundations]
---
# Lab 010: GitHub Copilot — First Steps

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Path:</strong> <a href="../paths/copilot/">🤖 GitHub Copilot</a></span>
  <span><strong>Time:</strong> ~45 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-github">GitHub Free</span> — Free tier (2,000 completions + 50 chat/month)</span>
</div>

## What You'll Learn

- Use **inline code completion** to write code from comments
- Use **Copilot Chat `/fix`** to find and understand real bugs
- Use **Copilot Edits** to refactor an entire file with natural language
- Use **inline chat** to extend code without leaving the editor
- Write prompts that get better results

This lab uses **hands-on exercises** — you'll open files with real bugs and incomplete code, then use Copilot to fix and extend them.

---

## Prerequisites

### 1. Enable GitHub Copilot Free

1. Go to [github.com/features/copilot](https://github.com/features/copilot) → **"Start for free"**
2. Sign in and follow the setup wizard

!!! tip "Students get Copilot Pro for free"
    → [GitHub Student Developer Pack](https://education.github.com/pack)

### 2. Install VS Code + Copilot extension

1. Install [VS Code](https://code.visualstudio.com)
2. Extensions (`Ctrl+Shift+X`) → search **"GitHub Copilot"** → Install both:
   - **GitHub Copilot** (completions)
   - **GitHub Copilot Chat** (chat panel)
3. Sign in when prompted — you'll see the Copilot icon in the status bar

### 3. Download the exercise files

Clone or download the exercise files for this lab:

```bash
git clone https://github.com/lcarli/AI-LearningHub.git
cd AI-LearningHub/docs/docs/en/labs/lab-010
```

Or copy each file directly from the sections below.

---

## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-010/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `exercise1_fibonacci.py` | Interactive exercise script | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-010/exercise1_fibonacci.py) |
| `exercise2_shopping_cart.py` | Interactive exercise script | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-010/exercise2_shopping_cart.py) |
| `exercise3_product_search.py` | Interactive exercise script | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-010/exercise3_product_search.py) |
| `exercise4_refactor_me.py` | Interactive exercise script | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-010/exercise4_refactor_me.py) |

---

## Exercise 1 — Inline Completion: Write Code from Comments

**Goal:** Learn how Copilot completes code as you type.

Create a new file `practice.py` and type each comment below. After each comment, **stop typing** and wait for Copilot's suggestion. Press `Tab` to accept.

```python
# Function that takes a list of prices and returns the average:

# Function that reads a CSV file and returns rows as a list of dicts:

# Async function that fetches JSON from a URL using httpx:

# Class OutdoorProduct with name, price, category attributes and a discount() method:
```

!!! tip "Keyboard shortcuts"
    | Key | Action |
    |-----|--------|
    | `Tab` | Accept suggestion |
    | `Esc` | Dismiss |
    | `Alt+]` / `Alt+[` | Next / previous suggestion |
    | `Ctrl+Enter` | Open all suggestions panel |

**Try better and worse prompts:**

| ❌ Vague | ✅ Specific |
|---------|-----------|
| `# sort this` | `# Sort list of dicts by 'price' descending, then 'name' ascending` |
| `# connect to db` | `# Connect to PostgreSQL using asyncpg, return a connection pool` |
| `# handle error` | `# Retry 3 times with exponential backoff if requests.Timeout is raised` |

---

## Exercise 2 — Copilot `/fix`: Bug Hunt 🐛

**Goal:** Use Copilot Chat to find, understand, and fix real bugs.

### File: [📥 `exercise1_fibonacci.py`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-010/exercise1_fibonacci.py)

```python title="exercise1_fibonacci.py — 3 bugs hidden inside"
--8<-- "labs/lab-010/exercise1_fibonacci.py"
```

**Steps:**

1. Copy the code above into a new file (or open it from the cloned repo)
2. Open **Copilot Chat** (`Ctrl+Shift+I`)
3. Select **all the code** (`Ctrl+A`)
4. Type: `/fix`

Copilot should identify all 3 bugs and explain each one. Before accepting, **read the explanation** — understanding *why* the code was wrong is the point.

**Expected output after fixing:**
```python
fibonacci(0)  # → []
fibonacci(1)  # → [0]
fibonacci(8)  # → [0, 1, 1, 2, 3, 5, 8, 13]
```

Run `python exercise1_fibonacci.py` — you should see: `✅ All tests passed!`

---

### File: [📥 `exercise2_shopping_cart.py`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-010/exercise2_shopping_cart.py)

```python title="exercise2_shopping_cart.py — 4 bugs hidden inside"
--8<-- "labs/lab-010/exercise2_shopping_cart.py"
```

This file has **4 bugs** in the `ShoppingCart` class. This time, before using `/fix`:

1. **Try to spot the bugs yourself first** — spend 2 minutes reading the code
2. Then use Copilot Chat: select all → `/fix`
3. Did Copilot find bugs you missed?

**Ask Copilot to explain one bug in depth:**
```
Why is iterating with "for item in self.items" wrong here? What does it actually iterate over?
```

**Expected output after fixing:**
```
TrailBlazer X200 x2 @ $189.99 = $379.98
Summit Pro Tent x1 @ $349.00 = $349.00

Total: $656.08
Unique items: 2
✅ All tests passed!
```

---

## Exercise 3 — Inline Chat: Fix + Extend

**Goal:** Fix bugs AND add a new feature using inline chat (`Ctrl+I`).

### File: [📥 `exercise3_product_search.py`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-010/exercise3_product_search.py)

```python title="exercise3_product_search.py — 2 bugs + 1 missing feature"
--8<-- "labs/lab-010/exercise3_product_search.py"
```

**Part A — Fix (2 bugs):**

1. Open the file in VS Code
2. Select all (`Ctrl+A`) → Copilot Chat → `/fix`
3. Verify: `python exercise3_product_search.py` — tests 1–4 should pass

**Part B — Extend (1 missing feature):**

The file mentions a `sort_by_price()` function that doesn't exist yet.

1. Place your cursor at the end of the file (before the tests section)
2. Press `Ctrl+I` (inline chat)
3. Type exactly:
   ```
   Add a sort_by_price(products, ascending=True) function that returns
   the products list sorted by price
   ```
4. Review the suggestion and press **Accept** (`Ctrl+Enter`)
5. Run the tests again — all 5 should pass now

---

## Exercise 4 — Copilot Edits: Refactor an Entire File

**Goal:** Use Copilot Edits to improve code quality with natural language instructions — without changing behavior.

### File: [📥 `exercise4_refactor_me.py`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-010/exercise4_refactor_me.py)

```python title="exercise4_refactor_me.py — works, but needs improvement"
--8<-- "labs/lab-010/exercise4_refactor_me.py"
```

This code **works correctly** but is hard to read and maintain. Use **Copilot Edits** to improve it step by step:

1. Open the Copilot Edits panel: `Ctrl+Shift+I` → click **"Open Copilot Edits"** (pencil icon)
2. Click **"Add Files"** and add `exercise4_refactor_me.py`
3. Run each of these prompts **one at a time**, reviewing changes before moving on:

**Prompt 1:**
```
Add type hints to all function parameters and return values
```

**Prompt 2:**
```
Add docstrings following Google style to every function
```

**Prompt 3:**
```
Refactor calculate_shipping to use early return instead of nested if/else
```

**Prompt 4:**
```
Add input validation: raise ValueError if price or quantity is negative
```

After each prompt, check that the test at the bottom still passes:
```bash
python exercise4_refactor_me.py
# Should still print: ✅ Refactoring complete — behavior unchanged!
```

!!! warning "Don't accept everything blindly"
    Sometimes Copilot adds extra complexity. If a suggestion makes the code harder to read, press **Discard** (`Ctrl+Backspace`) and rephrase.

---

## Bonus: Ask Copilot to explain, not just fix

Use these prompts on any of the exercise files to deepen your understanding:

```
/explain
```
```
What tests should I write for this function? Generate them.
```
```
What edge cases does this code not handle?
```
```
Is there a more Pythonic way to write this?
```

---

## What You Practiced

| Copilot feature | Exercise | Use case |
|----------------|----------|----------|
| Inline completion | Exercise 1 | Write new code from comments |
| Chat `/fix` | Exercise 2 | Understand and fix bugs |
| Inline chat `Ctrl+I` | Exercise 3 | Fix + extend in-place |
| Copilot Edits | Exercise 4 | Refactor entire files |

---

## Next Steps

- **Build a no-code Teams agent:** → [Lab 011 — Copilot Studio](lab-011-copilot-studio-first-agent.md)
- **Use Agent Mode to build a full feature:** → [Lab 016 — Copilot Agent Mode](lab-016-copilot-agent-mode.md)
- **Use free LLMs in your code:** → [Lab 013 — GitHub Models](lab-013-github-models.md)
