"""Challenge 006 starter: investigate an agent observability incident.

Goal: make all tests in test_observability.py pass.
Use only the Python standard library.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


TRACES_PATH = Path(__file__).with_name("traces.json")


def load_traces(path: Path = TRACES_PATH) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def agent_spans(spans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return root agent spans only."""
    # Broken: includes every span.
    return spans


def error_rate_pct(spans: list[dict[str, Any]]) -> float:
    """Compute error rate across root agent requests."""
    # Broken: divides by all spans rather than root agent spans.
    if not spans:
        return 0.0
    errors = sum(1 for span in spans if span["status"] == "ERROR")
    return round(errors / len(spans) * 100, 1)


def p95_latency_ms(spans: list[dict[str, Any]]) -> int:
    """Compute nearest-rank p95 latency for root agent requests."""
    # Broken: returns max over every span.
    return max(span["latency_ms"] for span in spans)


def find_incident_trace(spans: list[dict[str, Any]]) -> str:
    """Return trace_id for the failed root request with highest latency."""
    # Broken: picks first error span, which may be a child span.
    for span in spans:
        if span["status"] == "ERROR":
            return span["trace_id"]
    raise ValueError("No incident trace found.")


def identify_root_cause(spans: list[dict[str, Any]], trace_id: str) -> str:
    """Identify the failing child dependency that caused the incident."""
    # Broken: reports the root agent error instead of the dependency.
    for span in spans:
        if span["trace_id"] == trace_id and span["status"] == "ERROR":
            return span["error_type"] or "unknown"
    return "unknown"


def summarize_incident(spans: list[dict[str, Any]]) -> dict[str, Any]:
    """Return incident metrics and root cause summary."""
    roots = agent_spans(spans)
    incident_trace = find_incident_trace(spans)
    return {
        "incident_trace": incident_trace,
        "root_cause": identify_root_cause(spans, incident_trace),
        "error_rate_pct": error_rate_pct(roots),
        "p95_latency_ms": p95_latency_ms(roots),
    }


def run_incident_summary(path: Path = TRACES_PATH) -> dict[str, Any]:
    return summarize_incident(load_traces(path))


if __name__ == "__main__":
    print(json.dumps(run_incident_summary(), indent=2))
