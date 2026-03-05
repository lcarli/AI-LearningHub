#!/usr/bin/env python3
"""
🐛 Broken Conventions Analyzer — Lab 050 Bug-Fix Exercise
==========================================================

This script analyzes multi-agent traces but has 3 bugs in how it
interprets GenAI semantic conventions.  Fix them and run self-tests.

Usage:
    python lab-050/broken_conventions.py
"""

import io
import pandas as pd


def get_unique_agents(spans: pd.DataFrame) -> list[str]:
    """Return a sorted list of unique agent names from the trace data."""
    # 🐛 Bug #1: Uses the 'span_name' column instead of 'agent_name'
    #            GenAI convention: agent identity is in gen_ai.agent.name,
    #            NOT in the span name (which is the operation name)
    names = spans["span_name"].dropna().unique()
    return sorted(names)


def count_agent_spans(spans: pd.DataFrame) -> int:
    """Count spans that represent agent operations (not LLM or tool calls)."""
    # 🐛 Bug #2: Counts ALL spans instead of filtering for agent spans
    #            Agent spans have kind=INTERNAL AND a non-null agent_name
    return len(spans)


def calculate_total_tokens(spans: pd.DataFrame) -> int:
    """Return total tokens (input + output) across all LLM calls."""
    llm_spans = spans[spans["model"].notna()]
    # 🐛 Bug #3: Only sums input_tokens, forgets output_tokens
    return int(llm_spans["input_tokens"].sum())


# ═══════════════════════════════════════════════════════════════════════════
def run_tests() -> bool:
    test_csv = """\
trace_id,span_id,parent_span_id,span_name,agent_name,kind,duration_ms,model,input_tokens,output_tokens,tool_name,quality_score,status
A1,s1,,router_agent,Router,INTERNAL,5000,,,,,,OK
A1,s2,s1,classify_query,,CLIENT,800,gpt-4o-mini,80,25,,,OK
A1,s3,s1,product_specialist,ProductSpec,INTERNAL,2500,,,,,,OK
A1,s4,s3,search_reasoning,,CLIENT,1200,gpt-4o,200,120,,,OK
A1,s5,s3,search_products,,CLIENT,300,,,search_products,,OK
A1,s6,s1,reviewer,Reviewer,INTERNAL,500,,,,,0.95,OK
A1,s7,s6,quality_check,,CLIENT,400,gpt-4o-mini,150,30,,,OK
A2,s8,,router_agent,Router,INTERNAL,4000,,,,,,OK
A2,s9,s8,classify_query,,CLIENT,700,gpt-4o-mini,90,20,,,OK
A2,s10,s8,order_specialist,OrderSpec,INTERNAL,2800,,,,,,OK"""

    spans = pd.read_csv(io.StringIO(test_csv))
    passed = 0
    failed = 0

    # ── Test 1: Unique agents from agent_name column ─────────────────────
    #   Should be: ["OrderSpec", "ProductSpec", "Reviewer", "Router"]
    agents = get_unique_agents(spans)
    expected = ["OrderSpec", "ProductSpec", "Reviewer", "Router"]
    if agents == expected:
        print(f"✅ Test 1 PASSED: agents = {agents}")
        passed += 1
    else:
        print(f"❌ Test 1 FAILED: agents = {agents}  (expected {expected})")
        failed += 1

    # ── Test 2: Agent spans only (kind=INTERNAL + agent_name not null) ───
    #   s1(Router), s3(ProductSpec), s6(Reviewer), s8(Router), s10(OrderSpec) = 5
    count = count_agent_spans(spans)
    expected_count = 5
    if count == expected_count:
        print(f"✅ Test 2 PASSED: agent spans = {count}")
        passed += 1
    else:
        print(f"❌ Test 2 FAILED: agent spans = {count}  (expected {expected_count})")
        failed += 1

    # ── Test 3: Total tokens = input + output ────────────────────────────
    #   Input:  80+200+150+90 = 520
    #   Output: 25+120+30+20  = 195
    #   Total:  715
    tokens = calculate_total_tokens(spans)
    expected_tokens = 715
    if tokens == expected_tokens:
        print(f"✅ Test 3 PASSED: total tokens = {tokens}")
        passed += 1
    else:
        print(f"❌ Test 3 FAILED: total tokens = {tokens}  (expected {expected_tokens})")
        failed += 1

    print()
    if failed == 0:
        print("🎉 All 3 tests passed — great debugging!")
    else:
        print(f"🔧 {failed} test(s) failed — keep debugging!")
    return failed == 0


if __name__ == "__main__":
    print("🧪 Running self-tests for broken_conventions.py …\n")
    run_tests()
