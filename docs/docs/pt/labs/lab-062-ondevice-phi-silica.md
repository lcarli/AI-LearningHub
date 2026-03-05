---
tags: [on-device, phi-silica, windows-ai, npu, edge-ai, csharp]
---
# Lab 062: On-Device Agents with Phi Silica — Windows AI APIs

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Path:</strong> All paths</span>
  <span><strong>Time:</strong> ~90 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Uses mock benchmark data (no NPU hardware required)</span>
</div>

!!! info "Tradução em andamento"
    Este lab ainda está sendo traduzido. O conteúdo abaixo está em inglês.



## What You'll Learn

- How **Windows AI APIs** enable on-device inference using the Neural Processing Unit (NPU)
- What **Phi Silica** is — a model optimized for Windows NPU hardware
- Compare **NPU vs cloud** latency for agent skills (summarize, classify, rewrite, text_to_table)
- Handle **NPU unavailability** gracefully with cloud fallback strategies
- Measure **quality match rates** between on-device and cloud inference
- Build agents that work **offline-first** with intelligent degradation

---

## Introduction

Cloud-based AI is powerful, but it requires internet connectivity, introduces latency, and sends data off-device. **Windows AI APIs** with **Phi Silica** bring inference directly to the NPU (Neural Processing Unit) — a dedicated AI accelerator built into modern Windows devices.

On-device inference means: zero network latency, full data privacy, offline capability, and no per-token cost. The trade-off is that not every task can run on the NPU, and quality may differ from cloud models. This lab measures exactly where on-device inference shines and where you need cloud fallback.

### The Benchmark

You'll analyze **15 tasks** across 4 categories, comparing NPU (Phi Silica) vs cloud inference:

| Category | Count | Example |
|----------|-------|---------|
| **Summarize** | 4 | Meeting transcript, article, email thread, policy doc |
| **Classify** | 4 | Sentiment, intent, priority, language detection |
| **Rewrite** | 4 | Tone adjustment, simplification, formalization, translation |
| **Text-to-table** | 3 | Extract structured data from unstructured text |

---

## Prerequisites

```bash
pip install pandas
```

This lab analyzes pre-computed benchmark results — no NPU hardware, Windows AI SDK, or C# toolchain required. To run live on-device inference, you would need a Copilot+ PC with NPU and the Windows AI APIs.

---

!!! tip "Quick Start with GitHub Codespaces"
    [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/lcarli/AI-LearningHub?quickstart=1)

    All dependencies are pre-installed in the devcontainer.


## 📦 Supporting Files

!!! note "Download these files before starting the lab"
    Save all files to a `lab-062/` folder in your working directory.

| File | Description | Download |
|------|-------------|----------|
| `broken_ondevice.py` | Bug-fix exercise (3 bugs + self-tests) | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-062/broken_ondevice.py) |
| `ondevice_tasks.csv` | Dataset | [📥 Download](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-062/ondevice_tasks.csv) |

---

## Part 1: Understanding On-Device Inference

### Step 1: NPU architecture

The Neural Processing Unit (NPU) is a dedicated AI accelerator designed for efficient matrix operations:

```
Cloud Inference:
  App → [Network] → [Cloud GPU] → [Network] → Response
  Latency: ~800-1200ms

NPU Inference (Phi Silica):
  App → [Local NPU] → Response
  Latency: ~50-120ms
```

Key concepts:

| Concept | Description |
|---------|-------------|
| **NPU** | Neural Processing Unit — dedicated AI hardware in modern CPUs |
| **Phi Silica** | Microsoft's model optimized for Windows NPU execution |
| **Windows AI APIs** | System-level APIs for on-device AI inference |
| **Readiness check** | API to verify NPU availability before attempting inference |
| **Graceful fallback** | Strategy to fall back to cloud when NPU is unavailable |

!!! info "Phi Silica vs Phi-4 Mini"
    Phi Silica is specifically optimized for Windows NPU hardware — it's not just a smaller model, but one designed for the NPU's architecture. Phi-4 Mini (Lab 061) runs via ONNX Runtime on CPU/GPU. Both offer on-device inference but target different hardware paths.

---

## Part 2: Load Benchmark Data

