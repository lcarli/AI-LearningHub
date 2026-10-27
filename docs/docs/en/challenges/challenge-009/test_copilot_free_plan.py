import json
import unittest
from pathlib import Path

class CopilotFreePlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads(Path("copilot_free_plan.json").read_text(encoding="utf-8"))

    def test_free_and_auto_model(self):
        self.assertIs(self.plan["free_only"], True)
        self.assertIs(self.plan["auto_model_selection"], True)

    def test_bounded_steps(self):
        self.assertGreaterEqual(len(self.plan["steps"]), 4)
        self.assertTrue(all(isinstance(step, str) and step.strip() for step in self.plan["steps"]))

    def test_local_validation_and_fallback(self):
        commands = " ".join(self.plan["validation_commands"]).lower()
        self.assertNotIn("azure", commands)
        self.assertNotIn("cloud agent", commands)
        self.assertTrue(self.plan["manual_fallback"].strip())

if __name__ == "__main__":
    unittest.main()
