---
tags: [agent-framework, semantic-kernel, autogen, migration, python, dotnet]
---
# Lab 076: Microsoft Agent Framework — From SK to MAF

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~75 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Uses mock migration data</span>
</div>

!!! info "Tradução em andamento"
    Este lab ainda está sendo traduzido. O conteúdo abaixo está em inglês.



## What You'll Learn

- How **Semantic Kernel** and **AutoGen** are unified into the **Microsoft Agent Framework (MAF)**
- What **Agent Skills** (portable `.md` skill packages) are and how they enable reuse
- How **Graph Workflows** (DAG with checkpointing) replace linear pipelines
- Analyze a **migration matrix** comparing 15 features across SK, AutoGen, and MAF
- Identify migration effort levels and MAF-exclusive capabilities

## Introduction

The **Microsoft Agent Framework (MAF)** unifies Semantic Kernel and AutoGen into a single, cohesive platform for building AI agents. Released as a **Release Candidate in February 2026**, MAF brings together the best of both worlds:

- **Semantic Kernel's** plugin system, planners, and enterprise connectors
- **AutoGen's** multi-agent conversations, code execution, and group chat patterns

### Installation

```bash
pip install agent-framework
```

### Key Concepts

| Concept | Description |
|---------|------------|
| **Agent Skills** | Portable `.md` skill packages that define agent capabilities, inputs, outputs, and dependencies — shareable across teams and projects |
| **Graph Workflows** | DAG-based orchestration with checkpointing, retry, and branching — replacing linear pipelines |
| **DevUI** | Built-in development UI for debugging agent conversations, inspecting skill execution, and visualizing workflows |
| **Unified API** | Single API surface that replaces SK's `Kernel` and AutoGen's `AssistantAgent` with a common `Agent` class |

### The Scenario

You are a **Platform Engineer** at a company that has built agents using both Semantic Kernel and AutoGen. Leadership has decided to migrate to MAF. You have a **migration matrix** (`migration_matrix.csv`) that maps 15 features across the three frameworks — tracking availability, migration effort, and MAF-exclusive features.

Your job: analyze the matrix, identify quick wins, flag challenges, and build a migration plan.

!!! info "Mock Data"
    This lab uses a mock migration matrix CSV. The data reflects the actual feature mapping between Semantic Kernel, AutoGen, and MAF as documented in the migration guides.

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
    Save all files to a `lab-076/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_migration.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-076/broken_migration.py) |
| `migration_matrix.csv` | 15-feature comparison: SK vs AutoGen vs MAF | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-076/migration_matrix.csv) |

---

## Step 1: Understand the Migration Matrix

The migration matrix maps 15 features across three frameworks. Each row represents a capability:

| Column | Description |
|--------|-----------|
| **feature** | The capability being compared (e.g., `plugins`, `multi_agent_chat`) |
| **sk_support** | Whether Semantic Kernel supports this feature: `yes`, `partial`, or `no` |
| **autogen_support** | Whether AutoGen supports this feature: `yes`, `partial`, or `no` |
| **maf_support** | Whether MAF supports this feature: `yes`, `partial`, or `no` |
| **migration_effort** | Effort to migrate from SK/AutoGen to MAF: `low`, `medium`, or `high` |
| **category** | Feature category: `core`, `orchestration`, `tooling`, or `integration` |

---

## Step 2: Load and Explore the Matrix

```python
import pandas as pd

df = pd.read_csv("lab-076/migration_matrix.csv")

print(f"Total features: {len(df)}")
print(f"Categories: {df['category'].value_counts().to_dict()}")
print(f"Migration effort: {df['migration_effort'].value_counts().to_dict()}")
print(f"\nFull matrix:")
print(df[["feature", "sk_support", "autogen_support", "maf_support", "migration_effort"]].to_string(index=False))
```

**Expected output:**

```
Total features: 15
Categories: {'core': 5, 'orchestration': 4, 'tooling': 3, 'integration': 3}
Migration effort: {'low': 7, 'medium': 5, 'high': 3}
```

---

## Step 3: Identify Quick Wins (Low Migration Effort)

Features with `low` migration effort are your quick wins — start here:

```python
low_effort = df[df["migration_effort"] == "low"]
print(f"Quick wins (low effort): {len(low_effort)} features\n")
for _, row in low_effort.iterrows():
    print(f"  {row['feature']:>25s}  SK={row['sk_support']:<8s} AutoGen={row['autogen_support']:<8s} MAF={row['maf_support']}")
