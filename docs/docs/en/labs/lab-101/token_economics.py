"""Estimate token units without hardcoding vendor prices."""
import csv
import unittest
from pathlib import Path

def effective_units(row, cached_discount=0.5):
    uncached = int(row["input_tokens"]) - int(row["cached_tokens"])
    return (uncached + int(row["cached_tokens"]) * cached_discount + int(row["output_tokens"])) * int(row["requests"])

def load():
    with Path(__file__).with_name("cost_scenarios.csv").open() as handle:
        return list(csv.DictReader(handle))

class Tests(unittest.TestCase):
    def test_cache_reduces_units(self):
        row = load()[0]
        self.assertLess(effective_units(row), (int(row["input_tokens"]) + int(row["output_tokens"])) * int(row["requests"]))

if __name__ == "__main__":
    unittest.main()
