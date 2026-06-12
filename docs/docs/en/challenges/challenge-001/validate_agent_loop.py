"""Generate the completion code for Challenge 001.

Run after your implementation passes the tests:
    python validate_agent_loop.py
"""

from __future__ import annotations

import hashlib
import json

from starter_agent_loop import load_products, recommend_bundle, run_agent, search_products


def completion_code() -> str:
    products = load_products()
    search_skus = [
        item["sku"]
        for item in search_products(
            products,
            category="jacket",
            query="waterproof hiking",
            max_price=150,
            in_stock_only=True,
        )
    ]
    bundle_skus = sorted(
        item["sku"]
        for item in recommend_bundle(products, activity="camping", budget=170)
    )
    jacket_trace = run_agent("I need a waterproof hiking jacket under $150")["trace"]
    bundle_trace = run_agent("Build a weekend camping bundle under $170")["trace"]

    payload = {
        "challenge": "001-agent-loop",
        "search_skus": search_skus,
        "bundle_skus": bundle_skus,
        "tools": [jacket_trace[0]["tool"], bundle_trace[0]["tool"]],
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:8].upper()
    return f"CH001-{digest}"


if __name__ == "__main__":
    print(completion_code())
