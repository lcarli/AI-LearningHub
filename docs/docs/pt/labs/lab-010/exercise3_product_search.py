# exercise3_product_search.py
# 🐛 BUG HUNT + EXTEND — This file has 2 bugs AND is missing a feature.
#
# SCENARIO: OutdoorGear product search with filtering.
#
# TASK A (Fix): Find and fix the 2 bugs using Copilot /fix
# TASK B (Extend): Ask Copilot to add a sort_by_price() function
#   Prompt to use: "Add a sort_by_price(products, ascending=True) function
#                   that sorts the search results by price"
#
# EXPECTED OUTPUT after fixing:
#   search("boot")   → [{"name": "TrailBlazer X200", "price": 189.99, "category": "footwear"}]
#   search("tent")   → [{"name": "Summit Pro Tent",  "price": 349.00, "category": "camping"}]
#   search("xyz")    → []
#   search("")       → all 5 products
#
# HOW TO USE:
#   Step 1 — Fix bugs:  Select all → Copilot Chat → /fix
#   Step 2 — Extend:    Ctrl+I (inline chat) → type the prompt above
#   Step 3 — Test:      Run the tests at the bottom

CATALOG = [
    {"name": "TrailBlazer X200",      "price": 189.99, "category": "footwear"},
    {"name": "Summit Pro Tent",        "price": 349.00, "category": "camping"},
    {"name": "ClimbTech Pro Harness", "price": 129.99, "category": "climbing"},
    {"name": "OmniPack 45L",          "price": 279.99, "category": "packs"},
    {"name": "StormShell Jacket",      "price": 349.00, "category": "clothing"},
]

def search_products(query: str) -> list[dict]:
    """Return products matching query in name or category (case-insensitive)."""
    if not query:
        return CATALOG
    
    query_lower = query.lower()
    results = []
    for product in CATALOG:
        if query_lower in product["name"].lower or \   # BUG 1: missing () on .lower
           query_lower in product["category"].lower():
            result.append(product)                      # BUG 2: wrong variable name (result vs results)
    return results


def format_results(products: list[dict]) -> str:
    """Format search results for display."""
    if not products:
        return "No products found."
    lines = [f"Found {len(products)} product(s):"]
    for p in products:
        lines.append(f"  • {p['name']} — ${p['price']:.2f} ({p['category']})")
    return "\n".join(lines)


# --- Tests ---
if __name__ == "__main__":
    print("Test 1: search for 'boot'")
    r1 = search_products("boot")
    print(format_results(r1))
    assert len(r1) == 1 and r1[0]["name"] == "TrailBlazer X200"

    print("\nTest 2: search for 'tent'")
    r2 = search_products("tent")
    print(format_results(r2))
    assert len(r2) == 1 and r2[0]["name"] == "Summit Pro Tent"

    print("\nTest 3: empty search returns all")
    r3 = search_products("")
    assert len(r3) == 5

    print("\nTest 4: search 'xyz' returns empty")
    r4 = search_products("xyz")
    assert r4 == []

    # Test the sort function Copilot should have added:
    print("\nTest 5: sort by price ascending")
    sorted_asc = sort_by_price(CATALOG, ascending=True)
    assert sorted_asc[0]["name"] == "ClimbTech Pro Harness"  # cheapest first
    assert sorted_asc[-1]["price"] == 349.00

    print("\n✅ All tests passed!")
