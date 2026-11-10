"""
Comprehensive tests for Order Management (OT-01 to OT-06).
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from decimal import Decimal
from inventory.models import Product
from orders.models import Order, OrderItem, OrderStatus
from recommendations.services.recommendation_service import RecommendationEngineError
from recommendations.views import process_order_recommendation


class OrderModelTests(TestCase):
    def setUp(self):
        self.p1 = Product.objects.create(
            sku="LAPTOP-01",
            name="Laptop",
            length=Decimal("35.00"),
            width=Decimal("25.00"),
            height=Decimal("2.00"),
            weight=Decimal("2.00")
        )
        self.p2 = Product.objects.create(
            sku="MOUSE-01",
            name="Mouse",
            length=Decimal("12.00"),
            width=Decimal("7.00"),
            height=Decimal("4.00"),
            weight=Decimal("0.20")
        )

    def test_ot01_create_valid_order(self):
        """OT-01: Create valid order -> Order created."""
        order = Order.objects.create(
            order_number="ORD-1001",
            customer_name="Alice Smith",
            customer_email="alice@example.com",
            status=OrderStatus.PENDING
        )
        item = OrderItem.objects.create(order=order, product=self.p1, quantity=1)
        self.assertEqual(order.order_number, "ORD-1001")
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(item.product_sku_snapshot, "LAPTOP-01")

    def test_ot02_order_with_no_items_blocks_recommendation(self):
        """OT-02: Order with no items -> Recommendation blocked."""
        order = Order.objects.create(
            order_number="ORD-EMPTY",
            customer_name="Empty Order Customer"
        )
        self.assertFalse(order.can_recommend)
        with self.assertRaises(RecommendationEngineError):
            process_order_recommendation(order)

    def test_ot03_quantity_zero_validation_failure(self):
        """OT-03: Quantity is zero or negative -> Validation failure."""
        order = Order.objects.create(order_number="ORD-ZERO-QTY", customer_name="Bob")
        item = OrderItem(order=order, product=self.p1, quantity=0)
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_ot04_multiple_products_correct_total_weight(self):
        """OT-04: Multiple products -> Correct total weight."""
        order = Order.objects.create(order_number="ORD-MULTI", customer_name="Charlie")
        OrderItem.objects.create(order=order, product=self.p1, quantity=1)  # 2.00 kg
        OrderItem.objects.create(order=order, product=self.p2, quantity=2)  # 0.20 * 2 = 0.40 kg
        # Total: 2.40 kg
        self.assertEqual(order.total_weight, Decimal("2.40"))

    def test_ot05_multiple_units_item_expansion(self):
        """OT-05: Multiple units of same product -> Correct item expansion."""
        order = Order.objects.create(order_number="ORD-EXPAND", customer_name="Diana")
        OrderItem.objects.create(order=order, product=self.p2, quantity=3)
        items_payload = order.get_items_payload_for_recommendation()
        self.assertEqual(len(items_payload), 1)
        self.assertEqual(items_payload[0]["quantity"], 3)
        self.assertEqual(order.total_quantity, 3)

    def test_ot06_cancelled_order_blocks_recommendation(self):
        """OT-06: Cancelled order -> Recommendation blocked."""
        order = Order.objects.create(
            order_number="ORD-CANCEL",
            customer_name="Evan",
            status=OrderStatus.CANCELLED
        )
        OrderItem.objects.create(order=order, product=self.p1, quantity=1)
        self.assertFalse(order.can_recommend)
        with self.assertRaises(RecommendationEngineError):
            process_order_recommendation(order)

    def test_snapshot_preservation_on_product_update(self):
        """Historical snapshot must not change when product master is modified."""
        order = Order.objects.create(order_number="ORD-SNAP", customer_name="Fiona")
        item = OrderItem.objects.create(order=order, product=self.p1, quantity=1)

        # Snapshot recorded
        self.assertEqual(item.length_snapshot, Decimal("35.00"))

        # Modify original master product
        self.p1.length = Decimal("99.00")
        self.p1.save()

        # Item snapshot remains 35.00
        item.refresh_from_db()
        self.assertEqual(item.length_snapshot, Decimal("35.00"))
        self.assertNotEqual(item.length_snapshot, self.p1.length)
