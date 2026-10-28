import json
import unittest
from pathlib import Path

class Phase3ScenarioTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(Path("scenario.json").read_text(encoding="utf-8"))

    def test_identity_and_steps(self):
        self.assertEqual(self.data["lab"], "014")
        self.assertEqual(len(self.data["steps"]), 4)

    def test_free_first_contract(self):
        self.assertEqual(self.data["required_route"], "local")
        self.assertFalse(self.data["credentials_required"])

    def test_real_path_guardrails(self):
        real = self.data["real_path"]
        self.assertTrue(real["optional"])
        self.assertTrue(real["cost_cap_required"])
        self.assertTrue(real["cleanup_required"])

if __name__ == "__main__":
    unittest.main()
