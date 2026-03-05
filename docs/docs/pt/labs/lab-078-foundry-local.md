---
tags: [foundry-local, local-inference, free, ollama-alternative, python]
---
# Lab 078: Foundry Local — Run AI Models Offline

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-100">L100</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~45 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Runs entirely on local hardware</span>
</div>

!!! info "Tradução em andamento"
    Este lab ainda está sendo traduzido. O conteúdo abaixo está em inglês.



## What You'll Learn

- What **Foundry Local** is and how it enables offline AI model inference
- How to install and run models with `winget` and the `foundry` CLI
- How the **OpenAI-compatible API** makes Foundry Local a drop-in replacement
- Analyze a **model catalog** of 8 models — comparing sizes, hardware requirements, and quality
- Identify the **smallest model** and which models support **CPU-only** inference

## Introduction

**Foundry Local** is Microsoft's local inference runtime that lets you run AI models entirely on your own hardware — no cloud, no API keys, no internet required. It's a free alternative to Ollama, optimized for Windows with DirectML GPU acceleration.

### Installation

```bash
winget install Microsoft.FoundryLocal
```

### Running a Model

```bash
foundry model run phi-4-mini
```

This downloads the model (if needed) and starts a local server with an **OpenAI-compatible API** at `http://localhost:5273`:

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:5273/v1", api_key="not-needed")

response = client.chat.completions.create(
    model="phi-4-mini",
    messages=[{"role": "user", "content": "Explain quantum computing in 2 sentences."}]
)
print(response.choices[0].message.content)
```

### The Scenario

You are a **DevOps Engineer** evaluating Foundry Local for air-gapped (offline) deployments. You have a catalog of **8 models** (`foundry_models.csv`) with size, hardware requirements, and quality benchmarks. Your job: analyze the catalog, find the best model for different hardware profiles, and build a deployment recommendation.

!!! info "Mock Data"
    This lab uses a mock model catalog CSV. The model names and sizes are representative of the models available in Foundry Local's catalog as of early 2026.

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
    Save all files to a `lab-078/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_foundry_local.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-078/broken_foundry_local.py) |
| `foundry_models.csv` | 8-model catalog with sizes, hardware, and quality scores | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-078/foundry_models.csv) |

---

## Step 1: Understand the Model Catalog

Each model in the catalog has these attributes:

| Column | Description |
|--------|-----------|
| **model_name** | Model identifier (e.g., `phi-4-mini`, `qwen2.5-0.5b`) |
| **size_gb** | Download size in gigabytes |
| **parameters** | Number of model parameters (e.g., `3.8B`, `0.5B`) |
| **hardware** | Required hardware: `cpu_only`, `gpu_recommended`, or `gpu_required` |
| **quality_score** | Benchmark quality score (0.0–1.0) |
| **use_case** | Primary use case: `chat`, `coding`, `embedding`, or `general` |
| **quantization** | Quantization level: `q4`, `q8`, or `fp16` |

---

## Step 2: Load and Explore the Catalog

```python
import pandas as pd

df = pd.read_csv("lab-078/foundry_models.csv")

print(f"Total models: {len(df)}")
print(f"Hardware requirements: {df['hardware'].value_counts().to_dict()}")
print(f"Use cases: {df['use_case'].value_counts().to_dict()}")
print(f"\nFull catalog:")
print(df[["model_name", "size_gb", "parameters", "hardware", "quality_score"]].to_string(index=False))
```

**Expected output:**

```
Total models: 8
Hardware requirements: {'gpu_recommended': 4, 'cpu_only': 2, 'gpu_required': 2}
Use cases: {'chat': 3, 'coding': 2, 'general': 2, 'embedding': 1}
```

---

## Step 3: Find the Smallest Model

```python
smallest = df.loc[df["size_gb"].idxmin()]
largest = df.loc[df["size_gb"].idxmax()]

print(f"Smallest model: {smallest['model_name']} ({smallest['size_gb']} GB)")
print(f"  Parameters: {smallest['parameters']}")
print(f"  Hardware: {smallest['hardware']}")
print(f"  Quality: {smallest['quality_score']}")

print(f"\nLargest model: {largest['model_name']} ({largest['size_gb']} GB)")
print(f"  Parameters: {largest['parameters']}")
print(f"  Hardware: {largest['hardware']}")
print(f"  Quality: {largest['quality_score']}")

print(f"\nSize range: {smallest['size_gb']} GB – {largest['size_gb']} GB")
```

