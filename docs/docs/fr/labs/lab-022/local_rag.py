"""Dependency-free chunk, embed, search, and answer pipeline."""
import json
import math
import re
import unittest
from pathlib import Path

def chunks(text, words=12):
    tokens = text.split()
    return [" ".join(tokens[i:i+words]) for i in range(0, len(tokens), words)]

def embed(text, dims=64):
    vector = [0.0] * dims
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        vector[sum(map(ord, token)) % dims] += 1
    return vector

def cosine(a, b):
    dot = sum(x*y for x, y in zip(a, b))
    norm = math.sqrt(sum(x*x for x in a) * sum(y*y for y in b))
    return dot / norm if norm else 0

def search(query, docs, top_k=2):
    q = embed(query)
    ranked = sorted(((cosine(q, embed(d["text"])), d) for d in docs), reverse=True, key=lambda x: x[0])
    return ranked[:top_k]

class Tests(unittest.TestCase):
    def test_tent_retrieval(self):
        docs = json.loads(Path(__file__).with_name("documents.json").read_text())
        self.assertEqual(search("waterproof two person tent", docs, 1)[0][1]["id"], "tent")

if __name__ == "__main__":
    unittest.main()
