---
tags: [enterprise, work-iq, copilot-analytics, python, viva-insights, m365]
---
# Lab 047: Work IQ — Copilot Adoption Analytics

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~45 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Uses included mock dataset (live Viva Insights requires M365 Copilot license)</span>
</div>

!!! info "Traduction en cours"
    Ce lab est en cours de traduction. Le contenu ci-dessous est en anglais.



## What You'll Learn

- What **Work IQ** is and why adoption analytics matters for AI rollouts
- How to read and interpret Copilot usage data from Viva Insights and the M365 Admin Center
- Analyze adoption rates by department using Python and pandas
- Identify **adoption blockers**: licensing gaps, enablement gaps, and low engagement
- Build a **rollout scorecard** that turns raw data into an executive summary

## Introduction

![Work IQ Analytics Flow](../../assets/diagrams/work-iq-analytics-flow.svg)

**Work IQ** is Microsoft's framework for measuring and optimizing AI adoption across an organization. As companies move from *deploying* Microsoft 365 Copilot to *proving ROI*, the ability to analyze adoption data becomes a critical skill.

In 2025-2026, the question has shifted from _"Did we deploy Copilot?"_ to _"Is it actually being used? By whom? For what? And what value is it creating?"_

### The Scenario

You are the **AI Adoption Lead** at OutdoorGear Inc. The company deployed M365 Copilot to 52 employees across 7 departments three months ago. Leadership wants answers:

1. Which departments are actually using Copilot?
2. Where are licenses going unused — and why?
3. What features are people using most?
4. How much time has Copilot saved the organization?

You have a **usage data export** (similar to what Viva Insights and the M365 Admin Center provide). Your job: turn raw data into an actionable **adoption scorecard**.

!!! info "Live vs. Mock Data"
    This lab uses a **mock dataset** (`copilot_usage_data.csv`) so anyone can follow along without an M365 Copilot license. The data structure mirrors what you'd see in Viva Insights exports. If you have a live M365 environment, you can substitute your own data.

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Run the analysis scripts |
| `pandas` library | Data manipulation |
| (Optional) M365 Copilot license + Viva Insights | For live data instead of mock |

```bash
pip install pandas
```

---

!!! tip "Quick Start with GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    All dependencies are pre-installed in the devcontainer.


## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-047/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_scorecard.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-047/broken_scorecard.py) |
| `copilot_usage_data.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-047/copilot_usage_data.csv) |
| `scorecard_builder.py` | Starter script with TODOs | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-047/scorecard_builder.py) |

---

## Step 1: Understand the Key Metrics

Before touching data, you need to understand what Work IQ measures. These are the same metrics tracked by Viva Insights and the M365 Admin Center:

| Metric | What It Measures | Why It Matters |
|--------|-----------------|----------------|
| **Licensed** | User has an M365 Copilot license assigned | License ≠ usage; tracks investment allocation |
| **Enabled** | Admin has activated Copilot for the user | Gap between licensed and enabled = wasted spend |
| **Active Days** | Days the user interacted with any Copilot feature | Measures engagement depth, not just one-time trial |
| **Meetings Assisted** | Meetings where Copilot generated summaries/actions | High-value use case for managers |
| **Emails Drafted** | Emails composed or refined with Copilot help | Measures writing productivity |
| **Docs Summarized** | Documents summarized or analyzed by Copilot | Measures knowledge work efficiency |
| **Chats** | Copilot Chat interactions (questions, brainstorming) | Measures exploration and daily utility |
| **Time Saved (min)** | Estimated minutes saved by Copilot | The ultimate ROI metric |

### Key Formulas

```
Adoption Rate = (Active Users ÷ Enabled Users) × 100

Enablement Gap = Licensed Users − Enabled Users
    → Users with a paid license that admins haven't turned on

Licensing Gap = Total Users − Licensed Users
    → Users without any Copilot license at all
```

!!! warning "Viva Insights Privacy"
    In production Viva Insights, a **minimum group size of 5 users** is enforced for all reports. You cannot drill into departments smaller than 5. Our mock data ignores this for learning purposes, but keep it in mind for real deployments.

---

## Step 2: Load and Explore the Dataset

The dataset has **52 user records** across 7 departments. Start by loading it in Python:

```python
import pandas as pd

df = pd.read_csv("lab-047/copilot_usage_data.csv")

# Convert string booleans to Python booleans
for col in ["licensed", "enabled"]:
    df[col] = df[col].astype(str).str.strip().str.lower() == "true"

