---
tags: [reasoning, o3, deepseek-r1, chain-of-thought, benchmark, python]
---
# Lab 060: Reasoning Models — Chain-of-Thought with o3 and DeepSeek R1

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-200">L200</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~75 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Uses benchmark dataset (Azure OpenAI optional)</span>
</div>

## What You'll Learn

- How **reasoning models** (o3, DeepSeek R1) differ from standard models (GPT-4o) — extended thinking, chain-of-thought
- What a **thinking budget** is and how it controls the depth of model reasoning
- Compare **accuracy, speed, and token cost** across 3 models on 12 benchmark problems
- Identify which **problem categories and difficulty levels** benefit most from reasoning
- Apply a decision framework: **when to use reasoning models** vs standard models
- Understand **cost-performance trade-offs** for production deployments

---

## Introduction

Standard LLMs like GPT-4o generate answers in a single forward pass — fast, but they can stumble on problems that require multi-step logical reasoning. **Reasoning models** like o3 and DeepSeek R1 take a different approach: they use **extended thinking** (chain-of-thought) to break complex problems into steps, verify intermediate results, and backtrack when they detect errors.

The trade-off is clear: reasoning models are slower and use more tokens, but they achieve dramatically higher accuracy on hard problems.

### The Benchmark

You'll compare **3 models** on **12 problems** across 4 categories:

| Category | Easy | Medium | Hard |
|----------|------|--------|------|
| **Math** | Compound interest | System of equations | Prove √2 is irrational |
| **Code** | Reverse a string | Binary search | Thread-safe LRU cache |
| **Logic** | Syllogism | Three boxes puzzle | Wolf-goat-cabbage |
| **Planning** | Hiking itinerary | Delivery route | Microservices migration |

---

## Prerequisites

```bash
pip install pandas
```

This lab analyzes pre-computed benchmark results — no API key or Azure subscription required. To run live benchmarks, you would need access to GPT-4o, o3, and DeepSeek R1 via Azure OpenAI or the respective APIs.

---

## Part 1: Understanding Reasoning Models

### Step 1: How reasoning models work

Standard models generate tokens left-to-right without pausing to "think." Reasoning models add an internal deliberation phase:

```
Standard (GPT-4o):
  Input → [Generate tokens] → Output

Reasoning (o3 / DeepSeek R1):
  Input → [Think: break into steps] → [Verify each step] → [Backtrack if needed] → Output
```

Key concepts:

| Concept | Description |
|---------|-------------|
| **Chain-of-thought** | The model explicitly reasons through intermediate steps before answering |
| **Thinking budget** | Controls how much reasoning the model does (more budget = more thorough = slower) |
| **Extended thinking** | The model's internal deliberation — visible in some APIs as "thinking tokens" |
| **Self-verification** | The model checks its own intermediate results and corrects mistakes |

!!! info "Thinking Budget"
    The thinking budget controls how much reasoning the model does before producing a final answer. A higher budget lets the model explore more solution paths and verify more thoroughly — but costs more tokens and takes more time. For simple questions, a low budget suffices; for complex proofs, you want the full budget.

---

## Part 2: Load Benchmark Data

### Step 2: Load `reasoning_benchmark.csv`

The benchmark dataset contains results from running all 12 problems through each model:

```python
# reasoning_analysis.py
import pandas as pd

bench = pd.read_csv("lab-060/reasoning_benchmark.csv")

# Convert boolean columns
for model in ["gpt4o", "o3", "deepseek_r1"]:
    bench[f"{model}_correct"] = bench[f"{model}_correct"].astype(str).str.lower() == "true"

print(f"Problems: {len(bench)}")
print(f"Categories: {bench['category'].unique().tolist()}")
print(f"Difficulties: {bench['difficulty'].unique().tolist()}")
print(bench[["problem_id", "category", "difficulty"]].to_string(index=False))
```

**Expected output:**

```
Problems: 12
Categories: ['math', 'code', 'logic', 'planning']
Difficulties: ['easy', 'medium', 'hard']

problem_id category difficulty
       P01     math       easy
       P02     math     medium
       P03     math       hard
       P04     code       easy
       P05     code     medium
       P06     code       hard
       P07    logic       easy
       P08    logic     medium
       P09    logic       hard
       P10 planning       easy
       P11 planning     medium
       P12 planning       hard
```

---

## Part 3: Overall Accuracy Comparison

### Step 3: Calculate accuracy for each model