**Expected output:**

```
Smallest model: qwen2.5-0.5b (0.4 GB)
  Parameters: 0.5B
  Hardware: cpu_only
  Quality: 0.52
```

!!! tip "Edge Deployment"
    **qwen2.5-0.5b** at just **0.4 GB** is ideal for edge devices, IoT gateways, or machines with minimal storage. Despite its small size, it handles basic chat and summarization tasks reasonably well.

---

## Step 4: Identify CPU-Only Models

For air-gapped machines without GPUs:

```python
cpu_models = df[df["hardware"] == "cpu_only"]
print(f"CPU-only models: {len(cpu_models)}\n")
for _, row in cpu_models.iterrows():
    print(f"  {row['model_name']:>20s}  size={row['size_gb']}GB  quality={row['quality_score']}  use_case={row['use_case']}")
```

```python
# Compare CPU-only vs GPU models
gpu_models = df[df["hardware"] != "cpu_only"]
print(f"\nCPU-only avg quality: {cpu_models['quality_score'].mean():.2f}")
print(f"GPU models avg quality: {gpu_models['quality_score'].mean():.2f}")
print(f"Quality gap: {(gpu_models['quality_score'].mean() - cpu_models['quality_score'].mean()) * 100:.1f}pp")
```

!!! warning "Quality Trade-off"
    CPU-only models are smaller and run anywhere, but their quality scores are typically lower than GPU models. For production use cases requiring high accuracy, prefer GPU-recommended models with at least 4 GB VRAM.

---

## Step 5: Analyze by Use Case

```python
print("Models by use case:\n")
for use_case, group in df.groupby("use_case"):
    print(f"  {use_case.upper()} ({len(group)} models):")
    for _, row in group.iterrows():
        print(f"    {row['model_name']:>20s}  {row['size_gb']}GB  quality={row['quality_score']}")
    print()

# Best model per use case
print("Best model per use case (by quality):")
for use_case, group in df.groupby("use_case"):
    best = group.loc[group["quality_score"].idxmax()]
    print(f"  {use_case:>10s}: {best['model_name']} (quality={best['quality_score']}, size={best['size_gb']}GB)")
```

---

## Step 6: Build the Deployment Recommendation

```python
report = f"""# 📋 Foundry Local Deployment Recommendation

## Catalog Summary
| Metric | Value |
|--------|-------|
| Total Models | {len(df)} |
| CPU-Only | {len(cpu_models)} |
| GPU Recommended | {len(df[df['hardware'] == 'gpu_recommended'])} |
| GPU Required | {len(df[df['hardware'] == 'gpu_required'])} |
| Smallest | {smallest['model_name']} ({smallest['size_gb']} GB) |
| Largest | {largest['model_name']} ({largest['size_gb']} GB) |

## Hardware Profiles

### Profile A: Edge Device (CPU only, 2 GB storage)
"""

for _, row in cpu_models.iterrows():
    report += f"- **{row['model_name']}** — {row['size_gb']} GB, quality {row['quality_score']}\n"

report += f"""
### Profile B: Developer Laptop (GPU, 16 GB storage)
"""

for _, row in df[df["hardware"] == "gpu_recommended"].iterrows():
    report += f"- **{row['model_name']}** — {row['size_gb']} GB, quality {row['quality_score']}\n"

report += f"""
### Profile C: Workstation (High-end GPU, 64 GB storage)
"""

for _, row in df[df["hardware"] == "gpu_required"].iterrows():
    report += f"- **{row['model_name']}** — {row['size_gb']} GB, quality {row['quality_score']}\n"

print(report)

with open("lab-078/deployment_recommendation.md", "w") as f:
    f.write(report)
print("💾 Saved to lab-078/deployment_recommendation.md")
```

---

## 🐛 Bug-Fix Exercise

The file `lab-078/broken_foundry_local.py` contains **3 bugs** that produce incorrect model analysis. Can you find and fix them all?