print(f"Total records: {len(df)}")
print(f"Departments: {df['department'].nunique()}")
print(f"\nColumn types:\n{df.dtypes}")
print(f"\nFirst 5 rows:\n{df.head()}")
```

**Expected output:**

```
Total records: 52
Departments: 7
```

Take a moment to explore:

```python
# Quick summary by department
summary = df.groupby("department").agg(
    total=("user_id", "count"),
    licensed=("licensed", "sum"),
    enabled=("enabled", "sum"),
).reset_index()
print(summary)
```

??? question "**🤔 Before you continue:** Which department do you *predict* will have the highest adoption rate?"

    Think about it — then continue to Step 3 to find out if you're right!

---

## Step 3: Calculate Adoption Rates by Department

Now compute the adoption rate for each department. Remember: **adoption rate = active users ÷ enabled users × 100**.

An "active" user is anyone with `active_days > 0` (they used Copilot at least once during the month).

```python
results = []
for dept, group in df.groupby("department"):
    total = len(group)
    licensed = group["licensed"].sum()
    enabled = group["enabled"].sum()
    active = len(group[(group["enabled"] == True) & (group["active_days"] > 0)])
    rate = (active / enabled * 100) if enabled > 0 else 0

    results.append({
        "Department": dept,
        "Total": total,
        "Licensed": licensed,
        "Enabled": enabled,
        "Active": active,
        "Adoption %": round(rate, 1),
    })

adoption_df = pd.DataFrame(results).sort_values("Adoption %", ascending=False)
print(adoption_df.to_string(index=False))
```

**Expected output:**

| Department | Total | Licensed | Enabled | Active | Adoption % |
|------------|-------|----------|---------|--------|------------|
| Finance | 6 | 6 | 6 | 6 | 100.0 |
| Engineering | 12 | 11 | 10 | 9 | 90.0 |
| Marketing | 8 | 8 | 7 | 6 | 85.7 |
| Operations | 7 | 6 | 5 | 4 | 80.0 |
| Sales | 10 | 8 | 5 | 4 | 80.0 |
| HR | 5 | 3 | 3 | 2 | 66.7 |
| Legal | 4 | 3 | 2 | 1 | 50.0 |

!!! tip "Insight"
    **Finance leads at 100%** — every enabled user is active. **Legal is at 50%** — only 1 out of 2 enabled users has ever opened Copilot. But notice that Legal also has the fewest enabled users (2). Small sample sizes can be misleading — this is why Viva Insights enforces a minimum group size of 5.

---

## Step 4: Identify Adoption Blockers

Three types of blockers prevent Copilot adoption:

### 4a — Enablement Gap (Licensed but NOT Enabled)

```python
gap = df[(df["licensed"] == True) & (df["enabled"] == False)]
print(f"Enablement gap: {len(gap)} users\n")
print(gap[["department", "user_id"]].to_string(index=False))
```

**Expected output:**

```
Enablement gap: 7 users

  department user_id
 Engineering ENG-011
   Marketing MKT-008
       Sales SLS-004
       Sales SLS-005
       Sales SLS-006
       Legal LEG-003
  Operations OPS-006
```

!!! warning "The Sales Problem"
    **Sales has 3 licensed users stuck in the enablement gap** — that's 37.5% of their licensed users! This is likely an admin oversight. One ticket to IT could unlock 3 more active users.

### 4b — Licensing Gap (No License at All)

```python
unlicensed = df[df["licensed"] == False]
print(f"Unlicensed users: {len(unlicensed)}")
print(unlicensed.groupby("department")["user_id"].count())
```

### 4c — Zero-Usage Users (Enabled but Never Used)

```python
zero_usage = df[(df["enabled"] == True) & (df["active_days"] == 0)]
print(f"Enabled but never used: {len(zero_usage)} users")
print(zero_usage[["department", "user_id"]].to_string(index=False))
```

These users have Copilot available but haven't touched it. They may need training, awareness campaigns, or a nudge from their manager.

---

## Step 5: Feature Usage Analysis

Which Copilot features drive the most value at OutdoorGear?

```python
active = df[df["active_days"] > 0]

features = {
    "Meetings Assisted": active["meetings_assisted"].sum(),
    "Emails Drafted": active["emails_drafted"].sum(),
    "Docs Summarized": active["docs_summarized"].sum(),
    "Chats": active["chats"].sum(),
}

print("Feature Usage (total interactions among active users):")
for feat, count in sorted(features.items(), key=lambda x: x[1], reverse=True):
    pct = count / sum(features.values()) * 100
    print(f"  {feat:>20s}: {count:>5d}  ({pct:.1f}%)")
```

**Expected output:**

| Feature | Total | Share |
|---------|-------|-------|
| Chats | 400 | 32.8% |
| Meetings Assisted | 303 | 24.8% |
| Emails Drafted | 260 | 21.3% |
| Docs Summarized | 257 | 21.1% |

!!! tip "Insight"
    **Chats dominate** at 32.8% — users are primarily using Copilot for Q&A, brainstorming, and quick lookups. Meetings are the second most used feature, driven by Finance and Engineering where managers rely on meeting summaries.

---

## Step 6: Build the Scorecard

Now combine all your analysis into a single **Adoption Scorecard** for leadership:

```python
total_time = int(active["time_saved_min"].sum())

