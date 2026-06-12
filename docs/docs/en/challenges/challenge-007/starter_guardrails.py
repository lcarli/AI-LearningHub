"""Challenge 007 starter: red-team and harden simple agent guardrails.

Goal: make all tests in test_guardrails.py pass.
Use only the Python standard library.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


SCENARIOS_PATH = Path(__file__).with_name("scenarios.json")


def load_scenarios(path: Path = SCENARIOS_PATH) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def classify_scenario(text: str) -> str:
    """Classify input as allow, block, or redact."""
    # Broken: allows everything.
    return "allow"


def redact_pii(text: str) -> str:
    """Redact obvious PII before the agent sees the message."""
    # Broken: does not redact email addresses.
    return text


def apply_guardrails(text: str) -> dict[str, str]:
    """Apply guardrails and return action plus safe_text."""
    action = classify_scenario(text)
    return {"action": action, "safe_text": text}


def evaluate_guardrails(scenarios: list[dict[str, str]]) -> dict[str, int]:
    """Evaluate red-team outcomes."""
    allowed = blocked = redacted = false_positive = 0

    for scenario in scenarios:
        result = apply_guardrails(scenario["text"])
        action = result["action"]
        expected = scenario["expected"]
        if action == "allow":
            allowed += 1
        if action == "block":
            blocked += 1
        if action == "redact":
            redacted += 1
        if expected == "allow" and action != "allow":
            false_positive += 1

    return {
        "allowed": allowed,
        "blocked": blocked,
        "redacted": redacted,
        "false_positive": false_positive,
    }


def run_guardrail_suite(path: Path = SCENARIOS_PATH) -> dict[str, int]:
    return evaluate_guardrails(load_scenarios(path))


if __name__ == "__main__":
    print(json.dumps(run_guardrail_suite(), indent=2))
