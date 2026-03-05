"""
broken_plugin.py — OutdoorGear SK Plugin — INTENTIONALLY BROKEN

Lab 023: SK Plugins & Memory — Interactive Bug-Fix Exercise

This file contains 3 deliberate bugs in the Semantic Kernel plugin implementation.
Your task is to:
  1. Read the BUG comment near each issue
  2. Understand why it fails
  3. Fix it — then run the test at the bottom to verify

Prerequisites:
  pip install semantic-kernel openai
  export GITHUB_TOKEN=<your PAT>

Run:
  python broken_plugin.py

Expected output when all bugs are fixed:
  ✅ search_products: found 3 tents
  ✅ get_cart_total: $539.98
  ✅ calculate_price_with_tax: $269.99
"""

import asyncio
import os

import semantic_kernel as sk
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.functions import kernel_function


# ─────────────────────────────────────────────────────────────────────────────
# Data: OutdoorGear product catalog
# ─────────────────────────────────────────────────────────────────────────────
PRODUCTS = [
    {"id": "P001", "name": "TrailBlazer Tent 2P",          "category": "Tents",         "price": 249.99},
    {"id": "P002", "name": "Summit Dome 4P",                "category": "Tents",         "price": 549.99},
    {"id": "P003", "name": "TrailBlazer Solo",              "category": "Tents",         "price": 299.99},
    {"id": "P004", "name": "ArcticDown -20°C Sleeping Bag", "category": "Sleeping Bags", "price": 389.99},
    {"id": "P005", "name": "SummerLight +5°C Sleeping Bag", "category": "Sleeping Bags", "price": 149.99},
    {"id": "P006", "name": "Osprey Atmos 65L Backpack",     "category": "Backpacks",     "price": 289.99},
    {"id": "P007", "name": "DayHiker 22L Daypack",          "category": "Backpacks",     "price":  89.99},
]

# Shopping cart: list of (product_id, quantity)
CART = [
    ("P001", 1),  # TrailBlazer Tent 2P  × 1 = $249.99
    ("P007", 1),  # DayHiker 22L Daypack × 1 =  $89.99
    # Expected total: $339.98
]


# ─────────────────────────────────────────────────────────────────────────────
# The Plugin class
# ─────────────────────────────────────────────────────────────────────────────
class OutdoorGearPlugin:
    """
    SK Plugin for querying the OutdoorGear product catalog and shopping cart.
    """

    # =========================================================================
    # FUNCTION 1: search_products
    #
    # ❌ BUG #1 — Wrong decorator: missing @kernel_function
    #
    # Expected: Semantic Kernel discovers and can invoke this function
    # Actual:   SK ignores this method — it is not registered as a kernel function
    #
    # Hint: SK discovers plugin functions by looking for the @kernel_function decorator.
    #       Without it, the function is invisible to the kernel.
    # Fix:  Add @kernel_function(description="...") above the def statement.
    # =========================================================================
    # BUG #1: @kernel_function decorator is missing — add it here
    def search_products(
        self,
        keyword: str,
        category: str = "",
    ) -> str:
        """Search for OutdoorGear products by keyword and optional category."""
        keyword_lower = keyword.lower()
        results = [
            p for p in PRODUCTS
            if keyword_lower in p["name"].lower()
            and (not category or p["category"] == category)
        ]
        if not results:
            return f"No products found for keyword '{keyword}'"
        lines = [f"[{p['id']}] {p['name']} — ${p['price']:.2f}" for p in results]
        return "\n".join(lines)

    # =========================================================================
    # FUNCTION 2: get_cart_total
    #
    # ❌ BUG #2 — Logic error: calculates count instead of price total
    #
    # Expected: Returns the sum of (price × quantity) for all cart items → "$339.98"
    # Actual:   Returns the number of cart items → "2" (always a small integer)
    #
    # Hint: The loop accumulates `quantity` instead of `price * quantity`.
    # Fix:  Change `total += quantity` to `total += price * quantity`.
    # =========================================================================
    @kernel_function(description="Get the total price of all items in the shopping cart")
    def get_cart_total(self) -> str:
        """Returns the current shopping cart total as a formatted string."""
        total = 0.0
        for product_id, quantity in CART:
            product = next((p for p in PRODUCTS if p["id"] == product_id), None)
            if product:
                price = product["price"]
                total += quantity  # ← BUG #2: should be `total += price * quantity`
        return f"${total:.2f}"

    # =========================================================================
    # FUNCTION 3: calculate_price_with_tax
    #
    # ❌ BUG #3 — Tax calculation applied twice (compounding error)
    #
    # Expected: calculate_price_with_tax("P001", 0.08)
    #           → "$269.99" (249.99 × 1.08 = 269.9892 ≈ $269.99)
    # Actual:   → "$291.59" (249.99 × 1.08 × 1.08 — tax applied twice!)
    #
    # Hint: The tax is added to the price once, then the result is multiplied
    #       by (1 + tax_rate) again.
    # Fix:  Keep only one tax multiplication.
    # =========================================================================
    @kernel_function(description="Calculate the final price of a product including tax")
    def calculate_price_with_tax(
        self,
        product_id: str,
        tax_rate: float = 0.08,
    ) -> str:
        """
        Calculate a product's final price after applying sales tax.

        Args:
            product_id: The product ID (e.g. 'P001')
            tax_rate: Tax rate as a decimal (e.g. 0.08 for 8%). Default: 0.08
        """
        product = next((p for p in PRODUCTS if p["id"] == product_id), None)
        if product is None:
            return f"Product '{product_id}' not found"

        base_price = product["price"]

        # BUG #3: tax is applied twice
        price_with_tax = base_price + (base_price * tax_rate)  # first tax application
        final_price = price_with_tax * (1 + tax_rate)          # ← BUG: second tax application

        return f"${final_price:.2f}"


