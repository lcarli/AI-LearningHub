---
tags: [browser-automation, cua, openai, playwright, python, safety]
---
# Lab 058: Browser Automation Agents with OpenAI CUA

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Path:</strong> <a href="../paths/pro-code/">⚙️ Pro Code</a></span>
  <span><strong>Time:</strong> ~90 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Uses benchmark dataset; OpenAI API optional</span>
</div>

!!! info "Traduction en cours"
    Ce lab est en cours de traduction. Le contenu ci-dessous est en anglais.



## What You'll Learn

- What **OpenAI CUA** (Computer-Using Agent) is — GPT-4o vision driving a real cloud browser via screenshots
- The architectural difference between **CUA** (screenshot-based) and **Playwright** (code-based selectors)
- When to use CUA vs Playwright — dynamic sites without stable selectors vs structured, well-known pages
- Design **safety boundaries** — URL allowlists, session time limits, and action confirmation
- Analyze **web automation benchmarks** comparing CUA and Playwright across difficulty levels

## Introduction

**OpenAI CUA** operates a real browser through screenshots. The agent sees the rendered page as an image, reasons about what to do next, and sends structured actions (click coordinates, type text, scroll). This is fundamentally different from **Playwright**, which interacts with the page through code — CSS selectors, XPath queries, and programmatic API calls.

| Approach | How It "Sees" the Page | Interaction Method | Brittleness |
|----------|----------------------|-------------------|-------------|
| **CUA** | Screenshots (pixels) | Click coordinates, keyboard input | Resilient to DOM changes; struggles with dynamic SPAs |
| **Playwright** | DOM / HTML structure | CSS selectors, XPath, API calls | Breaks when selectors change; fast and precise |

### The Scenario

You are a **Web Automation Engineer** at OutdoorGear Inc. The team needs to automate tasks across multiple web properties — the e-commerce storefront, travel booking partners, support portal, and internal analytics dashboards. Some sites have stable, well-structured HTML; others are dynamic single-page applications with constantly changing selectors.

Your job is to evaluate **CUA vs Playwright** using a benchmark dataset of **10 tasks** attempted by both methods, and recommend which approach to use for each scenario.

!!! info "No Live Agent Required"
    This lab analyzes a **pre-recorded benchmark dataset** comparing CUA and Playwright results. You don't need an OpenAI API key or Playwright installation — all analysis is done locally with pandas. If you have API access, you can optionally extend the lab to run live CUA tasks.

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Run analysis scripts |
| `pandas` library | DataFrame operations |
| (Optional) OpenAI API key | For live CUA experiments |
| (Optional) Playwright | For live browser automation comparison |

```bash
pip install pandas
```

---

!!! tip "Quick Start with GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    All dependencies are pre-installed in the devcontainer.


## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-058/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_cua.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-058/broken_cua.py) |
| `browser_tasks.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-058/browser_tasks.csv) |

---

## Step 1: Understanding CUA vs Playwright

### CUA Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Browser     │────▶│  GPT-4o      │────▶│  Browser     │
│  Screenshot  │     │  Vision      │     │  Action      │
│  (pixels)    │     │  (reason)    │     │  (click/type)│
└─────────────┘     └──────────────┘     └──────────────┘
       ▲                                        │
       └────────────────────────────────────────┘
                    repeat until done
```

CUA sends screenshots to GPT-4o, which returns structured actions. The browser executes the action, takes a new screenshot, and the loop continues until the task is complete.

### Playwright Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│  Test Script │────▶│  Browser     │────▶│  DOM / HTML  │
│  (code)      │     │  Engine      │     │  (selectors) │
└─────────────┘     └──────────────┘     └──────────────┘
```

Playwright executes pre-written code that targets specific HTML elements using CSS selectors, XPath, or ARIA roles. It's fast, precise, and deterministic — but breaks when the page structure changes.

### When to Use Each

| Scenario | Best Approach | Why |
|----------|--------------|-----|
| Stable, well-structured site | **Playwright** | Selectors are reliable; faster and cheaper |
| Dynamic SPA with changing selectors | **CUA** | Vision-based; doesn't depend on DOM structure |
| CAPTCHA-protected pages | **CUA** | Can "see" and reason about CAPTCHAs |
| High-volume, repetitive tasks | **Playwright** | Faster execution; no API cost per action |
| Unknown/new site exploration | **CUA** | No pre-written selectors needed |

!!! tip "Key Difference"
    CUA uses **vision and screenshots** to understand the page — like a human looking at a screen. Playwright uses **code and selectors** — like a developer inspecting the HTML source. CUA is more flexible; Playwright is more reliable on known pages.

---

## Step 2: Load the Benchmark Dataset

The dataset contains **10 tasks**, each attempted by both CUA and Playwright:

```python
import pandas as pd

