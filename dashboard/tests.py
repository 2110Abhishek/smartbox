"""
Tests for Dashboard and Analytics (DASH-01 to DASH-06).
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from inventory.models import Product, ShippingBox
from orders.models import Order, OrderItem, OrderStatus
from recommendations.views import process_order_recommendation


class DashboardTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="dashuser", password="password123")
        self.client.login(username="dashuser", password="password123")

        self.prod = Product.objects.create(
            sku="DASH-PROD", name="Prod A", length=Decimal("10"), width=Decimal("10"), height=Decimal("10"), weight=Decimal("1")
        )
        self.box = ShippingBox.objects.create(
            code="DASH-BOX", name="Box A", length=Decimal("20"), width=Decimal("20"), height=Decimal("20"), max_weight=Decimal("5"), cost=Decimal("15")
        )
        self.order = Order.objects.create(order_number="ORD-DASH-1", customer_name="Customer 1")
        OrderItem.objects.create(order=self.order, product=self.prod, quantity=1)

    def test_dash01_to_06_dashboard_statistics(self):
        """DASH-01 to DASH-06: Displays active products, boxes, orders, costs and updates from DB."""
        # Generate a recommendation
        process_order_recommendation(self.order)

        response = self.client.get(reverse("dashboard:index"))
        self.assertEqual(response.status_code, 200)

        # Context asserts
        self.assertEqual(response.context["active_products_count"], 1)
        self.assertEqual(response.context["available_boxes_count"], 1)
        self.assertEqual(response.context["total_orders_count"], 1)
        self.assertEqual(response.context["total_packaging_cost"], Decimal("15.00"))
        self.assertEqual(response.context["most_common_box"]["selected_box_code"], "DASH-BOX")

    def test_analytics_view(self):
        process_order_recommendation(self.order)
        response = self.client.get(reverse("dashboard:analytics"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_recs"], 1)
        self.assertEqual(response.context["successful_recs"], 1)