scorecard = f"""# 📊 OutdoorGear Inc. — Copilot Adoption Scorecard

**Reporting Period:** March 2026 (1-month snapshot)

## Overall Metrics
| Metric | Value |
|--------|-------|
| Total Users | {len(df)} |
| Licensed | {df['licensed'].sum()} |
| Enabled | {df['enabled'].sum()} |
| Active | {len(active)} |
| Overall Adoption Rate | {len(active) / df['enabled'].sum() * 100:.1f}% |
| Time Saved | {total_time} min ({total_time / 60:.1f} hours) |
| Enablement Gap | {len(gap)} users |

## Department Ranking
{adoption_df.to_markdown(index=False)}

## Top Actions
1. **Close the Sales enablement gap** — 3 licensed users not yet enabled
2. **Investigate Legal adoption** — only 1 of 2 enabled users is active
3. **Scale Finance's success** — 100% adoption; learn what they're doing right
4. **Run training for zero-usage users** — {len(zero_usage)} enabled users never opened Copilot
"""

print(scorecard)

with open("lab-047/scorecard_report.md", "w") as f:
    f.write(scorecard)
print("💾 Saved to lab-047/scorecard_report.md")
```

---

## 🐛 Bug-Fix Exercise

The file `lab-047/broken_scorecard.py` contains **3 bugs** that produce incorrect adoption metrics. Can you find and fix them all?

Run the self-tests to see which ones fail:

```bash
python lab-047/broken_scorecard.py
```

You should see **3 failed tests**. Each test corresponds to one bug:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Adoption rate denominator | Should use enabled users, not total users |
| Test 2 | Enablement gap filter logic | Check the boolean conditions |
| Test 3 | Time conversion factor | Minutes → hours conversion |

Fix all 3 bugs, then re-run. When you see `🎉 All 3 tests passed`, you're done!

---


## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** In Microsoft Viva Insights, what is the default minimum group size to protect employee privacy?"

    - A) 3 users
    - B) 5 users
    - C) 10 users
    - D) 25 users

    ??? success "✅ Reveal Answer"
        **Correct: B) 5 users**

        Viva Insights enforces a minimum group size of **5** by default. Reports for groups smaller than 5 are suppressed to prevent identifying individual usage patterns. Admins can increase (but not decrease) this threshold.

??? question "**Q2 (Multiple Choice):** Which metric best indicates that users are *consistently* using Copilot over time, rather than just trying it once?"

    - A) Total emails drafted
    - B) Number of licensed users
    - C) Monthly active days average
    - D) Time saved in minutes

    ??? success "✅ Reveal Answer"
        **Correct: C) Monthly active days average**

        A high active-days count means the user returns to Copilot day after day — this measures **stickiness** and **habit formation**, not just a one-time trial. Total emails or time saved can be inflated by a single heavy-use day.

??? question "**Q3 (Run the Lab):** Which department has the highest Copilot adoption rate (active ÷ enabled × 100)?"

    Run the Step 3 analysis on [📥 `copilot_usage_data.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-047/copilot_usage_data.csv) and check the results.

    ??? success "✅ Reveal Answer"
        **Finance — 100.0%**

        Finance has 6 licensed, 6 enabled, and 6 active users — every single enabled user is actively using Copilot. This makes Finance the model department for scaling adoption best practices to other teams.

??? question "**Q4 (Run the Lab):** How many users across the organization are in the 'enablement gap' (licensed = true, enabled = false)?"

    Run the Step 4a analysis to find out.

    ??? success "✅ Reveal Answer"
        **7 users**

        The 7 users in the enablement gap are: ENG-011, MKT-008, SLS-004, SLS-005, SLS-006, LEG-003, and OPS-006. Sales alone accounts for 3 of these — the quickest win for improving overall adoption is to enable these users.

??? question "**Q5 (Run the Lab):** How many 'power users' are there (employees with `active_days >= 20`)?"

    Filter the dataset for users with 20+ active days and count them.

    ??? success "✅ Reveal Answer"
        **10 power users**

        - Engineering: ENG-001 (22), ENG-002 (20), ENG-004 (21), ENG-007 (23), ENG-009 (20) → 5
        - Marketing: MKT-003 (20) → 1
        - Finance: FIN-001 (22), FIN-002 (21), FIN-003 (20), FIN-005 (23) → 4
        - **Total: 10 power users** across Engineering, Marketing, and Finance

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| Work IQ | Framework for measuring AI adoption and proving ROI |
| Adoption Rate | active ÷ enabled × 100 — the primary health metric |
| Enablement Gap | Licensed but not enabled — the quickest fix for low adoption |
| Feature Mix | Which Copilot features drive the most value |
| Time Saved | Converting minutes into business impact for leadership |
| Scorecard | Combining metrics into an executive-ready report |

---

## Next Steps

- **[Lab 048](lab-048-work-iq-power-bi.md)** *(coming soon)* — Build advanced Power BI dashboards with Viva Insights Advanced Reporting
- **[Lab 033](lab-033-agent-observability.md)** — Agent Observability with Application Insights (similar analytics mindset for custom agents)
- **[Lab 035](lab-035-agent-evaluation.md)** — Agent Evaluation with Azure AI Eval SDK (measuring agent quality, not just adoption)
- **[Lab 038](lab-038-cost-optimization.md)** — AI Cost Optimization (the financial side of ROI)