tasks = pd.read_csv("lab-058/browser_tasks.csv")
print(f"Total rows: {len(tasks)}")
print(f"Unique tasks: {tasks['task_id'].nunique()}")
print(f"Website types: {sorted(tasks['website_type'].unique())}")
print(f"Difficulty levels: {sorted(tasks['difficulty'].unique())}")
print(f"\nDataset preview:")
print(tasks[["task_id", "task_description", "difficulty",
             "cua_completed", "playwright_completed"]].to_string(index=False))
```

**Expected output:**

```
Total rows: 10
Unique tasks: 10
Website types: ['auth', 'data', 'e-commerce', 'support', 'travel', 'webapp']
Difficulty levels: ['easy', 'hard', 'medium']
```

| task_id | task_description | difficulty | cua | playwright |
|---------|-----------------|------------|-----|------------|
| T01 | Search for hiking boots and filter by price | easy | ✓ | ✓ |
| T02 | Add a product to cart and view cart total | easy | ✓ | ✓ |
| T03 | Fill out a shipping address form | medium | ✓ | ✓ |
| ... | ... | ... | ... | ... |
| T10 | Navigate a dynamic SPA with client-side routing | hard | ✗ | ✓ |

---

## Step 3: Compare CUA vs Playwright Success Rates

Calculate and compare completion rates for both methods:

```python
cua_completed = tasks["cua_completed"].sum()
pw_completed = tasks["playwright_completed"].sum()
total = len(tasks)

cua_rate = (cua_completed / total) * 100
pw_rate = (pw_completed / total) * 100

print(f"CUA:        {cua_completed}/{total} = {cua_rate:.0f}%")
print(f"Playwright: {pw_completed}/{total} = {pw_rate:.0f}%")
print(f"Difference: {pw_rate - cua_rate:.0f} percentage points in Playwright's favor")
```

**Expected output:**

```
CUA:        7/10 = 70%
Playwright: 8/10 = 80%
Difference: 10 percentage points in Playwright's favor
```

### Where Each Method Excels

```python
# Tasks where CUA succeeded but Playwright failed
cua_only = tasks[(tasks["cua_completed"] == True) & (tasks["playwright_completed"] == False)]
print(f"CUA succeeded, Playwright failed ({len(cua_only)}):")
print(cua_only[["task_id", "task_description"]].to_string(index=False))

# Tasks where Playwright succeeded but CUA failed
pw_only = tasks[(tasks["playwright_completed"] == True) & (tasks["cua_completed"] == False)]
print(f"\nPlaywright succeeded, CUA failed ({len(pw_only)}):")
print(pw_only[["task_id", "task_description"]].to_string(index=False))
```

**Expected:**

- **CUA only**: T07 (Submit a support ticket with screenshot attachment) — dynamic form with file upload that's hard to script with selectors
- **Playwright only**: T06 (Compare hotel prices across 3 tabs), T10 (Navigate a dynamic SPA) — structured tasks where code-based navigation is more reliable

!!! tip "Insight"
    Playwright has a higher overall success rate (80% vs 70%), but CUA wins on tasks that involve **dynamic content** or **visual reasoning** (like attaching screenshots to support tickets). Playwright excels at **structured, multi-tab** workflows where precise selector-based navigation is needed.

---

## Step 4: Analyze by Difficulty

Break down success rates by difficulty level:

```python
print("Success rates by difficulty:\n")
for diff in ["easy", "medium", "hard"]:
    subset = tasks[tasks["difficulty"] == diff]
    cua_r = (subset["cua_completed"].sum() / len(subset)) * 100
    pw_r = (subset["playwright_completed"].sum() / len(subset)) * 100
    print(f"  {diff.upper()} ({len(subset)} tasks):")
    print(f"    CUA:        {subset['cua_completed'].sum()}/{len(subset)} = {cua_r:.0f}%")
    print(f"    Playwright: {subset['playwright_completed'].sum()}/{len(subset)} = {pw_r:.0f}%")
    print()
