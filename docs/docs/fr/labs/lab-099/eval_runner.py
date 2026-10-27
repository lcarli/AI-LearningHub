"""Deterministic baseline for a golden-set regression gate."""
import json
import unittest
from pathlib import Path

def load():
    return [json.loads(line) for line in Path(__file__).with_name("eval_dataset.jsonl").read_text().splitlines()]

def deterministic_pass(case):
    return case["expected"].lower() in case["candidate"].lower() if case["expected"] != "unknown" else "always" not in case["candidate"].lower()

def pass_rate(cases):
    return sum(deterministic_pass(case) for case in cases) / len(cases)

class Tests(unittest.TestCase):
    def test_regression_gate(self):
        self.assertGreaterEqual(pass_rate(load()), 0.5)

if __name__ == "__main__":
    unittest.main()
