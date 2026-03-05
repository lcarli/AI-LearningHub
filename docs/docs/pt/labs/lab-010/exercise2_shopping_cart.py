# exercise2_shopping_cart.py
# 🐛 BUG HUNT — This file has 4 bugs. Use Copilot Chat to find and fix them.
#
# SCENARIO: OutdoorGear Inc. shopping cart logic.
# The cart should:
#   - Add items with a quantity
#   - Calculate total price (sum of price × quantity)
#   - Apply a 10% discount on orders over $200
#   - Count unique items (not total quantity)
#
# EXPECTED OUTPUT:
#   Cart with 2x TrailBlazer ($189.99) + 1x Summit Tent ($349):
#   total before discount = $728.98
#   total after 10% discount = $656.08
#   unique_items = 2
#
# HOW TO USE:
#   1. Copy this file into VS Code
#   2. Try to run it: python exercise2_shopping_cart.py
#   3. Read the errors — but DON'T fix manually yet!
#   4. Select all code → Copilot Chat → /fix
#   5. Ask Copilot to explain EACH bug before fixing
#   6. Verify with the tests at the bottom

class ShoppingCart:
    def __init__(self):
        self.items = {}  # {product_name: {"price": float, "quantity": int}}
    
    def add_item(self, name: str, price: float, quantity: int = 1):
        if name in self.items:
            self.items[name]["quantity"] += quantity
        else:
            self.items[name] = {"price": price, "quantity": quantity}
    
    def get_total(self) -> float:
        """Calculate total price, applying 10% discount if over $200."""
        total = 0
        for item in self.items:            # BUG 1: iterating over keys only, not values
            total += item["price"] * item["quantity"]
        
        if total > 200:
            total = total * 0.90           # BUG 2: discount calculation correct, but...
                                           # should return rounded to 2 decimal places
        return total
    
    def count_unique_items(self) -> int:
        """Return the number of unique products (not total quantity)."""
        return sum(self.items.values())    # BUG 3: wrong — should be len(), not sum()
    
    def get_receipt(self) -> str:
        lines = []
        for name, details in self.items.items():
            subtotal = details["price"] + details["quantity"]  # BUG 4: + instead of *
            lines.append(f"  {name} x{details['quantity']} @ ${details['price']:.2f} = ${subtotal:.2f}")
        total = self.get_total()
        lines.append(f"\nTotal: ${total:.2f}")
        return "\n".join(lines)


# --- Tests ---
if __name__ == "__main__":
    cart = ShoppingCart()
    cart.add_item("TrailBlazer X200", 189.99, 2)
    cart.add_item("Summit Pro Tent", 349.00, 1)

    total = cart.get_total()
    unique = cart.count_unique_items()
    
    print(cart.get_receipt())
    print(f"\nUnique items: {unique}")
    
    assert unique == 2, f"Expected 2 unique items, got {unique}"
    assert abs(total - 656.08) < 0.01, f"Expected $656.08, got ${total}"
    print("\n✅ All tests passed!")
