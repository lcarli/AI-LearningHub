"""Acceptance tests for Challenge 008.

Run:
    python -m pytest test_local_agent.py
"""

from __future__ import annotations

from starter_local_agent import (
    DATA_PATH,
    REQUESTS_PATH,
    assert_no_cloud_config,
    classify_intent,
    evaluate_local_agent,
    load_json,
    lookup_policy,
    recommend_bundle,
    run_local_agent,
    search_products,
)


def test_no_cloud_config_required():
    assert assert_no_cloud_config() is True


def test_classify_intent_routes_supported_requests():
    assert classify_intent("Find a waterproof hiking jacket") == "product_search"
    assert classify_intent("What is the return window?") == "policy_lookup"
    assert classify_intent("Build a camping bundle under $170") == "bundle_recommendation"


def test_search_products_returns_relevant_in_stock_match():
    data = load_json(DATA_PATH)

    matches = search_products(data, "Find a waterproof hiking jacket")

    assert [item["name"] for item in matches] == ["RainShell Pro Jacket"]


def test_lookup_policy_selects_relevant_policy():
    data = load_json(DATA_PATH)

    assert "60 days" in lookup_policy(data, "What is the return window?")
    assert "5-8 business days" in lookup_policy(data, "How long to ship to Canada?")


def test_recommend_bundle_respects_budget_and_activity():
    data = load_json(DATA_PATH)

    bundle = recommend_bundle(data, 170)

    assert sum(item["price"] for item in bundle) <= 170
    assert [item["name"] for item in bundle] == [
        "BaseCamp Insulated Pad",
        "SparkMini Camp Stove",
        "TrailGlow Headlamp",
    ]


def test_run_local_agent_returns_answer_trace_and_no_cloud():
    result = run_local_agent("Build a camping bundle under $170", load_json(DATA_PATH))

    assert result["intent"] == "bundle_recommendation"
    assert "TrailGlow Headlamp" in result["answer"]
    assert result["trace"][0]["type"] == "intent"
    assert result["trace"][1]["name"] == "recommend_bundle"
    assert result["uses_cloud"] is False


def test_evaluate_local_agent_reports_expected_results():
    metrics = evaluate_local_agent(load_json(REQUESTS_PATH), load_json(DATA_PATH))

    assert metrics == {
        "intents": ["product_search", "policy_lookup", "bundle_recommendation"],
        "successful_requests": 3,
        "uses_cloud": False,
        "required_outputs": ["RainShell Pro Jacket", "60 days", "TrailGlow Headlamp"],
    }
