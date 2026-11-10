"""
End-to-End Integration Tests for Recommendation Engine and Persistence (RT-08, etc.).
"""
from django.test import TestCase
from decimal import Decimal
from inventory.models import Product, ShippingBox
from orders.models import Order, OrderItem, OrderStatus
from recommendations.models import Recommendation, BoxEvaluationResult, ProductPlacementRecord
from recommendations.views import process_order_recommendation


class RecommendationIntegrationTests(TestCase):
    def setUp(self):
        # Create standard boxes
        self.box_small = ShippingBox.objects.create(
            code="BOX-S",
            name="Small Box",
            length=Decimal("20.00"),
            width=Decimal("15.00"),
            height=Decimal("10.00"),
            max_weight=Decimal("3.00"),
            cost=Decimal("12.00"),
            is_active=True
        )
        self.box_medium = ShippingBox.objects.create(
            code="BOX-M",
            name="Medium Box",
            length=Decimal("40.00"),
            width=Decimal("30.00"),
            height=Decimal("20.00"),
            max_weight=Decimal("10.00"),
            cost=Decimal("25.00"),
            is_active=True
        )
        self.box_large = ShippingBox.objects.create(
            code="BOX-L",
            name="Large Box",
            length=Decimal("60.00"),
            width=Decimal("50.00"),
            height=Decimal("40.00"),
            max_weight=Decimal("20.00"),
            cost=Decimal("50.00"),
            is_active=True
        )

        # Create products
        self.mouse = Product.objects.create(
            sku="MOUSE-01",
            name="Wireless Mouse",
            length=Decimal("12.00"),
            width=Decimal("8.00"),
            height=Decimal("4.00"),
            weight=Decimal("0.25"),
            is_active=True
        )
        self.keyboard = Product.objects.create(
            sku="KB-01",
            name="Mechanical Keyboard",
            length=Decimal("38.00"),
            width=Decimal("14.00"),
            height=Decimal("4.00"),
            weight=Decimal("1.10"),
            is_active=True
        )

    def test_e2e_recommendation_flow_cheapest_eligible_selected(self):
        """End-to-end: Keyboard does not fit in Small Box (38 > 20), fits in Medium and Large. Medium is cheaper."""
        order = Order.objects.create(order_number="ORD-E2E-1", customer_name="Tech Store")
        OrderItem.objects.create(order=order, product=self.mouse, quantity=2)
        OrderItem.objects.create(order=order, product=self.keyboard, quantity=1)

        rec = process_order_recommendation(order)

        self.assertTrue(rec.has_suitable_box)
        self.assertEqual(rec.selected_box_code, "BOX-M")
        self.assertEqual(rec.selected_cost, Decimal("25.00"))
        self.assertEqual(order.status, OrderStatus.RECOMMENDED)

        # Check persisted BoxEvaluationResults
        eligible_results = rec.box_results.filter(is_eligible=True)
        self.assertEqual(eligible_results.count(), 2)  # BOX-M and BOX-L
        self.assertEqual(eligible_results.first().box_code, "BOX-M")

        # Check rejection of BOX-S
        rejected_results = rec.box_results.filter(is_eligible=False)
        self.assertEqual(rejected_results.count(), 1)
        self.assertEqual(rejected_results.first().box_code, "BOX-S")

        # Verify 3D placements persisted
        m_result = eligible_results.first()
        placements = m_result.placements.all()
        self.assertEqual(placements.count(), 3)  # 2 mice + 1 keyboard

    def test_rt08_historical_recommendation_remains_unchanged_after_master_edits(self):
        """RT-08: Master data changes do not overwrite historical recommendation records."""
        order = Order.objects.create(order_number="ORD-HIST", customer_name="Historic Customer")
        OrderItem.objects.create(order=order, product=self.mouse, quantity=1)

        rec = process_order_recommendation(order)
        original_cost = rec.selected_cost
        original_box_code = rec.selected_box_code

        # Edit master box cost
        self.box_small.cost = Decimal("99.99")
        self.box_small.save()

        # Edit master product dimensions
        self.mouse.length = Decimal("100.00")
        self.mouse.save()

        # Reload recommendation from DB
        rec.refresh_from_db()
        self.assertEqual(rec.selected_cost, original_cost)
        self.assertEqual(rec.selected_box_code, original_box_code)

    def test_confirmation_and_packaging_lifecycle(self):
        order = Order.objects.create(order_number="ORD-FLOW", customer_name="Flow User")
        OrderItem.objects.create(order=order, product=self.mouse, quantity=1)

        rec = process_order_recommendation(order)
        self.assertEqual(order.status, OrderStatus.RECOMMENDED)

        # Confirm box
        rec.confirm_box("BOX-S")
        self.assertTrue(rec.is_confirmed)
        self.assertEqual(rec.confirmed_box_code, "BOX-S")
        self.assertIsNotNone(rec.confirmed_at)
