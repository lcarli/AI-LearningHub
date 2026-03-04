---
tags: [power-bi, copilot, fabric, dax, analytics, low-code]
---
# Lab 075: Power BI Copilot — Autonomous Analytics & Data Storytelling

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~45 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Uses mock report data</span>
</div>

## What You'll Learn

- What **Power BI Copilot** is and how it transforms report creation with natural language
- How Copilot-assisted and Copilot-generated reports compare to manual creation
- Analyze a report dataset to measure **time savings**, **accuracy**, and **adoption** across departments
- Understand how DAX measure generation works with Copilot
- Build an **impact report** quantifying Copilot's value for the analytics team

## Introduction

**Power BI Copilot** brings generative AI directly into the Power BI experience within Microsoft Fabric. Analysts and business users can:

- **Create reports** by describing what they want in natural language
- **Generate DAX measures** without memorizing complex syntax
- **Build narratives** that automatically summarize key insights
- **Ask questions** about their data using conversational queries

### Creation Methods

| Method | Who | How It Works | Typical Time |
|--------|-----|-------------|-------------|
| **Manual** | Analyst | Hand-builds every visual, writes DAX manually | 2–4 hours |
| **Copilot-Assisted** | Analyst | Analyst starts; Copilot suggests visuals, generates DAX | 1–2 hours |
| **Copilot-Generated** | Business User | Describes report in natural language; Copilot builds it | 15–30 min |

### The Scenario

You are a **BI Team Lead** at a mid-sized company. Your team has been piloting Power BI Copilot for 3 months. You have **10 reports** across 4 departments — some manual, some Copilot-assisted, and some fully Copilot-generated. Leadership wants to know: _"Is Copilot actually saving time? Is the quality acceptable?"_

Your dataset (`powerbi_reports.csv`) has the answers. Your job: analyze the data and build a compelling impact report.

!!! info "Mock Data"
    This lab uses a mock report dataset. The data mirrors real-world patterns: Copilot-generated reports are faster but slightly less accurate; Copilot-assisted reports combine speed with analyst-level quality.

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Run the analysis scripts |
| `pandas` library | Data manipulation |

```bash
pip install pandas
```

---

## Step 1: Understand the Metrics

Before analyzing, understand what each column in the dataset measures:

| Column | Description |
|--------|-----------|
| **created_by** | `analyst` or `business_user` — who built the report |
| **creation_method** | `manual`, `copilot_assisted`, or `copilot_generated` |
| **pages** | Number of report pages |
| **visuals** | Total visual elements (charts, tables, cards) |
| **dax_measures** | Number of DAX measures in the data model |
| **copilot_queries** | Number of Copilot interactions used during creation |
| **time_saved_min** | Estimated minutes saved vs. fully manual creation |
| **accuracy_score** | Quality score (0.0–1.0) based on data accuracy review |

### Key Formulas

```
Copilot Adoption Rate = (Copilot reports ÷ Total reports) × 100

Avg Time Saved = Sum(time_saved_min for copilot reports) ÷ Count(copilot reports)

Quality Gap = Avg accuracy(manual) − Avg accuracy(copilot_generated)
```

---

## Step 2: Load and Explore the Dataset

The dataset has **10 reports** across 4 departments:

```python
import pandas as pd

df = pd.read_csv("lab-075/powerbi_reports.csv")

print(f"Total reports: {len(df)}")
print(f"Creation methods: {df['creation_method'].value_counts().to_dict()}")
print(f"Departments: {df['department'].unique().tolist()}")
print(f"\nAll reports:")
print(df[["report_id", "report_name", "creation_method", "time_saved_min", "accuracy_score"]].to_string(index=False))
```

**Expected output:**

```
Total reports: 10
Creation methods: {'copilot_assisted': 4, 'copilot_generated': 4, 'manual': 2}
Departments: ['Sales', 'Marketing', 'Operations', 'HR', 'Finance']
```

---

## Step 3: Measure Copilot Adoption

How many reports used Copilot in some form?

```python
copilot_reports = df[df["creation_method"].isin(["copilot_assisted", "copilot_generated"])]
manual_reports = df[df["creation_method"] == "manual"]

copilot_count = len(copilot_reports)
total = len(df)
adoption_rate = copilot_count / total * 100

print(f"Copilot-assisted/generated reports: {copilot_count}")
print(f"Manual reports:                     {len(manual_reports)}")
print(f"Copilot adoption rate:              {adoption_rate:.0f}%")
```

**Expected output:**

```
Copilot-assisted/generated reports: 8
Manual reports:                     2
Copilot adoption rate:              80%
```

Break down by creation method:

```python
for method, group in df.groupby("creation_method"):
    print(f"\n{method}:")
    print(f"  Reports: {len(group)}")
    print(f"  Avg pages: {group['pages'].mean():.1f}")
    print(f"  Avg visuals: {group['visuals'].mean():.1f}")
    print(f"  Avg DAX measures: {group['dax_measures'].mean():.1f}")
```

