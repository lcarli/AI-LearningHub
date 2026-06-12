"""Tests for Challenge 001.

Run:
    python -m pytest test_agent_loop.py
"""

from __future__ import annotations

from starter_agent_loop import (
    get_product_details,
    load_products,
    recommend_bundle,
    run_agent,
    search_products,
)


def test_search_filters_by_category_query_budget_and_stock():
    products = load_products()

    matches = search_products(
        products,
        category="jacket",
        query="waterproof hiking",
        max_price=150,
        in_stock_only=True,
    )

    assert [item["sku"] for item in matches] == ["JKT-RAIN-001"]


def test_get_product_details_returns_requested_sku():
    products = load_products()

    item = get_product_details(products, "STOVE-MINI-006")

    assert item["name"] == "SparkMini Camp Stove"
    assert item["price"] == 44.99


def test_recommend_bundle_respects_activity_budget_and_stock():
    products = load_products()

    bundle = recommend_bundle(products, activity="camping", budget=170)

    assert bundle
    assert sum(item["price"] for item in bundle) <= 170
    assert all(item["in_stock"] for item in bundle)
    assert {item["sku"] for item in bundle} >= {"PAD-INS-005", "STOVE-MINI-006", "LAMP-LED-008"}


def test_agent_loop_uses_search_tool_before_answering():
    result = run_agent("I need a waterproof hiking jacket under $150")

    assert "RainShell Pro Jacket" in result["final_answer"]
    assert "$129.99" in result["final_answer"]
    assert [step["type"] for step in result["trace"]] == ["tool", "final"]
    assert result["trace"][0]["tool"] == "search_products"


def test_agent_loop_can_answer_bundle_request():
    result = run_agent("Build a weekend camping bundle under $170")

    assert "BaseCamp Insulated Pad" in result["final_answer"]
    assert "SparkMini Camp Stove" in result["final_answer"]
    assert "TrailGlow Headlamp" in result["final_answer"]
    assert [step["type"] for step in result["trace"]] == ["tool", "final"]
    assert result["trace"][0]["tool"] == "recommend_bundle"
