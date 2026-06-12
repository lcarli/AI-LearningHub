"""Acceptance tests for Challenge 005.

Run:
    python -m pytest test_mcp_tool.py
"""

from __future__ import annotations

import pytest

from starter_mcp_tool import (
    ORDERS_PATH,
    REQUESTS_PATH,
    build_tool_manifest,
    evaluate_tool_contract,
    execute_tool,
    get_order_status,
    load_json,
    validate_arguments,
    validate_manifest,
)


def test_manifest_has_safe_schema_contract():
    manifest = build_tool_manifest()

    assert validate_manifest(manifest) is True
    assert manifest["name"] == "get_order_status"
    assert "inputSchema" in manifest
    assert manifest["inputSchema"]["required"] == ["order_id"]
    assert manifest["inputSchema"]["properties"]["order_id"]["type"] == "string"
    assert "customer_email" not in json_like(manifest)


def test_validate_arguments_rejects_missing_or_extra_fields():
    assert validate_arguments({"order_id": "OG-1001"}) == {"order_id": "OG-1001"}

    with pytest.raises(ValueError):
        validate_arguments({})

    with pytest.raises(ValueError):
        validate_arguments({"order_id": "OG-1001", "customer_email": "avery@example.com"})


def test_get_order_status_redacts_pii():
    orders = load_json(ORDERS_PATH)

    result = get_order_status(orders, order_id="OG-1001")

    assert result["order_id"] == "OG-1001"
    assert result["status"] == "delivered"
    assert "customer_email" not in result
    assert result["tracking_number"].endswith("6784")


def test_execute_tool_blocks_unknown_tool_and_invalid_arguments():
    orders = load_json(ORDERS_PATH)

    assert execute_tool("get_order_status", {"order_id": "OG-1002"}, orders)["status"] == "processing"

    with pytest.raises(ValueError):
        execute_tool("delete_order", {"order_id": "OG-1002"}, orders)

    with pytest.raises(ValueError):
        execute_tool("get_order_status", {"order_id": "OG-1002", "customer_email": "sam@example.com"}, orders)


def test_evaluate_tool_contract_reports_expected_metrics():
    metrics = evaluate_tool_contract(load_json(REQUESTS_PATH), load_json(ORDERS_PATH))

    assert metrics["valid_manifest"] is True
    assert metrics["successful_requests"] == 2
    assert metrics["blocked_invalid"] == 1
    assert metrics["statuses"] == ["delivered", "processing"]
    assert metrics["redacted"] is True


def json_like(value) -> str:
    return repr(value).lower()
