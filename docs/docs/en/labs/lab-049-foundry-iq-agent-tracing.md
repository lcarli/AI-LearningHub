---
tags: [observability, opentelemetry, azure-monitor, foundry, python, tracing]
---
# Lab 049: Foundry IQ — Agent Tracing with OpenTelemetry

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Path:</strong> <a href="../paths/foundry/">🏭 Microsoft Foundry</a></span>
  <span><strong>Time:</strong> ~75 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free</span> — Local mode with ConsoleSpanExporter (Azure Monitor optional)</span>
</div>

## What You'll Learn

- How **OpenTelemetry** provides observability for AI agents (traces, spans, attributes)
- Instrument agent code with the **GenAI semantic conventions** for model calls and tool use
- Capture **token usage, latency, and error rates** as structured telemetry
- Analyze agent traces to identify performance issues and cost drivers
- (Optional) Export traces to **Azure Monitor / Application Insights** and the **Foundry portal**
- Configure **privacy controls** for content recording

## Introduction

![Foundry IQ Tracing Architecture](../../assets/diagrams/foundry-iq-tracing.svg)

Production agents fail silently. A response degrades in quality — but nobody notices until a customer complains. Costs spike because a prompt grew too long — but the invoice comes 30 days later. A tool call starts timing out — but the agent returns a fallback answer instead of an error.

**Foundry IQ** is the observability layer that makes agent behavior visible. It uses **OpenTelemetry** — the industry-standard observability framework — with **GenAI semantic conventions** that define exactly how to capture AI-specific telemetry like token counts, model names, and tool calls.

### The Scenario

OutdoorGear Inc.'s customer service agent handles 1,000+ queries per day. The team needs:

1. **Latency tracking** — which queries take longest and why?
2. **Cost visibility** — how many tokens are consumed and at what cost?
3. **Error detection** — which traces fail, and what's the root cause?
4. **Quality monitoring** — are responses getting worse over time?

You have **10 sample traces** from the agent to analyze, plus a starter script to add tracing to new code.

---

## Prerequisites

| Requirement | Why |
|---|---|
| Python 3.10+ | Run the analysis and instrumentation |
| `pandas` | Analyze sample trace data |
| `opentelemetry-api`, `opentelemetry-sdk` | Local tracing (ConsoleSpanExporter) |
| (Optional) Azure AI Foundry project | Live trace export to Foundry portal |

```bash
pip install pandas opentelemetry-api opentelemetry-sdk
```

For Azure mode (optional):
```bash
pip install azure-ai-projects azure-monitor-opentelemetry opentelemetry-instrumentation-openai-v2
```

---

## Step 1: Understanding OpenTelemetry for AI

OpenTelemetry defines three signal types. For agent tracing, we focus on **traces**:

| Signal | What It Captures | Agent Example |
|--------|-----------------|---------------|
| **Traces** | End-to-end request flow as a tree of spans | Agent loop → LLM call → Tool call → Response |
| **Metrics** | Aggregated measurements over time | Token consumption, request count, latency histograms |
| **Logs** | Discrete events | "Agent selected tool: search_products" |

### Spans and Attributes

A **span** represents a single operation within a trace. Each span has:

- **Name**: e.g., `chat gpt-4o`
- **Kind**: `CLIENT` (outgoing call to LLM/tool) or `INTERNAL` (agent logic)
- **Duration**: start time to end time
- **Attributes**: key-value metadata following GenAI conventions
- **Status**: `OK` or `ERROR`
- **Parent**: links spans into a tree

### GenAI Semantic Conventions

The OpenTelemetry community defines standard attribute names for AI operations:

| Attribute | Description | Example |
|-----------|-------------|---------|
| `gen_ai.operation.name` | Operation type | `chat` |
| `gen_ai.request.model` | Model requested | `gpt-4o` |
| `gen_ai.usage.input_tokens` | Prompt tokens consumed | `150` |
| `gen_ai.usage.output_tokens` | Completion tokens | `85` |
| `gen_ai.response.finish_reason` | Why the model stopped | `stop`, `tool_calls` |
| `gen_ai.system` | Provider | `openai` |

!!! tip "Why Standards Matter"
    Using GenAI semantic conventions means your traces are readable by **any** OpenTelemetry-compatible backend — Jaeger, Zipkin, Datadog, Azure Monitor, Grafana Tempo — without custom parsing.

---

## Step 2: Analyze Sample Traces

