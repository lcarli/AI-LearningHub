---
tags: [computer-use, automation, anthropic, desktop, python, safety, persona-developer]
---
# Lab 057: Computer-Using Agents — Desktop Automation

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Path:</strong> <a href="../paths/pro-code/">⚙️ Pro Code</a></span>
  <span><strong>Time:</strong> ~90 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Uses benchmark dataset; Anthropic API optional</span>
</div>

## What You'll Learn

- What **computer-using agents** are — AI that interacts with a desktop the way a human does (screenshot → reason → click/type)
- The **screenshot–action loop**: the agent captures a screenshot, identifies UI elements, and executes mouse/keyboard actions
- How to run agents in a **Docker sandbox** to isolate them from the host system
- Design **safety guardrails** — domain allowlists, action confirmation prompts, and rate limits
- Analyze **desktop automation benchmarks** to understand where computer-use agents succeed and fail

## Introduction

Traditional automation relies on APIs, scripts, or RPA bots that interact with structured interfaces. But what happens when the application has **no API**? Legacy desktop apps, mainframe terminals, and thick-client software often expose nothing but a graphical user interface.

**Computer-using agents** solve this by operating the computer like a human would. The agent captures a **screenshot** of the current screen, sends it to a vision-language model (like Anthropic's `computer_20251124` tool), receives a structured action (move mouse, click, type text), executes it, and repeats. This screenshot→action loop lets the agent interact with *any* application that has a visual interface.

### The Scenario

You are an **Automation Engineer** at OutdoorGear Inc. The company relies on a legacy inventory management system — a thick-client Windows application with no API and no plans for modernization. Management wants to automate repetitive tasks like filling expense forms, generating reports, and navigating the ERP system.

Your job is to evaluate whether computer-use agents can handle these tasks reliably and safely, using a benchmark dataset of **10 desktop and browser tasks**.

!!! info "No Live Agent Required"
    This lab analyzes a **pre-recorded benchmark dataset** of computer-use task results. You don't need an Anthropic API key or a running agent — all analysis is done locally with pandas. If you have API access, you can optionally extend the lab to run live tasks.

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Run analysis scripts |
| `pandas` library | DataFrame operations |
| (Optional) Anthropic API key | For live computer-use experiments |

```bash
pip install pandas
```

---

!!! tip "Quick Start with GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    All dependencies are pre-installed in the devcontainer.


## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-057/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_safety.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-057/broken_safety.py) |
| `desktop_tasks.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-057/desktop_tasks.csv) |

---

## Step 1: Understanding Computer Use

Computer-use agents follow a simple but powerful loop:

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Screenshot  │────▶│  Vision LLM  │────▶│   Action     │
│  (pixels)    │     │  (reason)    │     │  (click/type)│
└─────────────┘     └──────────────┘     └──────────────┘
       ▲                                        │
       └────────────────────────────────────────┘
                    repeat until done
```

The key components:

| Component | Description |
|-----------|-------------|
| **Screenshot capture** | Captures the current screen as an image (PNG) |
| **Vision model** | Analyzes the screenshot to identify UI elements and decide the next action |
| **Action executor** | Translates model output into OS-level mouse/keyboard events |
| **Sandbox** | Docker container or VM that isolates the agent from the host |

Anthropic's `computer_20251124` tool provides three capabilities:

1. **Screenshot capture** — takes a picture of the current screen
2. **Mouse control** — move, click, double-click, drag
3. **Keyboard input** — type text, press key combinations

!!! tip "Why Screenshots?"
    Unlike traditional web scraping (which reads HTML/DOM), computer-use agents see the screen as *pixels*. This means they can interact with any visual interface — desktop apps, remote desktops, terminal emulators, even games — without needing access to the underlying code or DOM.

---

## Step 2: Load the Benchmark Dataset

The dataset contains **10 tasks** that a computer-use agent attempted, covering both desktop and browser scenarios:

```python
import pandas as pd

tasks = pd.read_csv("lab-057/desktop_tasks.csv")
print(f"Total tasks: {len(tasks)}")
print(f"Task types: {sorted(tasks['app_type'].unique())}")
print(f"Difficulty levels: {sorted(tasks['difficulty'].unique())}")
print(f"\nDataset preview:")
print(tasks[["task_id", "task_description", "app_type", "completed", "safety_risk"]].to_string(index=False))
```

**Expected output:**

```
Total tasks: 10
Task types: ['browser', 'desktop']
Difficulty levels: ['easy', 'hard', 'medium']
```

| task_id | task_description | app_type | completed | safety_risk |
|---------|-----------------|----------|-----------|-------------|
| T01 | Open calculator and compute 15 × 23 | desktop | True | low |
| T02 | Create a new text file on the desktop | desktop | True | low |
| T03 | Open browser and search for hiking boots | browser | True | low |
| ... | ... | ... | ... | ... |
| T10 | Navigate a multi-step checkout process | browser | False | high |

---

## Step 3: Analyze Completion Rates

Calculate overall and per-difficulty completion rates:

```python
completed = tasks["completed"].sum()
total = len(tasks)
rate = (completed / total) * 100
print(f"Completed: {completed}/{total}")
print(f"Completion rate: {rate:.0f}%")

print(f"\nBy difficulty:")
for diff in ["easy", "medium", "hard"]:
    subset = tasks[tasks["difficulty"] == diff]
    diff_rate = (subset["completed"].sum() / len(subset)) * 100
    print(f"  {diff}: {subset['completed'].sum()}/{len(subset)} = {diff_rate:.0f}%")
```

**Expected output:**

```
Completed: 7/10
Completion rate: 70%

By difficulty:
  easy: 2/2 = 100%
  medium: 4/4 = 100%
  hard: 1/4 = 25%
```

!!! tip "Insight"
    The agent handles **easy and medium** tasks reliably (100%) but struggles with **hard tasks** (25%). Hard tasks involve multi-step workflows, dynamic content, or security-sensitive operations — all challenging for screenshot-based navigation.

---

## Step 4: Safety Risk Analysis

Identify tasks with high safety risk:

```python
print("Safety risk distribution:")
print(tasks["safety_risk"].value_counts().sort_index())

high_risk = tasks[tasks["safety_risk"] == "high"]
print(f"\nHigh-risk tasks: {len(high_risk)}")
print(high_risk[["task_id", "task_description", "completed"]].to_string(index=False))
```

**Expected output:**

```
Safety risk distribution:
high      2
low       6
medium    2

High-risk tasks: 2
```

| task_id | task_description | completed |
|---------|-----------------|-----------|
| T08 | Log into a web application using credentials | False |
| T10 | Navigate a multi-step checkout process | False |

Both high-risk tasks **failed**, which is actually a good outcome — it means the agent didn't successfully perform potentially dangerous actions without proper guardrails.

!!! warning "Why These Are High-Risk"
    - **T08 (Login with credentials)**: The agent would need to read passwords from a password manager — a significant security risk if the agent is compromised or the sandbox is breached.
    - **T10 (Checkout process)**: Completing a purchase with real payment information could have financial consequences if the agent makes mistakes.

---

## Step 5: Desktop vs Browser Task Comparison

Compare how the agent performs on desktop vs browser tasks:

```python
print("Performance by app type:")
for app in ["desktop", "browser"]:
    subset = tasks[tasks["app_type"] == app]
    rate = (subset["completed"].sum() / len(subset)) * 100
    avg_time = subset[subset["completed"] == True]["time_sec"].mean()
    avg_actions = subset[subset["completed"] == True]["actions"].mean()
    print(f"\n  {app.upper()}:")
    print(f"    Tasks: {len(subset)}")
    print(f"    Completed: {subset['completed'].sum()}/{len(subset)} ({rate:.0f}%)")
    print(f"    Avg time (completed): {avg_time:.1f}s")
    print(f"    Avg actions (completed): {avg_actions:.1f}")
```

**Expected output:**

```
Performance by app type:

  DESKTOP:
    Tasks: 5
    Completed: 4/5 (80%)
    Avg time (completed): 20.5s
    Avg actions (completed): 8.0

  BROWSER:
    Tasks: 5
    Completed: 3/5 (60%)
    Avg time (completed): 26.0s
    Avg actions (completed): 10.7
```

!!! tip "Insight"
    Desktop tasks have a higher success rate (80% vs 60%) and require fewer actions on average. Browser tasks tend to involve more dynamic content and complex navigation, making them harder for screenshot-based agents.

---

## Step 6: Safety Guardrail Design

Based on the benchmark analysis, design guardrails for production deployment:

### Recommended Guardrails

| Guardrail | Purpose | Implementation |
|-----------|---------|----------------|
| **Domain allowlist** | Restrict which applications/sites the agent can access | Config file listing approved app names and URLs |
| **Action confirmation** | Require human approval for high-risk actions | Prompt before clicks on buttons like "Submit", "Purchase", "Delete" |
| **Session time limit** | Prevent runaway agents | Kill the agent after N minutes of inactivity |
| **Screenshot logging** | Audit trail of every action | Save every screenshot with timestamp and action taken |
| **Credential isolation** | Never expose passwords to the agent | Use environment variables or vault references, never screen-visible passwords |

### Guardrail Decision Matrix

```python
print("Guardrail recommendations by risk level:")
for _, task in tasks.iterrows():
    guardrails = []
    if task["safety_risk"] == "high":
        guardrails = ["domain_allowlist", "action_confirmation", "human_review"]
    elif task["safety_risk"] == "medium":
        guardrails = ["domain_allowlist", "screenshot_logging"]
    else:
        guardrails = ["screenshot_logging"]
    print(f"  {task['task_id']} ({task['safety_risk']}): {', '.join(guardrails)}")
```

!!! warning "Docker Sandbox is Essential"
    **Never run a computer-use agent on your host machine.** Always use a Docker container or VM. If the agent misinterprets a screenshot and clicks "Delete All" instead of "Select All", the damage is contained to the sandbox. Anthropic's reference implementation uses a Docker container with a virtual display (Xvfb) specifically for this reason.

---

## 🐛 Bug-Fix Exercise

The file `lab-057/broken_safety.py` has **3 bugs** in the safety analysis functions. Can you find and fix them all?

Run the self-tests to see which ones fail:

```bash
python lab-057/broken_safety.py
```

You should see **3 failed tests**. Each test corresponds to one bug:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Completion rate calculation | Denominator should be total tasks, not completed tasks |
| Test 2 | High-risk task counting | Should check for `"high"`, not `"medium"` |
| Test 3 | Average time for completed tasks | Must filter to completed tasks before computing mean |

Fix all 3 bugs, then re-run. When you see `🎉 All 3 tests passed`, you're done!

---


## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What capabilities does Anthropic's `computer_20251124` tool provide?"

    - A) Only keyboard input for typing commands
    - B) Screenshot capture, mouse control, and keyboard input
    - C) Direct DOM access and HTML parsing
    - D) API integration with desktop applications

    ??? success "✅ Reveal Answer"
        **Correct: B) Screenshot capture, mouse control, and keyboard input**

        The `computer_20251124` tool provides three core capabilities: (1) capturing screenshots of the current screen, (2) controlling the mouse (move, click, drag), and (3) sending keyboard input (typing text, pressing key combinations). It does *not* access the DOM or application APIs — it operates purely through the visual interface.

