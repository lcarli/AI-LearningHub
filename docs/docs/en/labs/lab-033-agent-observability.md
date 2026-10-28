---
tags:
- observability
- opentelemetry
- python
- free
lab:
  id: '033'
  level: L300
  journey: microsoft-foundry
  time_min: 45
  cost:
    tier: free
    requires: []
    estimate_usd: 0 within the documented free path or quota.
    simulation: false
    cleanup: false
  status: active
  last_verified: '2026-10-27'
  languages:
  - en
  - pt
  - fr
---
!!! warning "Backend update (October 2026)"
    GitHub Models inference was retired on July 30, 2026. Any references below are retained only for historical context while this lab is migrated. Use [Lab 013 — Free LLM backends](../labs/lab-013-github-models.md) to configure Foundry Local or Ollama before continuing.

# Lab 033: Agent Observability with Application Insights

<div class="lab-meta">
  <span><strong>Level:</strong> <span class="level-badge level-300">L300</span></span>
  <span><strong>Path:</strong> <a href="../paths/foundry/">Microsoft Foundry</a></span>
  <span><strong>Time:</strong> ~45 min</span>
  <span><strong>💰 Cost:</strong> <span class="level-badge cost-free">Free (local)</span> + optional Azure Application Insights (free tier)</span>
</div>

## What You'll Learn

- Add **OpenTelemetry tracing** to a Python AI agent
- Capture **LLM spans** — prompts, completions, token counts, latency
- Export traces to the console (free) or Azure Application Insights
- Build a **custom dashboard** of agent metrics
- Detect slow queries and high-cost interactions

---

## Introduction

Production agents fail silently. Without observability:

- You don't know why an agent gave a wrong answer
- You can't measure response quality over time
- You can't detect when token costs spike

**OpenTelemetry** is the open standard for distributed tracing. The `opentelemetry-sdk` package lets you instrument Python agents to emit spans for every LLM call, tool execution, and retrieval step.

---

## Prerequisites

- Python 3.11+
- `pip install opentelemetry-sdk opentelemetry-exporter-otlp openai`
- `GITHUB_TOKEN` set
- Optional: Azure subscription for Application Insights

---

## Lab Exercise

### Step 1: Install dependencies

```bash
pip install \
  opentelemetry-sdk \
  opentelemetry-exporter-otlp-proto-grpc \
  opentelemetry-instrumentation-requests \
  openai
```

### Step 2: Create a traced agent

```python
# traced_agent.py
import os, time, json
from openai import OpenAI
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
    BatchSpanProcessor,
)
from opentelemetry.sdk.resources import Resource

# --- Setup OpenTelemetry ---
resource = Resource.create({"service.name": "outdoorgear-agent", "service.version": "1.0.0"})
provider = TracerProvider(resource=resource)

# Export to console (free, always works)
provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

trace.set_tracer_provider(provider)
tracer = trace.get_tracer("outdoorgear.agent")

# --- OpenAI client ---
client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.environ["GITHUB_TOKEN"],
)

PRODUCTS = [
    {"name": "TrailBlazer X200", "price": 189.99, "category": "footwear"},
    {"name": "Summit Pro Tent",   "price": 349.00, "category": "camping"},
    {"name": "OmniPack 45L",     "price": 279.99, "category": "packs"},
]

def search_products(query: str) -> list[dict]:
    """Tool: search products (simulates DB query)."""
    q = query.lower()
    return [p for p in PRODUCTS if q in p["name"].lower() or q in p["category"].lower()]


def run_agent(user_message: str) -> str:
    """Run the agent with full OpenTelemetry tracing."""
    with tracer.start_as_current_span("agent.run") as agent_span:
        agent_span.set_attribute("user.message", user_message)
        agent_span.set_attribute("agent.name", "outdoorgear-assistant")

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_products",
                    "description": "Search products by keyword",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search keyword"}
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

        messages = [
            {"role": "system", "content": "You are a helpful outdoor gear assistant. Use search_products to find items."},
            {"role": "user",   "content": user_message}
        ]

        # --- LLM call span ---
        with tracer.start_as_current_span("llm.chat_completion") as llm_span:
            llm_span.set_attribute("llm.model", "gpt-4o-mini")
            llm_span.set_attribute("llm.prompt_messages", len(messages))

            start = time.perf_counter()
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=tools,
                tool_choice="auto",
            )
            latency_ms = (time.perf_counter() - start) * 1000

            usage = response.usage
            llm_span.set_attribute("llm.latency_ms", round(latency_ms, 2))
            llm_span.set_attribute("llm.prompt_tokens", usage.prompt_tokens)
            llm_span.set_attribute("llm.completion_tokens", usage.completion_tokens)
            llm_span.set_attribute("llm.total_tokens", usage.total_tokens)
            llm_span.set_attribute("llm.finish_reason", response.choices[0].finish_reason)

        # --- Tool call span (if needed) ---
        tool_calls = response.choices[0].message.tool_calls
        if tool_calls:
            messages.append(response.choices[0].message)

            for tc in tool_calls:
                with tracer.start_as_current_span("tool.search_products") as tool_span:
                    args = json.loads(tc.function.arguments)
                    tool_span.set_attribute("tool.name", tc.function.name)
                    tool_span.set_attribute("tool.query", args.get("query", ""))

                    t_start = time.perf_counter()
                    results = search_products(args["query"])
                    tool_span.set_attribute("tool.latency_ms", round((time.perf_counter() - t_start) * 1000, 2))
                    tool_span.set_attribute("tool.results_count", len(results))

                    messages.append({
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(results)
                    })

            # --- Final LLM call ---
            with tracer.start_as_current_span("llm.chat_completion_final") as final_span:
                start = time.perf_counter()
                final = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
                final_span.set_attribute("llm.latency_ms", round((time.perf_counter() - start) * 1000, 2))
                final_span.set_attribute("llm.total_tokens", final.usage.total_tokens)
                answer = final.choices[0].message.content
        else:
            answer = response.choices[0].message.content

        agent_span.set_attribute("agent.response_length", len(answer))
        return answer


# Test
questions = [
    "What hiking boots do you have?",
    "Show me camping gear",
    "What's the weather like today?",  # Off-topic — tests graceful handling
]

for q in questions:
    print(f"\n> {q}")
    answer = run_agent(q)
    print(f"  {answer}")
```

