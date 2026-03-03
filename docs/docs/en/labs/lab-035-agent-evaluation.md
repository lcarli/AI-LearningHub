---
tags: [evaluation, python, free, github-models]
---
# Lab 035: Agent Evaluation with Azure AI Eval SDK

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Path:</strong> <a href="../paths/pro-code/">Pro Code</a></span>
  <span><strong>Time:</strong> ~60 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-github">GitHub Free</span> — uses GitHub Models for evaluation</span>
</div>

## What You'll Learn

- Why **LLM-as-judge** evaluation works and when to use it
- Measure **groundedness**, **relevance**, **coherence**, and **fluency**
- Build a **golden dataset** for regression testing
- Evaluate your RAG agent automatically with `azure-ai-evaluation` SDK
- Track quality metrics over time and detect regressions

---

## Introduction

How do you know if your agent got better or worse after a change? Manual testing doesn't scale.

**LLM-as-judge evaluation** uses a second, independent LLM to score your agent's answers against criteria like:

- **Groundedness** — Is the answer supported by the retrieved documents?
- **Relevance** — Does the answer address what the user asked?
- **Coherence** — Is the answer logically structured?
- **Fluency** — Is the grammar correct?

This lab builds an automated evaluation pipeline for the OutdoorGear assistant.

---

## Prerequisites

- Python 3.11+
- `pip install azure-ai-evaluation openai`
- `GITHUB_TOKEN` set

---

## Lab Exercise

### Step 1: Install the evaluation SDK

```bash
pip install azure-ai-evaluation openai
```

### Step 2: Create a golden dataset

A **golden dataset** is a set of test questions with known-good answers. Create `eval_dataset.jsonl`:

```jsonl
{"query": "What is the return policy?", "response": "We offer a 60-day return window. Items must be unused in original packaging.", "context": "60-day return window. Items must be unused in original packaging. Worn footwear non-refundable unless defective."}
{"query": "Do you sell waterproof jackets?", "response": "Yes, we have the StormShell Jacket at $349 — a 3-layer Gore-Tex Pro shell.", "context": "StormShell Jacket ($349): 3-layer Gore-Tex Pro shell. 20k/20k waterproof rating."}
{"query": "How long does standard shipping take?", "response": "Standard shipping takes 3-5 business days and costs $5.99.", "context": "Standard $5.99 (3-5 days). Express $14.99 (1-2 days). Free on orders $75+."}
{"query": "What is the capital of France?", "response": "Paris is the capital of France.", "context": "OutdoorGear Inc. sells outdoor equipment including tents, boots, and apparel."}
{"query": "Tell me about the TrailBlazer X200", "response": "The TrailBlazer X200 is a waterproof hiking boot with Vibram outsole, priced at $189.99.", "context": "TrailBlazer X200 ($189.99): Waterproof Gore-Tex hiking boot. Vibram outsole. 3-season rated."}
```

Note the 4th entry — the agent answers a question unrelated to the knowledge base. Groundedness evaluation should flag this.

### Step 3: Run built-in evaluators

```python
# evaluate_agent.py
import os, json
from pathlib import Path
from azure.ai.evaluation import (
    GroundednessEvaluator,
    RelevanceEvaluator,
    CoherenceEvaluator,
    FluencyEvaluator,
)

# Use GitHub Models as the judge LLM
model_config = {
    "azure_endpoint": "https://models.inference.ai.azure.com",
    "api_key": os.environ["GITHUB_TOKEN"],
    "azure_deployment": "gpt-4o",
    "api_version": "2024-02-01",
}

# Initialize evaluators
groundedness = GroundednessEvaluator(model_config=model_config)
relevance    = RelevanceEvaluator(model_config=model_config)
coherence    = CoherenceEvaluator(model_config=model_config)
fluency      = FluencyEvaluator(model_config=model_config)

# Load dataset
dataset = [
    json.loads(line)
    for line in Path("eval_dataset.jsonl").read_text().splitlines()
    if line.strip()
]

results = []
for i, item in enumerate(dataset, 1):
    query    = item["query"]
    response = item["response"]
    context  = item["context"]

    print(f"Evaluating {i}/{len(dataset)}: {query[:50]}...")

    scores = {
        "query":        query,
        "response":     response[:80] + "...",
        "groundedness": groundedness(query=query, response=response, context=context)["groundedness"],
        "relevance":    relevance(query=query,    response=response, context=context)["relevance"],
        "coherence":    coherence(query=query,    response=response)["coherence"],
        "fluency":      fluency(response=response)["fluency"],
    }
    results.append(scores)

# Print report
print("\n" + "="*80)
print(f"{'Query':<45} {'Ground':>7} {'Relev':>6} {'Coher':>6} {'Fluency':>8}")
print("-"*80)
for r in results:
    print(
        f"{r['query'][:44]:<45} "
        f"{r['groundedness']:>7.1f} "
        f"{r['relevance']:>6.1f} "
        f"{r['coherence']:>6.1f} "
        f"{r['fluency']:>8.1f}"
    )

# Summary
print("="*80)
for metric in ["groundedness", "relevance", "coherence", "fluency"]:
    avg = sum(r[metric] for r in results) / len(results)
    status = "✅" if avg >= 3.5 else "⚠️" if avg >= 2.5 else "❌"
    print(f"{status} Avg {metric:15}: {avg:.2f}/5.0")
```

```bash
python evaluate_agent.py
```

