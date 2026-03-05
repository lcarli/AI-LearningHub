---
tags: [deep-research, multi-agent, synthesis, citations, python, persona-developer, persona-architect]
---
# Lab 079: Deep Research Agents — Multi-Step Knowledge Synthesis

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~90 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Uses mock research trace data</span>
</div>

## What You'll Learn

- How **Deep Research Agents** use a multi-agent pipeline for knowledge synthesis
- The **Planner → Researcher → Writer → Reviewer** architecture and role responsibilities
- How **citation tracking** ensures every claim maps back to a source
- Analyze a **14-step research trace** with agent roles, token usage, and quality scores
- Identify bottlenecks, token distribution, and quality patterns across the pipeline

## Introduction

**Deep Research Agents** implement a multi-step pipeline for producing well-sourced, comprehensive research reports. Instead of a single LLM generating an entire report, the work is divided across specialized agents:

### The Pipeline

```
  ┌──────────┐     ┌────────────┐     ┌──────────┐     ┌──────────┐
  │ Planner  │────►│ Researcher │────►│  Writer  │────►│ Reviewer │
  └──────────┘     └────────────┘     └──────────┘     └──────────┘
       │                 │                  │                │
  Decomposes        Gathers info       Synthesizes      Reviews &
  query into        from sources       findings into    provides
  sub-questions     with citations     prose report     feedback
```

| Agent | Role | Key Output |
|-------|------|-----------|
| **Planner** | Decomposes the research question into sub-questions and creates a research plan | Sub-questions, search strategy |
| **Researcher** | Executes searches, reads sources, extracts key findings with citations | Findings with source citations |
| **Writer** | Synthesizes findings into a coherent, well-structured report | Draft report with inline citations |
| **Reviewer** | Reviews the draft for accuracy, completeness, and citation quality | Feedback, quality score, approval/revision |

### Citation Tracking

Every claim in the final report must trace back to a source. The pipeline tracks:

- **sources_cited**: Number of unique sources cited in each step
- **quality_score**: Agent's self-assessed quality of the output (0.0–1.0)

### The Scenario

You are a **Research Team Lead** evaluating a deep research agent system. You have a **14-step research trace** (`research_trace.csv`) from a completed research run. Your job: analyze the trace to understand agent behavior, token usage, quality patterns, and identify optimization opportunities.

!!! info "Mock Data"
    This lab uses a mock research trace CSV. The data represents a realistic deep research run with 14 steps across 4 agent roles, including planning, multi-source research, writing, and iterative review.

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Run the analysis scripts |
| `pandas` library | Data manipulation |

```bash
pip install pandas
```

---

!!! tip "Quick Start with GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    All dependencies are pre-installed in the devcontainer.


## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-079/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_research.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-079/broken_research.py) |
| `research_trace.csv` | 14-step research trace with agent roles, tokens, and quality | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-079/research_trace.csv) |

---

## Step 1: Understand the Trace Format

Each row in the trace represents one step in the research pipeline:

| Column | Description |
|--------|-----------|
| **step_id** | Sequential step number (1–14) |
| **agent_role** | Which agent executed this step: `planner`, `researcher`, `writer`, `reviewer` |
| **action** | What the agent did (e.g., `decompose_query`, `search_sources`, `write_section`) |
| **tokens_used** | Number of tokens consumed in this step |
| **sources_cited** | Number of sources cited in this step's output |
| **quality_score** | Quality assessment of this step's output (0.0–1.0) |
| **duration_sec** | Time taken for this step in seconds |

---

## Step 2: Load and Explore the Trace

```python
import pandas as pd

df = pd.read_csv("lab-079/research_trace.csv")

print(f"Total steps: {len(df)}")
print(f"Agent roles: {df['agent_role'].value_counts().to_dict()}")
print(f"Total tokens: {df['tokens_used'].sum():,}")
print(f"Total sources cited: {df['sources_cited'].sum()}")
print(f"\nFull trace:")
print(df[["step_id", "agent_role", "action", "tokens_used", "sources_cited", "quality_score"]].to_string(index=False))
```

**Expected output:**

```
Total steps: 14
Agent roles: {'researcher': 6, 'writer': 4, 'reviewer': 2, 'planner': 2}
Total tokens: varies
Total sources cited: 10
```

---

## Step 3: Analyze Token Usage by Agent