Before instrumenting code, let's analyze real trace data. Load the 10 sample traces:

```python
import pandas as pd

traces = pd.read_csv("lab-049/sample_traces.csv")
print(f"Loaded {len(traces)} traces")
print(traces[["trace_id", "query_type", "model", "duration_ms", "status"]].to_string(index=False))
```

### 2a — Latency Analysis

```python
avg_latency = traces["duration_ms"].mean()
p95 = traces["duration_ms"].quantile(0.95)
slowest = traces.loc[traces["duration_ms"].idxmax()]

print(f"Average latency:  {avg_latency:.1f} ms  ({avg_latency/1000:.2f}s)")
print(f"P95 latency:      {p95:.0f} ms")
print(f"Slowest trace:    {slowest['trace_id']} at {slowest['duration_ms']} ms ({slowest['status']})")
```

**Expected:**
```
Average latency:  3150.0 ms  (3.15s)
P95 latency:      7650 ms
Slowest trace:    t006 at 8500 ms (ERROR)
```

### 2b — Token Usage

```python
total_input = traces["input_tokens"].sum()
total_output = traces["output_tokens"].sum()
total_tokens = total_input + total_output

print(f"Total input tokens:  {total_input:,}")
print(f"Total output tokens: {total_output:,}")
print(f"Total tokens:        {total_tokens:,}")

# Cost estimate (gpt-4o pricing: $5/1M input, $15/1M output)
input_cost = total_input / 1_000_000 * 5
output_cost = total_output / 1_000_000 * 15
print(f"Estimated cost:      ${input_cost + output_cost:.4f}")
```

### 2c — Error Analysis

```python
errors = traces[traces["status"] == "ERROR"]
error_rate = len(errors) / len(traces) * 100
print(f"Error rate: {error_rate:.1f}% ({len(errors)} of {len(traces)} traces)")
if len(errors) > 0:
    print(f"Error types: {errors['error_type'].value_counts().to_dict()}")
```

### 2d — Query Type Breakdown

```python
by_type = traces.groupby("query_type").agg(
    count=("trace_id", "count"),
    avg_ms=("duration_ms", "mean"),
    avg_tokens=("input_tokens", "mean"),
).reset_index()
print(by_type.to_string(index=False))
```

---

## Step 3: Instrument an Agent (Local Mode)

Open `lab-049/traced_agent.py` and complete the **5 TODOs**:

| TODO | What to implement |
|------|------------------|
| TODO 1 | Set up `TracerProvider` with `ConsoleSpanExporter` |
| TODO 2 | Wrap the LLM call in a span with GenAI attributes |
| TODO 3 | Record token usage as span attributes |
| TODO 4 | Create a root span for the agent loop |
| TODO 5 | Record errors with `span.set_status(StatusCode.ERROR)` |

Run the starter script to see trace output in your console:

```bash
python lab-049/traced_agent.py
```

Before completing the TODOs, the script prints `❌ TODO 1 not implemented`. After completing TODO 1, you'll see JSON-formatted span data printed to the console.

---

## Step 4: Export to Azure Monitor (Optional)

If you have an Azure AI Foundry project, replace the ConsoleSpanExporter with Azure Monitor:

```python
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor

# Get connection string from Foundry project
project = AIProjectClient(
    credential=DefaultAzureCredential(),
    endpoint="https://<your-resource>.services.ai.azure.com/api/projects/<your-project>",
)
conn_str = project.telemetry.get_application_insights_connection_string()

# Configure Azure Monitor exporter
configure_azure_monitor(connection_string=conn_str)

# Auto-instrument OpenAI SDK
OpenAIInstrumentor().instrument()
```

Then navigate to **Foundry portal → Tracing** to see your traces in a visual timeline.

!!! warning "Content Recording"
    By default, message content is **NOT** recorded in spans (privacy protection). To enable:

    ```bash
    # PowerShell
    $env:OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT = "true"

    # Bash
    export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
    ```

    ⚠️ Never enable this in production with customer data unless you have proper data handling policies.

---

## Step 5: Build Alerting Rules

In production, you'd configure alerts in Azure Monitor for:

| Alert | Condition | Severity |
|-------|-----------|----------|
| High latency | P95 duration > 10s | Warning |
| Error spike | Error rate > 5% in 5 min | Critical |
| Token cost | Daily token cost > $50 | Warning |
| Quality drop | Avg evaluation score < 0.7 | Critical |

These map to Azure Monitor alert rules using KQL queries on Application Insights data.

