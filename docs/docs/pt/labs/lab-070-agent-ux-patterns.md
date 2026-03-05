---
tags: [ux, adaptive-cards, teams, proactive, accessibility, python]
---
# Lab 070: Agent UX Patterns — Chat, Adaptive Cards & Proactive Notifications

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~60 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Mock interaction data (no Teams or Azure Bot Service required)</span>
</div>

!!! info "Tradução em andamento"
    Este lab ainda está sendo traduzido. O conteúdo abaixo está em inglês.



## What You'll Learn

- Core **UX patterns** for AI agent interactions in enterprise environments
- Design effective **chat interfaces** with typing indicators and source citations
- Build **Adaptive Cards** for structured data display and user input
- Implement **proactive notification** patterns for agent-initiated messages
- Apply **accessibility** best practices to agent UX
- Measure UX quality using **user satisfaction** metrics

!!! abstract "Prerequisite"
    Familiarity with **chatbot** concepts is recommended. No front-end development experience is required — this lab analyzes UX patterns using mock interaction data.

## Introduction

An AI agent's intelligence is only as effective as its **user experience**. Poor UX — missing typing indicators, no source citations, inaccessible Adaptive Cards — erodes user trust and adoption. Great agent UX follows established patterns:

| UX Pattern | Purpose | Impact |
|-----------|---------|--------|
| **Typing Indicator** | Shows the agent is processing | Reduces perceived latency |
| **Source Citation** | Links answers to source documents | Builds trust and verifiability |
| **Adaptive Cards** | Structured display with actions | Enables rich interactions |
| **Proactive Notifications** | Agent-initiated messages | Keeps users informed |
| **Error Messaging** | Clear, actionable error states | Reduces frustration |
| **Accessibility** | Screen reader support, keyboard nav | Ensures inclusive access |

### The Scenario

You are a **UX Designer** auditing an enterprise agent's interaction patterns. You have data on **12 UX patterns** used across the organization, including satisfaction scores, implementation status, and accessibility compliance. Your job: identify high-impact patterns, find gaps, and recommend improvements.

---

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Run analysis scripts |
| `pandas` | Analyze UX pattern data |

```bash
pip install pandas
```

---

!!! tip "Quick Start with GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    All dependencies are pre-installed in the devcontainer.


## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-070/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_ux.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-070/broken_ux.py) |
| `ux_patterns.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-070/ux_patterns.csv) |

---

## Step 1: Understanding Agent UX Principles

Effective agent UX follows a layered approach:

```
User Input → [Typing Indicator] → Agent Processing → [Response Formatting]
                                                            ↓
                                                   ┌── Plain Text Chat
                                                   ├── Adaptive Card
                                                   ├── Source Citation
                                                   └── Error Message
                                                            ↓
                                              [Accessibility Check] → User
```

Key principles:

1. **Responsiveness** — Always acknowledge user input immediately (typing indicators)
2. **Transparency** — Cite sources and explain confidence levels
3. **Structure** — Use Adaptive Cards for complex data, plain text for simple answers
4. **Proactivity** — Notify users of important events without requiring a prompt
5. **Accessibility** — Ensure all interactions work with screen readers and keyboard navigation

!!! info "Why UX Matters for Agent Adoption"
    Research shows that agents with proper UX patterns (source citations, typing indicators, clear errors) have 2-3x higher user retention than agents with bare text responses. Users trust agents more when they can verify answers and understand the agent's state.

---

## Step 2: Load and Explore UX Patterns

The dataset contains **12 UX patterns** with satisfaction scores and implementation data:

```python
import pandas as pd

patterns = pd.read_csv("lab-070/ux_patterns.csv")
print(f"Total patterns: {len(patterns)}")
print(f"Categories: {sorted(patterns['category'].unique())}")
print(f"\nAll patterns:")
print(patterns[["pattern_id", "pattern_name", "category", "satisfaction_score"]]
      .to_string(index=False))
```

**Expected:**

```
Total patterns: 12
```

---

## Step 3: Satisfaction Analysis

Identify the highest and lowest satisfaction patterns:

```python
print("Patterns ranked by satisfaction score:")
ranked = patterns.sort_values("satisfaction_score", ascending=False)
print(ranked[["pattern_name", "category", "satisfaction_score"]].to_string(index=False))

highest = patterns.loc[patterns["satisfaction_score"].idxmax()]
print(f"\nHighest satisfaction: {highest['pattern_name']} ({highest['satisfaction_score']})")
print(f"Average satisfaction: {patterns['satisfaction_score'].mean():.2f}")
```

**Expected:**

```
Highest satisfaction: Source Citation (4.8)
Average satisfaction: 4.17
```

!!! tip "Source Citations Win"
    Source Citation has the highest satisfaction score (4.8 out of 5.0). Users strongly prefer agents that link answers to verifiable sources — it builds trust and allows users to dive deeper. This pattern should be implemented in every enterprise agent.

---

## Step 4: Category Analysis

Analyze patterns by category:

```python
print("Average satisfaction by category:")
cat_stats = patterns.groupby("category").agg(
    count=("pattern_id", "count"),
    avg_satisfaction=("satisfaction_score", "mean")
).sort_values("avg_satisfaction", ascending=False)
print(cat_stats.to_string())
```

Categories group related patterns (e.g., "trust" patterns like source citations and confidence indicators, "responsiveness" patterns like typing indicators and streaming).

---

## Step 5: Accessibility Compliance Check

Check which patterns meet accessibility standards:

```python
accessible = patterns[patterns["accessible"] == True]
not_accessible = patterns[patterns["accessible"] == False]
print(f"Accessible patterns: {len(accessible)} / {len(patterns)}")
print(f"Non-accessible patterns: {len(not_accessible)}")