??? question "**Q2 (Multiple Choice):** What is the primary purpose of running a computer-use agent inside a Docker sandbox?"

    - A) To improve the agent's screenshot resolution
    - B) To reduce API costs by batching requests
    - C) To isolate the agent from the host system and contain potential damage
    - D) To enable the agent to run multiple tasks in parallel

    ??? success "✅ Reveal Answer"
        **Correct: C) To isolate the agent from the host system and contain potential damage**

        A Docker sandbox (or VM) creates a boundary between the agent and your real system. If the agent misinterprets a screenshot and performs an unintended action — like deleting files or clicking the wrong button — the damage is contained within the sandbox and doesn't affect your host machine, files, or accounts.

??? question "**Q3 (Run the Lab):** What is the overall task completion rate?"

    Load [📥 `desktop_tasks.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-057/desktop_tasks.csv) and calculate `completed.sum() / total`.

    ??? success "✅ Reveal Answer"
        **70%**

        7 out of 10 tasks were completed successfully. The 3 failed tasks (T07, T08, T10) were all **hard** difficulty — the agent struggled with complex multi-step workflows and security-sensitive operations.

??? question "**Q4 (Run the Lab):** How many high-risk tasks are in the dataset?"

    Filter tasks where `safety_risk == "high"` and count them.

    ??? success "✅ Reveal Answer"
        **2**

        Tasks T08 (Log into a web application using credentials from a password manager) and T10 (Navigate a multi-step checkout process on an e-commerce site) are classified as high-risk. Both involve sensitive operations — credential handling and financial transactions — where agent errors could have serious consequences.

??? question "**Q5 (Run the Lab):** What is the average number of actions for completed tasks only?"

    Filter to `completed == True`, then compute `actions.mean()`.

    ??? success "✅ Reveal Answer"
        **≈ 9.1**

        Completed tasks: T01(5) + T02(7) + T03(6) + T04(12) + T05(9) + T06(14) + T09(11) = **64 actions** across **7 tasks**. Average = 64 ÷ 7 ≈ **9.14 actions per completed task**.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| Computer Use Concept | Screenshot→action loop: capture screen, reason with vision LLM, execute mouse/keyboard |
| Benchmark Analysis | 70% completion rate; easy/medium tasks reliable, hard tasks challenging |
| Safety Risks | High-risk tasks (credentials, payments) require extra guardrails |
| Desktop vs Browser | Desktop tasks had higher success (80%) than browser tasks (60%) |
| Guardrail Design | Domain allowlists, action confirmation, Docker sandboxing, credential isolation |
| Docker Sandbox | Essential isolation layer — never run computer-use agents on your host |

---

## Next Steps

- **[Lab 058](lab-058-browser-automation-cua.md)** — Browser Automation Agents with OpenAI CUA
- Explore Anthropic's [computer-use reference implementation](https://docs.anthropic.com/en/docs/agents-and-tools/computer-use) for live agent setup