---

## 🐛 Bug-Fix Exercise

The file `lab-049/broken_tracing.py` has **3 bugs** in the trace analysis logic:

```bash
python lab-049/broken_tracing.py
```

| Test | What it checks | Hint |
|------|---------------|------|
| Test 1 | Average latency should include ALL traces | Don't filter by status |
| Test 2 | Token cost uses different rates for input vs output | Input is cheaper |
| Test 3 | Error rate denominator | Divide by total, not by errors |

---

## 📁 Supporting Files

```
lab-049/
├── sample_traces.csv     ← 10 traces with latency, tokens, status
├── traced_agent.py       ← Starter script with 5 TODOs
└── broken_tracing.py     ← Bug-fix exercise (3 bugs + self-tests)
```

```bash
pip install pandas opentelemetry-api opentelemetry-sdk
cd docs/docs/en/labs
python lab-049/broken_tracing.py     # Bug-fix exercise
python lab-049/traced_agent.py       # Instrumentation exercise
```

---

## 🧠 Knowledge Check

??? question "**Q1 (Multiple Choice):** What does the environment variable `OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT` control?"

    - A) Whether traces are exported to Azure Monitor
    - B) Whether LLM request/response message content is recorded in spans
    - C) Whether tool call results are logged
    - D) The maximum number of spans per trace

    ??? success "✅ Reveal Answer"
        **Correct: B) Whether LLM request/response message content is recorded in spans**

        By default, message content is NOT included in spans to protect privacy. Setting this variable to `true` captures the full prompt and completion text — useful for debugging but dangerous in production with real customer data.

??? question "**Q2 (Multiple Choice):** In OpenTelemetry, what is the correct `span kind` for an agent's internal logic (routing, planning, reasoning)?"

    - A) CLIENT
    - B) SERVER
    - C) INTERNAL
    - D) PRODUCER

    ??? success "✅ Reveal Answer"
        **Correct: C) INTERNAL**

        `INTERNAL` spans represent operations that don't cross a network boundary — such as agent reasoning, routing decisions, and memory lookups. `CLIENT` spans are used for outgoing calls to LLMs, tools, and external APIs.

??? question "**Q3 (Run the Lab):** What is the average trace duration across all 10 sample traces?"

    Load `sample_traces.csv` and calculate `traces["duration_ms"].mean()`.

    ??? success "✅ Reveal Answer"
        **3,150.0 ms (3.15 seconds)**

        Sum of all durations: 2500+1800+5200+1200+3100+8500+1500+2000+4000+1700 = 31,500 ms ÷ 10 = **3,150 ms**. Note that the slowest trace (t006, 8500ms) is an ERROR — it significantly raises the average.

??? question "**Q4 (Run the Lab):** What is the total token count (input + output) across all traces?"

    Sum `input_tokens` and `output_tokens` columns.

    ??? success "✅ Reveal Answer"
        **3,255 tokens**

        Input: 150+120+350+100+200+500+130+160+280+110 = **2,100**. Output: 85+60+200+45+120+300+55+90+150+50 = **1,155**. Total: 2,100 + 1,155 = **3,255**.

??? question "**Q5 (Run the Lab):** Which trace has the highest latency and what is its status?"

    Find the row with the maximum `duration_ms`.

    ??? success "✅ Reveal Answer"
        **Trace t006 — 8,500 ms — status: ERROR (timeout)**

        The slowest trace is also the only error. It attempted 3 tool calls for an order status query but timed out. This pattern (slow = error) is common — timeouts are a leading cause of both high latency and errors in agent systems.

---

## Summary

| Topic | What You Learned |
|-------|-----------------|
| OpenTelemetry | Industry-standard observability framework (traces, metrics, logs) |
| GenAI Conventions | Standard attributes for AI: model, tokens, tool calls |
| Trace Analysis | Latency, token cost, error rate from structured trace data |
| Instrumentation | TracerProvider, SpanProcessor, span attributes |
| Azure Integration | Application Insights, Foundry portal tracing dashboard |
| Privacy | Content recording controls via environment variables |

---

## Next Steps

- **[Lab 050](lab-050-multi-agent-observability.md)** — Multi-Agent Observability with GenAI Semantic Conventions (L400)
- **[Lab 033](lab-033-agent-observability.md)** — Agent Observability with Application Insights (complementary approach)
- **[Lab 038](lab-038-cost-optimization.md)** — AI Cost Optimization (using trace data to reduce costs)
