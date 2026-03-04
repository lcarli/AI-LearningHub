---
tags: [structured-outputs, json-schema, pydantic, reliability, python]
---
# Lab 072: Structured Outputs — Guaranteed JSON for Agents

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~45 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Uses mock extraction data</span>
</div>

## What You'll Learn

- What **Structured Outputs** are and why agents need guaranteed JSON
- How JSON Schema enforcement differs from free-form "please return JSON" prompts
- Analyze extraction test results comparing schema-enforced vs. no-schema outputs
- Measure **schema validity rates** and **field accuracy** across input types
- Build a **reliability report** proving structured outputs eliminate parsing failures

## Introduction

When an agent extracts information from unstructured text — emails, invoices, resumes, support tickets — it needs to return **structured data** that downstream systems can parse reliably. Without schema enforcement, even the best models occasionally return malformed JSON, missing fields, or unexpected types.

**Structured Outputs** solve this by constraining the model's output to a JSON Schema at decoding time. The model literally *cannot* produce invalid JSON.

| Approach | Validity Guarantee | Field Accuracy | Parsing Failures |
|----------|-------------------|----------------|-----------------|
| Free-form prompt ("return JSON") | ❌ No guarantee | Variable | Common |
| JSON mode | ✅ Valid JSON | Variable | Rare |
| **Structured Outputs (JSON Schema)** | ✅ Valid + schema-compliant | High | **Zero** |

### The Scenario

You are a **Data Engineer** building an extraction pipeline for an insurance company. The pipeline processes 5 document types: emails, invoices, resumes, support tickets, and product reviews. You've run **15 extraction tests** — 10 with schema enforcement and 5 without — and need to prove that structured outputs are production-ready.

Your dataset (`structured_outputs.csv`) contains the results. Your job: analyze validity rates, field accuracy, and build the case for schema enforcement.

!!! info "Mock Data"
    This lab uses a mock test results CSV. The patterns mirror real-world behavior: schema-enforced outputs achieve near-perfect accuracy, while free-form outputs are inconsistent.

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Run the analysis scripts |
| `pandas` library | Data manipulation |

```bash
pip install pandas
```

---

## Step 1: Understand Structured Outputs

Structured Outputs work by providing a **JSON Schema** alongside your prompt. The model's decoder is constrained to only produce tokens that result in valid JSON matching the schema.

### Example Schema (Pydantic)

```python
from pydantic import BaseModel
from typing import List

class EmailExtraction(BaseModel):
    name: str
    email: str
    subject: str
    urgency: str  # "low", "medium", "high"

class InvoiceExtraction(BaseModel):
    vendor: str
    amount: float
    date: str
    line_items: List[str]
```

### How It Works

1. You define a JSON Schema (or Pydantic model)
2. You pass it to the API alongside your prompt
3. The model's token sampling is constrained to match the schema
4. The output is **guaranteed** to be valid JSON matching your schema — every field present, every type correct

!!! tip "Pydantic Integration"
    OpenAI's Python SDK can accept a Pydantic model directly via `response_format=EmailExtraction`. The SDK handles the schema conversion automatically.

---

## Step 2: Load and Explore the Test Results

The dataset has **15 extraction tests** — 10 with schema enforcement (`gpt-4o`) and 5 without (`gpt-4o-no-schema`):

```python
import pandas as pd

df = pd.read_csv("lab-072/structured_outputs.csv")

# Convert string booleans
for col in ["structured_output_valid", "json_parse_success"]:
    df[col] = df[col].astype(str).str.strip().str.lower() == "true"

print(f"Total tests: {len(df)}")
print(f"Models: {df['model'].unique().tolist()}")
print(f"Input types: {df['input_type'].unique().tolist()}")
print(f"\nFirst 5 rows:\n{df.head()}")
```

**Expected output:**

```
Total tests: 15
Models: ['gpt-4o', 'gpt-4o-no-schema']
Input types: ['email', 'invoice', 'resume', 'support_ticket', 'product_review']
```

---

## Step 3: Compare Schema Validity Rates

The `structured_output_valid` column indicates whether the output matched the expected schema (all fields present, correct types):

```python
schema_rows = df[df["model"] == "gpt-4o"]
no_schema_rows = df[df["model"] == "gpt-4o-no-schema"]

schema_valid_rate = schema_rows["structured_output_valid"].mean() * 100
no_schema_valid_rate = no_schema_rows["structured_output_valid"].mean() * 100

print(f"Schema-enforced validity rate:  {schema_valid_rate:.0f}%")
print(f"No-schema validity rate:        {no_schema_valid_rate:.0f}%")
```