```

!!! tip "Migration Strategy"
    **Start with low-effort features** to build team confidence and demonstrate MAF's unified API. These typically have direct equivalents in SK or AutoGen, making the migration straightforward.

---

## Step 4: Find MAF-Exclusive Features

Which features exist in MAF but not in Semantic Kernel?

```python
maf_only_vs_sk = df[(df["maf_support"] == "yes") & (df["sk_support"] == "no")]
print(f"Features in MAF but NOT in SK: {len(maf_only_vs_sk)}\n")
for _, row in maf_only_vs_sk.iterrows():
    print(f"  {row['feature']:>25s}  category={row['category']}")
```

```python
# Features exclusive to MAF (not in SK AND not in AutoGen)
maf_exclusive = df[(df["maf_support"] == "yes") & (df["sk_support"] == "no") & (df["autogen_support"] == "no")]
print(f"\nMAF-exclusive features (not in SK or AutoGen): {len(maf_exclusive)}")
for _, row in maf_exclusive.iterrows():
    print(f"  {row['feature']}: {row['category']}")
```

---

## Step 5: Analyze High-Effort Migrations

These features need the most planning:

```python
high_effort = df[df["migration_effort"] == "high"]
print(f"High-effort migrations: {len(high_effort)}\n")
for _, row in high_effort.iterrows():
    print(f"  {row['feature']}")
    print(f"    SK: {row['sk_support']}, AutoGen: {row['autogen_support']}, MAF: {row['maf_support']}")
    print(f"    Category: {row['category']}")
    print()
```

!!! warning "Migration Risk"
    High-effort features often involve **architectural changes** — e.g., replacing custom orchestration with Graph Workflows or converting proprietary plugins to Agent Skills. Plan 2–4 weeks per high-effort feature.

---

## Step 6: Build the Migration Plan

```python
report = f"""# 📋 MAF Migration Plan

## Matrix Summary
| Metric | Value |
|--------|-------|
| Total Features | {len(df)} |
| Low Effort | {len(df[df['migration_effort'] == 'low'])} |
| Medium Effort | {len(df[df['migration_effort'] == 'medium'])} |
| High Effort | {len(df[df['migration_effort'] == 'high'])} |
| MAF-only (vs SK) | {len(maf_only_vs_sk)} |

## Phase 1: Quick Wins (Weeks 1–2)
Migrate {len(low_effort)} low-effort features:
"""
for _, row in low_effort.iterrows():
    report += f"- {row['feature']} ({row['category']})\n"

report += f"""
## Phase 2: Medium Effort (Weeks 3–5)
Migrate {len(df[df['migration_effort'] == 'medium'])} medium-effort features with dedicated sprint time.

## Phase 3: High Effort (Weeks 6–10)
Migrate {len(high_effort)} high-effort features requiring architectural changes.

## New Capabilities Unlocked
MAF-exclusive features not available in SK or AutoGen:
"""
for _, row in maf_exclusive.iterrows():
    report += f"- **{row['feature']}** ({row['category']})\n"

print(report)

with open("lab-076/migration_plan.md", "w") as f:
    f.write(report)