!!! tip "Insight"
    **80% of reports** now use Copilot — a strong adoption signal. Manual reports tend to have more pages and visuals, suggesting complex dashboards are still built by hand. Copilot-generated reports are smaller but created by business users who couldn't build them at all before.

---

## Step 4: Calculate Time Savings

The `time_saved_min` column estimates how much time Copilot saved compared to fully manual creation:

```python
total_time_saved = df["time_saved_min"].sum()
copilot_time_saved = copilot_reports["time_saved_min"].sum()
avg_time_saved = copilot_reports["time_saved_min"].mean()

print(f"Total time saved (all reports):      {total_time_saved} min")
print(f"Total time saved (copilot reports):  {copilot_time_saved} min")
print(f"Avg time saved per copilot report:   {avg_time_saved:.1f} min")
print(f"Total hours saved:                   {total_time_saved / 60:.1f} hours")
```

**Expected output:**

```
Total time saved (all reports):      395 min
Total time saved (copilot reports):  395 min
Avg time saved per copilot report:   49.4 min
Total hours saved:                   6.6 hours
```

Break down by method:

```python
for method in ["copilot_assisted", "copilot_generated"]:
    subset = df[df["creation_method"] == method]
    print(f"\n{method}:")
    print(f"  Total saved: {subset['time_saved_min'].sum()} min")
    print(f"  Avg saved:   {subset['time_saved_min'].mean():.1f} min")
```

---

## Step 5: Assess Quality and Accuracy

Time savings are meaningless if quality suffers. Compare accuracy scores:

```python
for method in df["creation_method"].unique():
    subset = df[df["creation_method"] == method]
    avg_acc = subset["accuracy_score"].mean()
    print(f"  {method:>20s}: avg accuracy = {avg_acc:.2f}")
```

**Expected output:**

```
              manual: avg accuracy = 0.96
    copilot_assisted: avg accuracy = 0.94
   copilot_generated: avg accuracy = 0.85
```

```python
# Quality gap analysis
manual_acc = manual_reports["accuracy_score"].mean()
assisted_acc = df[df["creation_method"] == "copilot_assisted"]["accuracy_score"].mean()
generated_acc = df[df["creation_method"] == "copilot_generated"]["accuracy_score"].mean()

print(f"\nQuality gap (manual vs. assisted):  {(manual_acc - assisted_acc) * 100:.1f}pp")
print(f"Quality gap (manual vs. generated): {(manual_acc - generated_acc) * 100:.1f}pp")
```

!!! warning "Quality Trade-off"
    **Copilot-assisted reports** (analyst + Copilot) achieve **0.94 accuracy** — only 2pp below manual. **Copilot-generated reports** (business user + Copilot) score **0.85** — acceptable for exploration but may need analyst review before executive distribution.

---

## Step 6: Build the Impact Report

```python
total_copilot_queries = copilot_reports["copilot_queries"].sum()

report = f"""# 📊 Power BI Copilot Impact Report

## Adoption Summary
| Metric | Value |
|--------|-------|
| Total Reports | {len(df)} |
| Copilot Reports | {copilot_count} ({adoption_rate:.0f}%) |
| Manual Reports | {len(manual_reports)} |
| Total Copilot Queries | {total_copilot_queries} |

## Time Savings
| Metric | Value |
|--------|-------|
| Total Time Saved | {total_time_saved} min ({total_time_saved / 60:.1f} hours) |
| Avg per Copilot Report | {avg_time_saved:.1f} min |
| Copilot-Assisted Avg | {df[df['creation_method']=='copilot_assisted']['time_saved_min'].mean():.1f} min |
| Copilot-Generated Avg | {df[df['creation_method']=='copilot_generated']['time_saved_min'].mean():.1f} min |

## Quality Assessment
| Method | Avg Accuracy | Rating |
|--------|-------------|--------|
| Manual | {manual_acc:.2f} | ⭐⭐⭐ Gold standard |
| Copilot-Assisted | {assisted_acc:.2f} | ⭐⭐⭐ Production-ready |
| Copilot-Generated | {generated_acc:.2f} | ⭐⭐ Review recommended |

## Recommendations
1. **Encourage Copilot-assisted** for analyst-built reports — saves ~41 min with near-manual quality
2. **Use Copilot-generated** for exploratory/departmental reports — saves ~58 min, good for self-service
3. **Add review step** for Copilot-generated reports going to executives — accuracy gap of {(manual_acc - generated_acc) * 100:.0f}pp
4. **Track DAX measure accuracy** — Copilot-generated DAX may need validation for complex calculations
"""

print(report)

with open("lab-075/impact_report.md", "w") as f:
    f.write(report)
print("💾 Saved to lab-075/impact_report.md")
```

---

## 🐛 Bug-Fix Exercise

The file `lab-075/broken_powerbi.py` contains **3 bugs** that produce incorrect Power BI metrics. Can you find and fix them all?