**Expected output:**

```
Schema-enforced validity rate:  100%
No-schema validity rate:        0%
```

!!! tip "Insight"
    **100% vs. 0%** — this is the entire argument for structured outputs. With schema enforcement, every single extraction passes validation. Without it, *none* do (some may parse as JSON, but fields are missing or types are wrong).

---

## Step 4: Analyze Field Accuracy

Even when JSON is valid, the extracted *values* may not be accurate. The `field_accuracy_pct` column measures how many fields had the correct value:

```python
schema_accuracy = schema_rows["field_accuracy_pct"].mean()
no_schema_accuracy = no_schema_rows["field_accuracy_pct"].mean()

print(f"Avg field accuracy (with schema):    {schema_accuracy:.0f}%")
print(f"Avg field accuracy (without schema): {no_schema_accuracy:.0f}%")
```

**Expected output:**

```
Avg field accuracy (with schema):    98%
Avg field accuracy (without schema): 68%
```

Break it down by input type:

```python
accuracy_by_type = df.groupby(["input_type", "model"])["field_accuracy_pct"].mean().unstack()
print(accuracy_by_type.round(1))
```

```python
# Which input types show the biggest accuracy gap?
for input_type in df["input_type"].unique():
    schema_acc = df[(df["input_type"] == input_type) & (df["model"] == "gpt-4o")]["field_accuracy_pct"].mean()
    no_schema_acc = df[(df["input_type"] == input_type) & (df["model"] == "gpt-4o-no-schema")]["field_accuracy_pct"].mean()
    gap = schema_acc - no_schema_acc if not pd.isna(no_schema_acc) else 0
    print(f"  {input_type:>20s}: schema={schema_acc:.0f}%  no-schema={no_schema_acc:.0f}%  gap={gap:.0f}pp")
```

---

## Step 5: Measure Latency and Token Usage

Schema enforcement has a small overhead — the model must conform to constraints during decoding:

```python
for model in df["model"].unique():
    subset = df[df["model"] == model]
    avg_time = subset["time_ms"].mean()
    avg_tokens = subset["tokens"].mean()
    print(f"{model:>20s}: avg_time={avg_time:.0f}ms  avg_tokens={avg_tokens:.0f}")
```

**Expected output:**

```
           gpt-4o: avg_time=915ms  avg_tokens=139
  gpt-4o-no-schema: avg_time=660ms  avg_tokens=121
```

!!! warning "Latency Trade-off"
    Schema-enforced outputs are ~38% slower on average. This is expected — constrained decoding requires additional processing. For most agent workflows, the reliability guarantee far outweighs the latency cost.

---

## Step 6: Build the Reliability Report

```python
report = f"""# 📊 Structured Outputs Reliability Report

## Test Summary
| Metric | With Schema | Without Schema |
|--------|-------------|----------------|
| Tests Run | {len(schema_rows)} | {len(no_schema_rows)} |
| Schema Valid | {schema_valid_rate:.0f}% | {no_schema_valid_rate:.0f}% |
| Avg Field Accuracy | {schema_accuracy:.0f}% | {no_schema_accuracy:.0f}% |
| Avg Latency | {schema_rows['time_ms'].mean():.0f}ms | {no_schema_rows['time_ms'].mean():.0f}ms |
| Avg Tokens | {schema_rows['tokens'].mean():.0f} | {no_schema_rows['tokens'].mean():.0f} |

## Conclusion
Structured Outputs deliver **{schema_valid_rate:.0f}% schema validity** vs. {no_schema_valid_rate:.0f}%
without enforcement. Field accuracy improves from {no_schema_accuracy:.0f}% to {schema_accuracy:.0f}%.

**Recommendation:** Enable Structured Outputs for all extraction pipelines.
The ~38% latency overhead is justified by zero parsing failures in production.
"""

print(report)

with open("lab-072/reliability_report.md", "w") as f:
    f.write(report)
print("💾 Saved to lab-072/reliability_report.md")
```

---

## 🐛 Bug-Fix Exercise

The file `lab-072/broken_structured.py` contains **3 bugs** that produce incorrect metrics. Can you find and fix them all?

Run the self-tests to see which ones fail:

```bash
python lab-072/broken_structured.py
```

