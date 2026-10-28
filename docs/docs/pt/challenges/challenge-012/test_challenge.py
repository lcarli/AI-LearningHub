import json
import unittest
from pathlib import Path

class Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads(Path("security_plan.json").read_text())
    def test_attack_defense_pairing(self):
        self.assertEqual(len(self.plan["attacks"]), len(self.plan["controls"]))
        self.assertGreaterEqual(len(self.plan["attacks"]), 4)
    def test_owasp_mapping(self):
        self.assertTrue(self.plan["owasp_mapping_required"])

if __name__ == "__main__":
    unittest.main()