Run the self-tests to see which ones fail:

```bash
python lab-075/broken_powerbi.py
```

You should see **3 failed tests**. Each test corresponds to one bug:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Copilot report count | Should count copilot methods, not `manual` |
| Test 2 | Total time saved | Should sum `time_saved_min`, not average it |
| Test 3 | Average accuracy by method | Should filter by method before averaging |

Fix all 3 bugs, then re-run. When you see `All passed!`, you're done!

---

## 📁 Supporting Files

```
lab-075/
├── powerbi_reports.csv     ← 10 reports (2 manual + 4 assisted + 4 generated)
└── broken_powerbi.py       ← Bug-fix exercise (3 bugs + self-tests)
```

**Quick start:**

```bash
pip install pandas
cd docs/docs/en/labs

# Option A: Follow along with the lab steps (copy-paste code)
python -c "import pandas; print('pandas ready!')"

# Option B: Fix the bugs
python lab-075/broken_powerbi.py
```

---

## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What is the key difference between 'copilot_assisted' and 'copilot_generated' report creation?"

    - A) Copilot-assisted uses a different model than copilot-generated
    - B) Copilot-assisted is started by an analyst who uses Copilot for help; copilot-generated is created entirely from a natural language description
    - C) Copilot-generated reports are always more accurate
    - D) Copilot-assisted reports cannot include DAX measures

    ??? success "✅ Reveal Answer"
        **Correct: B) Copilot-assisted is started by an analyst who uses Copilot for help; copilot-generated is created entirely from a natural language description**

        In copilot-assisted mode, an analyst drives the process and uses Copilot to suggest visuals, generate DAX, or create narrative summaries. In copilot-generated mode, a business user describes the desired report in natural language and Copilot builds it from scratch — faster but with less human oversight.

??? question "**Q2 (Multiple Choice):** Why might copilot-generated reports need a review step before executive distribution?"

    - A) They use too many visuals
    - B) They have lower accuracy scores due to less human oversight during creation
    - C) They are generated too quickly
    - D) They cannot include DAX measures

    ??? success "✅ Reveal Answer"
        **Correct: B) They have lower accuracy scores due to less human oversight during creation**

        Copilot-generated reports average ~0.85 accuracy compared to ~0.96 for manual reports. Without an analyst validating data mappings, filter logic, and DAX calculations, there's a higher risk of subtle errors — especially for complex business metrics.

??? question "**Q3 (Run the Lab):** How many reports were created using Copilot (either assisted or generated)?"

    Run the Step 3 analysis on `powerbi_reports.csv` and count copilot reports.

    ??? success "✅ Reveal Answer"
        **8 reports**

        Of the 10 reports in the dataset, 4 are `copilot_assisted` (R02, R04, R07, R09) and 4 are `copilot_generated` (R03, R05, R08, R10). Only 2 are `manual` (R01, R06). Total copilot reports = **8**.

??? question "**Q4 (Run the Lab):** What is the total time saved across all reports?"

    Run the Step 4 analysis to calculate total time saved.

    ??? success "✅ Reveal Answer"
        **395 minutes**

        Sum of all `time_saved_min` values: 0 + 45 + 60 + 30 + 50 + 0 + 55 + 65 + 35 + 55 = **395 minutes** (6.6 hours). Manual reports (R01, R06) have 0 time saved since they are the baseline.

??? question "**Q5 (Run the Lab):** What is the average time saved per Copilot report?"

    Divide total copilot time saved by the number of copilot reports.

    ??? success "✅ Reveal Answer"
        **49.4 minutes**

        Total time saved by copilot reports = 45 + 60 + 30 + 50 + 55 + 65 + 35 + 55 = 395 min. Number of copilot reports = 8. Average = 395 ÷ 8 = **49.4 minutes** per report.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| Power BI Copilot | AI-powered report creation, DAX generation, and data narratives |
| Creation Methods | Manual, Copilot-assisted (analyst+AI), Copilot-generated (business user+AI) |
| Time Savings | 49.4 min average per Copilot report; 395 min total across pilot |
| Quality Trade-off | Assisted=0.94 accuracy (near-manual); Generated=0.85 (needs review) |
| Adoption | 80% of reports used Copilot — strong pilot adoption signal |
| Self-Service BI | Copilot-generated enables business users to create their own reports |

---

## Next Steps

- **[Lab 048](lab-048-work-iq-power-bi.md)** — Work IQ Power BI dashboards (advanced analytics with Viva Insights)
- **[Lab 047](lab-047-work-iq-copilot-analytics.md)** — Work IQ Copilot Adoption Analytics (measuring Copilot usage across M365)
- **[Lab 074](lab-074-foundry-agent-service.md)** — Foundry Agent Service (deploying AI agents that feed data to Power BI)
- **[Lab 038](lab-038-cost-optimization.md)** — AI Cost Optimization (managing Copilot and AI costs)
