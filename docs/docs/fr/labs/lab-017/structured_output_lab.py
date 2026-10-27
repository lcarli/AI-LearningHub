"""Validate a compact structured-output contract."""
import unittest

ALLOWED = {"sku", "quantity", "priority"}

def validate(value):
    if set(value) != ALLOWED:
        return False
    return (
        isinstance(value["sku"], str)
        and isinstance(value["quantity"], int)
        and value["quantity"] > 0
        and value["priority"] in {"normal", "urgent"}
    )

class Tests(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(validate({"sku": "TENT-1", "quantity": 2, "priority": "normal"}))
    def test_extra_property(self):
        self.assertFalse(validate({"sku": "TENT-1", "quantity": 2, "priority": "normal", "debug": True}))

if __name__ == "__main__":
    unittest.main()
