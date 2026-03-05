#!/usr/bin/env python3
"""
🐛 Broken ROI Calculator — Lab 048 Bug-Fix Exercise
=====================================================

This script has 3 bugs that produce WRONG impact analytics.
Find and fix all 3, then run the self-tests to verify.

Usage:
    python lab-048/broken_roi_calculator.py
"""

import io
import math
import pandas as pd


def calculate_roi(usage: pd.DataFrame, hourly_rate: float = 50.0) -> float:
    """Return the total dollar value of time saved."""
    total_minutes = usage["total_time_saved_min"].sum()
    # 🐛 Bug #1: Multiplies minutes directly by hourly rate
    #            instead of converting to hours first (÷ 60)
    return total_minutes * hourly_rate


def calculate_usage_correlation(
    merged: pd.DataFrame, outcome_col: str
) -> float:
    """Return the Pearson correlation between Copilot usage and a business outcome."""
    # 🐛 Bug #2: Correlates 'licensed' (nearly constant) instead of 'active_users'
    return merged["licensed"].corr(merged[outcome_col])


def calculate_adoption_growth(usage: pd.DataFrame) -> float:
    """Return the adoption growth rate (%) from the first month to the last."""
    jan = usage[usage["month"] == "2026-01"]["active_users"].sum()
    mar = usage[usage["month"] == "2026-03"]["active_users"].sum()
    # 🐛 Bug #3: Divides by March instead of January (inverted growth base)
    return (mar - jan) / mar * 100


# ═══════════════════════════════════════════════════════════════════════════
#  Self-Tests
# ═══════════════════════════════════════════════════════════════════════════
def run_tests() -> bool:
    test_usage = pd.DataFrame({
        "month": ["2026-01", "2026-02", "2026-03"],
        "active_users": [10, 15, 20],
        "total_time_saved_min": [600, 900, 1200],
        "licensed": [20, 20, 20],
    })

    test_outcomes = pd.DataFrame({
        "month": ["2026-01", "2026-02", "2026-03"],
        "employee_satisfaction": [70, 75, 82],
    })

    merged = pd.merge(test_usage, test_outcomes, on="month")

    passed = 0
    failed = 0

    # ── Test 1: ROI should convert minutes → hours first ─────────────────
    #   2700 min ÷ 60 = 45 hours × $50 = $2,250
    roi = calculate_roi(test_usage)
    expected_roi = 2250.0
    if abs(roi - expected_roi) < 1:
        print(f"✅ Test 1 PASSED: ROI = ${roi:,.0f}  (expected ${expected_roi:,.0f})")
        passed += 1
    else:
        print(f"❌ Test 1 FAILED: ROI = ${roi:,.0f}  (expected ${expected_roi:,.0f})")
        failed += 1

    # ── Test 2: Correlation should use active_users, not licensed ─────────
    #   active_users [10,15,20] vs satisfaction [70,75,82] → ~0.99
    corr = calculate_usage_correlation(merged, "employee_satisfaction")
    if not math.isnan(corr) and corr > 0.9:
        print(f"✅ Test 2 PASSED: correlation = {corr:.3f}  (expected > 0.9)")
        passed += 1
    else:
        corr_str = f"{corr:.3f}" if not math.isnan(corr) else "NaN"
        print(f"❌ Test 2 FAILED: correlation = {corr_str}  (expected > 0.9)")
        failed += 1

    # ── Test 3: Growth base should be January, not March ─────────────────
    #   (20 − 10) / 10 = 100%
    growth = calculate_adoption_growth(test_usage)
    expected_growth = 100.0
    if abs(growth - expected_growth) < 0.1:
        print(f"✅ Test 3 PASSED: growth = {growth:.1f}%  (expected {expected_growth:.1f}%)")
        passed += 1
    else:
        print(f"❌ Test 3 FAILED: growth = {growth:.1f}%  (expected {expected_growth:.1f}%)")
        failed += 1

    print()
    if failed == 0:
        print("🎉 All 3 tests passed — great debugging!")
    else:
        print(f"🔧 {failed} test(s) failed — keep debugging!")
    return failed == 0


if __name__ == "__main__":
    print("🧪 Running self-tests for broken_roi_calculator.py …\n")
    run_tests()