You should see **3 failed tests**. Each test corresponds to one bug:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Schema success rate metric | Should check `structured_output_valid`, not `json_parse_success` |
| Test 2 | No-schema accuracy | Should filter by the no-schema model, not the schema model |
| Test 3 | Average tokens per model | Should filter by model before averaging |

Fix all 3 bugs, then re-run. When you see `All passed!`, you're done!

---

## 📁 Supporting Files

- 📥 [broken_structured.py](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-072/broken_structured.py)
- 📥 [structured_outputs.csv](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-072/structured_outputs.csv)

```
lab-072/
├── structured_outputs.csv     ← 15 extraction tests (10 schema + 5 no-schema)
└── broken_structured.py       ← Bug-fix exercise (3 bugs + self-tests)
```

**Quick start:**

```bash
pip install pandas
cd docs/docs/en/labs

# Option A: Follow along with the lab steps (copy-paste code)
python -c "import pandas; print('pandas ready!')"

# Option B: Fix the bugs
python lab-072/broken_structured.py
```

---

## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What distinguishes Structured Outputs from regular JSON mode?"

    - A) Structured Outputs are faster than JSON mode
    - B) Structured Outputs guarantee the output matches a specific JSON Schema, not just valid JSON
    - C) Structured Outputs work without an API key
    - D) Structured Outputs use a different model architecture

    ??? success "✅ Reveal Answer"
        **Correct: B) Structured Outputs guarantee the output matches a specific JSON Schema, not just valid JSON**

        JSON mode ensures valid JSON syntax (proper brackets, quotes, etc.), but the *structure* — which fields exist, their types, nesting — is not enforced. Structured Outputs constrain the decoder to match a specific schema, guaranteeing every field is present with the correct type.

??? question "**Q2 (Multiple Choice):** Which Python library integrates most seamlessly with OpenAI's Structured Outputs for schema definition?"

    - A) dataclasses
    - B) marshmallow
    - C) Pydantic
    - D) attrs

    ??? success "✅ Reveal Answer"
        **Correct: C) Pydantic**

        OpenAI's Python SDK directly accepts Pydantic `BaseModel` subclasses via the `response_format` parameter. The SDK converts the Pydantic model to a JSON Schema automatically, making schema definition as simple as writing a Python class.

??? question "**Q3 (Run the Lab):** What is the schema validity rate for schema-enforced extraction tests?"

    Run the Step 3 analysis on `structured_outputs.csv` and check the results.

    ??? success "✅ Reveal Answer"
        **100%**

        All 10 schema-enforced tests (`model=gpt-4o`) have `structured_output_valid=true`. The constrained decoder guarantees that every output matches the defined JSON Schema — zero parsing or validation failures.

??? question "**Q4 (Run the Lab):** What is the schema validity rate for tests **without** schema enforcement?"

    Run the Step 3 analysis to compare.

    ??? success "✅ Reveal Answer"
        **0%**

        All 5 no-schema tests (`model=gpt-4o-no-schema`) have `structured_output_valid=false`. Even though some produce parseable JSON (`json_parse_success=true`), they fail schema validation because fields are missing, have wrong types, or use unexpected key names.

??? question "**Q5 (Run the Lab):** What is the average field accuracy for schema-enforced tests (gpt-4o rows)?"

    Run the Step 4 analysis to calculate it.

    ??? success "✅ Reveal Answer"
        **98%**

        The 10 schema-enforced tests have field accuracies of 100, 100, 100, 95, 100, 90, 100, 100, 100, and 95. The mean is (100+100+100+95+100+90+100+100+100+95) ÷ 10 = **98%**.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| Structured Outputs | JSON Schema-constrained decoding that guarantees valid output |
| Schema Validity | 100% with enforcement vs. 0% without — eliminates parsing failures |
| Field Accuracy | 98% with schema vs. 68% without — structure improves content accuracy |
| Pydantic Integration | Define schemas as Python classes for seamless API integration |
| Latency Trade-off | ~38% overhead is justified by production reliability |
| Production Readiness | Zero parsing failures makes structured outputs essential for pipelines |

---

## Next Steps

- **[Lab 018](lab-018-function-calling.md)** — Function Calling (the foundation for tool-using agents)
- **[Lab 017](lab-017-structured-output.md)** — Structured Output deep-dive (complementary theory)
- **[Lab 071](lab-071-context-caching.md)** — Context Caching (cost optimization for schema-heavy workflows)
- **[Lab 073](lab-073-swe-bench.md)** — Agent Benchmarking with SWE-bench (evaluate agent quality)
