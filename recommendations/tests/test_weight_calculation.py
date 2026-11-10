"""
Tests for order weight calculation (Formula W_total = sum(W_i * Q_i) & OT-04).
"""
import unittest
from decimal import Decimal
from recommendations.services.weight_calculator import calculate_order_weight


class WeightCalculationTests(unittest.TestCase):
    def test_single_item_weight(self):
        items = [{"sku": "P1", "weight": "2.50", "quantity": 1}]
        total = calculate_order_weight(items)
        self.assertEqual(total, Decimal("2.50"))

    def test_multiple_quantities_weight(self):
        items = [{"sku": "P1", "weight": "1.25", "quantity": 4}]
        total = calculate_order_weight(items)
        self.assertEqual(total, Decimal("5.00"))

    def test_prd_example_weight(self):
        # PRD Stage 2 Example:
        # Laptop: 2 kg * 1 = 2 kg
        # Mouse: 0.2 kg * 2 = 0.4 kg
        # Keyboard: 0.8 kg * 1 = 0.8 kg
        # Total: 3.2 kg
        items = [
            {"sku": "LAPTOP", "weight": "2.00", "quantity": 1},
            {"sku": "MOUSE", "weight": "0.20", "quantity": 2},
            {"sku": "KEYBOARD", "weight": "0.80", "quantity": 1},
        ]
        total = calculate_order_weight(items)
        self.assertEqual(total, Decimal("3.20"))

    def test_empty_items_weight(self):
        self.assertEqual(calculate_order_weight([]), Decimal("0.00"))


if __name__ == "__main__":
    unittest.main()
