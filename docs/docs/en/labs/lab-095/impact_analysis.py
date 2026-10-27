"""Analyze fictional Copilot, DORA, and SPACE signals."""
import csv
import unittest
from pathlib import Path

def load():
    with Path(__file__).with_name("copilot_metrics.csv").open() as handle:
        return list(csv.DictReader(handle))

def adoption(row):
    return int(row["active"]) / int(row["eligible"])

def acceptance(row):
    shown = int(row["shown_suggestions"])
    return int(row["accepted_suggestions"]) / shown if shown else 0

class Tests(unittest.TestCase):
    def test_metrics(self):
        before, after = load()
        self.assertGreater(adoption(after), adoption(before))
        self.assertAlmostEqual(acceptance(after), 0.575)

if __name__ == "__main__":
    unittest.main()