### Step 2: Load [📥 `ondevice_tasks.csv`](https://github.com/lcarli/AI-LearningHub/raw/main/docs/docs/en/labs/lab-062/ondevice_tasks.csv)

The benchmark dataset contains results from running 15 tasks through NPU and cloud inference:

```python
# ondevice_analysis.py
import pandas as pd

bench = pd.read_csv("lab-062/ondevice_tasks.csv")

print(f"Tasks: {len(bench)}")
print(f"Categories: {bench['category'].unique().tolist()}")
print(bench[["task_id", "category", "description", "npu_available"]].to_string(index=False))
```

**Expected output:**

```
Tasks: 15
Categories: ['summarize', 'classify', 'rewrite', 'text_to_table']

task_id      category                      description  npu_available
    T01     summarize          Meeting transcript summary           True
    T02     summarize                    Article digest           True
    T03     summarize              Email thread summary           True
    T04     summarize                Policy doc summary           True
    T05      classify              Sentiment analysis           True
    T06      classify                Intent detection           True
    T07      classify              Priority assignment           True
    T08      classify             Language detection           True
    T09       rewrite                 Tone adjustment           True
    T10       rewrite                  Simplification           True
    T11       rewrite                  Formalization           True
    T12       rewrite    Translation (EN→ES snippet)          False
    T13 text_to_table      Invoice data extraction           True
    T14 text_to_table      Resume parsing to table           True
    T15 text_to_table  Schedule extraction to table           True
```

---

## Part 3: NPU Availability

### Step 3: Check NPU readiness across tasks

```python
# NPU availability
available = bench["npu_available"].sum()
unavailable = len(bench) - available
print(f"NPU available: {available}/{len(bench)}")
print(f"NPU unavailable: {unavailable}")

# Which tasks have no NPU support?
no_npu = bench[bench["npu_available"] == False]
print("\nTasks without NPU support:")
print(no_npu[["task_id", "category", "description"]].to_string(index=False))
```

**Expected output:**

```
NPU available: 14/15
NPU unavailable: 1

Tasks without NPU support:
task_id category                   description
    T12  rewrite  Translation (EN→ES snippet)
```

!!! warning "NPU Limitation"
    Translation (T12) is not available on the NPU — Phi Silica is optimized for English-language tasks and does not support cross-language translation on-device. Your agent must detect this and fall back to cloud inference.

---

## Part 4: Quality Match Analysis

### Step 4: Compare NPU vs cloud quality

```python
# Quality match for NPU-available tasks only
npu_tasks = bench[bench["npu_available"] == True]
quality_match = npu_tasks["quality_match"].sum()
total_available = len(npu_tasks)
match_rate = quality_match / total_available * 100

print(f"Quality match (NPU-available tasks): {quality_match}/{total_available} = {match_rate:.0f}%")

# Which NPU-available tasks have quality mismatch?
mismatches = npu_tasks[npu_tasks["quality_match"] == False]
print("\nQuality mismatches (NPU available but lower quality):")
print(mismatches[["task_id", "category", "description"]].to_string(index=False))
```

**Expected output:**

```
Quality match (NPU-available tasks): 13/14 = 93%

Quality mismatches (NPU available but lower quality):
task_id      category              description
    T04     summarize  Policy doc summary
```

!!! info "Quality Insight"
    93% of NPU-available tasks match cloud quality. The only mismatch is T04 (policy document summary) — a complex document that pushes the on-device model's context limits. For 13 of 14 available tasks, NPU quality is indistinguishable from cloud.

```python
# Quality by category (NPU-available tasks only)
print("\nQuality match by category:")
for cat in npu_tasks["category"].unique():
    cat_data = npu_tasks[npu_tasks["category"] == cat]
    matches = cat_data["quality_match"].sum()
    total = len(cat_data)
    print(f"  {cat:>13}: {matches}/{total}")
```

**Expected output:**

```
Quality match by category:
      summarize: 3/4
       classify: 4/4
        rewrite: 3/3
  text_to_table: 3/3
```

---

## Part 5: Latency Comparison

### Step 5: NPU vs cloud latency

