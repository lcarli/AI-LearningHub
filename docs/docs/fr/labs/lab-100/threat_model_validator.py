import json
import unittest
from pathlib import Path

def load():
    return json.loads(Path(__file__).with_name("threat_model.json").read_text())

class Tests(unittest.TestCase):
    def test_complete_threats(self):
        model = load()
        self.assertGreaterEqual(len(model["assets"]), 3)
        self.assertTrue(all(t.get("id") and t.get("control") for t in model["threats"]))

if __name__ == "__main__":
    unittest.main()