```python
# Overall accuracy
for model in ["gpt4o", "o3", "deepseek_r1"]:
    correct = bench[f"{model}_correct"].sum()
    total = len(bench)
    print(f"{model:>12}: {correct}/{total} = {correct/total*100:.1f}%")
```

**Expected output:**

```
      gpt4o: 6/12 = 50.0%
          o3: 12/12 = 100.0%
 deepseek_r1: 11/12 = 91.7%
```

!!! warning "Key Finding"
    GPT-4o gets only half the problems right, while o3 achieves a perfect score. DeepSeek R1 misses just one problem (P12 — the hardest planning problem). The gap is dramatic on hard problems.

```python
# Which problems does GPT-4o get wrong?
gpt4o_fails = bench[bench["gpt4o_correct"] == False]
print("GPT-4o failures:")
print(gpt4o_fails[["problem_id", "category", "difficulty", "description"]].to_string(index=False))
```

**Expected output:**

```
GPT-4o failures:
problem_id category difficulty                                       description
       P03     math       hard                    Prove that sqrt(2) is irrational
       P06     code       hard          Design a thread-safe LRU cache in Python
       P08    logic     medium  Three boxes puzzle: one has gold - find the optimal strategy
       P09    logic       hard  River crossing puzzle with wolf-goat-cabbage constraints
       P11 planning     medium  Optimize a delivery route for 5 stops minimizing distance
       P12 planning       hard  Design a microservices migration plan for a monolith app
```

GPT-4o fails on **all hard problems** plus two medium problems (P08, P11) that require multi-step reasoning.

```python
# What does DeepSeek R1 get wrong?
r1_fails = bench[bench["deepseek_r1_correct"] == False]
print("DeepSeek R1 failures:")
print(r1_fails[["problem_id", "category", "difficulty", "description"]].to_string(index=False))
```

**Expected output:**

```
DeepSeek R1 failures:
problem_id  category difficulty                                          description
       P12  planning       hard  Design a microservices migration plan for a monolith app
```

DeepSeek R1 fails only on P12 — the most complex planning problem requiring both technical knowledge and multi-step project planning.

---

## Part 4: Accuracy by Category and Difficulty

### Step 4: Break down accuracy by category

```python
# Accuracy by category
for category in bench["category"].unique():
    cat_data = bench[bench["category"] == category]
    print(f"\n{category.upper()}:")
    for model in ["gpt4o", "o3", "deepseek_r1"]:
        correct = cat_data[f"{model}_correct"].sum()
        total = len(cat_data)
        print(f"  {model:>12}: {correct}/{total}")
```

**Expected output:**

```
MATH:
        gpt4o: 2/3
            o3: 3/3
   deepseek_r1: 3/3

CODE:
        gpt4o: 2/3
            o3: 3/3
   deepseek_r1: 3/3

LOGIC:
        gpt4o: 1/3
            o3: 3/3
   deepseek_r1: 3/3

PLANNING:
        gpt4o: 1/3
            o3: 3/3
   deepseek_r1: 2/3
```

```python
# Accuracy by difficulty
for diff in ["easy", "medium", "hard"]:
    diff_data = bench[bench["difficulty"] == diff]
    print(f"\n{diff.upper()}:")
    for model in ["gpt4o", "o3", "deepseek_r1"]:
        correct = diff_data[f"{model}_correct"].sum()
        total = len(diff_data)
        print(f"  {model:>12}: {correct}/{total} = {correct/total*100:.0f}%")
```

**Expected output:**

```
EASY:
        gpt4o: 4/4 = 100%
            o3: 4/4 = 100%
   deepseek_r1: 4/4 = 100%

MEDIUM:
        gpt4o: 2/4 = 50%
            o3: 4/4 = 100%
   deepseek_r1: 4/4 = 100%

HARD:
        gpt4o: 0/4 = 0%
            o3: 4/4 = 100%
   deepseek_r1: 3/4 = 75%
```

!!! info "Difficulty Insight"
    All three models ace easy problems. The gap appears at medium difficulty (GPT-4o drops to 50%) and becomes dramatic on hard problems (GPT-4o: 0%, DeepSeek R1: 75%, o3: 100%). Reasoning models earn their keep on hard problems.

---

## Part 5: Speed vs Accuracy Trade-offs

### Step 5: Analyze response time by model

```python
# Average time per model
for model in ["gpt4o", "o3", "deepseek_r1"]:
    avg_time = bench[f"{model}_time_sec"].mean()
    print(f"{model:>12}: {avg_time:.1f}s average")

# Time vs accuracy scatter
print("\nProblem-level detail:")
for _, row in bench.iterrows():
    print(f"  {row['problem_id']} ({row['difficulty']:>6}): "
          f"GPT-4o={row['gpt4o_time_sec']:.1f}s "
          f"o3={row['o3_time_sec']:.1f}s "
          f"R1={row['deepseek_r1_time_sec']:.1f}s")
```

