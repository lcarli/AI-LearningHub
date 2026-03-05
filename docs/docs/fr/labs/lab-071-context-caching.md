---
tags: [caching, cost-optimization, anthropic, google, openai, python]
---
# Lab 071: Context Caching — Cutting Costs for Large-Document Agents

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~60 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Uses mock benchmark data</span>
</div>

!!! info "Traduction en cours"
    Ce lab est en cours de traduction. Le contenu ci-dessous est en anglais.



## What You'll Learn

- What **context caching** is and how providers (Anthropic, Google, OpenAI) implement it
- How cache hits reduce **time-to-first-token (TTFT)** and **per-request cost**
- Analyze a benchmark CSV to quantify latency and cost savings across 3 providers
- Identify when caching delivers the highest ROI for large-document agent workloads
- Build a **cache performance report** comparing hit vs. miss economics

## Introduction

When an agent processes the same 100k-token document across multiple turns, you pay for those input tokens every single time — unless you use **context caching**. All three major providers now offer caching mechanisms:

| Provider | Feature | How It Works |
|----------|---------|-------------|
| **Anthropic** | Prompt Caching | Cache breakpoints in system/user messages; cached tokens billed at 10% of input price |
| **Google** | Context Caching | Explicit cache creation via API; cached tokens billed at 25% of input price |
| **OpenAI** | Automatic Caching | Automatic prefix matching for prompts ≥1024 tokens; cached tokens billed at 50% of input price |

### The Scenario

You are an **AI Platform Engineer** at a legal-tech company. Your contract-review agent processes 150k–200k token documents. Each contract requires 3–5 follow-up questions against the same document. Leadership wants to know: _"How much money and latency can we save by enabling context caching?"_

You have a **benchmark dataset** (`cache_benchmark.csv`) with 15 requests across 3 providers — a mix of cache hits and misses. Your job: analyze the data and build a cost-savings report.

!!! info "Mock Data"
    This lab uses a mock benchmark CSV so anyone can follow along without API keys. The data structure and cost ratios mirror real-world caching behavior from each provider's documentation.

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
    Save all files to a `lab-071/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_cache.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-071/broken_cache.py) |
| `cache_benchmark.csv` | Benchmark dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-071/cache_benchmark.csv) |

---

## Step 1: Understand Context Caching Mechanics

Before analyzing data, understand the key concepts:

| Concept | Definition |
|---------|-----------|
| **Cache Miss** | First request — full context sent to model, no cached data exists |
| **Cache Hit** | Subsequent request — context found in cache, reduced input processing |
| **TTFT** | Time-to-first-token — how fast the model starts responding |
| **Input Cost** | Cost charged when context is NOT cached (full price) |
| **Cached Cost** | Cost charged when context IS cached (discounted price) |

### Key Insight

Cache hits save money in two ways:

1. **Lower token cost** — cached tokens are billed at a fraction of the input price
2. **Lower latency** — the model doesn't need to re-process the full context, so TTFT drops dramatically

---

## Step 2: Load and Explore the Benchmark Data

The dataset has **15 requests** across 3 providers. Start by loading it:

```python
import pandas as pd

df = pd.read_csv("lab-071/cache_benchmark.csv")

print(f"Total requests: {len(df)}")
print(f"Providers: {df['provider'].unique().tolist()}")
print(f"Cache statuses: {df['cache_status'].value_counts().to_dict()}")
print(f"\nColumns: {list(df.columns)}")
print(f"\nFirst 5 rows:\n{df.head()}")
```

**Expected output:**

```
Total requests: 15
Providers: ['anthropic', 'google', 'openai']
Cache statuses: {'hit': 9, 'miss': 6}
```

Explore the data by provider:

```python
summary = df.groupby("provider").agg(
    requests=("request_id", "count"),
    hits=("cache_status", lambda x: (x == "hit").sum()),
    misses=("cache_status", lambda x: (x == "miss").sum()),
    avg_tokens=("context_tokens", "mean"),
).reset_index()
print(summary)
```

---

## Step 3: Analyze Latency Impact — TTFT Comparison

The biggest user-facing benefit of caching is **latency reduction**. Compare TTFT for cache hits vs. misses:

```python
hits = df[df["cache_status"] == "hit"]
misses = df[df["cache_status"] == "miss"]

avg_hit_ttft = hits["ttft_ms"].mean()
avg_miss_ttft = misses["ttft_ms"].mean()
speedup = avg_miss_ttft / avg_hit_ttft

