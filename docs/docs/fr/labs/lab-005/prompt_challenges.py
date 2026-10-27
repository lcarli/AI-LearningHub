"""Score whether a prompt contains an executable contract."""
import unittest

FIELDS = ("goal:", "context:", "constraints:", "output:", "validation:")

def score(prompt):
    lowered = prompt.lower()
    return sum(field in lowered for field in FIELDS)

class Tests(unittest.TestCase):
    def test_structured_prompt(self):
        prompt = "Goal: fix parser\nContext: parser.py\nConstraints: no API change\nOutput: patch\nValidation: pytest"
        self.assertEqual(score(prompt), 5)
    def test_vague_prompt(self):
        self.assertLess(score("make it better"), 2)

if __name__ == "__main__":
    unittest.main()
