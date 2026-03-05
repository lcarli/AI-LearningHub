---
tags: [swe-bench, benchmarking, evaluation, coding-agents, python]
---
# Lab 073: Agent Benchmarking with SWE-bench

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~90 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Uses mock benchmark results</span>
</div>

## What You'll Learn

- What **SWE-bench** is and why it's the gold standard for evaluating coding agents
- How different agent strategies (direct prompt, chain-of-thought, agentic loop) affect resolve rates
- Analyze benchmark results across models and strategies to find the best agent configuration
- Measure the **cost-performance trade-off** — higher resolve rates cost more per issue
- Build a **benchmark comparison report** for selecting the right agent architecture

## Introduction

**SWE-bench** is a benchmark for evaluating AI coding agents on real-world GitHub issues. Each task is a genuine bug or feature request from popular open-source Python repositories (Django, scikit-learn, sympy, etc.). The agent must:

1. Read the issue description
2. Navigate the codebase
3. Write a patch that fixes the issue
4. Pass the repository's test suite

| Benchmark Variant | Issues | Difficulty | Use Case |
|-------------------|--------|-----------|----------|
| **SWE-bench Full** | 2,294 | Mixed | Comprehensive evaluation |
| **SWE-bench Lite** | 300 | Curated subset | Quick comparison (used in this lab) |
| **SWE-bench Verified** | 500 | Human-verified | Gold-standard evaluation |

### The Scenario

You are an **AI Platform Architect** evaluating coding agents for your engineering team. You've benchmarked **8 agent configurations** across 3 models (GPT-4o, o3, Claude 3.5 Sonnet) and 4 strategies (direct prompt, chain-of-thought, agentic loop, mini SWE-agent). Your dataset (`swe_bench_results.csv`) contains the results. Your job: identify the best agent configuration and understand the cost-performance trade-offs.

!!! info "Mock Data"
    This lab uses mock benchmark results that mirror published SWE-bench leaderboard trends. Real benchmarking requires significant compute — this mock dataset lets you learn the analysis methodology without the cost.

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Run the analysis scripts |
| `pandas` library | Data manipulation |

```bash
pip install pandas
```

---

## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-073/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_benchmark.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-073/broken_benchmark.py) |
| `swe_bench_results.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-073/swe_bench_results.csv) |

---

## Step 1: Understand Agent Strategies

Before analyzing results, understand the four strategies being benchmarked:

| Strategy | How It Works | Expected Performance | Expected Cost |
|----------|-------------|---------------------|---------------|
| **Direct Prompt** | Single prompt with issue + codebase context → patch | Lowest | Lowest |
| **Chain of Thought** | Prompt with explicit reasoning steps → patch | Medium | Medium |
| **Agentic Loop** | Multi-turn loop: read code → reason → edit → test → iterate | Highest | Highest |
| **Mini SWE-agent** | Lightweight agent with file navigation and edit tools | Medium-High | Medium |

### Key Metrics

| Metric | Definition |
|--------|-----------|
| **Resolve Rate** | % of issues where the agent's patch passes all tests |
| **Avg Time** | Average seconds per issue attempt |
| **Avg Cost** | Average USD per issue attempt |

---

## Step 2: Load and Explore the Results

The dataset has **8 agent configurations** tested on SWE-bench Lite (300 issues) and Verified (500 issues):

```python
import pandas as pd

df = pd.read_csv("lab-073/swe_bench_results.csv")

print(f"Total configurations: {len(df)}")
print(f"Models: {df['model'].unique().tolist()}")
print(f"Strategies: {df['strategy'].unique().tolist()}")
print(f"\nAll results:")
print(df.to_string(index=False))
```

**Expected output:**

```
Total configurations: 8
Models: ['gpt-4o', 'o3', 'claude-3.5-sonnet']
Strategies: ['direct_prompt', 'chain_of_thought', 'agentic_loop', 'mini_swe_agent']
```

---

## Step 3: Find the Best and Worst Agents

Rank agents by resolve rate to find the top performers:

```python
ranked = df.sort_values("resolve_rate_pct", ascending=False)
print("Agent Ranking by Resolve Rate:")
print(ranked[["agent_name", "model", "strategy", "resolve_rate_pct", "avg_cost_usd"]].to_string(index=False))
```

**Expected output:**

| Rank | Agent | Model | Strategy | Resolve Rate | Cost/Issue |
|------|-------|-------|----------|-------------|-----------|
| 1 | Agentic o3 | o3 | agentic_loop | 65.0% | $5.50 |
| 2 | Agentic Claude | claude-3.5-sonnet | agentic_loop | 56.0% | $3.20 |
| 3 | Agentic GPT-4o | gpt-4o | agentic_loop | 50.0% | $2.50 |
| 4 | Baseline o3 | o3 | direct_prompt | 45.0% | $3.00 |
| 5 | CoT GPT-4o | gpt-4o | chain_of_thought | 40.0% | $1.20 |
| 6 | Mini SWE-agent | gpt-4o | mini_swe_agent | 35.0% | $1.80 |
| 7 | Baseline Claude | claude-3.5-sonnet | direct_prompt | 35.0% | $0.95 |
| 8 | Baseline GPT-4o | gpt-4o | direct_prompt | 30.0% | $0.85 |

```python
best = ranked.iloc[0]
worst = ranked.iloc[-1]
print(f"\nBest agent:  {best['agent_name']} ({best['resolve_rate_pct']}%)")
print(f"Worst agent: {worst['agent_name']} ({worst['resolve_rate_pct']}%)")
```

!!! tip "Insight"
    **Agentic o3 leads at 65%** — but at $5.50 per issue. **Baseline GPT-4o is cheapest** at $0.85 but resolves only 30%. The agentic loop strategy consistently outperforms other strategies for the same model.

---

## Step 4: Measure the Agentic Improvement

How much does the agentic loop strategy improve over the baseline (direct prompt) for the same model?

```python
lite = df[df["benchmark"] == "swe-bench-lite"]

