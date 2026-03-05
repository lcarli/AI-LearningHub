---
tags: [claude-code, copilot-cli, coding-tools, developer-experience, comparison]
---
# Lab 081: Agentic Coding Tools — Claude Code vs Copilot CLI

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~45 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span></span>
</div>

## What You'll Learn

- What **agentic coding tools** are — AI assistants that operate directly in your terminal with full codebase context
- Compare **Claude Code** and **GitHub Copilot CLI** across 10 real-world developer tasks
- Understand how each tool handles **code understanding**, **generation**, **debugging**, and **git workflows**
- Measure **time savings** versus manual approaches for common development tasks
- Debug a broken comparison analysis script by fixing 3 bugs

## Introduction

A new category of developer tools has emerged: **agentic coding assistants** that run in your terminal, read your entire codebase, and execute multi-step tasks autonomously. Unlike IDE-based copilots that suggest single lines or blocks, these tools can search codebases, write tests, create commits, refactor modules, and debug failing pipelines — all from a single natural-language prompt.

Two leading tools in this space are:

| Tool | Vendor | How It Works |
|------|--------|-------------|
| **Claude Code** | Anthropic | Terminal agent that reads your codebase, executes commands, and edits files directly |
| **GitHub Copilot CLI** | GitHub | Terminal agent integrated with GitHub ecosystem, runs commands and edits files |

Both tools share a common pattern: they accept a natural-language task, analyze your codebase for context, plan an approach, and execute it — often in a single interaction.

### The Scenario

You are a **Tech Lead** at OutdoorGear Inc. evaluating terminal-based coding assistants for your engineering team. You've benchmarked both tools across **10 representative developer tasks** and now need to analyze the results to make a recommendation.

!!! info "No Tool Installation Required"
    This lab analyzes a **pre-recorded benchmark dataset** comparing task completion times and success rates. You don't need Claude Code or Copilot CLI installed — all analysis is done locally with pandas.

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Run analysis scripts |
| `pandas` library | DataFrame operations |

```bash
pip install pandas
```

---

!!! tip "Quick Start with GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    All dependencies are pre-installed in the devcontainer.


## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-081/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_tools.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-081/broken_tools.py) |
| `coding_tools_comparison.csv` | Dataset — 10 tasks compared across tools | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-081/coding_tools_comparison.csv) |

---

## Step 1: Understanding Agentic Coding Tools

Both Claude Code and Copilot CLI follow a similar agent loop:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  User Prompt │────▶│  Codebase    │────▶│  Plan &      │
│  (terminal)  │     │  Analysis    │     │  Execute     │
└──────────────┘     └──────────────┘     └──────────────┘
                                                │
                     ┌──────────────┐            │
                     │  Edit files, │◀───────────┘
                     │  run commands│
                     └──────────────┘
```

Key capabilities shared by both tools:

| Capability | Description |
|-----------|-------------|
| **Codebase understanding** | Read and reason about project structure, dependencies, and patterns |
| **Code generation** | Write new code (functions, tests, modules) aligned with project conventions |
| **Debugging** | Analyze errors, trace issues, and apply fixes |
| **Git workflows** | Stage changes, create commits with conventional messages, manage branches |
| **Refactoring** | Restructure code while preserving behavior |
| **Code review** | Review changes and suggest improvements |

---

## Step 2: Load the Benchmark Dataset

The dataset contains **10 tasks** benchmarked across both tools and manual completion:

```python
import pandas as pd

tasks = pd.read_csv("lab-081/coding_tools_comparison.csv")
print(f"Total tasks: {len(tasks)}")
print(f"Categories: {sorted(tasks['category'].unique())}")
print(f"\nDataset preview:")
print(tasks[["task_id", "task_description", "category"]].to_string(index=False))
```

**Expected output:**

```
Total tasks: 10
Categories: ['code_generation', 'code_review', 'code_understanding', 'codebase_search', 'debugging', 'devops', 'git_workflow', 'migration', 'refactoring', 'scaffolding']
```

| task_id | task_description | category |
|---------|-----------------|----------|
| T01 | Explain a complex function in the codebase | code_understanding |
| T02 | Find all API endpoints in the project | codebase_search |
| ... | ... | ... |
| T10 | Debug a failing CI pipeline | devops |

---

## Step 3: Compare Success Rates

Calculate success rates for each tool:

```python
for col in ["claude_code_success", "copilot_cli_success"]:
    tasks[col] = tasks[col].astype(str).str.lower() == "true"

cc_success = tasks["claude_code_success"].sum()
cp_success = tasks["copilot_cli_success"].sum()
total = len(tasks)

