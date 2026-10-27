import unittest
from decimal import Decimal
from legacy_calculator import total

class Tests(unittest.TestCase):
    def test_rounding_and_quantity(self):
        self.assertEqual(total([{"price": "19.995", "quantity": 2}]), Decimal("39.99"))

if __name__ == "__main__":
    unittest.main()