Run the self-tests to see which ones fail:

```bash
python lab-078/broken_foundry_local.py
```

You should see **3 failed tests**. Each test corresponds to one bug:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Smallest model name | Should find min `size_gb`, not max |
| Test 2 | CPU-only model count | Should filter `hardware == "cpu_only"`, not `"gpu_required"` |
| Test 3 | Total model count | Should use `len(df)`, not a hardcoded value |

Fix all 3 bugs, then re-run. When you see `All passed!`, you're done!

---


## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What makes Foundry Local different from cloud-based AI services?"

    - A) It only supports Microsoft models
    - B) It runs AI models entirely on local hardware with no internet required
    - C) It requires an Azure subscription
    - D) It only works on Linux

    ??? success "✅ Reveal Answer"
        **Correct: B) It runs AI models entirely on local hardware with no internet required**

        Foundry Local is a local inference runtime — models are downloaded once and run entirely offline. It uses an OpenAI-compatible API, making it a drop-in replacement for cloud endpoints. No API keys, no internet, no per-token costs.

??? question "**Q2 (Multiple Choice):** Why does Foundry Local use an OpenAI-compatible API?"

    - A) It's built by OpenAI
    - B) It enables drop-in replacement — existing code that calls OpenAI APIs works without changes
    - C) OpenAI requires all inference engines to use their API format
    - D) It only runs OpenAI models

    ??? success "✅ Reveal Answer"
        **Correct: B) It enables drop-in replacement — existing code that calls OpenAI APIs works without changes**

        By exposing the same `/v1/chat/completions` endpoint format, Foundry Local lets developers switch from cloud to local inference by changing only the `base_url`. All existing SDKs, tools, and frameworks that speak the OpenAI API format work immediately.

??? question "**Q3 (Run the Lab):** What is the smallest model in the catalog, and how large is it?"

    Run the Step 3 analysis on [📥 `foundry_models.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-078/foundry_models.csv) to find the smallest model.

    ??? success "✅ Reveal Answer"
        **qwen2.5-0.5b at 0.4 GB**

        The smallest model in the catalog is **qwen2.5-0.5b** with only **0.4 GB** download size and 0.5B parameters. It runs on CPU only and achieves a quality score of 0.52 — suitable for basic chat and edge deployments.

??? question "**Q4 (Run the Lab):** How many models support CPU-only inference?"

    Run the Step 4 analysis to filter models with `hardware == "cpu_only"`.

    ??? success "✅ Reveal Answer"
        **2 models**

        Only **2 models** support CPU-only inference. These are the smallest models in the catalog, optimized with aggressive quantization (q4) to run without GPU acceleration. They're ideal for edge devices and air-gapped environments.

??? question "**Q5 (Run the Lab):** How many total models are available in the Foundry Local catalog?"

    Load the CSV and check the total row count.

    ??? success "✅ Reveal Answer"
        **8 models**

        The Foundry Local catalog includes **8 models** across 4 use cases: chat (3), coding (2), general (2), and embedding (1). Hardware requirements range from CPU-only to GPU-required.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| Foundry Local | Microsoft's local inference runtime — free, offline, no API keys |
| Installation | `winget install Microsoft.FoundryLocal` + `foundry model run` |
| OpenAI Compatibility | Drop-in replacement via `http://localhost:5273/v1` |
| Model Catalog | 8 models from 0.4 GB to multi-GB, CPU to GPU-required |
| Smallest Model | qwen2.5-0.5b at 0.4 GB — runs on CPU, ideal for edge |
| Hardware Profiles | CPU-only (2 models), GPU-recommended (4), GPU-required (2) |

---

## Next Steps

- **[Lab 074](lab-074-foundry-agent-service.md)** — Foundry Agent Service (deploy agents using Foundry models)
- **[Lab 071](lab-071-context-caching.md)** — Context Caching (optimize local inference with prompt caching)
- **[Lab 038](lab-038-cost-optimization.md)** — AI Cost Optimization (compare local vs. cloud inference costs)
- **[Lab 076](lab-076-microsoft-agent-framework.md)** — Microsoft Agent Framework (use Foundry Local as the inference backend for MAF agents)