```

**Expected output:**

```
Success rates by difficulty:

  EASY (2 tasks):
    CUA:        2/2 = 100%
    Playwright: 2/2 = 100%

  MEDIUM (3 tasks):
    CUA:        3/3 = 100%
    Playwright: 3/3 = 100%

  HARD (5 tasks):
    CUA:        2/5 = 40%
    Playwright: 3/5 = 60%
```

!!! tip "Insight"
    Both methods handle **easy and medium** tasks perfectly (100%). The gap appears in **hard tasks** where Playwright's selector-based approach has a slight edge (60% vs 40%). However, the tasks where CUA wins (T07) are precisely the ones where Playwright's selectors can't handle dynamic, visual content.

---

## Step 5: Screenshot Analysis

CUA takes screenshots at every step — more screenshots generally means a harder or longer task:

```python
total_screenshots = tasks["cua_screenshots"].sum()
print(f"Total CUA screenshots across all tasks: {total_screenshots}")

print(f"\nScreenshots per task:")
print(tasks[["task_id", "task_description", "difficulty",
             "cua_screenshots", "cua_completed"]].to_string(index=False))

avg_by_diff = tasks.groupby("difficulty")["cua_screenshots"].mean()
print(f"\nAverage screenshots by difficulty:")
print(avg_by_diff.to_string())
```

**Expected output:**

```
Total CUA screenshots across all tasks: 122
```

| task_id | difficulty | screenshots | completed |
|---------|-----------|-------------|-----------|
| T01 | easy | 3 | True |
| T02 | easy | 5 | True |
| T03 | medium | 8 | True |
| T04 | medium | 6 | True |
| T05 | medium | 10 | True |
| T06 | hard | 18 | False |
| T07 | hard | 14 | True |
| T08 | hard | 16 | False |
| T09 | hard | 22 | True |
| T10 | hard | 20 | False |

```
Average screenshots by difficulty:
easy       4.0
medium     8.0
hard      18.0
```

!!! tip "Screenshot Cost"
    Each screenshot is sent to GPT-4o as an image token — at ~765 tokens per screenshot (typical web page), 122 screenshots ≈ 93,000 tokens. At GPT-4o pricing, this is roughly **$0.47 in input tokens** for the entire benchmark run. CUA is cost-effective for moderate workloads but can add up for high-volume tasks.

---

## Step 6: Safety Considerations

### URL Allowlist

Restrict CUA to approved domains:

```python
# Analyze domain patterns in the dataset
print("URL patterns in tasks:")
print(tasks["url_pattern"].value_counts().to_string())

internal = tasks[tasks["url_pattern"] != "external"]
external = tasks[tasks["url_pattern"] == "external"]
print(f"\nInternal domains: {len(internal)} tasks")
print(f"External domains: {len(external)} tasks")

