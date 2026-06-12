"""Challenge 008 starter: build a fully local mini-agent.

Goal: make all tests in test_local_agent.py pass.
Use only the Python standard library. No network calls.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


DATA_PATH = Path(__file__).with_name("local_data.json")
REQUESTS_PATH = Path(__file__).with_name("eval_requests.json")


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def assert_no_cloud_config() -> bool:
    """Return True only if the implementation is local-only."""
    # Broken: this pretends cloud configuration is required.
    return False


def classify_intent(text: str) -> str:
    """Classify request intent using local deterministic logic."""
    # Broken: routes everything to product search.
    return "product_search"


def search_products(data: dict[str, Any], text: str) -> list[dict[str, Any]]:
    """Find in-stock products matching request keywords."""
    # Broken: returns every product.
    return data["products"]


def lookup_policy(data: dict[str, Any], text: str) -> str:
    """Return the relevant local policy text."""
    # Broken: returns the first policy regardless of request.
    return data["policies"][0]["text"]


def recommend_bundle(data: dict[str, Any], budget: float) -> list[dict[str, Any]]:
    """Return an in-stock camping bundle within budget."""
    # Broken: ignores budget.
    return data["products"]


def run_local_agent(text: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Route a request to local tools and return intent, answer, and trace."""
    data = data or load_json(DATA_PATH)
    intent = classify_intent(text)
    trace = [{"type": "intent", "value": intent}]

    if intent == "product_search":
        products = search_products(data, text)
        answer = ", ".join(item["name"] for item in products)
        trace.append({"type": "tool", "name": "search_products"})
    elif intent == "policy_lookup":
        answer = lookup_policy(data, text)
        trace.append({"type": "tool", "name": "lookup_policy"})
    elif intent == "bundle_recommendation":
        match = re.search(r"\$?(\d+)", text)
        budget = float(match.group(1)) if match else 0.0
        bundle = recommend_bundle(data, budget)
        answer = ", ".join(item["name"] for item in bundle)
        trace.append({"type": "tool", "name": "recommend_bundle"})
    else:
        raise ValueError(f"Unsupported intent: {intent}")

    return {"intent": intent, "answer": answer, "trace": trace, "uses_cloud": not assert_no_cloud_config()}


def evaluate_local_agent(
    requests: list[dict[str, str]],
    data: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate local-only behavior against fixture requests."""
    intents: list[str] = []
    required_outputs: list[str] = []
    successful = 0
    uses_cloud = False

    for request in requests:
        result = run_local_agent(request["text"], data)
        intents.append(result["intent"])
        uses_cloud = uses_cloud or result["uses_cloud"]
        if request["required_output"] in result["answer"] and result["intent"] == request["expected_intent"]:
            successful += 1
            required_outputs.append(request["required_output"])

    return {
        "intents": intents,
        "successful_requests": successful,
        "uses_cloud": uses_cloud,
        "required_outputs": required_outputs,
    }


def run_eval(
    data_path: Path = DATA_PATH,
    requests_path: Path = REQUESTS_PATH,
) -> dict[str, Any]:
    return evaluate_local_agent(load_json(requests_path), load_json(data_path))


if __name__ == "__main__":
    print(json.dumps(run_eval(), indent=2))