print("💾 Saved to lab-076/migration_plan.md")
```

---

## 🐛 Bug-Fix Exercise

The file `lab-076/broken_migration.py` contains **3 bugs** that produce incorrect migration analysis. Can you find and fix them all?

Run the self-tests to see which ones fail:

```bash
python lab-076/broken_migration.py
```

You should see **3 failed tests**. Each test corresponds to one bug:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Low-effort feature count | Should filter `migration_effort == "low"`, not `"high"` |
| Test 2 | MAF-only vs SK count | Should check `sk_support == "no"`, not `"yes"` |
| Test 3 | Total feature count | Should use `len(df)`, not `len(df.columns)` |

Fix all 3 bugs, then re-run. When you see `All passed!`, you're done!

---


## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What is the Microsoft Agent Framework (MAF)?"

    - A) A new version of AutoGen with a different name
    - B) A unified framework combining Semantic Kernel and AutoGen into a single platform
    - C) A cloud-only service for running agents on Azure
    - D) A replacement for LangChain

    ??? success "✅ Reveal Answer"
        **Correct: B) A unified framework combining Semantic Kernel and AutoGen into a single platform**

        MAF merges the strengths of both frameworks: SK's enterprise plugin system and planners with AutoGen's multi-agent conversations and code execution. It provides a single `Agent` class, portable Agent Skills, and DAG-based Graph Workflows.

??? question "**Q2 (Multiple Choice):** What are Agent Skills in MAF?"

    - A) Python functions decorated with `@skill`
    - B) Portable `.md` skill packages that define capabilities, inputs, outputs, and dependencies
    - C) Pre-trained model weights for specific tasks
    - D) Azure Functions that agents can call

    ??? success "✅ Reveal Answer"
        **Correct: B) Portable `.md` skill packages that define capabilities, inputs, outputs, and dependencies**

        Agent Skills are markdown-based packages that describe what an agent can do, what inputs it needs, what outputs it produces, and what dependencies are required. They're shareable across teams and projects, enabling a marketplace of reusable agent capabilities.

??? question "**Q3 (Run the Lab):** How many features have a 'low' migration effort?"

    Run the Step 3 analysis on [📥 `migration_matrix.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-076/migration_matrix.csv) and count the low-effort features.

    ??? success "✅ Reveal Answer"
        **7 features**

        Of the 15 features in the migration matrix, **7 have `migration_effort = "low"`**. These are the quick wins for Phase 1 of the migration — typically features with direct equivalents between SK/AutoGen and MAF.

??? question "**Q4 (Run the Lab):** How many features are available in MAF but NOT in Semantic Kernel?"

    Run the Step 4 analysis to find features where `maf_support = "yes"` and `sk_support = "no"`.

    ??? success "✅ Reveal Answer"
        **The count of features where MAF has `yes` support but SK has `no` support.**

        These represent capabilities that teams gain by migrating from SK to MAF — such as multi-agent chat patterns, code execution sandboxes, and other features that originated in AutoGen and are now available in the unified framework.

??? question "**Q5 (Run the Lab):** How many total features are tracked in the migration matrix?"

    Load the CSV and check the total row count.

    ??? success "✅ Reveal Answer"
        **15 features**

        The migration matrix tracks **15 features** across 4 categories: core (5), orchestration (4), tooling (3), and integration (3). Each feature is evaluated for support in SK, AutoGen, and MAF, along with migration effort.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| Microsoft Agent Framework | Unified platform merging Semantic Kernel and AutoGen (RC Feb 2026) |
| Agent Skills | Portable `.md` skill packages for reusable agent capabilities |
| Graph Workflows | DAG-based orchestration with checkpointing, replacing linear pipelines |
| Migration Matrix | 15 features compared across SK, AutoGen, and MAF |
| Migration Strategy | Start with low-effort (7 features), plan for high-effort (3 features) |
| DevUI | Built-in development UI for debugging and visualizing agent workflows |

---

## Next Steps

- **[Lab 034](lab-034-multi-agent-sk.md)** — Multi-Agent with Semantic Kernel (understand what you're migrating from)
- **[Lab 036](lab-036-autogen-basics.md)** — AutoGen Basics (understand AutoGen patterns before MAF)
- **[Lab 074](lab-074-foundry-agent-service.md)** — Foundry Agent Service (deploy MAF agents to production)
- **[Lab 073](lab-073-swe-bench.md)** — SWE-Bench (evaluate MAF agents on real-world coding tasks)