print(f"Avg TTFT (cache hit):  {avg_hit_ttft:.0f} ms")
print(f"Avg TTFT (cache miss): {avg_miss_ttft:.0f} ms")
print(f"Speedup factor:        {speedup:.1f}x faster with cache")
```

**Expected output:**

```
Avg TTFT (cache hit):  217 ms
Avg TTFT (cache miss): 2583 ms
Speedup factor:        11.9x faster with cache
```

Now break it down by provider:

```python
ttft_by_provider = df.groupby(["provider", "cache_status"])["ttft_ms"].mean().unstack()
ttft_by_provider["speedup"] = ttft_by_provider["miss"] / ttft_by_provider["hit"]
print(ttft_by_provider.round(0))
```

!!! tip "Insight"
    Cache hits are roughly **10–15x faster** across all providers. For an agent handling follow-up questions on a large document, this means sub-second responses instead of 2–3 second waits per turn.

---

## Step 4: Analyze Cost Savings

Now compute the financial impact. Each row has `input_cost_usd` (charged on miss) and `cached_cost_usd` (charged on hit):

```python
total_miss_cost = misses["input_cost_usd"].sum()
total_hit_cost = hits["cached_cost_usd"].sum()
savings = total_miss_cost - total_hit_cost

print(f"Total cost (cache misses): ${total_miss_cost:.2f}")
print(f"Total cost (cache hits):   ${total_hit_cost:.2f}")
print(f"Total savings:             ${savings:.2f}")
print(f"Savings ratio:             {savings / total_miss_cost * 100:.0f}%")
```

**Expected output:**

```
Total cost (cache misses): $1.80
Total cost (cache hits):   $0.36
Total savings:             $1.44
Savings ratio:             80%
```

Break it down by provider:

```python
cost_by_provider = []
for provider, group in df.groupby("provider"):
    miss_cost = group[group["cache_status"] == "miss"]["input_cost_usd"].sum()
    hit_cost = group[group["cache_status"] == "hit"]["cached_cost_usd"].sum()
    cost_by_provider.append({
        "Provider": provider,
        "Miss Cost": f"${miss_cost:.2f}",
        "Hit Cost": f"${hit_cost:.2f}",
        "Savings": f"${miss_cost - hit_cost:.2f}",
    })

print(pd.DataFrame(cost_by_provider).to_string(index=False))
```

---

## Step 5: Calculate Cache Hit Rate and ROI Metrics

```python
hit_rate = len(hits) / len(df) * 100
cost_per_request_with_cache = (total_miss_cost + total_hit_cost) / len(df)
cost_per_request_without_cache = total_miss_cost / len(misses)

print(f"Overall cache hit rate:          {hit_rate:.0f}%")
print(f"Avg cost/request (with cache):   ${cost_per_request_with_cache:.3f}")
print(f"Avg cost/request (without cache):${cost_per_request_without_cache:.3f}")
```

### Projecting Annual Savings

```python
daily_requests = 500
annual_requests = daily_requests * 365
annual_savings = (savings / len(df)) * annual_requests

print(f"\nProjected annual savings at {daily_requests} requests/day:")
print(f"  ${annual_savings:,.0f}")
```

!!! warning "Real-World Considerations"
    Cache hit rates depend on usage patterns. Sequential follow-up questions on the same document get near-100% hit rates. Diverse, unrelated queries may see 0% hits. Size your savings estimates based on your actual agent conversation patterns.

---

## Step 6: Build the Cache Performance Report

Combine all analysis into a summary report:

```python
report = f"""# 📊 Context Caching Benchmark Report

## Overview
| Metric | Value |
|--------|-------|
| Total Requests | {len(df)} |
| Cache Hits | {len(hits)} ({hit_rate:.0f}%) |
| Cache Misses | {len(misses)} |
| Providers Tested | {', '.join(df['provider'].unique())} |

## Latency Impact
| Metric | Value |
|--------|-------|
| Avg TTFT (hit) | {avg_hit_ttft:.0f} ms |
| Avg TTFT (miss) | {avg_miss_ttft:.0f} ms |
| Speedup | {speedup:.1f}x |

## Cost Impact
| Metric | Value |
|--------|-------|
| Total Miss Cost | ${total_miss_cost:.2f} |
| Total Hit Cost | ${total_hit_cost:.2f} |
| Total Savings | ${savings:.2f} |
| Savings Rate | {savings / total_miss_cost * 100:.0f}% |

## Recommendation
Enable context caching for all large-document agent workflows.
Expected ROI: {savings / total_miss_cost * 100:.0f}% cost reduction, {speedup:.0f}x latency improvement.
"""