print(f"Claude Code:  {cc_success}/{total} = {cc_success/total*100:.0f}%")
print(f"Copilot CLI:  {cp_success}/{total} = {cp_success/total*100:.0f}%")

failed_cp = tasks[tasks["copilot_cli_success"] == False]
if len(failed_cp) > 0:
    print(f"\nCopilot CLI failures:")
    print(failed_cp[["task_id", "task_description", "category"]].to_string(index=False))
```

**Expected output:**

```
Claude Code:  10/10 = 100%
Copilot CLI:   9/10 =  90%

Copilot CLI failures:
 task_id                  task_description category
     T10 Debug a failing CI pipeline   devops
```

!!! tip "Insight"
    Claude Code completed all 10 tasks successfully (100%). Copilot CLI completed 9 out of 10 (90%), failing only on T10 — debugging a failing CI pipeline, which requires deep context about CI configuration, environment variables, and build systems.

---

## Step 4: Compare Completion Times

Analyze how fast each tool completes tasks:

```python
cc_avg = tasks["claude_code_time_sec"].mean()
cp_avg = tasks["copilot_cli_time_sec"].mean()
manual_avg = tasks["manual_time_sec"].mean()

print(f"Average completion time:")
print(f"  Claude Code:  {cc_avg:.1f}s")
print(f"  Copilot CLI:  {cp_avg:.1f}s")
print(f"  Manual:       {manual_avg:.1f}s")

print(f"\nSpeedup over manual:")
print(f"  Claude Code:  {manual_avg/cc_avg:.0f}x faster")
print(f"  Copilot CLI:  {manual_avg/cp_avg:.0f}x faster")
```

**Expected output:**

```
Average completion time:
  Claude Code:  20.5s
  Copilot CLI:  24.5s
  Manual:       1005.0s

Speedup over manual:
  Claude Code:  49x faster
  Copilot CLI:  41x faster
```

```python
print("\nPer-task comparison:")
for _, t in tasks.iterrows():
    faster = "Claude Code" if t["claude_code_time_sec"] < t["copilot_cli_time_sec"] else "Copilot CLI"
    print(f"  {t['task_id']} ({t['category']:>20}): CC={t['claude_code_time_sec']:>3}s  "
          f"CP={t['copilot_cli_time_sec']:>3}s  → {faster}")
```

!!! tip "Insight"
    Claude Code is faster on average (20.5s vs 24.5s). The only task where Copilot CLI was faster is **T06 (git workflow)** — creating a conventional commit message — likely due to tighter GitHub integration.

---

## Step 5: Analyze by Task Category

Compare tool performance across different task types:

```python
print("Performance by category:")
for _, row in tasks.iterrows():
    cc_status = "✅" if row["claude_code_success"] else "❌"
    cp_status = "✅" if row["copilot_cli_success"] else "❌"
    print(f"  {row['category']:>20}: CC {cc_status} ({row['claude_code_time_sec']:>3}s)  "
          f"CP {cp_status} ({row['copilot_cli_time_sec']:>3}s)  "
          f"Advantage: {row['tool_advantage']}")
```

**Expected output:**

```
  code_understanding: CC ✅ ( 8s)  CP ✅ (12s)  Advantage: 10x faster
     codebase_search: CC ✅ ( 5s)  CP ✅ ( 8s)  Advantage: 40x faster
     code_generation: CC ✅ (25s)  CP ✅ (30s)  Advantage: 20x faster
          debugging: CC ✅ (18s)  CP ✅ (22s)  Advantage: 45x faster
        refactoring: CC ✅ (35s)  CP ✅ (40s)  Advantage: 30x faster
       git_workflow: CC ✅ ( 4s)  CP ✅ ( 3s)  Advantage: 8x faster
        code_review: CC ✅ (15s)  CP ✅ (20s)  Advantage: 35x faster
        scaffolding: CC ✅ (45s)  CP ✅ (50s)  Advantage: 75x faster
          migration: CC ✅ (30s)  CP ✅ (35s)  Advantage: 55x faster
             devops: CC ✅ (20s)  CP ❌ (25s)  Advantage: 45x faster
