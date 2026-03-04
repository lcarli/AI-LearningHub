---
tags: [slm, phi-4, onnx, privacy, local-inference, python]
---
# Lab 061: SLMs — Phi-4 Mini for Low-Cost Agent Skills

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~60 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Uses mock benchmark data (no API key required)</span>
</div>

## What You'll Learn

- How **Small Language Models (SLMs)** like Phi-4 Mini compare to frontier models like GPT-4o
- When SLMs offer a better trade-off: **low latency, privacy, and zero cloud cost**
- Run **ONNX Runtime** inference locally for agent skills (classify, extract, summarize, route, draft)
- Analyze a **15-task benchmark** comparing Phi-4 Mini vs GPT-4o on accuracy, latency, and cost
- Identify which task types SLMs handle well — and where they fall short
- Apply a **privacy-first inference** strategy for sensitive workloads

---

## Introduction

Frontier models like GPT-4o deliver exceptional quality, but they come with latency, cost, and privacy trade-offs. **Small Language Models (SLMs)** like Phi-4 Mini run locally via ONNX Runtime, offering dramatically lower latency, zero cloud cost, and full data privacy — your data never leaves the device.

The question isn't "which model is better" — it's "which tasks can an SLM handle just as well?" This lab uses a 15-task benchmark to find the answer.

### The Benchmark

You'll compare **Phi-4 Mini (local)** vs **GPT-4o (cloud)** across **15 tasks** in 5 categories:

| Category | Count | Example |
|----------|-------|---------|
| **Classify** | 3 | Sentiment analysis, intent detection, topic tagging |
| **Extract** | 3 | Entity extraction, key-value parsing, date normalization |
| **Summarize** | 3 | Meeting notes, article digest, support ticket summary |
| **Route** | 3 | Ticket routing, escalation decision, queue assignment |
| **Draft** | 3 | Email reply, report paragraph, product description |

---

## Prerequisites

```bash
pip install pandas
```

This lab analyzes pre-computed benchmark results — no API key, GPU, or ONNX Runtime installation required. To run live inference, you would need ONNX Runtime and the Phi-4 Mini ONNX model.

---

## Part 1: Understanding SLMs

### Step 1: SLMs vs frontier models

SLMs are compact models (typically 1–4B parameters) optimized for specific task patterns. They trade breadth for efficiency:

```
Frontier Model (GPT-4o):
  Cloud API → [Large model] → High accuracy, high latency, per-token cost

Small Language Model (Phi-4 Mini):
  Local ONNX → [Compact model] → Good accuracy, very low latency, zero cost
```

Key concepts:

| Concept | Description |
|---------|-------------|
| **SLM** | Small Language Model — compact model optimized for specific tasks |
| **ONNX Runtime** | Cross-platform inference engine for running models locally |
| **Privacy-first inference** | Data never leaves the device — critical for PII, health, finance |
| **Task routing** | Directing simple tasks to SLMs and complex tasks to frontier models |

!!! info "When to consider SLMs"
    SLMs excel at well-defined, constrained tasks like classification, extraction, and routing. They struggle with open-ended creative tasks that require broad world knowledge. The ideal architecture routes each task to the right-sized model.

---

## Part 2: Load Benchmark Data

### Step 2: Load `slm_benchmark.csv`

The benchmark dataset contains results from running all 15 tasks through both models:

```python
# slm_analysis.py
import pandas as pd

bench = pd.read_csv("lab-061/slm_benchmark.csv")

print(f"Tasks: {len(bench)}")
print(f"Categories: {bench['category'].unique().tolist()}")
print(bench[["task_id", "category", "description"]].to_string(index=False))
```

**Expected output:**

```
Tasks: 15
Categories: ['classify', 'extract', 'summarize', 'route', 'draft']

task_id  category                          description
    T01  classify                   Sentiment analysis
    T02  classify                     Intent detection
    T03  classify                        Topic tagging
    T04   extract                  Entity extraction
    T05   extract                  Key-value parsing
    T06   extract                Date normalization
    T07 summarize                     Meeting notes
    T08 summarize                    Article digest
    T09 summarize            Support ticket summary
    T10     draft                       Email reply
    T11     draft                  Report paragraph
    T12     draft              Product description
    T13     route                   Ticket routing
    T14 summarize       Compliance document summary
    T15     route              Escalation decision
```

---

## Part 3: Accuracy Comparison

### Step 3: Calculate accuracy for each model

```python
# Overall accuracy
for model in ["phi4_mini", "gpt4o"]:
    correct = bench[f"{model}_correct"].sum()
    total = len(bench)
    print(f"{model:>10}: {correct}/{total} = {correct/total*100:.0f}%")
```

**Expected output:**

```
 phi4_mini: 12/15 = 80%
     gpt4o: 15/15 = 100%
```

!!! warning "Key Finding"
    Phi-4 Mini achieves 80% accuracy — solid for most agent tasks. GPT-4o gets everything right, but at much higher latency and cost. The 3 tasks Phi-4 Mini fails on reveal where SLMs hit their limits.