```python
print("Token usage by agent role:\n")
for role, group in df.groupby("agent_role"):
    total_tokens = group["tokens_used"].sum()
    avg_tokens = group["tokens_used"].mean()
    steps = len(group)
    print(f"  {role:>12s}: {total_tokens:>7,} tokens across {steps} steps (avg {avg_tokens:,.0f}/step)")

print(f"\nTotal tokens: {df['tokens_used'].sum():,}")
```

```python
# Token share by agent
total_tokens = df["tokens_used"].sum()
print("\nToken distribution:")
for role, group in df.groupby("agent_role"):
    share = group["tokens_used"].sum() / total_tokens * 100
    bar = "█" * int(share / 2)
    print(f"  {role:>12s}: {share:>5.1f}% {bar}")
```

!!! tip "Optimization Insight"
    The **Researcher** typically consumes the most tokens because it processes multiple sources per sub-question. To reduce costs, consider caching source extractions and limiting the number of sources per sub-question.

---

## Step 4: Analyze Citation Flow

```python
print("Citation flow through the pipeline:\n")
for _, row in df.iterrows():
    cited = "📚" * row["sources_cited"] if row["sources_cited"] > 0 else "—"
    print(f"  Step {row['step_id']:>2}: [{row['agent_role']:>10s}] {row['action']:<25s} sources={row['sources_cited']}  {cited}")

total_sources = df["sources_cited"].sum()
print(f"\nTotal sources cited across all steps: {total_sources}")

# Sources by agent role
print("\nSources cited by role:")
for role, group in df.groupby("agent_role"):
    print(f"  {role:>12s}: {group['sources_cited'].sum()} sources")
```

---

## Step 5: Quality Analysis

```python
print("Quality scores by agent role:\n")
for role, group in df.groupby("agent_role"):
    avg_q = group["quality_score"].mean()
    min_q = group["quality_score"].min()
    max_q = group["quality_score"].max()
    print(f"  {role:>12s}: avg={avg_q:.2f}  min={min_q:.2f}  max={max_q:.2f}")

# Find the lowest-quality step
worst_step = df.loc[df["quality_score"].idxmin()]
print(f"\nLowest quality step:")
print(f"  Step {worst_step['step_id']}: [{worst_step['agent_role']}] {worst_step['action']}")
print(f"  Quality: {worst_step['quality_score']}")
print(f"  Tokens: {worst_step['tokens_used']}")

# Find the highest-quality step
best_step = df.loc[df["quality_score"].idxmax()]
print(f"\nHighest quality step:")
print(f"  Step {best_step['step_id']}: [{best_step['agent_role']}] {best_step['action']}")
print(f"  Quality: {best_step['quality_score']}")
```

!!! warning "Quality Variance"
    Watch for **quality drops in later Researcher steps** — this often indicates source exhaustion (the agent is finding lower-quality sources for harder sub-questions). Consider adding a quality threshold that triggers re-search with alternative queries.

---

## Step 6: Build the Research Analysis Report

```python
writer_tokens = df[df["agent_role"] == "writer"]["tokens_used"].sum()
researcher_steps = len(df[df["agent_role"] == "researcher"])
total_duration = df["duration_sec"].sum()

report = f"""# 📋 Deep Research Trace Analysis

## Pipeline Summary
| Metric | Value |
|--------|-------|
| Total Steps | {len(df)} |
| Total Tokens | {df['tokens_used'].sum():,} |
| Total Sources Cited | {total_sources} |
| Total Duration | {total_duration:.0f}s ({total_duration/60:.1f} min) |
| Avg Quality | {df['quality_score'].mean():.2f} |

## Agent Breakdown
| Role | Steps | Tokens | Sources | Avg Quality |
|------|-------|--------|---------|-------------|
"""

for role in ["planner", "researcher", "writer", "reviewer"]:
    group = df[df["agent_role"] == role]
    report += f"| {role} | {len(group)} | {group['tokens_used'].sum():,} | {group['sources_cited'].sum()} | {group['quality_score'].mean():.2f} |\n"

report += f"""
## Key Findings
- **Researcher** executed {researcher_steps} steps — the most of any agent role
- **Writer** consumed {writer_tokens:,} tokens for synthesis
- **Total sources cited**: {total_sources} across the pipeline
- **Quality** {'improved' if df.iloc[-1]['quality_score'] > df.iloc[0]['quality_score'] else 'varied'} through the pipeline

## Optimization Recommendations
1. **Cache source extractions** to reduce Researcher token usage
2. **Parallelize sub-question research** — steps are independent
3. **Add quality gates** between pipeline stages
4. **Limit sources per sub-question** to top-3 most relevant
"""

print(report)

with open("lab-079/research_analysis.md", "w") as f:
    f.write(report)
print("💾 Saved to lab-079/research_analysis.md")
```