Expected output:
```
============================================================
Query                                         Ground  Relev  Coher  Fluency
------------------------------------------------------------
What is the return policy?                       4.0    5.0    5.0      5.0
Do you sell waterproof jackets?                  5.0    5.0    4.0      5.0
How long does standard shipping take?            5.0    5.0    5.0      5.0
What is the capital of France?                   1.0    1.0    4.0      5.0  ← flagged!
Tell me about the TrailBlazer X200               5.0    5.0    5.0      5.0
============================================================
✅ Avg groundedness    : 4.00/5.0
✅ Avg relevance       : 4.20/5.0
✅ Avg coherence       : 4.60/5.0
✅ Avg fluency         : 5.00/5.0
```

The Paris question is correctly flagged with low groundedness (1.0) — the answer is not supported by the OutdoorGear context.

### Step 4: Build a custom evaluator

Sometimes you need domain-specific criteria. Here's a custom evaluator for **price accuracy**:

```python
# custom_evaluator.py
from azure.ai.evaluation import PromptTemplateEvaluator

PRICE_ACCURACY_TEMPLATE = """
You are evaluating whether an AI assistant correctly stated product prices.

Query: {{query}}
Response: {{response}}
Ground truth context: {{context}}

Score the price accuracy from 1-5:
- 5: All prices mentioned are exactly correct
- 4: Prices are approximately correct (within 10%)
- 3: Some prices correct, some missing
- 2: Prices are wrong or made up
- 1: No prices when prices were relevant, or completely wrong prices

Return a JSON object: {"price_accuracy": <score>, "reason": "<brief explanation>"}
"""

price_evaluator = PromptTemplateEvaluator(
    prompt_template=PRICE_ACCURACY_TEMPLATE,
    model_config=model_config,
    result_key="price_accuracy",
)

# Test it
result = price_evaluator(
    query="How much is the TrailBlazer X200?",
    response="The TrailBlazer X200 costs $189.99.",
    context="TrailBlazer X200 ($189.99): Waterproof Gore-Tex hiking boot."
)
print(f"Price accuracy score: {result['price_accuracy']}")
```

### Step 5: Automate in CI/CD

Add this to your GitHub Actions workflow (see [Lab 037](lab-037-cicd-github-actions.md)):

```yaml
- name: Evaluate agent quality
  run: |
    pip install azure-ai-evaluation openai
    python evaluate_agent.py | tee eval_report.txt
    # Fail if avg groundedness < 3.5
    python -c "
    import json, sys
    results = [json.loads(l) for l in open('eval_results.jsonl')]
    avg_g = sum(r['groundedness'] for r in results) / len(results)
    print(f'Avg groundedness: {avg_g:.2f}')
    sys.exit(0 if avg_g >= 3.5 else 1)
    "
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## Evaluation Metrics Reference

| Metric | What it measures | Good score |
|--------|-----------------|------------|
| Groundedness | Answer supported by context | ≥ 4.0 |
| Relevance | Answers the user's question | ≥ 4.0 |
| Coherence | Logical, well-structured | ≥ 4.0 |
| Fluency | Grammatically correct | ≥ 4.5 |

Scores are 1–5. Below 3.0 on groundedness usually indicates hallucination.

---

## 📁 Supporting Files

```
lab-035/
└── eval_dataset.jsonl    ← 20 OutdoorGear Q&A pairs for evaluation
```

Each line is a JSON object with `query`, `ground_truth`, `category`, and `product_ids`. The dataset covers product recommendations, pricing, comparisons, and an out-of-scope test case.

**Load it in Python:**
```python
import json

with open("lab-035/eval_dataset.jsonl") as f:
    dataset = [json.loads(line) for line in f]

print(f"Loaded {len(dataset)} evaluation examples")
# Categories: tents, sleeping_bags, backpacks, pricing, recommendations, out_of_scope
categories = set(d["category"] for d in dataset)
print(f"Categories: {categories}")
```

---

## 🧠 Knowledge Check

??? question "**Q1 (Run the Lab):** Load `lab-035/eval_dataset.jsonl` in Python. How many examples are in the dataset, and how many are in the `out_of_scope` category?"

    Run the loader code from the Supporting Files section above.

    ??? success "✅ Reveal Answer"
        **20 total examples. 1 example is in the `out_of_scope` category.**

        The dataset has exactly 20 lines. Run `sum(1 for d in dataset if d["category"] == "out_of_scope")` to confirm there is 1 out-of-scope example. That example tests whether your agent correctly refuses to answer questions unrelated to outdoor gear.

??? question "**Q2 (Run the Lab):** For the single `out_of_scope` example in `eval_dataset.jsonl`, what is the value of the `product_ids` field?"

    Load the dataset and filter for `category == "out_of_scope"`. Print the `product_ids` field.

    ??? success "✅ Reveal Answer"
        **`[]` (empty list)**

        The out-of-scope example has `"product_ids": []` because the question is not about any specific product — it's testing whether the agent refuses to answer irrelevant questions (like asking for cooking recipes). A well-designed agent should return a refusal message rather than hallucinating an answer. Your evaluation metric should check that the agent's `groundedness` score is high and it does NOT reference any product IDs.

??? question "**Q3 (Multiple Choice):** How many examples in `eval_dataset.jsonl` are in the `tents` category?"

    - A) 3
    - B) 5
    - C) 7
    - D) 4

    ??? success "✅ Reveal Answer"
        **Correct: B — 5 examples**

        The `tents` category has 5 examples, making it the largest single category. Run `sum(1 for d in dataset if d["category"] == "tents")` to confirm. The full breakdown: tents(5), backpacks(4), sleeping_bags(3), pricing(3), recommendations(3), out_of_scope(1), comparisons(1).

---

## Next Steps

- **CI/CD for agents:** → [Lab 037 — GitHub Actions for AI Agents](lab-037-cicd-github-actions.md)
- **Enterprise RAG evaluation:** → [Lab 042 — Enterprise RAG with Evaluations](lab-042-enterprise-rag.md)
