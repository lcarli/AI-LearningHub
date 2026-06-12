"""Acceptance tests for Challenge 006.

Run:
    python -m pytest test_observability.py
"""

from __future__ import annotations

from starter_observability import (
    agent_spans,
    error_rate_pct,
    find_incident_trace,
    identify_root_cause,
    load_traces,
    p95_latency_ms,
    summarize_incident,
)


def test_agent_spans_returns_root_agent_requests_only():
    spans = load_traces()
    roots = agent_spans(spans)

    assert [span["trace_id"] for span in roots] == ["tr-001", "tr-002", "tr-003", "tr-004"]
    assert all(span["kind"] == "agent" and span["parent_id"] is None for span in roots)


def test_error_rate_uses_root_agent_requests():
    roots = agent_spans(load_traces())

    assert error_rate_pct(roots) == 25.0


def test_p95_latency_uses_nearest_rank_over_root_requests():
    roots = agent_spans(load_traces())

    assert p95_latency_ms(roots) == 2200


def test_find_incident_trace_returns_failed_root_request():
    assert find_incident_trace(load_traces()) == "tr-003"


def test_identify_root_cause_reports_failing_dependency():
    spans = load_traces()

    assert identify_root_cause(spans, "tr-003") == "inventory_api_timeout"


def test_summarize_incident_returns_expected_report():
    summary = summarize_incident(load_traces())

    assert summary == {
        "incident_trace": "tr-003",
        "root_cause": "inventory_api_timeout",
        "error_rate_pct": 25.0,
        "p95_latency_ms": 2200,
    }
