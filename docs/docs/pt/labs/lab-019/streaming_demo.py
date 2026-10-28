"""Replay typed streaming events."""
import unittest

EVENTS = [
    {"type": "response.started"},
    {"type": "content.delta", "text": "Water"},
    {"type": "content.delta", "text": "proof"},
    {"type": "response.completed", "usage": {"input": 12, "output": 2}},
]

def render(events):
    return "".join(event.get("text", "") for event in events if event["type"] == "content.delta")

class Tests(unittest.TestCase):
    def test_render(self):
        self.assertEqual(render(EVENTS), "Waterproof")
    def test_completion_has_usage(self):
        self.assertIn("usage", EVENTS[-1])

if __name__ == "__main__":
    unittest.main()
