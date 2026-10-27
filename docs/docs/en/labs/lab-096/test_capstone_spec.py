import unittest
from pathlib import Path

class Tests(unittest.TestCase):
    def test_required_sections(self):
        text = Path("capstone_spec.md").read_text().lower()
        for heading in ("goal", "non-goals", "acceptance criteria", "risks and approvals", "validation", "deployment and rollback"):
            self.assertIn(f"## {heading}", text)

if __name__ == "__main__":
    unittest.main()