```bash
python traced_agent.py
```

You'll see structured JSON spans in the console output showing each LLM call, token counts, and latency.

### Step 3: Add structured metrics logging

```python
# metrics_logger.py
import json, datetime
from pathlib import Path

METRICS_FILE = Path("agent_metrics.jsonl")

def log_metrics(user_message: str, response: str, prompt_tokens: int,
                completion_tokens: int, latency_ms: float, tool_calls: int = 0):
    """Append a metrics record to a JSONL file for analysis."""
    record = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "user_message": user_message[:100],
        "response_length": len(response),
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "latency_ms": round(latency_ms, 2),
        "tool_calls": tool_calls,
        "estimated_cost_usd": round((prompt_tokens * 0.00000015) + (completion_tokens * 0.0000006), 6),
    }
    with open(METRICS_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")
    return record
```

### Step 4: Analyze metrics

```python
# analyze_metrics.py
import json
from pathlib import Path
from collections import defaultdict

records = [json.loads(line) for line in Path("agent_metrics.jsonl").read_text().splitlines() if line]

if not records:
    print("No metrics yet. Run traced_agent.py first.")
else:
    total_tokens = sum(r["total_tokens"] for r in records)
    avg_latency  = sum(r["latency_ms"] for r in records) / len(records)
    total_cost   = sum(r["estimated_cost_usd"] for r in records)
    tool_calls   = sum(r["tool_calls"] for r in records)

    print(f"=== Agent Metrics Report ===")
    print(f"Total requests:    {len(records)}")
    print(f"Total tokens used: {total_tokens:,}")
    print(f"Avg latency:       {avg_latency:.0f}ms")
    print(f"Total tool calls:  {tool_calls}")
    print(f"Estimated cost:    ${total_cost:.4f}")
    print()

    # Slowest requests
    slowest = sorted(records, key=lambda r: r["latency_ms"], reverse=True)[:3]
    print("=== Slowest Requests ===")
    for r in slowest:
        print(f"  {r['latency_ms']}ms — '{r['user_message']}'")
```

### Step 5: (Optional) Export to Azure Application Insights

If you have an Azure subscription, you can export traces to Application Insights for production monitoring:

```bash
pip install azure-monitor-opentelemetry
```

```python
# Replace the console exporter with Azure Monitor:
from azure.monitor.opentelemetry import configure_azure_monitor

configure_azure_monitor(
    connection_string=os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
)
# No other code changes needed — OTel handles the rest
```

Get the connection string from:
> Azure Portal → Application Insights resource → Overview → Connection String

---

## What Each Span Captures

| Span | Key attributes |
|------|---------------|
| `agent.run` | user.message, agent.name |
| `llm.chat_completion` | model, latency_ms, prompt_tokens, completion_tokens |
| `tool.search_products` | tool.name, query, results_count, latency_ms |
| `llm.chat_completion_final` | latency_ms, total_tokens |

---

## Next Steps

- **Multi-Agent Orchestration:** → [Lab 034 — SK Multi-Agent](lab-034-multi-agent-sk.md)
- **Agent Evaluation:** → [Lab 035 — Evaluation SDK](lab-035-agent-evaluation.md)

<!-- phase3-modernization:start -->
## Phase 3 modernization

!!! warning "Verified 2026-10-27"
    Emit OpenTelemetry GenAI-aligned spans and attributes, and connect to Foundry Control Plane only through documented stable surfaces. Label experimental semantic conventions explicitly.

```mermaid
flowchart LR
  L[Legacy or current lab] --> C[Phase 3 contract]
  C --> V[Local validation]
  V --> R[Optional Real adapter]
  R --> O[Operations and cleanup]
```

- [OpenTelemetry generative AI conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)
- [Foundry observability](https://learn.microsoft.com/azure/ai-foundry/concepts/trace-agent-concept)
<!-- phase3-modernization:end -->
