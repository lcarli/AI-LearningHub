"""Challenge 005 starter: define and execute a safe MCP-style tool.

Goal: make all tests in test_mcp_tool.py pass.
Use only the Python standard library.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ORDERS_PATH = Path(__file__).with_name("orders.json")
REQUESTS_PATH = Path(__file__).with_name("tool_requests.json")


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def build_tool_manifest() -> dict[str, Any]:
    """Return the MCP-style tool definition for get_order_status."""
    # Broken: missing input schema and safety-focused description.
    return {"name": "get_order_status", "description": "Get order data"}


def validate_manifest(manifest: dict[str, Any]) -> bool:
    """Validate the required shape of the tool manifest."""
    # Broken: only checks the name.
    return manifest.get("name") == "get_order_status"


def validate_arguments(arguments: dict[str, Any]) -> dict[str, str]:
    """Accept only the tool arguments allowed by the manifest."""
    # Broken: accepts extra fields and missing order IDs.
    return arguments


def get_order_status(orders: list[dict[str, Any]], *, order_id: str) -> dict[str, Any]:
    """Return a safe order-status payload without exposing customer PII."""
    # Broken: returns the raw order, including email.
    for order in orders:
        if order["order_id"] == order_id:
            return order
    raise ValueError(f"Unknown order_id: {order_id}")


def execute_tool(
    tool_name: str,
    arguments: dict[str, Any],
    orders: list[dict[str, Any]],
) -> dict[str, Any]:
    """Validate and execute a supported tool call."""
    # Broken: no tool-name or argument validation.
    return get_order_status(orders, order_id=arguments.get("order_id", ""))


def evaluate_tool_contract(
    requests: list[dict[str, Any]],
    orders: list[dict[str, Any]],
) -> dict[str, Any]:
    """Evaluate manifest validity, request handling, and PII redaction."""
    manifest = build_tool_manifest()
    statuses: list[str] = []
    successful_requests = 0
    blocked_invalid = 0
    redacted = True

    for request in requests:
        try:
            result = execute_tool(request["tool"], request["arguments"], orders)
        except (ValueError, KeyError, TypeError):
            blocked_invalid += 1
            continue

        successful_requests += 1
        statuses.append(result.get("status"))
        if "customer_email" in result:
            redacted = False

    return {
        "valid_manifest": validate_manifest(manifest),
        "successful_requests": successful_requests,
        "blocked_invalid": blocked_invalid,
        "statuses": statuses,
        "redacted": redacted,
    }


def run_contract_suite(
    orders_path: Path = ORDERS_PATH,
    requests_path: Path = REQUESTS_PATH,
) -> dict[str, Any]:
    return evaluate_tool_contract(load_json(requests_path), load_json(orders_path))


if __name__ == "__main__":
    print(json.dumps(run_contract_suite(), indent=2))
