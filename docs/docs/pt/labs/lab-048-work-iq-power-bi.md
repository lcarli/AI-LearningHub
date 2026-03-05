---
tags: [enterprise, work-iq, copilot-analytics, python, power-bi, viva-insights, roi]
---
# Lab 048: Work IQ — Copilot Impact Analytics & Power BI

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~90 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Uses included mock datasets (live Viva Insights requires M365 Copilot license)</span>
</div>

!!! info "Tradução em andamento"
    Este lab ainda está sendo traduzido. O conteúdo abaixo está em inglês.



## What You'll Learn

- How **impact attribution** works — connecting Copilot usage to business outcomes
- Calculate the **dollar value of time saved** (ROI) from Copilot adoption data
- Use **Pearson correlation** to measure the relationship between usage and KPIs
- Analyze **month-over-month adoption trends** to identify growth patterns
- Write an **executive impact narrative** that tells a data-driven story
- Understand how these analyses map to **Power BI** dashboards and Viva Insights Advanced Reporting

!!! abstract "Prerequisite"
    Complete **[Lab 047: Work IQ — Copilot Adoption Analytics](lab-047-work-iq-copilot-analytics.md)** first. This lab builds on the adoption analysis concepts and OutdoorGear Inc. scenario from Lab 047.

## Introduction

![Impact Attribution Model](../../assets/diagrams/impact-attribution-model.svg)

In Lab 047 you answered _"Who is using Copilot?"_. Now executives want the harder question answered: _"What value is Copilot creating?"_

**Impact attribution** connects AI tool usage to real business outcomes — revenue growth, faster response times, employee satisfaction, and project delivery. This is the analysis that secures continued AI investment.

### The Scenario

Three months have passed since OutdoorGear Inc. deployed M365 Copilot. You now have:

1. **Copilot usage data** — 3 months of aggregated metrics per department (active users, feature usage, time saved)
2. **Business outcome KPIs** — revenue change, ticket resolution rates, response times, satisfaction scores, project delivery

Your mission: **prove (or disprove) that Copilot is driving measurable business improvement** — and present your findings to the board.

!!! warning "Correlation ≠ Causation"
    This lab teaches you to find **correlations** between usage and outcomes. Correlation does NOT prove that Copilot *caused* the improvement — other factors (new hires, process changes, seasonality) could contribute. Always present findings as "departments with higher Copilot usage *tend to* show better outcomes" rather than "Copilot *caused* the improvement."

---

## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-048/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_roi_calculator.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-048/broken_roi_calculator.py) |
| `business_outcomes.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-048/business_outcomes.csv) |
| `copilot_quarterly_summary.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-048/copilot_quarterly_summary.csv) |
| `impact_analyzer.py` | Starter script with TODOs | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-048/impact_analyzer.py) |

---

## Step 1: Understand Impact Analytics

Before coding, understand the three pillars of impact analytics:

| Pillar | What It Measures | Example |
|--------|-----------------|---------|
| **ROI (Return on Investment)** | Dollar value of time saved vs. license cost | 188 hours saved × $50/hr = $9,400 |
| **Correlation** | Statistical relationship between usage and outcomes | r = 0.97 between active days and satisfaction |
| **Trend Analysis** | How adoption and outcomes change over time | 60% growth in active users over 3 months |

### Viva Insights Advanced Reporting

In a live M365 environment, Viva Insights Advanced Reporting gives you:

- **100+ Copilot metrics** sliced by department, role, manager, and location
- **Organizational data import** to add custom attributes (cost center, hire date, etc.)
- **Privacy controls**: minimum group size of 5, data aggregation, role-based access
- **Power BI templates** for pre-built dashboards

In this lab, we simulate these capabilities with Python and CSV exports.

!!! tip "Power BI Connection"
    If you have Power BI Desktop installed, you can load both CSVs directly into Power BI to create interactive dashboards. All the analysis we do in Python maps 1:1 to Power BI visuals: tables → matrix, correlations → scatter charts, trends → line charts.