```python
# Average NPU latency (available tasks only)
npu_tasks = bench[bench["npu_available"] == True]
npu_avg = npu_tasks["npu_latency_ms"].mean()
cloud_avg = npu_tasks["cloud_latency_ms"].mean()
speedup = cloud_avg / npu_avg

print(f"NPU avg latency:   {npu_avg:.1f}ms")
print(f"Cloud avg latency: {cloud_avg:.1f}ms")
print(f"Speedup:           {speedup:.0f}×")
```

**Expected output:**

```
NPU avg latency:   83.1ms
Cloud avg latency: 874.3ms
Speedup:           10×
```

```python
# Per-task latency comparison
print("\nPer-task latency (NPU-available only):")
for _, row in npu_tasks.iterrows():
    print(f"  {row['task_id']} ({row['category']:>13}): "
          f"NPU={row['npu_latency_ms']:.0f}ms  "
          f"Cloud={row['cloud_latency_ms']:.0f}ms")
```

!!! info "Latency Advantage"
    NPU inference averages 83.1ms — over **10× faster** than cloud at 874.3ms. This is even faster than CPU-based ONNX Runtime (Lab 061's 82.3ms) because the NPU is purpose-built for AI workloads. For real-time agent experiences, this sub-100ms latency enables truly responsive interactions.

---

## Part 6: Graceful Fallback Strategy

### Step 6: Implement fallback logic

The correct pattern for on-device agents is: **check readiness → attempt NPU → fall back to cloud**:

```csharp
// C# — Windows AI API pattern
async Task<string> RunAgentSkill(string input, SkillType skill)
{
    // 1. Check NPU readiness for this skill
    var readiness = await PhiSilicaModel.CheckReadinessAsync(skill);

    if (readiness == AIReadiness.Available)
    {
        // 2. Run on NPU
        return await PhiSilicaModel.InferAsync(input, skill);
    }
    else
    {
        // 3. Fall back to cloud
        Console.WriteLine($"NPU unavailable for {skill}, falling back to cloud");
        return await CloudModel.InferAsync(input, skill);
    }
}
```

!!! warning "Anti-pattern: No Readiness Check"
    Never assume the NPU is available. Always call `CheckReadinessAsync()` first. Some tasks (like translation) are not supported on-device, and NPU availability can change based on hardware and driver state.

```python
# Simulate fallback strategy
print("Fallback strategy simulation:")
for _, row in bench.iterrows():
    if row["npu_available"]:
        engine = "NPU"
        latency = row["npu_latency_ms"]
    else:
        engine = "CLOUD (fallback)"
        latency = row["cloud_latency_ms"]
    print(f"  {row['task_id']}: {engine:>20} → {latency:.0f}ms")
```

---

## Part 7: Decision Framework

### Step 7: When to use on-device inference

| Scenario | Recommended | Why |
|----------|------------|-----|
| **Offline operation** | NPU | No internet required |
| **Privacy-sensitive data** | NPU | Data never leaves device |
| **Real-time agent UX** | NPU | Sub-100ms latency |
| **Translation** | Cloud | NPU doesn't support cross-language |
| **Complex documents** | Cloud (or NPU with fallback) | NPU may have quality gaps on complex inputs |
| **Batch processing** | NPU | Zero per-token cost at scale |

```python
# Summary dashboard
print("""
╔══════════════════════════════════════════════════════╗
║   On-Device Benchmark — Phi Silica (NPU) vs Cloud   ║
╠══════════════════════════════════════════════════════╣
║  Metric                    NPU         Cloud        ║
║  ─────────────────         ───         ─────        ║
║  Tasks supported           14/15       15/15        ║
║  Quality match (avail.)    93%         baseline     ║
║  Avg latency               83.1ms      874.3ms     ║
║  Speedup                   10×+        baseline     ║
║  Privacy                   Full        Data sent    ║
║  Offline capable           Yes         No           ║
╠══════════════════════════════════════════════════════╣
║  Strategy: NPU-first with cloud fallback            ║
║  Check readiness → attempt NPU → fall back if needed║
╚══════════════════════════════════════════════════════╝
""")
```

---

## 🐛 Bug-Fix Exercise

The file `lab-062/broken_ondevice.py` has **3 bugs** in the on-device analysis functions. Run the self-tests:

```bash
python lab-062/broken_ondevice.py
```

You should see **3 failed tests**:

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | NPU availability count | Which column represents availability — `npu_available` or `quality_match`? |
| Test 2 | Speedup calculation | Is the ratio `npu / cloud` or `cloud / npu`? |
| Test 3 | Quality match filter | Are you filtering for `npu_available == True` before checking quality? |

Fix all 3 bugs and re-run until you see `🎉 All 3 tests passed`.

---


## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What is the primary advantage of NPU-based inference with Phi Silica?"

    - A) Higher accuracy than all cloud models
    - B) Fast inference without internet connectivity
    - C) Support for all languages and modalities
    - D) Unlimited context window size

    ??? success "✅ Reveal Answer"
        **Correct: B) Fast inference without internet connectivity**

        The NPU enables on-device inference at ~83ms average — no network round-trip, no internet dependency, and full data privacy. It doesn't claim higher accuracy than cloud models (quality match is 93%), and it has limitations (e.g., no translation support). The key advantage is the combination of speed, privacy, and offline capability.