for model in lite["model"].unique():
    model_data = lite[lite["model"] == model]
    baseline = model_data[model_data["strategy"] == "direct_prompt"]
    agentic = model_data[model_data["strategy"] == "agentic_loop"]

    if not baseline.empty and not agentic.empty:
        b_rate = baseline["resolve_rate_pct"].values[0]
        a_rate = agentic["resolve_rate_pct"].values[0]
        improvement = a_rate - b_rate
        print(f"{model:>20s}: baseline={b_rate:.0f}%  agentic={a_rate:.0f}%  improvement=+{improvement:.0f}pp")
```

**Expected output:**

```
              gpt-4o: baseline=30%  agentic=50%  improvement=+20pp
                  o3: baseline=45%  agentic=65%  improvement=+20pp
    claude-3.5-sonnet: baseline=35%  agentic=56%  improvement=+21pp
```

!!! tip "Insight"
    The agentic loop adds **+20–21 percentage points** across all models. This consistent improvement suggests that the strategy (iterative code navigation + testing) matters as much as the underlying model.

---

## Step 5: Analyze Cost-Performance Trade-offs

More capable agents cost more. Calculate the cost per resolved issue to find the most efficient option:

```python
df["cost_per_resolved"] = df["avg_cost_usd"] * df["total_issues"] / df["resolved"]
df["cost_per_resolved"] = df["cost_per_resolved"].round(2)

efficiency = df.sort_values("cost_per_resolved")
print("Cost Efficiency Ranking:")
print(efficiency[["agent_name", "resolve_rate_pct", "avg_cost_usd", "cost_per_resolved"]].to_string(index=False))
```

```python
# Cost to resolve 100 issues with each agent
for _, row in df.iterrows():
    issues_needed = 100 / (row["resolve_rate_pct"] / 100)
    total_cost = issues_needed * row["avg_cost_usd"]
    print(f"  {row['agent_name']:>20s}: {total_cost:>8.0f} USD to resolve 100 issues")
```

!!! warning "The Cost Curve"
    Going from 30% to 65% resolve rate (2.2x improvement) costs $5.50 vs. $0.85 per attempt (6.5x more expensive). Diminishing returns kick in hard — evaluate whether the marginal resolve rate improvement justifies the cost for your use case.

---

## Step 6: Build the Benchmark Report

```python
best_agent = df.loc[df["resolve_rate_pct"].idxmax()]
cheapest_agent = df.loc[df["avg_cost_usd"].idxmin()]
best_efficiency = df.loc[df["cost_per_resolved"].idxmin()]

report = f"""# 📊 SWE-bench Agent Benchmark Report

## Summary
| Metric | Value |
|--------|-------|
| Configurations Tested | {len(df)} |
| Models | {', '.join(df['model'].unique())} |
| Strategies | {', '.join(df['strategy'].unique())} |

## Top Results
| Category | Agent | Score |
|----------|-------|-------|
| Highest Resolve Rate | {best_agent['agent_name']} | {best_agent['resolve_rate_pct']:.0f}% |
| Lowest Cost/Attempt | {cheapest_agent['agent_name']} | ${cheapest_agent['avg_cost_usd']:.2f} |
| Best Cost/Resolved | {best_efficiency['agent_name']} | ${best_efficiency['cost_per_resolved']:.2f} |

## Key Finding
The **agentic loop** strategy consistently adds +20pp resolve rate over
baseline for the same model. The best agent ({best_agent['agent_name']})
achieves {best_agent['resolve_rate_pct']:.0f}% at ${best_agent['avg_cost_usd']:.2f}/attempt.

## Recommendation
- **High-value fixes:** Use {best_agent['agent_name']} (highest success rate)
- **High-volume triage:** Use {cheapest_agent['agent_name']} (lowest cost, acceptable rate)
- **Balanced workloads:** Use {best_efficiency['agent_name']} (best cost per resolved issue)
"""

