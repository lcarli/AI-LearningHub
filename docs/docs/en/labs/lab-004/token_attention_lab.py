"""Small deterministic token and attention explorer."""
import re
import unittest

def tokens(text):
    return re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)

def next_token(probabilities):
    return max(probabilities, key=probabilities.get)

def grounded(answer_terms, evidence_terms):
    return set(answer_terms).issubset(set(evidence_terms))

class Tests(unittest.TestCase):
    def test_tokenizer(self):
        self.assertEqual(tokens("Hello, world!"), ["Hello", ",", "world", "!"])
    def test_next_token(self):
        self.assertEqual(next_token({"tent": .7, "boot": .2, "pack": .1}), "tent")
    def test_grounding(self):
        self.assertTrue(grounded(["waterproof", "jacket"], ["waterproof", "jacket", "blue"]))

if __name__ == "__main__":
    unittest.main()
