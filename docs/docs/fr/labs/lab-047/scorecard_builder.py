#!/usr/bin/env python3
"""
Copilot Adoption Scorecard Builder — Lab 047
=============================================

OutdoorGear Inc. has deployed Microsoft 365 Copilot to 52 employees across
7 departments.  Leadership wants a data-driven adoption scorecard.

Complete the 5 TODOs below, then run this script to generate the report.

Usage:
    pip install pandas
    python lab-047/scorecard_builder.py
"""

import sys
import pandas as pd


# ── TODO 1 ───────────────────────────────────────────────────────────────────
def load_data(filepath: str) -> pd.DataFrame | None:
    """Load the Copilot usage CSV and ensure boolean columns are parsed."""
    # TODO 1: Read the CSV file with pd.read_csv().
    #   After loading, convert the 'licensed' and 'enabled' columns from
    #   string ("true"/"false") to proper Python booleans.
    #   Hint: df["col"] = df["col"].astype(str).str.strip().str.lower() == "true"
    #   Return the DataFrame.
    return None


# ── TODO 2 ───────────────────────────────────────────────────────────────────
def calculate_adoption_rates(df: pd.DataFrame) -> pd.DataFrame | None:
    """Return a DataFrame with one row per department and these columns:
        department, total_users, licensed, enabled, active, adoption_rate

    'active' = users with active_days > 0
    'adoption_rate' = active / enabled * 100  (0 if no enabled users)
    """
    # TODO 2: Group by 'department' and compute each column.
    #   Hint: use .groupby("department").apply(...) or loop over groups.
    #   Round adoption_rate to 1 decimal place.
    return None


# ── TODO 3 ───────────────────────────────────────────────────────────────────
def find_enablement_gaps(df: pd.DataFrame) -> pd.DataFrame | None:
    """Return a DataFrame of users who are licensed=True but enabled=False.
    These users have a license but their admin has not enabled Copilot yet.
    """
    # TODO 3: Filter the DataFrame for the enablement gap.
    return None


# ── TODO 4 ───────────────────────────────────────────────────────────────────
def analyze_feature_usage(df: pd.DataFrame) -> dict | None:
    """For active users only (active_days > 0), return a dict of total
    interactions per feature:
        {"Meetings": N, "Emails": N, "Docs": N, "Chats": N}
    """
    # TODO 4: Filter for active users, then sum each feature column.
    return None


# ── TODO 5 ───────────────────────────────────────────────────────────────────
def build_scorecard(
    adoption: pd.DataFrame,
    gaps: pd.DataFrame,
    features: dict,
    total_time_saved_min: int,
) -> str | None:
    """Return a Markdown-formatted scorecard string containing:
    - Overall adoption rate (total active / total enabled * 100)
    - Department ranking table (highest to lowest adoption_rate)
    - Enablement gap summary (count + which departments)
    - Top feature by total usage
    - Total time saved converted to hours
    """
    # TODO 5: Build and return the scorecard as a multi-line string.
    return None


# ═══════════════════════════════════════════════════════════════════════════
#  Main — run the pipeline
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    filepath = "lab-047/copilot_usage_data.csv"

    # Step 1
    df = load_data(filepath)
    if df is None:
        print("❌ TODO 1 not implemented — load_data()")
        sys.exit(1)
    print(f"✅ Loaded {len(df)} user records from {filepath}\n")

    # Step 2
    adoption = calculate_adoption_rates(df)
    if adoption is None:
        print("❌ TODO 2 not implemented — calculate_adoption_rates()")
        sys.exit(1)
    print("📊 Adoption Rates by Department:")
    print(adoption.to_string(index=False))
    print()

    # Step 3
    gaps = find_enablement_gaps(df)
    if gaps is None:
        print("❌ TODO 3 not implemented — find_enablement_gaps()")
        sys.exit(1)
    print(f"⚠️  Enablement Gap: {len(gaps)} users licensed but NOT enabled")
    gap_depts = gaps["department"].value_counts()
    for dept, cnt in gap_depts.items():
        print(f"   • {dept}: {cnt} user(s)")
    print()

    # Step 4
    features = analyze_feature_usage(df)
    if features is None:
        print("❌ TODO 4 not implemented — analyze_feature_usage()")
        sys.exit(1)
    print("🔧 Feature Usage (total interactions among active users):")
    for feat, count in sorted(features.items(), key=lambda x: x[1], reverse=True):
        print(f"   {feat}: {count}")
    print()

    # Step 5
    active_df = df[df["active_days"] > 0]
    total_time = int(active_df["time_saved_min"].sum())
    scorecard = build_scorecard(adoption, gaps, features, total_time)
    if scorecard is None:
        print("❌ TODO 5 not implemented — build_scorecard()")
        sys.exit(1)
    print("=" * 60)
    print(scorecard)

    out_path = "lab-047/scorecard_report.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(scorecard)
    print(f"\n💾 Scorecard saved to {out_path}")
