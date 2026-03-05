#!/usr/bin/env python3
"""
Traced OutdoorGear Agent — Lab 049
====================================

An agent with OpenTelemetry instrumentation for Azure AI Foundry tracing.
Complete the 5 TODOs to fully instrument the agent.

Works in two modes:
  - LOCAL mode (default): traces go to console — no Azure needed
  - AZURE mode: set APPLICATIONINSIGHTS_CONNECTION_STRING to export to Azure

Usage:
    pip install opentelemetry-api opentelemetry-sdk opentelemetry-exporter-otlp
    python lab-049/traced_agent.py
"""

import os
import json
import time
import random

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from opentelemetry.trace import StatusCode


# ── TODO 1 ───────────────────────────────────────────────────────────────────
def setup_tracing() -> trace.Tracer:
    """Configure the OpenTelemetry tracer provider.

    Steps:
      1. Create a TracerProvider
      2. Add a SimpleSpanProcessor with ConsoleSpanExporter (local mode)
      3. Set the provider as the global tracer provider
      4. Return a tracer named "outdoor-gear-agent"

    For Azure mode (optional), check APPLICATIONINSIGHTS_CONNECTION_STRING
    and use azure-monitor-opentelemetry instead.
    """
    # TODO 1: Set up the tracer provider and return a tracer.
    # Hint:
    #   provider = TracerProvider()
    #   provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))
    #   trace.set_tracer_provider(provider)
    #   return trace.get_tracer("outdoor-gear-agent")
    return None


# ── Simulated LLM call ──────────────────────────────────────────────────────
def call_llm(model: str, messages: list[dict], tracer: trace.Tracer) -> dict:
    """Simulate an LLM call with proper OpenTelemetry instrumentation."""

    # ── TODO 2 ───────────────────────────────────────────────────────────
    # Wrap the LLM call in a span using: with tracer.start_as_current_span(...)
    # Set span attributes following GenAI semantic conventions:
    #   gen_ai.operation.name = "chat"
    #   gen_ai.request.model = model
    #   gen_ai.system = "openai"
    #
    # Hint:
    #   with tracer.start_as_current_span(f"chat {model}") as span:
    #       span.set_attribute("gen_ai.operation.name", "chat")
    #       span.set_attribute("gen_ai.request.model", model)
    #       ...

    # Simulate latency
    latency = random.uniform(0.5, 2.0)
    time.sleep(latency)

    # Simulate response
    input_tokens = sum(len(m.get("content", "").split()) * 2 for m in messages)
    output_tokens = random.randint(30, 150)
    response_text = f"[Simulated response from {model}]"

    # ── TODO 3 ───────────────────────────────────────────────────────────
    # Record token usage as span attributes:
    #   gen_ai.usage.input_tokens = input_tokens
    #   gen_ai.usage.output_tokens = output_tokens
    #   gen_ai.response.finish_reason = "stop"

    return {
        "content": response_text,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "latency_ms": int(latency * 1000),
    }


# ── Simulated tool call ─────────────────────────────────────────────────────
def call_tool(tool_name: str, args: dict, tracer: trace.Tracer) -> dict:
    """Simulate a tool call with tracing."""
    time.sleep(random.uniform(0.1, 0.5))
    return {"result": f"[Simulated {tool_name} result]", "tool": tool_name}


# ── Agent loop ───────────────────────────────────────────────────────────────
def run_agent(query: str, tracer: trace.Tracer) -> str:
    """Run the OutdoorGear agent with full tracing."""
    if tracer is None:
        print("❌ TODO 1 not implemented — setup_tracing()")
        return ""

    # ── TODO 4 ───────────────────────────────────────────────────────────
    # Create a root span for the entire agent run:
    #   with tracer.start_as_current_span("outdoor_gear_agent") as root:
    #       root.set_attribute("user.query", query)
    #       ... rest of the agent logic ...

    print(f"🔍 Processing query: {query}")

    # Step 1: Classify the query
    classification = call_llm(
        "gpt-4o-mini",
        [{"role": "user", "content": f"Classify this query: {query}"}],
        tracer,
    )

    # Step 2: Generate response (might need tool calls)
    needs_tool = "product" in query.lower() or "order" in query.lower()
    if needs_tool:
        tool_result = call_tool("search_products", {"query": query}, tracer)
        context = tool_result["result"]
    else:
        context = "No tool needed"

    response = call_llm(
        "gpt-4o",
        [
            {"role": "system", "content": "You are OutdoorGear assistant."},
            {"role": "user", "content": query},
            {"role": "assistant", "content": f"Context: {context}"},
        ],
        tracer,
    )

    return response["content"]


# ── Error simulation ─────────────────────────────────────────────────────────
def run_agent_with_error(query: str, tracer: trace.Tracer) -> str:
    """Run an agent call that will fail — demonstrates error recording."""
    if tracer is None:
        return ""

    # ── TODO 5 ───────────────────────────────────────────────────────────
    # When an error occurs, record it on the span:
    #   span.set_status(StatusCode.ERROR, "description of error")
    #   span.record_exception(exception)
    #
    # Hint: use try/except inside the span context manager

    try:
        raise TimeoutError("LLM request timed out after 30s")
    except TimeoutError as e:
        print(f"⚠️  Error: {e}")
        return f"Error: {e}"


# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("🔭 OutdoorGear Agent with OpenTelemetry Tracing\n")

    tracer = setup_tracing()

    # Run a few queries
    queries = [
        "What tents do you have in stock?",
        "What's the return policy?",
        "Show me hiking boots under $100",
    ]

    for q in queries:
        result = run_agent(q, tracer)
        print(f"   → {result}\n")

    # Run one that errors
    print("--- Simulating error scenario ---")
    run_agent_with_error("Check order status for ORD-999", tracer)

    print("\n✅ Done! Check the console output for trace spans.")
    print("   In Azure mode, traces appear in Foundry portal → Tracing.")