---

## Step 2: Load and Merge the Datasets

You have two datasets to work with:

**[📥 `copilot_quarterly_summary.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-048/copilot_quarterly_summary.csv)** — Aggregated usage data (21 rows: 7 departments × 3 months)

| Column | Description |
|--------|-------------|
| `department` | Department name |
| `month` | Month (2026-01, 2026-02, 2026-03) |
| `licensed` / `enabled` / `active_users` | User counts |
| `avg_active_days` | Average active days among active users |
| `total_meetings` / `total_emails` / `total_docs` / `total_chats` | Feature totals |
| `total_time_saved_min` | Estimated minutes saved |

**[📥 `business_outcomes.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-048/business_outcomes.csv)** — Department KPIs (21 rows: 7 departments × 3 months)

| Column | Description |
|--------|-------------|
| `revenue_change_pct` | Revenue change vs. previous year (%) |
| `tickets_resolved_per_person` | Support tickets resolved per person |
| `avg_response_hours` | Average response time (hours) |
| `employee_satisfaction` | Satisfaction score (0-100) |
| `projects_on_time_pct` | Projects delivered on time (%) |

Load and merge them:

```python
import pandas as pd

usage = pd.read_csv("lab-048/copilot_quarterly_summary.csv")
outcomes = pd.read_csv("lab-048/business_outcomes.csv")

# Merge on department + month
merged = pd.merge(usage, outcomes, on=["department", "month"])
print(f"Merged: {len(merged)} rows × {len(merged.columns)} columns")
print(merged.head())
```

**Expected:** 21 rows × 17 columns.

---

## Step 3: Calculate ROI — Dollar Value of Time Saved

The simplest ROI metric: **how much is the time saved worth?**

```python
HOURLY_RATE = 50  # Average fully-loaded cost per employee-hour

total_minutes = usage["total_time_saved_min"].sum()
total_hours = total_minutes / 60
dollar_value = total_hours * HOURLY_RATE

print(f"Total time saved: {total_minutes:,} minutes")
print(f"                = {total_hours:.1f} hours")
print(f"Dollar value:    = ${dollar_value:,.0f} (at ${HOURLY_RATE}/hr)")
```

**Expected output:**

```
Total time saved: 11,280 minutes
                = 188.0 hours
Dollar value:    = $9,400 (at $50/hr)
```

### Per-Department ROI Breakdown

```python
dept_roi = usage.groupby("department")["total_time_saved_min"].sum().reset_index()
dept_roi["hours"] = dept_roi["total_time_saved_min"] / 60
dept_roi["dollar_value"] = dept_roi["hours"] * HOURLY_RATE
dept_roi = dept_roi.sort_values("dollar_value", ascending=False)
print(dept_roi[["department", "hours", "dollar_value"]].to_string(index=False))
```

**Expected output:**

| Department | Hours | Dollar Value |
|------------|-------|-------------|
| Engineering | 65.2 | $3,262 |
| Finance | 45.9 | $2,296 |
| Marketing | 34.3 | $1,713 |
| Operations | 19.6 | $979 |
| Sales | 15.5 | $775 |
| HR | 6.4 | $321 |
| Legal | 1.1 | $54 |

!!! tip "Insight"
    Engineering generates the most absolute value ($3,262) because it has the most users. But **Finance has the highest ROI per user** — 6 users generating $2,296 vs. Engineering's 12 users generating $3,262. Finance's per-user value is **$383** vs. Engineering's **$272**.

---

## Step 4: Correlate Usage with Business Outcomes

Now the critical question: **does higher Copilot usage correlate with better business outcomes?**

```python
# Pearson correlation between average active days and employee satisfaction
correlation = merged["avg_active_days"].corr(merged["employee_satisfaction"])
print(f"Correlation (active_days ↔ satisfaction): {correlation:.3f}")
```

**Expected output:**