**Expected output:**

```
      gpt4o: 2.1s average
          o3: 7.1s average
 deepseek_r1: 5.4s average

Problem-level detail:
  P01 (  easy): GPT-4o=1.2s o3=3.5s R1=2.8s
  P02 (medium): GPT-4o=1.8s o3=4.2s R1=3.5s
  P03 (  hard): GPT-4o=2.5s o3=8.1s R1=6.5s
  ...
  P12 (  hard): GPT-4o=4.0s o3=15.0s R1=11.0s
```

!!! warning "Speed Trade-off"
    o3 is **3.4× slower** than GPT-4o on average (7.1s vs 2.1s). On the hardest problem (P12), o3 takes 15 seconds — acceptable for complex tasks, but too slow for real-time chat. Choose your model based on problem complexity, not blanket deployment.

---

## Part 6: Token Cost Analysis

### Step 6: Compare token usage

```python
# Average tokens per model
for model in ["gpt4o", "o3", "deepseek_r1"]:
    avg_tokens = bench[f"{model}_tokens"].mean()
    total_tokens = bench[f"{model}_tokens"].sum()
    print(f"{model:>12}: {avg_tokens:.0f} avg tokens, {total_tokens:,} total")

# Cost ratio (relative to GPT-4o)
gpt4o_total = bench["gpt4o_tokens"].sum()
for model in ["o3", "deepseek_r1"]:
    model_total = bench[f"{model}_tokens"].sum()
    ratio = model_total / gpt4o_total
    print(f"\n{model} uses {ratio:.1f}× more tokens than GPT-4o")
```

**Expected output:**

```
      gpt4o: 287 avg tokens, 3,440 total
          o3: 878 avg tokens, 10,530 total
 deepseek_r1: 725 avg tokens, 8,700 total

o3 uses 3.1× more tokens than GPT-4o
deepseek_r1 uses 2.5× more tokens than GPT-4o
```

The extra tokens come from chain-of-thought reasoning — the model is "thinking out loud" internally. This is the cost of higher accuracy.

---

## Part 7: When to Use Each Model

### Step 7: Decision framework

Based on the benchmark results, here's when to use each model:

| Scenario | Recommended Model | Why |
|----------|------------------|-----|
| Simple Q&A, FAQ | **GPT-4o** | 100% accuracy on easy problems, 3× faster, 3× cheaper |
| Multi-step reasoning | **o3** or **DeepSeek R1** | GPT-4o drops to 0% on hard problems |
| Cost-sensitive production | **DeepSeek R1** | 91.7% accuracy at 2.5× tokens (vs o3's 3.1×) |
| Maximum accuracy required | **o3** | 100% accuracy, but 3.4× slower and 3.1× more expensive |
| Real-time conversation | **GPT-4o** | 2.1s avg — reasoning models are too slow for chat |
| Code generation (complex) | **o3** | Thread-safe, concurrent code needs careful reasoning |
| Mathematical proofs | **o3** or **DeepSeek R1** | Both handle formal proofs; GPT-4o cannot |

```python
# Summary dashboard
print("""
╔══════════════════════════════════════════════════════╗
║      Reasoning Model Benchmark — Summary             ║
╠══════════════════════════════════════════════════════╣
║  Model        Accuracy   Avg Time   Avg Tokens       ║
║  ─────────    ────────   ────────   ──────────       ║
║  GPT-4o        50.0%      2.1s        287            ║
║  o3           100.0%      7.1s        878            ║
║  DeepSeek R1   91.7%      5.4s        725            ║
╠══════════════════════════════════════════════════════╣
║  Key Insight: Use GPT-4o for simple tasks,           ║
║  reasoning models for complex multi-step problems.   ║
╚══════════════════════════════════════════════════════╝
""")
```

---

## 🐛 Bug-Fix Exercise

The file `lab-060/broken_reasoning.py` has **3 bugs** in the benchmark analysis functions. Run the self-tests:

```bash
python lab-060/broken_reasoning.py
```

You should see **3 failed tests**:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Model accuracy calculation | Which column represents correctness — `_correct` or `_time_sec`? |
| Test 2 | Finding the fastest model | Should you use `min` or `max` to find the fastest? |
| Test 3 | Hard-problem accuracy | Which difficulty level are you filtering for? |

Fix all 3 bugs and re-run until you see `🎉 All 3 tests passed`.

---

## 📁 Supporting Files

```
lab-060/
├── reasoning_benchmark.csv    ← 12 problems × 3 models (accuracy, time, tokens)
└── broken_reasoning.py        ← Bug-fix exercise (3 bugs + self-tests)
```

**Quick start:**

```bash
pip install pandas
cd docs/docs/en/labs

# Follow along with the lab steps
python -c "import pandas; print('ready!')"

# Or fix the bugs
python lab-060/broken_reasoning.py
```

---

## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** When should you use a reasoning model instead of a standard model like GPT-4o?"

    - A) For all tasks — reasoning models are always better
    - B) For complex multi-step problems requiring logical reasoning, proofs, or planning
    - C) For real-time chat applications where speed is critical
    - D) For simple FAQ and classification tasks

    ??? success "✅ Reveal Answer"
        **Correct: B) For complex multi-step problems requiring logical reasoning, proofs, or planning**

        Reasoning models excel when problems require breaking down into steps, verifying intermediate results, or exploring multiple solution paths. GPT-4o achieves 100% on easy problems — reasoning models add no value there but cost 3× more. Reserve reasoning models for hard problems where GPT-4o's single-pass approach fails.

