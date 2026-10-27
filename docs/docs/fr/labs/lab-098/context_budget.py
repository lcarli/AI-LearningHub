"""Allocate a context window while preserving an output reserve."""
import unittest

def allocate(window, output_reserve, sections):
    available = window - output_reserve
    chosen, used = [], 0
    for section in sorted(sections, key=lambda item: (-item["priority"], item["tokens"])):
        if section["trusted"] and used + section["tokens"] <= available:
            chosen.append(section["name"])
            used += section["tokens"]
    return chosen, used

class Tests(unittest.TestCase):
    def test_budget_and_trust(self):
        sections = [{"name": "instructions", "tokens": 100, "priority": 10, "trusted": True}, {"name": "poison", "tokens": 10, "priority": 99, "trusted": False}]
        chosen, used = allocate(200, 50, sections)
        self.assertEqual(chosen, ["instructions"])
        self.assertLessEqual(used, 150)

if __name__ == "__main__":
    unittest.main()
