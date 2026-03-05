#!/usr/bin/env python3
"""
🐛 Broken Trace Analyzer — Lab 049 Bug-Fix Exercise
=====================================================

This script analyzes agent traces but has 3 bugs.
Fix them and run the self-tests to verify.

Usage:
    python lab-049/broken_tracing.py
"""

import pandas as pd
import io


def calculate_avg_latency(traces: pd.DataFrame) -> float:
    """Return the average trace duration in milliseconds across ALL traces."""
    # 🐛 Bug #1: Filters to OK traces only — should include ALL traces
    #            (including errors) for accurate latency measurement
    ok_traces = traces[traces["status"] == "OK"]
    return ok_traces["duration_ms"].mean()


def calculate_token_cost(
    traces: pd.DataFrame,
    input_rate: float = 0.005,   # $ per 1K input tokens
    output_rate: float = 0.015,  # $ per 1K output tokens
) -> float:
    """Return the total cost of all LLM calls based on token usage."""
    total_input = traces["input_tokens"].sum()
    total_output = traces["output_tokens"].sum()
    # 🐛 Bug #2: Uses output_rate for BOTH input and output tokens
    #            Input tokens should use input_rate (they're cheaper)
    cost = (total_input + total_output) / 1000 * output_rate
    return cost


def calculate_error_rate(traces: pd.DataFrame) -> float:
    """Return the error rate as a percentage (0-100)."""
    errors = traces[traces["status"] == "ERROR"]
    # 🐛 Bug #3: Divides by error count instead of total trace count
    return len(errors) / len(errors) * 100


# ═══════════════════════════════════════════════════════════════════════════
#  Self-Tests
# ═══════════════════════════════════════════════════════════════════════════
def run_tests() -> bool:
    test_csv = """\
trace_id,timestamp,query_type,model,duration_ms,input_tokens,output_tokens,status,tool_calls,error_type
t1,2026-01-01T00:00:00Z,faq,gpt-4o,1000,100,50,OK,0,
t2,2026-01-01T00:01:00Z,search,gpt-4o,2000,200,100,OK,1,
t3,2026-01-01T00:02:00Z,order,gpt-4o,3000,150,75,ERROR,0,timeout
t4,2026-01-01T00:03:00Z,faq,gpt-4o,5000,300,150,OK,0,
t5,2026-01-01T00:04:00Z,search,gpt-4o,4000,250,125,ERROR,1,timeout"""

    traces = pd.read_csv(io.StringIO(test_csv))
    passed = 0
    failed = 0

    # ── Test 1: Average latency should include ALL traces ────────────────
    #   (1000+2000+3000+5000+4000) / 5 = 3000.0
    avg = calculate_avg_latency(traces)
    expected = 3000.0
    if abs(avg - expected) < 0.1:
        print(f"✅ Test 1 PASSED: avg latency = {avg:.1f} ms  (expected {expected:.1f})")
        passed += 1
    else:
        print(f"❌ Test 1 FAILED: avg latency = {avg:.1f} ms  (expected {expected:.1f})")
        failed += 1

    # ── Test 2: Token cost with correct rates ────────────────────────────
    #   Input:  (100+200+150+300+250) = 1000 → 1000/1000 × $0.005 = $0.005
    #   Output: (50+100+75+150+125)   = 500  → 500/1000  × $0.015 = $0.0075
    #   Total: $0.0125
    cost = calculate_token_cost(traces)
    expected_cost = 0.0125
    if abs(cost - expected_cost) < 0.0001:
        print(f"✅ Test 2 PASSED: cost = ${cost:.4f}  (expected ${expected_cost:.4f})")
        passed += 1
    else:
        print(f"❌ Test 2 FAILED: cost = ${cost:.4f}  (expected ${expected_cost:.4f})")
        failed += 1

    # ── Test 3: Error rate should use total count as denominator ──────────
    #   2 errors / 5 total = 40%
    rate = calculate_error_rate(traces)
    expected_rate = 40.0
    if abs(rate - expected_rate) < 0.1:
        print(f"✅ Test 3 PASSED: error rate = {rate:.1f}%  (expected {expected_rate:.1f}%)")
        passed += 1
    else:
        print(f"❌ Test 3 FAILED: error rate = {rate:.1f}%  (expected {expected_rate:.1f}%)")
        failed += 1

    print()
    if failed == 0:
        print("🎉 All 3 tests passed — great debugging!")
    else:
        print(f"🔧 {failed} test(s) failed — keep debugging!")
    return failed == 0


if __name__ == "__main__":
    print("🧪 Running self-tests for broken_tracing.py …\n")
    run_tests()