high_risk = tasks[tasks["safety_risk"] == "high"]
print(f"\nHigh-risk tasks: {len(high_risk)}")
print(high_risk[["task_id", "task_description", "safety_risk", "url_pattern"]].to_string(index=False))
```

### Recommended Safety Boundaries

| Boundary | Purpose | Implementation |
|----------|---------|----------------|
| **URL allowlist** | Restrict which sites CUA can visit | `allowed_domains = ["*.outdoorgear.com"]` |
| **Session time limit** | Prevent runaway agents | Kill session after 5 minutes of inactivity |
| **Action confirmation** | Human approval for risky actions | Prompt before form submissions on payment pages |
| **Screenshot retention** | Audit trail | Save all screenshots with timestamps for review |
| **Credential handling** | Never expose passwords in screenshots | Use browser-level autofill; keep passwords out of visible fields |

!!! warning "External Sites"
    Task T10 targets an external domain (`external`). In production, CUA should **never** be pointed at external sites without explicit allowlisting. An unconstrained agent could navigate to phishing sites, download malware, or leak sensitive data through form submissions on untrusted domains.

---

## 🐛 Bug-Fix Exercise

The file `lab-058/broken_cua.py` has **3 bugs** in the CUA analysis functions. Can you find and fix them all?

Run the self-tests to see which ones fail:

```bash
python lab-058/broken_cua.py
```

You should see **3 failed tests**. Each test corresponds to one bug:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | CUA success rate | Should use `cua_completed` column, not `playwright_completed` |
| Test 2 | Total CUA screenshots | Should use `sum()`, not `max()` |
| Test 3 | CUA success rate by difficulty | Must filter by the `difficulty` parameter before computing rate |

Fix all 3 bugs, then re-run. When you see `🎉 All 3 tests passed`, you're done!

---


## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What is the key difference between CUA and Playwright for browser automation?"

    - A) CUA is faster because it skips page rendering
    - B) CUA uses vision/screenshots to understand pages, while Playwright uses code-based CSS selectors
    - C) Playwright can handle CAPTCHAs but CUA cannot
    - D) CUA requires access to the page's HTML source code

    ??? success "✅ Reveal Answer"
        **Correct: B) CUA uses vision/screenshots to understand pages, while Playwright uses code-based CSS selectors**

        CUA sends screenshots to a vision-language model (GPT-4o) and receives click/type actions based on what it "sees" — just like a human looking at a screen. Playwright interacts with the DOM directly using CSS selectors, XPath, or ARIA roles. This fundamental difference means CUA is more flexible (works on any visual interface) while Playwright is more precise (direct DOM access).

??? question "**Q2 (Multiple Choice):** When is CUA a better choice than Playwright?"

    - A) For high-volume, repetitive tasks on stable pages
    - B) For dynamic sites without stable CSS selectors
    - C) When you need deterministic, reproducible test results
    - D) When the page has a well-documented API

    ??? success "✅ Reveal Answer"
        **Correct: B) For dynamic sites without stable CSS selectors**

        CUA excels on sites where the DOM structure changes frequently — dynamic SPAs, sites with A/B testing, or pages with randomized element IDs. Because CUA "sees" the page visually, it doesn't depend on CSS selectors that might break with every deployment. Playwright is better for stable, well-structured sites where selectors are reliable.

??? question "**Q3 (Run the Lab):** What is the CUA success rate?"

    Count tasks where `cua_completed == True` and divide by total tasks.

    ??? success "✅ Reveal Answer"
        **70%**

        7 out of 10 tasks were completed successfully by CUA. The 3 failures (T06, T08, T10) were all **hard** difficulty tasks involving multi-tab comparison, CAPTCHA handling, and dynamic SPA navigation.

??? question "**Q4 (Run the Lab):** What is the Playwright success rate?"

    Count tasks where `playwright_completed == True` and divide by total tasks.

    ??? success "✅ Reveal Answer"
        **80%**

        8 out of 10 tasks were completed successfully by Playwright. The 2 failures (T07, T08) involved a screenshot-attachment upload (which requires visual reasoning beyond selectors) and a CAPTCHA-protected form (which neither method could handle).

??? question "**Q5 (Run the Lab):** What is the total number of CUA screenshots across all tasks?"

    Compute `tasks["cua_screenshots"].sum()`.

    ??? success "✅ Reveal Answer"
        **122**

        Sum of all screenshots: 3 + 5 + 8 + 6 + 10 + 18 + 14 + 16 + 22 + 20 = **122 screenshots**. Hard tasks required significantly more screenshots (avg 18) compared to easy tasks (avg 4), reflecting the additional reasoning steps needed for complex workflows.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| CUA Architecture | GPT-4o vision drives a cloud browser via screenshot→action loop |
| Playwright Architecture | Code-based selectors interact directly with the DOM |
| CUA vs Playwright | CUA: 70% success, flexible; Playwright: 80% success, precise |
| Difficulty Impact | Both methods ace easy/medium; hard tasks reveal their differences |
| Screenshot Overhead | 122 total screenshots; hard tasks require 4× more than easy |
| Safety Design | URL allowlists, session limits, credential isolation, audit trails |

---

## Next Steps

- **[Lab 057](lab-057-computer-use-agents.md)** — Computer-Using Agents for Desktop Automation
- Explore OpenAI's [CUA documentation](https://platform.openai.com/docs/guides/computer-using-agent) for live agent setup
- Try [Playwright](https://playwright.dev/) for code-based browser automation
