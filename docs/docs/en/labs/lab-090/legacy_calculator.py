"""Legacy price parser used for characterization practice."""
from decimal import Decimal, ROUND_HALF_UP

def total(lines):
    amount = sum(Decimal(item["price"]) * int(item["quantity"]) for item in lines)
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
