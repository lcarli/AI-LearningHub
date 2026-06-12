"""Challenge 001 starter: build a small agent loop from scratch.

Goal: make all tests in test_agent_loop.py pass without using an agent framework.
You may use only the Python standard library.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


DATA_PATH = Path(__file__).with_name("products.json")


@dataclass
class AgentState:
    user_request: str
    observations: list[dict[str, Any]] = field(default_factory=list)
    trace: list[dict[str, Any]] = field(default_factory=list)
    final_answer: str | None = None
    parsed: dict[str, Any] = field(default_factory=dict)


def load_products(path: Path = DATA_PATH) -> list[dict[str, Any]]:
    """Load the OutdoorGear product catalog."""
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def search_products(
    products: list[dict[str, Any]],
    *,
    category: str | None = None,
    query: str | None = None,
    max_price: float | None = None,
    in_stock_only: bool = True,
) -> list[dict[str, Any]]:
    """Return products matching category, query words, price, and stock filters."""
    raise NotImplementedError("Filter products by category, query, max_price, and stock.")


def get_product_details(products: list[dict[str, Any]], sku: str) -> dict[str, Any]:
    """Return one product by SKU, or raise ValueError if it does not exist."""
    raise NotImplementedError("Find the product with the requested SKU.")


def recommend_bundle(
    products: list[dict[str, Any]],
    *,
    activity: str,
    budget: float,
) -> list[dict[str, Any]]:
    """Build a useful in-stock bundle for an activity without exceeding budget."""
    raise NotImplementedError("Select a bundle that fits the activity and budget.")


def parse_request(user_request: str) -> dict[str, Any]:
    """Extract enough structure from the user request to drive tool selection."""
    raise NotImplementedError("Extract intent, category or activity, budget, and SKU if present.")


def choose_next_action(state: AgentState) -> dict[str, Any]:
    """Return the next action as {'type': 'tool'|'final', ...}."""
    raise NotImplementedError("Choose the next tool call or final answer based on state.")


def execute_tool(
    products: list[dict[str, Any]],
    tool_name: str,
    arguments: dict[str, Any],
) -> Any:
    """Execute one of the allowed tools by name."""
    raise NotImplementedError("Dispatch to search_products, get_product_details, or recommend_bundle.")


def format_answer(state: AgentState) -> str:
    """Turn the latest observation into a concise user-facing answer."""
    raise NotImplementedError("Summarize the tool result with product names, prices, and rationale.")


def run_agent(
    user_request: str,
    *,
    products_path: Path = DATA_PATH,
    max_steps: int = 5,
) -> dict[str, Any]:
    """Run perceive -> decide -> act -> observe until the agent can answer."""
    products = load_products(products_path)
    state = AgentState(user_request=user_request)
    state.parsed = parse_request(user_request)

    for step in range(max_steps):
        action = choose_next_action(state)
        action_type = action.get("type")

        if action_type == "final":
            state.final_answer = format_answer(state)
            state.trace.append({"step": step + 1, "type": "final"})
            return {"final_answer": state.final_answer, "trace": state.trace}

        if action_type != "tool":
            raise ValueError(f"Unknown action type: {action_type!r}")

        tool_name = action["tool"]
        arguments = action.get("arguments", {})
        result = execute_tool(products, tool_name, arguments)
        state.observations.append({"tool": tool_name, "result": result})
        state.trace.append({"step": step + 1, "type": "tool", "tool": tool_name, "arguments": arguments})

    raise RuntimeError("Agent reached max_steps without producing a final answer.")


if __name__ == "__main__":
    answer = run_agent("I need a waterproof hiking jacket under $150")
    print(answer["final_answer"])