print(report)

with open("lab-073/benchmark_report.md", "w") as f:
    f.write(report)
print("💾 Saved to lab-073/benchmark_report.md")
```

---

## 🐛 Bug-Fix Exercise

The file `lab-073/broken_benchmark.py` contains **3 bugs** that produce incorrect benchmark analysis. Can you find and fix them all?

Run the self-tests to see which ones fail:

```bash
python lab-073/broken_benchmark.py
```

You should see **3 failed tests**. Each test corresponds to one bug:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Best agent selection | Should find the agent with the *highest* resolve rate, not lowest |
| Test 2 | Average cost per resolved issue | Should divide by *resolved* count, not total issues |
| Test 3 | Agentic vs. baseline comparison | Should filter by *model* before comparing strategies |

Fix all 3 bugs, then re-run. When you see `All passed!`, you're done!

---


## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What does SWE-bench measure about a coding agent?"

    - A) How fast it can generate code
    - B) Whether it can resolve real GitHub issues by producing patches that pass tests
    - C) How many lines of code it can write per minute
    - D) Whether it can explain code to a human

    ??? success "✅ Reveal Answer"
        **Correct: B) Whether it can resolve real GitHub issues by producing patches that pass tests**

        SWE-bench evaluates agents on their ability to fix genuine bugs and implement features from real open-source repositories. The agent must produce a patch, and the patch must pass the project's existing test suite to count as "resolved."

??? question "**Q2 (Multiple Choice):** Why does the agentic loop strategy outperform direct prompting?"

    - A) It uses a larger context window
    - B) It iterates: reading code, reasoning, editing, and testing in a loop
    - C) It uses a more expensive model
    - D) It has access to the internet

    ??? success "✅ Reveal Answer"
        **Correct: B) It iterates: reading code, reasoning, editing, and testing in a loop**

        The agentic loop gives the agent multiple turns to explore the codebase, form hypotheses, write patches, run tests, and revise. This mirrors how human developers work — rarely does a one-shot attempt solve a complex bug.

??? question "**Q3 (Run the Lab):** Which agent configuration has the highest resolve rate?"

    Run the Step 3 analysis on [📥 `swe_bench_results.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-073/swe_bench_results.csv) and check the ranking.

    ??? success "✅ Reveal Answer"
        **Agentic o3 — 65%**

        Agent AG05 ("Agentic o3") using the `o3` model with the `agentic_loop` strategy resolves 195 out of 300 issues (65.0%), the highest of all 8 configurations.

??? question "**Q4 (Run the Lab):** Which agent configuration has the lowest resolve rate?"

    Check the bottom of the Step 3 ranking.

    ??? success "✅ Reveal Answer"
        **Baseline GPT-4o — 30%**

        Agent AG01 ("Baseline GPT-4o") using the `gpt-4o` model with the `direct_prompt` strategy resolves only 90 out of 300 issues (30.0%). Direct prompting with no iteration yields the lowest performance.

??? question "**Q5 (Run the Lab):** How many percentage points does the agentic loop improve over the baseline for the same model?"

    Run the Step 4 analysis to compute the agentic improvement per model.

    ??? success "✅ Reveal Answer"
        **+20pp for GPT-4o (30%→50%), +20pp for o3 (45%→65%), +21pp for Claude (35%→56%)**

        The agentic loop consistently adds 20–21 percentage points of resolve rate over the direct-prompt baseline, regardless of the underlying model. This demonstrates that agent architecture matters as much as model capability.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| SWE-bench | Gold-standard benchmark using real GitHub issues and test suites |
| Resolve Rate | Primary metric — % of issues where the agent's patch passes tests |
| Agentic Loop | +20pp improvement over direct prompting for any model |
| Cost Trade-off | 65% resolve rate costs 6.5x more per attempt than 30% |
| Model vs. Strategy | Strategy (agentic loop) contributes as much as model choice |
| Benchmark Analysis | How to rank, compare, and report on agent configurations |

---

## Next Steps

- **[Lab 035](lab-035-agent-evaluation.md)** — Agent Evaluation with Azure AI Eval SDK (custom evaluation beyond SWE-bench)
- **[Lab 038](lab-038-cost-optimization.md)** — AI Cost Optimization (managing the cost of agentic loops)
- **[Lab 040](lab-040-autogen-multi-agent.md)** — AutoGen Multi-Agent (building agentic loops with AutoGen)
- **[Lab 074](lab-074-foundry-agent-service.md)** — Foundry Agent Service (deploying agents to production)
