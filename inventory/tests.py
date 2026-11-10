"""
Comprehensive tests for Product and Shipping Box Management (PT-01 to PT-06 & BT-01 to BT-06).
"""
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from decimal import Decimal
from inventory.models import Product, ShippingBox


class ProductModelTests(TestCase):
    def test_pt01_create_valid_product(self):
        """PT-01: Create valid product -> Product created."""
        prod = Product.objects.create(
            sku="PROD-001",
            name="Mechanical Keyboard",
            length=Decimal("45.00"),
            width=Decimal("15.00"),
            height=Decimal("4.00"),
            weight=Decimal("1.20"),
            is_active=True
        )
        self.assertEqual(prod.sku, "PROD-001")
        self.assertEqual(prod.volume, Decimal("2700.00"))
        self.assertTrue(prod.is_active)

    def test_pt02_duplicate_sku_raises_error(self):
        """PT-02: Duplicate SKU -> Integrity failure."""
        Product.objects.create(
            sku="PROD-DUP",
            name="Item 1",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("1.00")
        )
        with self.assertRaises(IntegrityError):
            Product.objects.create(
                sku="PROD-DUP",
                name="Item 2",
                length=Decimal("20.00"),
                width=Decimal("20.00"),
                height=Decimal("20.00"),
                weight=Decimal("2.00")
            )

    def test_pt03_zero_or_negative_dimensions_validation(self):
        """PT-03: Zero or negative dimensions -> Validation failure."""
        prod = Product(
            sku="PROD-ZERO-DIM",
            name="Zero Dim Item",
            length=Decimal("0.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("1.00")
        )
        with self.assertRaises(ValidationError):
            prod.full_clean()

    def test_pt04_negative_weight_validation(self):
        """PT-04: Negative weight -> Validation failure."""
        prod = Product(
            sku="PROD-NEG-WT",
            name="Negative Weight Item",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("-1.50")
        )
        with self.assertRaises(ValidationError):
            prod.full_clean()

    def test_pt05_missing_product_name_validation(self):
        """PT-05: Missing product name -> Validation failure."""
        prod = Product(
            sku="PROD-NO-NAME",
            name="",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("1.00")
        )
        with self.assertRaises(ValidationError):
            prod.full_clean()

    def test_pt06_deactivate_product(self):
        """PT-06: Deactivate product -> Product is marked inactive."""
        prod = Product.objects.create(
            sku="PROD-DEACT",
            name="Deactivated Product",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            weight=Decimal("1.00"),
            is_active=False
        )
        self.assertFalse(prod.is_active)


class ShippingBoxModelTests(TestCase):
    def test_bt01_create_valid_box(self):
        """BT-01: Create valid box -> Box created."""
        box = ShippingBox.objects.create(
            code="BOX-MED",
            name="Medium Shipping Box",
            length=Decimal("40.00"),
            width=Decimal("30.00"),
            height=Decimal("20.00"),
            max_weight=Decimal("10.00"),
            cost=Decimal("25.00"),
            is_active=True
        )
        self.assertEqual(box.code, "BOX-MED")
        self.assertEqual(box.volume, Decimal("24000.00"))
        self.assertEqual(box.cost, Decimal("25.00"))

    def test_bt02_duplicate_box_code_raises_error(self):
        """BT-02: Duplicate box code -> Validation failure."""
        ShippingBox.objects.create(
            code="BOX-DUP",
            name="Box 1",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            max_weight=Decimal("5.00"),
            cost=Decimal("10.00")
        )
        with self.assertRaises(IntegrityError):
            ShippingBox.objects.create(
                code="BOX-DUP",
                name="Box 2",
                length=Decimal("20.00"),
                width=Decimal("20.00"),
                height=Decimal("20.00"),
                max_weight=Decimal("5.00"),
                cost=Decimal("15.00")
            )

    def test_bt03_negative_cost_validation(self):
        """BT-03: Negative cost -> Validation failure."""
        box = ShippingBox(
            code="BOX-NEG-COST",
            name="Negative Cost Box",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            max_weight=Decimal("5.00"),
            cost=Decimal("-5.00")
        )
        with self.assertRaises(ValidationError):
            box.full_clean()

    def test_bt04_zero_internal_dimensions_validation(self):
        """BT-04: Zero internal dimensions -> Validation failure."""
        box = ShippingBox(
            code="BOX-ZERO-DIM",
            name="Zero Dim Box",
            length=Decimal("0.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            max_weight=Decimal("5.00"),
            cost=Decimal("10.00")
        )
        with self.assertRaises(ValidationError):
            box.full_clean()

    def test_bt05_zero_payload_capacity_validation(self):
        """BT-05: Zero payload capacity -> Validation failure."""
        box = ShippingBox(
            code="BOX-ZERO-WT",
            name="Zero Weight Box",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            max_weight=Decimal("0.00"),
            cost=Decimal("10.00")
        )
        with self.assertRaises(ValidationError):
            box.full_clean()

    def test_bt06_inactive_box(self):
        """BT-06: Inactive box status set."""
        box = ShippingBox.objects.create(
            code="BOX-INACT",
            name="Inactive Box",
            length=Decimal("10.00"),
            width=Decimal("10.00"),
            height=Decimal("10.00"),
            max_weight=Decimal("5.00"),
            cost=Decimal("10.00"),
            is_active=False
        )
        self.assertFalse(box.is_active)
