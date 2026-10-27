import json
import unittest
from pathlib import Path

class Tests(unittest.TestCase):
    def test_boundaries(self):
        data = json.loads(Path("sdk_agent_contract.json").read_text())
        self.assertIn("cancellation", data["host"]["owns"])
        self.assertIn("authorization-boundary", data["mcp"]["owns"])
        self.assertIn(data["provider"]["mode"], {"copilot-or-local-byok"})

if __name__ == "__main__":
    unittest.main()
