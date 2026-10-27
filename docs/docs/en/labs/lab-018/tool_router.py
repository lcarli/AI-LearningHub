"""Typed tool router with explicit approval."""
import unittest

def route(request, approved=False):
    if request.get("tool") != "inventory.adjust":
        return "deny:unknown-tool"
    args = request.get("arguments", {})
    if set(args) != {"sku", "delta"} or not isinstance(args["delta"], int) or abs(args["delta"]) > 20:
        return "deny:invalid-arguments"
    if args["delta"] != 0 and not approved:
        return "approval-required"
    return "executed"

class Tests(unittest.TestCase):
    def test_approval(self):
        req = {"tool": "inventory.adjust", "arguments": {"sku": "T1", "delta": -1}}
        self.assertEqual(route(req), "approval-required")
        self.assertEqual(route(req, approved=True), "executed")

if __name__ == "__main__":
    unittest.main()
