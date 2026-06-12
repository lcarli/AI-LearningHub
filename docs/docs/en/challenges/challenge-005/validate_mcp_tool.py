"""Generate the completion code for Challenge 005.

Run after your implementation passes the tests:
    python validate_mcp_tool.py
"""

from __future__ import annotations

import hashlib
import json

from starter_mcp_tool import ORDERS_PATH, REQUESTS_PATH, evaluate_tool_contract, load_json


def completion_code() -> str:
    metrics = evaluate_tool_contract(load_json(REQUESTS_PATH), load_json(ORDERS_PATH))
    payload = {
        "challenge": "005-mcp-tool-builder",
        "valid_manifest": metrics["valid_manifest"],
        "successful_requests": metrics["successful_requests"],
        "blocked_invalid": metrics["blocked_invalid"],
        "statuses": metrics["statuses"],
        "redacted": metrics["redacted"],
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:8].upper()
    return f"CH005-{digest}"


if __name__ == "__main__":
    print(completion_code())
