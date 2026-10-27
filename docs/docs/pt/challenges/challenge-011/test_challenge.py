import json
import unittest
from pathlib import Path

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads(Path("rag_eval_plan.json").read_text())
    def test_golden_set_and_thresholds(self):
        self.assertGreaterEqual(len(self.plan["golden_queries"]), 2)
        self.assertEqual(self.plan["thresholds"]["unsupported_claims"], 0)
        self.assertGreaterEqual(self.plan["thresholds"]["citation_coverage"], 1.0)
    def test_candidate_is_explicit(self):
        self.assertIn("chunk_words", self.plan["candidate"])
        self.assertIn("top_k", self.plan["candidate"])

if __name__ == "__main__":
    unittest.main()
