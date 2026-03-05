#!/usr/bin/env python3
"""
Multi-Agent Dashboard Builder — Lab 050
=========================================

Analyze multi-agent trace data using GenAI semantic conventions.
Complete the 5 TODOs to build observability metrics.

Usage:
    pip install pandas
    python lab-050/dashboard_builder.py
"""

import sys
import pandas as pd


# ── TODO 1 ───────────────────────────────────────────────────────────────────
def load_spans(filepath: str) -> pd.DataFrame | None:
    """Load the multi-agent spans CSV."""
    # TODO 1: Load the CSV with pd.read_csv().
    #   Return the DataFrame.
    return None


# ── TODO 2 ───────────────────────────────────────────────────────────────────
def count_agent_spans(spans: pd.DataFrame) -> dict | None:
    """Count the number of agent spans (kind=INTERNAL with an agent_name).

    Returns a dict:
      - total_agent_spans: int
      - unique_agents: sorted list of unique agent names
      - spans_per_agent: dict mapping agent_name -> count
    """
    # TODO 2: Filter spans where kind == "INTERNAL" and agent_name is not null.
    #   Count total, get unique names, and group by agent_name.
    return None


# ── TODO 3 ───────────────────────────────────────────────────────────────────
def analyze_llm_usage(spans: pd.DataFrame) -> dict | None:
    """Analyze LLM token usage across all model calls.

    Returns a dict:
      - total_input_tokens: int
      - total_output_tokens: int
      - total_tokens: int
      - by_model: dict mapping model_name -> {"input": N, "output": N}
      - total_llm_calls: int
    """
    # TODO 3: Filter spans where model is not null (LLM calls).
    #   Sum input_tokens and output_tokens, group by model.
    return None


# ── TODO 4 ───────────────────────────────────────────────────────────────────
def analyze_tool_calls(spans: pd.DataFrame) -> dict | None:
    """Analyze tool call patterns.

    Returns a dict:
      - total_tool_calls: int
      - by_tool: dict mapping tool_name -> count
      - trace_with_most_tools: trace_id with the most tool calls
    """
    # TODO 4: Filter spans where tool_name is not null.
    #   Count total, group by tool_name, find the trace with the most.
    return None


# ── TODO 5 ───────────────────────────────────────────────────────────────────
def analyze_quality(spans: pd.DataFrame) -> dict | None:
    """Analyze quality scores from reviewer agents.

    Returns a dict:
      - avg_quality: float (average of all non-null quality_score values)
      - min_quality: float
      - max_quality: float
      - traces_below_threshold: list of trace_ids where quality < 0.8
    """
    # TODO 5: Filter spans where quality_score is not null.
    #   Compute avg, min, max, and find traces below 0.8 threshold.
    return None


# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    filepath = "lab-050/multi_agent_spans.csv"

    # Step 1
    spans = load_spans(filepath)
    if spans is None:
        print("❌ TODO 1 not implemented — load_spans()")
        sys.exit(1)
    print(f"✅ Loaded {len(spans)} spans from {filepath}\n")

    # Step 2
    agents = count_agent_spans(spans)
    if agents is None:
        print("❌ TODO 2 not implemented — count_agent_spans()")
        sys.exit(1)
    print(f"🤖 Agent Spans: {agents['total_agent_spans']} total")
    print(f"   Unique agents: {agents['unique_agents']}")
    for name, count in sorted(agents["spans_per_agent"].items()):
        print(f"   • {name}: {count} span(s)")
    print()

    # Step 3
    llm = analyze_llm_usage(spans)
    if llm is None:
        print("❌ TODO 3 not implemented — analyze_llm_usage()")
        sys.exit(1)
    print(f"🧠 LLM Usage: {llm['total_llm_calls']} calls, {llm['total_tokens']} tokens")
    for model, usage in sorted(llm["by_model"].items()):
        print(f"   • {model}: {usage['input']} in + {usage['output']} out")
    print()

    # Step 4
    tools = analyze_tool_calls(spans)
    if tools is None:
        print("❌ TODO 4 not implemented — analyze_tool_calls()")
        sys.exit(1)
    print(f"🔧 Tool Calls: {tools['total_tool_calls']} total")
    print(f"   Trace with most tools: {tools['trace_with_most_tools']}")
    for tool, count in sorted(tools["by_tool"].items()):
        print(f"   • {tool}: {count}")
    print()

    # Step 5
    quality = analyze_quality(spans)
    if quality is None:
        print("❌ TODO 5 not implemented — analyze_quality()")
        sys.exit(1)
    print(f"📊 Quality Scores:")
    print(f"   Average: {quality['avg_quality']:.3f}")
    print(f"   Min: {quality['min_quality']:.2f}  Max: {quality['max_quality']:.2f}")
    print(f"   Traces below 0.8: {quality['traces_below_threshold']}")