??? question "**Q2 (Multiple Choice):** What does the 'thinking budget' control in a reasoning model?"

    - A) The maximum number of API calls per minute
    - B) The total cost in dollars for a single request
    - C) How much reasoning the model does before producing a final answer
    - D) The maximum length of the output response

    ??? success "✅ Reveal Answer"
        **Correct: C) How much reasoning the model does before producing a final answer**

        The thinking budget controls the depth of the model's internal deliberation. A higher budget allows the model to explore more solution paths, verify intermediate steps more thoroughly, and backtrack when it detects errors. This produces more accurate results but consumes more tokens and takes more time.

??? question "**Q3 (Run the Lab):** What is o3's accuracy on the 12-problem benchmark?"

    Calculate `bench["o3_correct"].sum() / len(bench) * 100`.

    ??? success "✅ Reveal Answer"
        **100% (12/12)**

        o3 correctly solves all 12 problems across every category and difficulty level — including P12 (microservices migration plan), which is the only problem DeepSeek R1 fails. This perfect score comes at a cost: o3 averages 7.1 seconds and 878 tokens per problem.

??? question "**Q4 (Run the Lab):** What is GPT-4o's accuracy on the benchmark?"

    Calculate `bench["gpt4o_correct"].sum() / len(bench) * 100`.

    ??? success "✅ Reveal Answer"
        **50% (6/12)**

        GPT-4o correctly solves 6 of 12 problems. It gets all 4 easy problems right but fails on all 4 hard problems (P03, P06, P09, P12) and 2 medium problems (P08, P11). The failures span all categories — math, code, logic, and planning — confirming that the issue is reasoning depth, not domain knowledge.

??? question "**Q5 (Run the Lab):** Which model fails only on problem P12?"

    Check which model has `_correct == False` for exactly one problem, and that problem is P12.

    ??? success "✅ Reveal Answer"
        **DeepSeek R1**

        DeepSeek R1 achieves 91.7% accuracy (11/12), failing only on P12 — "Design a microservices migration plan for a monolith app." This is the hardest planning problem, requiring both deep technical knowledge and complex multi-step project planning. o3 solves it; GPT-4o fails on it plus 5 other problems.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| Reasoning Models | Extended thinking via chain-of-thought for complex problems |
| Thinking Budget | Controls reasoning depth — more budget = more accurate but slower |
| Accuracy | GPT-4o: 50%, DeepSeek R1: 91.7%, o3: 100% on 12-problem benchmark |
| Speed Trade-off | GPT-4o: 2.1s avg, DeepSeek R1: 5.4s, o3: 7.1s — reasoning costs time |
| Token Cost | Reasoning models use 2.5–3.1× more tokens than GPT-4o |
| Decision Framework | Use GPT-4o for simple tasks; reasoning models for hard multi-step problems |

---

## Next Steps

- **[Lab 059](lab-059-voice-agents-realtime.md)** — Voice Agents with GPT Realtime API (real-time interaction, different modality)
- **[Lab 043](lab-043-multimodal-agents.md)** — Multimodal Agents with GPT-4o Vision (another GPT-4o capability)
- **[Lab 038](lab-038-cost-optimization.md)** — Cost Optimization (applying the cost-performance trade-offs from this lab)
