import json
import unittest
from pathlib import Path

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads(Path("spec_to_pr_plan.json").read_text())
    def test_scope_and_acceptance(self):
        self.assertTrue(self.plan["goal"])
        self.assertTrue(self.plan["non_goals"])
        self.assertGreaterEqual(len(self.plan["acceptance_criteria"]), 3)
    def test_bounded_execution(self):
        self.assertGreaterEqual(len(self.plan["steps"]), 4)
        self.assertTrue(any("test" in command for command in self.plan["validation_commands"]))

if __name__ == "__main__":
    unittest.main()