# ─────────────────────────────────────────────────────────────────────────────
# Test runner (verifies each function independently, no LLM needed for unit tests)
# ─────────────────────────────────────────────────────────────────────────────
def run_unit_tests():
    """Run tests directly on the plugin (no SK kernel needed)."""
    plugin = OutdoorGearPlugin()
    all_passed = True

    # Test 1: search_products
    print("\nTest 1: search_products('tent')")
    result = plugin.search_products("tent")
    count = result.count("[P")
    if count == 3:
        print(f"  ✅ Passed — found 3 tents")
    else:
        print(f"  ❌ Failed — expected 3 tents, got: {repr(result[:100])}")
        all_passed = False

    # Test 2: get_cart_total
    print("\nTest 2: get_cart_total()")
    result = plugin.get_cart_total()
    if result == "$339.98":
        print(f"  ✅ Passed — cart total = {result}")
    else:
        print(f"  ❌ Failed — expected $339.98, got: {result}")
        all_passed = False

    # Test 3: calculate_price_with_tax
    print("\nTest 3: calculate_price_with_tax('P001', 0.08)")
    result = plugin.calculate_price_with_tax("P001", 0.08)
    if result == "$269.99":
        print(f"  ✅ Passed — price with tax = {result}")
    else:
        print(f"  ❌ Failed — expected $269.99, got: {result}")
        all_passed = False

    print()
    if all_passed:
        print("🎉 All tests passed! Your plugin is bug-free.")
    else:
        print("🔧 Some tests failed. Review the BUG comments and try again.")

    return all_passed


# ─────────────────────────────────────────────────────────────────────────────
# SK integration test (uses GitHub Models — requires GITHUB_TOKEN)
# ─────────────────────────────────────────────────────────────────────────────
async def run_sk_integration_test():
    """Run a full SK agent invocation to verify the plugin is discoverable."""
    print("\n--- SK Integration Test (requires GITHUB_TOKEN) ---")

    kernel = sk.Kernel()
    kernel.add_service(
        OpenAIChatCompletion(
            ai_model_id="gpt-4o-mini",
            api_key=os.environ["GITHUB_TOKEN"],
            base_url="https://models.inference.ai.azure.com",
        )
    )

    plugin = kernel.add_plugin(OutdoorGearPlugin(), plugin_name="OutdoorGear")

    # List what SK discovered
    discovered = [name for name in plugin.functions]
    print(f"SK discovered {len(discovered)} functions: {discovered}")

    if "search_products" not in discovered:
        print("  ⚠️  search_products not discovered — did you add @kernel_function? (Bug #1)")
    else:
        print("  ✅ search_products is registered in the kernel")


if __name__ == "__main__":
    # Unit tests first (no API calls needed)
    unit_pass = run_unit_tests()

    # SK integration test (tests plugin discovery)
    if os.environ.get("GITHUB_TOKEN"):
        asyncio.run(run_sk_integration_test())
    else:
        print("\n(Skipping SK integration test — set GITHUB_TOKEN to enable)")