```python
# Which tasks does Phi-4 Mini get wrong?
phi4_fails = bench[bench["phi4_mini_correct"] == False]
print("Phi-4 Mini failures:")
print(phi4_fails[["task_id", "category", "description"]].to_string(index=False))
```

**Expected output:**

```
Phi-4 Mini failures:
task_id  category                    description
    T10     draft                     Email reply
    T11     draft                Report paragraph
    T14 summarize  Compliance document summary
```

Phi-4 Mini fails on **2 draft tasks** (T10, T11) and **1 summarize task** (T14). Draft tasks require creative, nuanced writing — exactly where SLMs struggle. T14 is a complex compliance document that exceeds the model's context capacity.

---

## Part 4: Latency Comparison

### Step 4: Compare inference latency

```python
# Average latency per model
for model in ["phi4_mini", "gpt4o"]:
    avg_ms = bench[f"{model}_latency_ms"].mean()
    print(f"{model:>10}: {avg_ms:.1f}ms average")

# Speedup
phi4_avg = bench["phi4_mini_latency_ms"].mean()
gpt4o_avg = bench["gpt4o_latency_ms"].mean()
speedup = gpt4o_avg / phi4_avg
print(f"\nPhi-4 Mini is {speedup:.0f}× faster than GPT-4o")
```

**Expected output:**

```
 phi4_mini: 82.3ms average
     gpt4o: 996.7ms average

Phi-4 Mini is 12× faster than GPT-4o
```

!!! info "Latency Advantage"
    Phi-4 Mini runs locally via ONNX Runtime at 82.3ms average — **12× faster** than GPT-4o's cloud round-trip of ~1 second. For agent skills that execute repeatedly (classification, routing), this latency difference compounds dramatically.

```python
# Per-task latency comparison
print("\nPer-task latency:")
for _, row in bench.iterrows():
    print(f"  {row['task_id']} ({row['category']:>9}): "
          f"Phi-4={row['phi4_mini_latency_ms']:.0f}ms  "
          f"GPT-4o={row['gpt4o_latency_ms']:.0f}ms")
```

---

## Part 5: Cost Analysis

### Step 5: Calculate cloud cost avoided

```python
# Total cloud cost for GPT-4o
total_cost = bench["gpt4o_cost_usd"].sum()
print(f"Total GPT-4o cloud cost: ${total_cost:.4f}")
print(f"Phi-4 Mini local cost:   $0.0000")
print(f"Cost avoided by using SLM: ${total_cost:.4f}")

# Cost per category
print("\nCost by category:")
for cat in bench["category"].unique():
    cat_cost = bench[bench["category"] == cat]["gpt4o_cost_usd"].sum()
    print(f"  {cat:>9}: ${cat_cost:.4f}")
```

**Expected output:**

```
Total GPT-4o cloud cost: $0.0121
Phi-4 Mini local cost:   $0.0000
Cost avoided by using SLM: $0.0121

Cost by category:
  classify: $0.0018
   extract: $0.0021
 summarize: $0.0035
     route: $0.0015
     draft: $0.0032
```

While $0.0121 seems small for 15 tasks, at scale (thousands of agent invocations per day), the savings compound rapidly — and the privacy benefit is priceless for sensitive data.

---

## Part 6: Task Routing Strategy

### Step 6: Build a routing decision

Based on the benchmark, the optimal strategy routes tasks by category:

| Category | Recommended Model | Why |
|----------|------------------|-----|
| **Classify** | Phi-4 Mini | 100% accuracy, 12× faster, zero cost |
| **Extract** | Phi-4 Mini | 100% accuracy, 12× faster, zero cost |
| **Route** | Phi-4 Mini | 100% accuracy, 12× faster, zero cost |
| **Summarize** | Phi-4 Mini (with fallback) | 2/3 correct; fall back to GPT-4o for complex docs |
| **Draft** | GPT-4o | SLM fails on creative writing — use frontier model |

```python
# Summary dashboard
print("""
╔══════════════════════════════════════════════════════╗
║     SLM Benchmark — Phi-4 Mini vs GPT-4o            ║
╠══════════════════════════════════════════════════════╣
║  Metric              Phi-4 Mini     GPT-4o          ║
║  ─────────────       ──────────     ──────          ║
║  Accuracy              80%          100%            ║
║  Avg Latency           82.3ms       996.7ms         ║
║  Speedup               12×          baseline        ║
║  Cloud Cost             $0           $0.0121        ║
║  Privacy                Full         Data leaves    ║
╠══════════════════════════════════════════════════════╣
║  Route: classify/extract/route → SLM                ║
║  Route: draft → frontier model                      ║
║  Route: summarize → SLM with fallback               ║
╚══════════════════════════════════════════════════════╝
""")
```

---

## 🐛 Bug-Fix Exercise

The file `lab-061/broken_slm.py` has **3 bugs** in the SLM analysis functions. Run the self-tests:

```bash
python lab-061/broken_slm.py
```