---

## 🐛 Bug-Fix Exercise

The file `lab-079/broken_research.py` contains **3 bugs** that produce incorrect research analysis. Can you find and fix them all?

Run the self-tests to see which ones fail:

```bash
python lab-079/broken_research.py
```

You should see **3 failed tests**. Each test corresponds to one bug:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Total sources cited | Should sum `sources_cited`, not count rows |
| Test 2 | Writer token count | Should filter `agent_role == "writer"`, not `"researcher"` |
| Test 3 | Researcher step count | Should count rows where `agent_role == "researcher"`, not sum tokens |

Fix all 3 bugs, then re-run. When you see `All passed!`, you're done!

---


## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What is the primary advantage of a multi-agent pipeline over a single-LLM approach for research?"

    - A) It uses fewer tokens overall
    - B) Each agent specializes in one task, enabling better quality and traceability
    - C) It requires only one model deployment
    - D) It eliminates the need for citations

    ??? success "✅ Reveal Answer"
        **Correct: B) Each agent specializes in one task, enabling better quality and traceability**

        By splitting research into planning, searching, writing, and reviewing, each agent can be optimized for its specific task. The Researcher can focus on source quality, the Writer on prose coherence, and the Reviewer on factual accuracy. This specialization typically produces higher-quality output than a single end-to-end generation.

??? question "**Q2 (Multiple Choice):** Why is citation tracking important in deep research agents?"

    - A) It reduces token usage
    - B) It ensures every claim maps back to a source, enabling verification and trust
    - C) It makes the report longer
    - D) It is required by the LLM's terms of service

    ??? success "✅ Reveal Answer"
        **Correct: B) It ensures every claim maps back to a source, enabling verification and trust**

        Citation tracking creates an auditable chain from each claim in the final report back to its source. This enables reviewers to verify factual accuracy, users to explore primary sources, and organizations to maintain research integrity — critical for high-stakes applications like legal, medical, or financial research.

??? question "**Q3 (Run the Lab):** What is the total number of sources cited across all steps?"

    Run the Step 4 analysis on [📥 `research_trace.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-079/research_trace.csv) and sum the `sources_cited` column.

    ??? success "✅ Reveal Answer"
        **10 sources**

        The sum of all `sources_cited` values across the 14 steps equals **10**. Most sources are cited during Researcher steps, with some additional citations added during the Writer's synthesis.

??? question "**Q4 (Run the Lab):** How many total tokens did the Writer agent consume?"

    Run the Step 3 analysis and find the total tokens for the `writer` role.

    ??? success "✅ Reveal Answer"
        **Sum of `tokens_used` where `agent_role == "writer"`**

        The Writer's total token count includes all writing and synthesis steps. Filter the trace for `agent_role == "writer"` and sum the `tokens_used` column to get the exact value.

??? question "**Q5 (Run the Lab):** How many steps did the Researcher agent execute?"

    Count the rows where `agent_role == "researcher"`.

    ??? success "✅ Reveal Answer"
        **6 steps**

        The Researcher executed **6 steps** — the most of any agent role. This makes sense because the Researcher handles multiple sub-questions from the Planner, with each sub-question potentially requiring multiple search and extraction steps.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| Deep Research Agents | Multi-agent pipeline for knowledge synthesis with citation tracking |
| Pipeline Architecture | Planner → Researcher → Writer → Reviewer with specialized roles |
| Citation Tracking | Every claim maps back to a source across the pipeline |
| Token Distribution | Researcher uses most tokens; Writer synthesizes; Reviewer validates |
| Quality Patterns | Quality varies by step — later research steps may show source exhaustion |
| Optimization | Cache sources, parallelize research, add quality gates |

---

## Next Steps

- **[Lab 034](lab-034-multi-agent-sk.md)** — Multi-Agent with Semantic Kernel (build the agents themselves)
- **[Lab 067](lab-067-graphrag.md)** — GraphRAG (enhance research with knowledge graph retrieval)
- **[Lab 033](lab-033-agent-observability.md)** — Agent Observability (monitor deep research pipelines in production)
- **[Lab 076](lab-076-microsoft-agent-framework.md)** — Microsoft Agent Framework (implement pipelines with MAF Graph Workflows)
