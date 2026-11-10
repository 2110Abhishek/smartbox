"""
Weight calculation service for orders.
Formula: W_total = sum(W_i * Q_i)
"""
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Dict, Any


def calculate_order_weight(items: List[Dict[str, Any]]) -> Decimal:
    """
    Calculate the total weight of an order from a list of item dictionaries:
    Each item dictionary should have 'weight' and 'quantity'.
    Returns Decimal with 2 decimal places.
    """
    total = Decimal("0.00")
    for item in items:
        unit_weight = Decimal(str(item.get("weight", 0)))
        qty = Decimal(str(item.get("quantity", 0)))
        total += unit_weight * qty
    return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
