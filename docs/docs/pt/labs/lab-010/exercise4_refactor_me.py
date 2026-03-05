# exercise4_refactor_me.py
# ✏️  REFACTORING CHALLENGE — No bugs here, but the code is terrible.
#
# TASK: Use Copilot Edits to improve this code WITHOUT changing its behavior.
#
# TRY THESE COPILOT EDITS PROMPTS (one at a time):
#   1. "Add type hints to all function parameters and return values"
#   2. "Add docstrings following Google style to every function"  
#   3. "Replace the magic numbers with named constants at the top of the file"
#   4. "Refactor calculate_shipping to use early return instead of nested ifs"
#   5. "Add input validation: raise ValueError for negative prices or quantities"
#
# After each prompt, review what Copilot changed. Accept or reject with Ctrl+Enter / Ctrl+Backspace.
#
# GOAL: By the end, this code should be production-ready.

STANDARD_SHIPPING = 5.99
EXPRESS_SHIPPING = 14.99
FREE_SHIPPING_THRESHOLD = 75.0
DISCOUNT_THRESHOLD = 200.0
DISCOUNT_RATE = 0.10

def calculate_price(p, q):
    return p * q

def calculate_shipping(t):
    if t >= 75:
        return 0
    else:
        if t > 50:
            return 5.99
        else:
            return 14.99

def apply_discount(t):
    if t > 200:
        d = t * 0.10
        t = t - d
    return round(t, 2)

def order_summary(items):
    t = 0
    for i in items:
        t = t + calculate_price(i[0], i[1])
    s = calculate_shipping(t)
    t_with_shipping = t + s
    final = apply_discount(t_with_shipping)
    return {"subtotal": round(t, 2), "shipping": s, "discount_applied": t > 200, "total": final}


# Test — this should still pass after all refactoring
if __name__ == "__main__":
    items = [(189.99, 1), (349.00, 1)]   # (price, quantity)
    result = order_summary(items)
    print(result)
    assert result["total"] == 489.59, f"Got {result['total']}"
    print("✅ Refactoring complete — behavior unchanged!")