if len(not_accessible) > 0:
    print(f"\nPatterns needing accessibility fixes:")
    print(not_accessible[["pattern_name", "category", "satisfaction_score"]].to_string(index=False))
```

!!! warning "Accessibility Gaps"
    Any non-accessible pattern is a compliance risk and excludes users who rely on assistive technologies. Adaptive Cards must include `altText` for images, `label` for inputs, and proper `speak` properties for screen readers.

---

## Step 6: UX Quality Dashboard

Build a comprehensive UX quality report:

```python
total = len(patterns)
avg_sat = patterns["satisfaction_score"].mean()
highest_name = patterns.loc[patterns["satisfaction_score"].idxmax(), "pattern_name"]
highest_score = patterns["satisfaction_score"].max()
accessible_count = (patterns["accessible"] == True).sum()

dashboard = f"""
╔════════════════════════════════════════════════════════╗
║     Agent UX Patterns — Quality Report                 ║
╠════════════════════════════════════════════════════════╣
║ Total Patterns:              {total:>5}                     ║
║ Average Satisfaction:        {avg_sat:>5.2f}                     ║
║ Highest Satisfaction:  {highest_name:>12} ({highest_score})           ║
║ Accessible Patterns:         {accessible_count:>5} / {total}                ║
║ Categories:                  {patterns['category'].nunique():>5}                     ║
╚════════════════════════════════════════════════════════╝
"""
print(dashboard)
```

---

## 🐛 Bug-Fix Exercise

The file `lab-070/broken_ux.py` has **3 bugs** in how it analyzes UX pattern data:

```bash
python lab-070/broken_ux.py
```

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Pattern count | Should count all rows with `len()`, not unique categories |
| Test 2 | Highest satisfaction pattern | Should use `idxmax()`, not `idxmin()` |
| Test 3 | Average satisfaction | Should use `mean()`, not `median()` |

---


## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** Why are typing indicators important for AI agent UX?"

    - A) They make the agent smarter
    - B) They reduce perceived latency and signal that the agent is actively processing the request
    - C) They are required by Microsoft Teams
    - D) They improve the agent's response accuracy

    ??? success "✅ Reveal Answer"
        **Correct: B) They reduce perceived latency and signal that the agent is actively processing the request**

        Typing indicators provide immediate visual feedback that the agent received the user's message and is working on a response. Without them, users may think the agent is broken or unresponsive, especially during longer processing times. This simple pattern significantly improves perceived responsiveness and user trust.

??? question "**Q2 (Multiple Choice):** What is the primary benefit of Adaptive Cards over plain text responses?"

    - A) They are faster to render
    - B) They enable structured data display with interactive elements like buttons, inputs, and formatted layouts
    - C) They work without internet
    - D) They are simpler to implement

    ??? success "✅ Reveal Answer"
        **Correct: B) They enable structured data display with interactive elements like buttons, inputs, and formatted layouts**

        Adaptive Cards transform agent responses from plain text into rich, interactive experiences. They can display tables, images, action buttons, input forms, and formatted text — enabling users to interact with data directly rather than typing follow-up queries. They are particularly effective for approval workflows, data summaries, and multi-step processes.

??? question "**Q3 (Run the Lab):** Which UX pattern has the highest user satisfaction score?"

    Sort patterns by `satisfaction_score` descending and check the top entry.

    ??? success "✅ Reveal Answer"
        **Source Citation with a satisfaction score of 4.8**

        Source Citation is the highest-rated UX pattern (4.8 out of 5.0). Users strongly prefer agents that link answers to verifiable source documents, as it builds trust and allows them to verify information. This pattern should be a default in every enterprise agent.

??? question "**Q4 (Run the Lab):** What is the average satisfaction score across all patterns?"

    Compute `patterns['satisfaction_score'].mean()`.

    ??? success "✅ Reveal Answer"
        **4.17 average satisfaction**

        The average satisfaction score across all 12 UX patterns is 4.17 out of 5.0, indicating generally positive user reception. However, the variance between the highest (4.8) and lowest scores suggests that some patterns need improvement to match the quality of top performers.

??? question "**Q5 (Run the Lab):** How many UX patterns are in the dataset?"

    Check `len(patterns)`.

    ??? success "✅ Reveal Answer"
        **12 patterns**

        The dataset contains 12 UX patterns spanning categories like trust (source citations, confidence indicators), responsiveness (typing indicators, streaming), structure (Adaptive Cards, carousels), proactivity (notifications, suggestions), and accessibility (screen reader support, keyboard navigation).

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| Chat UX | Design responsive chat with typing indicators and streaming |
| Source Citations | Build trust by linking answers to verifiable sources |
| Adaptive Cards | Display structured data with interactive elements |
| Proactive Notifications | Enable agent-initiated messages for timely updates |
| Accessibility | Ensure inclusive UX with screen reader and keyboard support |
| Satisfaction Metrics | Measure and compare UX pattern effectiveness |

---

## Next Steps

- **[Lab 069](lab-069-declarative-agents.md)** — Declarative Agents (configure agent behavior via manifests)
- **[Lab 066](lab-066-copilot-studio-governance.md)** — Copilot Studio Governance (govern agent deployments)
- **[Lab 008](lab-008-responsible-ai.md)** — Responsible AI (foundational UX and safety principles)