```
Correlation (active_days ↔ satisfaction): 0.970
```

A correlation of **0.970** is extremely strong. Departments with higher average active days consistently show higher employee satisfaction.

### Correlation Matrix

Check multiple outcome metrics at once:

```python
usage_cols = ["avg_active_days", "active_users"]
outcome_cols = ["employee_satisfaction", "revenue_change_pct",
                "projects_on_time_pct", "avg_response_hours"]

corr_matrix = merged[usage_cols + outcome_cols].corr()
print("\nCorrelation with avg_active_days:")
for col in outcome_cols:
    r = corr_matrix.loc["avg_active_days", col]
    direction = "↑ positive" if r > 0 else "↓ negative"
    print(f"  {col:>30s}: r = {r:+.3f}  ({direction})")
```

You should see:

- **employee_satisfaction**: strong positive (~0.97)
- **revenue_change_pct**: strong positive
- **projects_on_time_pct**: strong positive
- **avg_response_hours**: strong **negative** (higher usage → *lower* response time = faster)

!!! warning "Remember: Correlation ≠ Causation"
    A correlation of 0.97 is impressive, but it doesn't prove Copilot *caused* the satisfaction increase. High-performing departments may have adopted Copilot faster *because* they're already efficient. Present this as evidence of a **relationship**, not proof of causation.

---

## Step 5: Trend Analysis — Month-over-Month Growth

Track how adoption is growing over time:

```python
monthly = usage.groupby("month")["active_users"].sum().reset_index()
monthly.columns = ["Month", "Active Users"]
print(monthly.to_string(index=False))

jan = monthly[monthly["Month"] == "2026-01"]["Active Users"].values[0]
mar = monthly[monthly["Month"] == "2026-03"]["Active Users"].values[0]
growth = (mar - jan) / jan * 100
print(f"\nGrowth (Jan → Mar): {jan} → {mar} = {growth:.1f}%")
```

**Expected output:**

```
   Month  Active Users
 2026-01            20
 2026-02            28
 2026-03            32

Growth (Jan → Mar): 20 → 32 = 60.0%
```

### Department-Level Trends

```python
print("\nDepartment-level growth (Jan → Mar):")
for dept in usage["department"].unique():
    d = usage[usage["department"] == dept]
    j = d[d["month"] == "2026-01"]["active_users"].values[0]
    m = d[d["month"] == "2026-03"]["active_users"].values[0]
    g = ((m - j) / j * 100) if j > 0 else float("inf")
    arrow = "📈" if g > 50 else "📊" if g > 0 else "⚠️"
    print(f"  {arrow} {dept}: {j} → {m} ({g:+.0f}%)")
```

### Satisfaction Improvement by Department

```python
print("\nSatisfaction improvement (Jan → Mar):")
for dept in outcomes["department"].unique():
    d = outcomes[outcomes["department"] == dept]
    j = d[d["month"] == "2026-01"]["employee_satisfaction"].values[0]
    m = d[d["month"] == "2026-03"]["employee_satisfaction"].values[0]
    delta = m - j
    print(f"  {dept:>15s}: {j} → {m}  (Δ = {delta:+d})")
```

**Expected output:**

| Department | Jan | Mar | Δ |
|------------|-----|-----|---|
| Finance | 75 | 88 | **+13** ← largest |
| Engineering | 72 | 84 | +12 |
| Marketing | 70 | 80 | +10 |
| Operations | 68 | 76 | +8 |
| HR | 62 | 68 | +6 |
| Sales | 65 | 70 | +5 |
| Legal | 58 | 62 | +4 ← smallest |

!!! tip "The Story Writes Itself"
    **Finance** (highest Copilot adoption at 100%) shows the **largest satisfaction improvement (+13)**. **Legal** (lowest adoption at 50%) shows the **smallest improvement (+4)**. This is the correlation story you'll present to the board.

---

## Step 6: Build the Impact Narrative

Combine all findings into an executive-ready document:

```python
narrative = f"""# 📋 OutdoorGear Inc. — Copilot Impact Report
## Q1 2026 (January – March)

### Executive Summary

Over Q1 2026, Microsoft 365 Copilot adoption at OutdoorGear Inc. grew
**{growth:.0f}%** (from {jan} to {mar} active users). The estimated value of
time saved is **${dollar_value:,.0f}** ({total_hours:.0f} hours at $50/hr).

There is a **strong positive correlation (r = {correlation:.2f})** between
Copilot usage intensity and employee satisfaction — departments with higher
average active days consistently report higher satisfaction scores.

### Key Metrics

| Metric | Value |
|--------|-------|
| Active Users (March) | {mar} of 52 employees |
| Adoption Growth (Q1) | {growth:.0f}% |
| Total Time Saved | {total_hours:.0f} hours |
| Estimated ROI | ${dollar_value:,.0f} |
| Usage ↔ Satisfaction Correlation | r = {correlation:.2f} |

### Department Spotlight: Finance 🏆

Finance achieved **100% adoption** with all 6 employees actively using Copilot
an average of 20.5 days/month. They show the **largest satisfaction improvement
(+13 points)** and the **highest per-user ROI ($383/user)**.

### Top 3 Recommendations

1. **Enable the 7 users in the licensing gap** — Sales has 3 licensed users
   not yet enabled. This is the fastest path to increasing adoption.
2. **Replicate Finance's playbook** — interview the Finance team to understand
   what drove their 100% adoption and apply those practices org-wide.
3. **Targeted training for Legal and HR** — lowest adoption departments
   need hands-on enablement sessions, not just license assignment.
"""

print(narrative)

with open("lab-048/impact_narrative.md", "w") as f:
    f.write(narrative)
print("💾 Saved to lab-048/impact_narrative.md")
```

---

## Step 7: Power BI Dashboard (Optional)

If you have **Power BI Desktop** installed, you can create an interactive version of this analysis:

1. **Open Power BI Desktop** → Get Data → Text/CSV
2. Load `copilot_quarterly_summary.csv` and `business_outcomes.csv`
3. In the **Model** view, create a relationship on `department` + `month`
4. Create these visuals:

| Visual Type | X-Axis | Y-Axis | Purpose |
|-------------|--------|--------|---------|
| Clustered Bar | Department | active_users | Adoption by department |
| Line Chart | Month | active_users | Adoption trend |
| Scatter Plot | avg_active_days | employee_satisfaction | Correlation visualization |
| Card | — | dollar_value | ROI headline |
| Matrix | Department × Month | All KPIs | Detailed breakdown |

!!! info "No Power BI? No Problem"
    The Python analysis above produces identical insights. Power BI adds interactivity (filtering, drilling, sharing) but the underlying data and formulas are the same. If you have **matplotlib** installed, you can also create charts in Python:

    ```python
    # pip install matplotlib
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Chart 1: Adoption trend
    monthly.plot(x="Month", y="Active Users", kind="bar", ax=axes[0], color="#3b82f6")
    axes[0].set_title("Copilot Adoption Growth")
    axes[0].set_ylabel("Active Users")

    # Chart 2: Correlation scatter
    axes[1].scatter(merged["avg_active_days"], merged["employee_satisfaction"],
                    c="#8b5cf6", s=60, alpha=0.7)
    axes[1].set_xlabel("Avg Active Days")
    axes[1].set_ylabel("Employee Satisfaction")
    axes[1].set_title(f"Usage vs Satisfaction (r = {correlation:.2f})")

    plt.tight_layout()
    plt.savefig("lab-048/impact_charts.png", dpi=150)
    plt.show()
    print("📊 Charts saved to lab-048/impact_charts.png")
    ```

---

## 🐛 Bug-Fix Exercise

The file `lab-048/broken_roi_calculator.py` contains **3 bugs** that produce wrong impact analytics. Run the self-tests:

```bash
python lab-048/broken_roi_calculator.py
```

You should see **3 failed tests**:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | ROI calculation | Check the unit conversion (minutes → hours) |
| Test 2 | Correlation column | Which column actually measures *usage*? |
| Test 3 | Growth rate base | Which month is the *starting point*? |

Fix all 3 bugs and re-run until you see `🎉 All 3 tests passed`.

---


## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What does 'impact attribution' mean in the context of Work IQ?"

    - A) Counting how many users have a Copilot license
    - B) Connecting AI tool usage to measurable business outcomes
    - C) Tracking which department has the most active users
    - D) Measuring the total cost of AI licenses

    ??? success "✅ Reveal Answer"
        **Correct: B) Connecting AI tool usage to measurable business outcomes**

        Impact attribution goes beyond adoption metrics (who is using Copilot?) to answer the ROI question: is Copilot usage correlated with improved business outcomes like revenue growth, faster response times, and higher employee satisfaction?

??? question "**Q2 (Multiple Choice):** Why is the 'correlation ≠ causation' principle critical when presenting Copilot ROI to leadership?"

    - A) Because correlations are always unreliable
    - B) Because other factors could explain the business improvements
    - C) Because Copilot usage data is not accurate
    - D) Because leadership doesn't understand statistics

    ??? success "✅ Reveal Answer"
        **Correct: B) Because other factors could explain the business improvements**

        High-performing departments may adopt AI tools faster because they're already well-managed — the improvement might be due to leadership quality, hiring, process changes, or seasonal trends. Always present findings as "departments with higher usage *tend to* show better outcomes" rather than claiming direct causation.

??? question "**Q3 (Run the Lab):** What is the estimated total dollar value of time saved across all departments over Q1 2026 (at $50/hr)?"

    Calculate: sum all `total_time_saved_min` values, convert to hours, multiply by $50.

    ??? success "✅ Reveal Answer"
        **$9,400**

        Total time saved: 11,280 minutes ÷ 60 = 188.0 hours × $50/hr = **$9,400**. Engineering contributes the most absolute value ($3,262), but Finance has the highest per-user ROI ($383/user).

??? question "**Q4 (Run the Lab):** Which department shows the largest improvement in employee satisfaction from January to March 2026?"

    Compare each department's January and March `employee_satisfaction` scores.

    ??? success "✅ Reveal Answer"
        **Finance (+13 points: 75 → 88)**

        Finance improved from 75 to 88, a delta of +13. This aligns with Finance having the highest Copilot adoption rate (100%). Engineering is second with +12 (72 → 84). Legal shows the smallest improvement (+4), matching its low adoption.

??? question "**Q5 (Run the Lab):** What is the overall adoption growth rate from January to March 2026?"

    Sum `active_users` for January and March across all departments, then calculate the percentage growth.

    ??? success "✅ Reveal Answer"
        **60.0%**

        January: 6+4+2+1+4+0+3 = **20** active users. March: 9+6+4+2+6+1+4 = **32** active users. Growth = (32 − 20) ÷ 20 × 100 = **60.0%**.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| Impact Attribution | Connecting usage data to business KPIs |
| ROI Calculation | Time saved → hours → dollar value |
| Pearson Correlation | Measuring statistical relationships (r = 0.97) |
| Trend Analysis | Month-over-month adoption growth (60%) |
| Impact Narrative | Executive-ready storytelling with data |
| Power BI Mapping | How Python analysis maps to Power BI visuals |

---

## Next Steps

- **[Lab 033](lab-033-agent-observability.md)** — Agent Observability with Application Insights (monitoring custom agents the same way Viva monitors Copilot)
- **[Lab 038](lab-038-cost-optimization.md)** — AI Cost Optimization (the financial side of ROI for custom AI deployments)
- **[Lab 035](lab-035-agent-evaluation.md)** — Agent Evaluation with Azure AI Eval SDK (quality metrics, not just adoption)
