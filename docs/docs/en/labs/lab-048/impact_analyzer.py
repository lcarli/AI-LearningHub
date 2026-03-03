#!/usr/bin/env python3
"""
Copilot Impact Analyzer — Lab 048
===================================

OutdoorGear Inc. wants to prove Copilot ROI to the board.  You have 3 months
of usage data and business-outcome KPIs.  Complete the 5 TODOs to build a
full impact analysis.

Usage:
    pip install pandas
    python lab-048/impact_analyzer.py
"""

import sys
import pandas as pd


# ── TODO 1 ───────────────────────────────────────────────────────────────────
def load_and_merge(usage_path: str, outcomes_path: str) -> pd.DataFrame | None:
    """Load both CSVs and merge them on (department, month).
    Return the merged DataFrame.
    """
    # TODO 1: Read both CSVs with pd.read_csv(), then merge on
    #   ['department', 'month'] using pd.merge().
    #   Return the merged DataFrame.
    return None


# ── TODO 2 ───────────────────────────────────────────────────────────────────
def calculate_roi(usage: pd.DataFrame, hourly_rate: float = 50.0) -> dict | None:
    """Calculate the dollar value of time saved.

    Returns a dict with:
      - total_minutes: sum of total_time_saved_min across all rows
      - total_hours:   total_minutes / 60
      - dollar_value:  total_hours * hourly_rate
      - per_department: dict mapping department -> dollar_value
    """
    # TODO 2: Sum total_time_saved_min, convert to hours, multiply by rate.
    #   Also compute per-department breakdown.
    return None


# ── TODO 3 ───────────────────────────────────────────────────────────────────
def correlate_usage_with_outcomes(
    merged: pd.DataFrame,
    usage_col: str = "avg_active_days",
    outcome_col: str = "employee_satisfaction",
) -> float | None:
    """Return the Pearson correlation coefficient between a usage metric
    and a business outcome across all (department, month) rows.
    """
    # TODO 3: Use pandas .corr() or compute manually.
    #   Return a single float (the correlation coefficient).
    return None


# ── TODO 4 ───────────────────────────────────────────────────────────────────
def calculate_adoption_growth(usage: pd.DataFrame) -> dict | None:
    """Calculate month-over-month adoption growth.

    Returns a dict with:
      - jan_active: total active_users in 2026-01
      - mar_active: total active_users in 2026-03
      - growth_pct: (mar - jan) / jan * 100
      - by_department: dict mapping department -> growth from Jan to Mar
    """
    # TODO 4: Group by month, sum active_users, compare Jan to Mar.
    #   For per-department, compare each department's Jan vs Mar active_users.
    return None


# ── TODO 5 ───────────────────────────────────────────────────────────────────
def build_impact_narrative(
    roi: dict,
    correlation: float,
    growth: dict,
    merged: pd.DataFrame,
) -> str | None:
    """Generate a Markdown executive impact narrative.

    Include:
    - Executive summary (1 paragraph)
    - ROI table (total + per department)
    - Correlation insight
    - Growth trend
    - Top 3 recommendations
    """
    # TODO 5: Build and return a multi-line Markdown string.
    return None


# ═══════════════════════════════════════════════════════════════════════════
#  Main — run the full impact analysis pipeline
# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    usage_path = "lab-048/copilot_quarterly_summary.csv"
    outcomes_path = "lab-048/business_outcomes.csv"

    # Step 1
    merged = load_and_merge(usage_path, outcomes_path)
    if merged is None:
        print("❌ TODO 1 not implemented — load_and_merge()")
        sys.exit(1)
    print(f"✅ Merged dataset: {len(merged)} rows × {len(merged.columns)} columns\n")

    # Step 2
    usage = pd.read_csv(usage_path)
    roi = calculate_roi(usage)
    if roi is None:
        print("❌ TODO 2 not implemented — calculate_roi()")
        sys.exit(1)
    print(f"💰 Total ROI: ${roi['dollar_value']:,.0f}")
    print(f"   ({roi['total_hours']:.1f} hours saved × $50/hr)\n")

    # Step 3
    corr = correlate_usage_with_outcomes(merged)
    if corr is None:
        print("❌ TODO 3 not implemented — correlate_usage_with_outcomes()")
        sys.exit(1)
    print(f"📈 Correlation (active_days ↔ satisfaction): {corr:.3f}\n")

    # Step 4
    growth = calculate_adoption_growth(usage)
    if growth is None:
        print("❌ TODO 4 not implemented — calculate_adoption_growth()")
        sys.exit(1)
    print(f"🚀 Adoption Growth (Jan→Mar): {growth['growth_pct']:.1f}%")
    print(f"   Jan: {growth['jan_active']} active → Mar: {growth['mar_active']} active\n")

    # Step 5
    narrative = build_impact_narrative(roi, corr, growth, merged)
    if narrative is None:
        print("❌ TODO 5 not implemented — build_impact_narrative()")
        sys.exit(1)
    print("=" * 60)
    print(narrative)

    out_path = "lab-048/impact_narrative.md"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(narrative)
    print(f"\n💾 Narrative saved to {out_path}")