??? question "**Q2 (Multiple Choice):** What is the correct pattern for handling NPU unavailability in a production agent?"

    - A) Crash with an error message telling the user to upgrade hardware
    - B) Always use cloud inference to avoid NPU issues entirely
    - C) Check NPU readiness first, then fall back to cloud if unavailable
    - D) Retry NPU inference 10 times before giving up

    ??? success "✅ Reveal Answer"
        **Correct: C) Check NPU readiness first, then fall back to cloud if unavailable**

        The correct pattern is: check readiness → attempt NPU → fall back to cloud. This ensures the agent works on all hardware configurations and for all task types. Some tasks (like translation) are never available on NPU, and hardware availability can vary. A graceful fallback provides the best user experience — fast on-device when possible, reliable cloud when needed.

??? question "**Q3 (Run the Lab):** How many tasks have NPU unavailable?"

    Calculate `(bench["npu_available"] == False).sum()`.

    ??? success "✅ Reveal Answer"
        **1 task (T12 — Translation)**

        Only T12 (Translation EN→ES snippet) lacks NPU support. All other 14 tasks — summarize, classify, rewrite, and text_to_table — can run on the NPU via Phi Silica. This means 93% of the benchmark tasks can run entirely on-device.

??? question "**Q4 (Run the Lab):** What is the quality match rate for NPU-available tasks?"

    Filter for `npu_available == True`, then calculate `quality_match.sum() / len(filtered) * 100`.

    ??? success "✅ Reveal Answer"
        **93% (13/14)**

        Of the 14 tasks where NPU is available, 13 produce quality that matches cloud inference — a 93% match rate. The only mismatch is T04 (policy document summary), where the complex document exceeds the on-device model's effective context capacity. For the vast majority of tasks, on-device quality is indistinguishable from cloud.

??? question "**Q5 (Run the Lab):** What is the average NPU latency for available tasks?"

    Filter for `npu_available == True`, then calculate `npu_latency_ms.mean()`.

    ??? success "✅ Reveal Answer"
        **83.1ms**

        The average NPU latency across 14 available tasks is 83.1ms. Compared to the cloud average of 874.3ms, this represents a 10×+ speedup. Sub-100ms latency enables real-time agent interactions — the user perceives the response as instant. This latency advantage is the strongest argument for on-device inference in interactive agent experiences.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| Windows AI APIs | System-level APIs for on-device NPU inference |
| Phi Silica | Model optimized for Windows NPU hardware |
| NPU Availability | 14/15 tasks supported; translation requires cloud fallback |
| Quality Match | 93% of NPU-available tasks match cloud quality |
| Latency | NPU avg 83.1ms vs cloud 874.3ms — 10×+ faster |
| Fallback Pattern | Check readiness → NPU → cloud fallback |

---

## Next Steps

- **[Lab 061](lab-061-slm-phi4-mini.md)** — SLMs with Phi-4 Mini (CPU/GPU-based local inference via ONNX Runtime)
- **[Lab 063](lab-063-agent-identity-entra.md)** — Agent Identity with Entra (securing agents that access cloud resources)
- **[Lab 043](lab-043-multimodal-agents.md)** — Multimodal Agents (extending agent capabilities beyond text)
