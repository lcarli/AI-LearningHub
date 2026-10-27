"""Dependency-free local similarity explorer."""
import math
import re
import unittest

def vectorize(text, dims=64):
    vector = [0.0] * dims
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        vector[sum(ord(c) for c in token) % dims] += 1.0
    return vector

def cosine(a, b):
    dot = sum(x*y for x, y in zip(a, b))
    norm = math.sqrt(sum(x*x for x in a) * sum(y*y for y in b))
    return dot / norm if norm else 0.0

def search(query, documents):
    q = vectorize(query)
    return sorted(((cosine(q, vectorize(text)), name) for name, text in documents.items()), reverse=True)

class Tests(unittest.TestCase):
    def test_exact_topic_ranks_first(self):
        docs = {"tent": "waterproof camping tent", "boot": "leather hiking boot"}
        self.assertEqual(search("waterproof tent", docs)[0][1], "tent")

if __name__ == "__main__":
    unittest.main()