print(report)

with open("lab-071/cache_report.md", "w") as f:
    f.write(report)
print("💾 Saved to lab-071/cache_report.md")
```

---

## 🐛 Bug-Fix Exercise

The file `lab-071/broken_cache.py` contains **3 bugs** that produce incorrect caching metrics. Can you find and fix them all?

Run the self-tests to see which ones fail:

```bash
python lab-071/broken_cache.py
```

You should see **3 failed tests**. Each test corresponds to one bug:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Average cached TTFT | Should average hit TTFT, not miss TTFT |
| Test 2 | Total cost savings | Should be sum of miss input costs minus sum of hit cached costs |
| Test 3 | Cache hit rate | Should count hits / total, not misses / total |

Fix all 3 bugs, then re-run. When you see `All passed!`, you're done!

---


## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What is the primary benefit of context caching for multi-turn agent conversations?"

    - A) It improves the model's reasoning accuracy
    - B) It reduces input token costs and time-to-first-token on repeated context
    - C) It allows the model to remember previous conversations permanently
    - D) It increases the maximum context window size

    ??? success "✅ Reveal Answer"
        **Correct: B) It reduces input token costs and time-to-first-token on repeated context**

        Context caching stores previously processed input tokens so they don't need to be re-sent and re-processed. This reduces both the cost (cached tokens are billed at a discount) and latency (TTFT drops dramatically because the model skips re-reading the cached context).

??? question "**Q2 (Multiple Choice):** Which provider charges the lowest rate for cached tokens relative to full input price?"

    - A) OpenAI (50% of input price)
    - B) Google (25% of input price)
    - C) Anthropic (10% of input price)
    - D) All providers charge the same cached rate

    ??? success "✅ Reveal Answer"
        **Correct: C) Anthropic (10% of input price)**

        Anthropic's prompt caching bills cached tokens at just 10% of the standard input price, making it the most aggressive discount. Google charges 25% and OpenAI charges 50%. However, pricing models change — always check the latest documentation.

??? question "**Q3 (Run the Lab):** What is the average TTFT for cache **hits** across all providers?"

    Run the Step 3 analysis on [📥 `cache_benchmark.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-071/cache_benchmark.csv) and check the results.

    ??? success "✅ Reveal Answer"
        **217 ms**

        The 9 cache-hit requests have TTFTs of 180, 175, 190, 220, 210, 230, 250, 240, and 260 ms. The mean is (180+175+190+220+210+230+250+240+260) ÷ 9 = **217 ms** (rounded).

??? question "**Q4 (Run the Lab):** What is the average TTFT for cache **misses** across all providers?"

    Run the Step 3 analysis to find out.

    ??? success "✅ Reveal Answer"
        **2583 ms**

        The 6 cache-miss requests have TTFTs of 2800, 2750, 3200, 3100, 1800, and 1850 ms. The mean is (2800+2750+3200+3100+1800+1850) ÷ 6 = **2583 ms** (rounded).

??? question "**Q5 (Run the Lab):** What is the total cost savings (miss costs minus hit costs) across all 15 requests?"

    Run the Step 4 analysis to calculate it.

    ??? success "✅ Reveal Answer"
        **$1.44**

        Total miss input costs = $0.45 + $0.45 + $0.20 + $0.20 + $0.25 + $0.25 = **$1.80**. Total hit cached costs = $0.045×3 + $0.05×3 + $0.025×3 = $0.135 + $0.15 + $0.075 = **$0.36**. Savings = $1.80 − $0.36 = **$1.44**.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| Context Caching | Stores processed input tokens to avoid re-sending on follow-up requests |
| TTFT Impact | Cache hits reduce TTFT by ~12x (from ~2.6s to ~217ms) |
| Cost Savings | 80% cost reduction on cached requests across all providers |
| Provider Comparison | Anthropic (10%), Google (25%), OpenAI (50%) cached token discounts |
| ROI Analysis | How to project savings based on request volume and hit rates |
| Benchmark Methodology | Structuring cache experiments with hit/miss tracking |

---

## Next Steps

- **[Lab 038](lab-038-cost-optimization.md)** — AI Cost Optimization (broader cost strategies beyond caching)
- **[Lab 019](lab-019-streaming-responses.md)** — Streaming Responses (complementary latency optimization)
- **[Lab 033](lab-033-agent-observability.md)** — Agent Observability (monitor cache hit rates in production)
- **[Lab 072](lab-072-structured-outputs.md)** — Structured Outputs (guaranteed JSON for cost-efficient agent pipelines)