```

Both tools provide **massive speedups** over manual work (8x to 75x faster), with the biggest gains in scaffolding and codebase search tasks.

---

## Step 6: Making a Recommendation

Summarize the comparison:

```python
print("=== Tool Comparison Summary ===\n")
print(f"{'Metric':<30} {'Claude Code':>12} {'Copilot CLI':>12}")
print("-" * 56)
print(f"{'Success Rate':<30} {'100%':>12} {'90%':>12}")
print(f"{'Avg Time (s)':<30} {cc_avg:>12.1f} {cp_avg:>12.1f}")
print(f"{'Tasks Won (speed)':<30} {'9':>12} {'1':>12}")
print(f"{'Manual Speedup':<30} {f'{manual_avg/cc_avg:.0f}x':>12} {f'{manual_avg/cp_avg:.0f}x':>12}")
```

!!! tip "Recommendation"
    Both tools deliver exceptional productivity gains. **Claude Code** edges ahead in this benchmark with perfect success rate and faster average times. **Copilot CLI** excels at git workflows and offers tighter GitHub integration. For teams already in the GitHub ecosystem, Copilot CLI is a natural choice; for maximum reliability across diverse tasks, Claude Code is the stronger option.

---

## 🐛 Bug-Fix Exercise

The file `lab-081/broken_tools.py` has **3 bugs** in the analysis functions. Can you find and fix them all?

Run the self-tests to see which ones fail:

```bash
python lab-081/broken_tools.py
```

You should see **3 failed tests**. Each test corresponds to one bug:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Average speedup calculation | Should compute speedup from Claude Code times, not Copilot CLI times |
| Test 2 | Both-tools success rate | Should use AND (`&`) not OR (`|`) for "both succeeded" |
| Test 3 | Fastest tool detection | Comparison operator is reversed |

Fix all 3 bugs, then re-run. When you see `All passed!`, you're done!

---

## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What distinguishes agentic coding tools from traditional IDE-based copilots?"

    - A) They only work with Python code
    - B) They operate in the terminal, read entire codebases, and execute multi-step tasks autonomously
    - C) They require a GPU to run locally
    - D) They only suggest single-line completions

    ??? success "✅ Reveal Answer"
        **Correct: B) They operate in the terminal, read entire codebases, and execute multi-step tasks autonomously**

        Unlike IDE-based copilots that suggest code completions within an editor, agentic coding tools like Claude Code and Copilot CLI run in the terminal, analyze your full project structure, and can perform complex multi-step tasks — searching codebases, writing tests, creating commits, and debugging pipelines — all from a single natural-language prompt.

??? question "**Q2 (Multiple Choice):** What is the primary advantage of agentic coding tools over manual development?"

    - A) They produce bug-free code every time
    - B) They eliminate the need for code review
    - C) They dramatically reduce time for common tasks (often 10x–75x faster)
    - D) They replace the need for version control

    ??? success "✅ Reveal Answer"
        **Correct: C) They dramatically reduce time for common tasks (often 10x–75x faster)**

        The benchmark shows speedups ranging from 8x (git workflows) to 75x (scaffolding) compared to manual completion. While the tools don't produce perfect code every time and code review remains important, the time savings for routine tasks are substantial.

??? question "**Q3 (Run the Lab):** What is Claude Code's success rate across all 10 tasks?"

    Load [📥 `coding_tools_comparison.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-081/coding_tools_comparison.csv) and count `claude_code_success == True`.

    ??? success "✅ Reveal Answer"
        **100% (10/10)**

        Claude Code successfully completed all 10 tasks in the benchmark, including code understanding, generation, debugging, refactoring, git workflows, code review, scaffolding, migration, and DevOps tasks.

??? question "**Q4 (Run the Lab):** What is Copilot CLI's success rate, and which task did it fail?"

    Count `copilot_cli_success == True` and identify the failed task.

    ??? success "✅ Reveal Answer"
        **90% (9/10) — failed T10 (Debug a failing CI pipeline)**

        Copilot CLI succeeded on 9 out of 10 tasks. The only failure was T10 — debugging a failing CI pipeline — which requires deep context about CI configuration, environment variables, and build system interactions.

??? question "**Q5 (Run the Lab):** Which tool is fastest overall based on average completion time?"

    Compute `claude_code_time_sec.mean()` and `copilot_cli_time_sec.mean()`.

    ??? success "✅ Reveal Answer"
        **Claude Code (20.5s avg vs 24.5s avg)**

        Claude Code's average completion time is 20.5 seconds compared to Copilot CLI's 24.5 seconds. Claude Code was faster on 9 out of 10 tasks; Copilot CLI was faster only on T06 (git workflow, 3s vs 4s).

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| Agentic Coding Tools | Terminal-based AI assistants that read codebases and execute multi-step tasks |
| Claude Code | 100% success rate, 20.5s average, strongest at complex tasks |
| Copilot CLI | 90% success rate, 24.5s average, excels at git workflows |
| Time Savings | Both tools provide 8x–75x speedup over manual development |
| Task Categories | Both handle code understanding, generation, review, and refactoring well |
| Recommendation | Claude Code for reliability; Copilot CLI for GitHub integration |

---

## Next Steps

- **[Lab 082](lab-082-agent-guardrails.md)** — Agent Guardrails: NeMo & Azure Content Safety
- Try both tools on your own codebase to see which fits your workflow best
