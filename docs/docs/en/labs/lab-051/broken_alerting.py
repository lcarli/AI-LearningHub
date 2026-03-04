#!/usr/bin/env python3
"""
🐛 Broken Alerting Engine — Lab 051 Bug-Fix Exercise

Analyzes sensor events for anomalies but has 3 bugs.
Fix them and run the self-tests to verify.

Usage:
    python lab-051/broken_alerting.py
"""

import io
import pandas as pd


def detect_temp_anomalies(events: pd.DataFrame, threshold: float = 30.0) -> pd.DataFrame:
    """Return temperature events above the threshold."""
    temp = events[events["sensor_type"] == "temperature"]
    # 🐛 Bug #1: Threshold is hardcoded to 50 instead of using the parameter
    return temp[temp["value"] > 50]


def detect_low_stock(events: pd.DataFrame, threshold: float = 10.0) -> pd.DataFrame:
    """Return stock_level events below the threshold (critical stock)."""
    stock = events[events["sensor_type"] == "stock_level"]
    # 🐛 Bug #2: Uses > instead of < — finds HIGH stock, not LOW stock
    return stock[stock["value"] > threshold]


def calculate_anomaly_rate(events: pd.DataFrame, warehouse_id: str, anomaly_count: int) -> float:
    """Return the anomaly rate (%) for a specific warehouse."""
    # 🐛 Bug #3: Divides by total events across ALL warehouses
    #            instead of events for this specific warehouse
    total = len(events)
    return anomaly_count / total * 100


def run_tests() -> bool:
    test_csv = """\
timestamp,warehouse_id,warehouse_city,sensor_type,value,unit
2026-01-01T00:00:00Z,W1,City1,temperature,35.0,celsius
2026-01-01T00:01:00Z,W1,City1,temperature,22.0,celsius
2026-01-01T00:02:00Z,W1,City1,stock_level,3.0,units
2026-01-01T00:03:00Z,W1,City1,stock_level,50.0,units
2026-01-01T00:04:00Z,W2,City2,temperature,28.0,celsius
2026-01-01T00:05:00Z,W2,City2,stock_level,15.0,units"""

    events = pd.read_csv(io.StringIO(test_csv))
    passed = 0
    failed = 0

    # ── Test 1: Temperature anomalies above 30°C ────────────────────────
    #   Only W1 at 35°C → 1 anomaly
    anomalies = detect_temp_anomalies(events, threshold=30.0)
    if len(anomalies) == 1:
        print(f"✅ Test 1 PASSED: temp anomalies = {len(anomalies)}")
        passed += 1
    else:
        print(f"❌ Test 1 FAILED: temp anomalies = {len(anomalies)}  (expected 1)")
        failed += 1

    # ── Test 2: Low stock below 10 units ─────────────────────────────────
    #   Only W1 at 3 → 1 critical stock event
    low = detect_low_stock(events, threshold=10.0)
    if len(low) == 1:
        print(f"✅ Test 2 PASSED: low stock events = {len(low)}")
        passed += 1
    else:
        print(f"❌ Test 2 FAILED: low stock events = {len(low)}  (expected 1)")
        failed += 1

    # ── Test 3: Anomaly rate for warehouse W1 ────────────────────────────
    #   W1 has 4 events, 1 anomaly → 1/4 = 25%
    rate = calculate_anomaly_rate(events, "W1", 1)
    if abs(rate - 25.0) < 0.1:
        print(f"✅ Test 3 PASSED: W1 anomaly rate = {rate:.1f}%")
        passed += 1
    else:
        print(f"❌ Test 3 FAILED: W1 anomaly rate = {rate:.1f}%  (expected 25.0%)")
        failed += 1

    print()
    if failed == 0:
        print("🎉 All 3 tests passed — great debugging!")
    else:
        print(f"🔧 {failed} test(s) failed — keep debugging!")
    return failed == 0


if __name__ == "__main__":
    print("🧪 Running self-tests for broken_alerting.py …\n")
    run_tests()