You should see **3 failed tests**:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Accuracy calculation | Which column represents correctness — `_correct` or `_latency_ms`? |
| Test 2 | Cost calculation | Are you summing `_tokens` or `_cost_usd`? |
| Test 3 | Filtering failed tasks | Are you filtering for `category == "draft"` or missing the filter entirely? |

Fix all 3 bugs and re-run until you see `🎉 All 3 tests passed`.

---

## 📁 Supporting Files

- 📥 [broken_slm.py](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-061/broken_slm.py)
- 📥 [slm_benchmark.csv](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-061/slm_benchmark.csv)

```
lab-061/
├── slm_benchmark.csv    ← 15 tasks × 2 models (accuracy, latency, cost)
└── broken_slm.py        ← Bug-fix exercise (3 bugs + self-tests)
```

**Quick start:**

```bash
pip install pandas
cd docs/docs/en/labs

# Follow along with the lab steps
python -c "import pandas; print('ready!')"

# Or fix the bugs
python lab-061/broken_slm.py
```

---

## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What are the primary advantages of using an SLM like Phi-4 Mini over a frontier model like GPT-4o?"

    - A) Higher accuracy on all task types
    - B) Low latency, data privacy, and zero cloud cost
    - C) Better creative writing and summarization
    - D) Larger context window and more parameters

    ??? success "✅ Reveal Answer"
        **Correct: B) Low latency, data privacy, and zero cloud cost**

        SLMs run locally via ONNX Runtime, delivering 12× lower latency (82.3ms vs 996.7ms), keeping all data on-device for full privacy, and eliminating per-token cloud costs. They don't beat frontier models on accuracy (80% vs 100%), but for well-defined tasks like classification, extraction, and routing, the accuracy is sufficient and the operational benefits are significant.

??? question "**Q2 (Multiple Choice):** When should you NOT use an SLM like Phi-4 Mini?"

    - A) For sentiment classification
    - B) For entity extraction
    - C) For complex creative writing tasks
    - D) For ticket routing

    ??? success "✅ Reveal Answer"
        **Correct: C) For complex creative writing tasks**

        The benchmark shows Phi-4 Mini fails on both draft tasks (T10: email reply, T11: report paragraph). Creative writing requires nuanced language generation, broad world knowledge, and stylistic flexibility — areas where SLMs lack the capacity of frontier models. Classify, extract, and route tasks are well-suited to SLMs.

??? question "**Q3 (Run the Lab):** What is Phi-4 Mini's accuracy on the 15-task benchmark?"

    Calculate `bench["phi4_mini_correct"].sum() / len(bench) * 100`.

    ??? success "✅ Reveal Answer"
        **80% (12/15)**

        Phi-4 Mini correctly handles 12 of 15 tasks. It achieves 100% accuracy on classify (3/3), extract (3/3), and route (3/3) tasks, but fails on 2 draft tasks (T10, T11) and 1 complex summarize task (T14). This 80% accuracy is sufficient for a task-routing architecture where only appropriate tasks are sent to the SLM.

??? question "**Q4 (Run the Lab):** How much faster is Phi-4 Mini compared to GPT-4o?"

    Calculate `bench["gpt4o_latency_ms"].mean() / bench["phi4_mini_latency_ms"].mean()`.

    ??? success "✅ Reveal Answer"
        **~12× faster**

        Phi-4 Mini averages 82.3ms per task via local ONNX Runtime inference, while GPT-4o averages 996.7ms including cloud round-trip. The ratio is 996.7 / 82.3 ≈ 12×. For agent pipelines that execute many skills sequentially, this latency reduction compounds — a 10-step agent pipeline drops from ~10 seconds to under 1 second.

??? question "**Q5 (Run the Lab):** How much total cloud cost is avoided by using Phi-4 Mini for all 15 tasks?"

    Calculate `bench["gpt4o_cost_usd"].sum()`.

    ??? success "✅ Reveal Answer"
        **$0.0121**

        The total GPT-4o cloud cost across all 15 tasks is $0.0121. While this seems small, it scales linearly — 10,000 invocations per day would cost ~$8/day or ~$240/month. With Phi-4 Mini running locally, the cloud cost is exactly $0. The real value is often privacy rather than cost: for healthcare, finance, and legal workloads, keeping data on-device may be a compliance requirement.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| SLMs | Compact models optimized for specific tasks — fast, private, free |
| Phi-4 Mini | 80% accuracy on 15-task benchmark, 12× faster than GPT-4o |
| ONNX Runtime | Local inference engine — no cloud dependency |
| Task Routing | Route classify/extract/route to SLM; draft to frontier model |
| Privacy | SLM inference keeps all data on-device — critical for sensitive workloads |
| Cost | $0.0121 cloud cost avoided per 15 tasks; compounds at scale |

---

## Next Steps

- **[Lab 062](lab-062-ondevice-phi-silica.md)** — On-Device Agents with Phi Silica (NPU-accelerated on-device inference)
- **[Lab 060](lab-060-reasoning-models.md)** — Reasoning Models (when you need maximum accuracy over speed)
- **[Lab 044](lab-044-phi4-ollama-production.md)** — Phi-4 with Ollama in Production (alternative local deployment)
