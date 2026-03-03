#!/usr/bin/env python3
"""
🐛 Broken Scorecard — Lab 047 Bug-Fix Exercise
================================================

This script has 3 bugs that produce WRONG adoption metrics.
Find and fix all 3, then run the self-tests to verify.

Usage:
    python lab-047/broken_scorecard.py
"""

import io
import pandas as pd


def calculate_adoption_rate(df: pd.DataFrame, department: str) -> float:
    """Return the adoption rate (%) for a department.
    Correct formula: active users / enabled users * 100
    """
    dept_df = df[df["department"] == department]
    active = dept_df[dept_df["active_days"] > 0]
    # 🐛 Bug #1: Uses total users as the denominator instead of enabled users
    total = len(dept_df)
    if total == 0:
        return 0.0
    return len(active) / total * 100


def find_enablement_gap(df: pd.DataFrame) -> pd.DataFrame:
    """Return users who are licensed but NOT enabled (the 'enablement gap').
    These users have a paid license sitting unused because admins haven't
    turned on Copilot for them.
    """
    # 🐛 Bug #2: Logic is inverted — finds users who are NOT licensed
    #            AND NOT enabled, instead of licensed AND NOT enabled
    gap = df[(df["licensed"] == False) & (df["enabled"] == False)]
    return gap


def calculate_time_saved_hours(df: pd.DataFrame) -> float:
    """Return total time saved across all active users, in hours."""
    active = df[df["active_days"] > 0]
    total_minutes = active["time_saved_min"].sum()
    # 🐛 Bug #3: Divides by 100 instead of 60 to convert minutes → hours
    return total_minutes / 100


# ═══════════════════════════════════════════════════════════════════════════
#  Self-Tests — run these to verify your fixes
# ═══════════════════════════════════════════════════════════════════════════
def run_tests() -> bool:
    test_csv = """\
department,user_id,licensed,enabled,active_days,meetings_assisted,emails_drafted,docs_summarized,chats,time_saved_min
Engineering,E1,true,true,20,10,5,8,15,200
Engineering,E2,true,true,0,0,0,0,0,0
Engineering,E3,true,false,0,0,0,0,0,0
Engineering,E4,false,false,0,0,0,0,0,0
Engineering,E5,false,false,0,0,0,0,0,0
Sales,S1,true,true,15,8,6,3,5,120
Sales,S2,true,true,10,5,4,2,3,90"""

    df = pd.read_csv(io.StringIO(test_csv))
    for col in ["licensed", "enabled"]:
        df[col] = df[col].astype(str).str.strip().str.lower() == "true"

    passed = 0
    failed = 0

    # ── Test 1: Adoption rate denominator ────────────────────────────────
    #   Engineering: 5 total, 2 enabled, 1 active → 1/2 = 50%
    rate = calculate_adoption_rate(df, "Engineering")
    expected = 50.0
    if abs(rate - expected) < 0.1:
        print(f"✅ Test 1 PASSED: Engineering adoption = {rate:.1f}%  (expected {expected}%)")
        passed += 1
    else:
        print(f"❌ Test 1 FAILED: Engineering adoption = {rate:.1f}%  (expected {expected}%)")
        failed += 1

    # ── Test 2: Enablement gap logic ─────────────────────────────────────
    #   Only E3 (licensed=True, enabled=False) should appear
    gap = find_enablement_gap(df)
    expected_count = 1
    if len(gap) == expected_count:
        print(f"✅ Test 2 PASSED: Enablement gap = {len(gap)} user(s)  (expected {expected_count})")
        passed += 1
    else:
        print(f"❌ Test 2 FAILED: Enablement gap = {len(gap)} user(s)  (expected {expected_count})")
        failed += 1

    # ── Test 3: Time conversion ──────────────────────────────────────────
    #   Active users: E1(200) + S1(120) + S2(90) = 410 min → 6.83 h
    hours = calculate_time_saved_hours(df)
    expected_hours = 410 / 60
    if abs(hours - expected_hours) < 0.1:
        print(f"✅ Test 3 PASSED: Time saved = {hours:.2f} h  (expected {expected_hours:.2f} h)")
        passed += 1
    else:
        print(f"❌ Test 3 FAILED: Time saved = {hours:.2f} h  (expected {expected_hours:.2f} h)")
        failed += 1

    print()
    if failed == 0:
        print("🎉 All 3 tests passed — great debugging!")
    else:
        print(f"🔧 {failed} test(s) failed — keep debugging!")
    return failed == 0


if __name__ == "__main__":
    print("🧪 Running self-tests for broken_scorecard.py …\n")
    run_tests()
