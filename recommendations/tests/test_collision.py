"""
Unit tests for 3D collision and boundary checks (AL-05, AL-06, etc.).
"""
import unittest
from decimal import Decimal
from recommendations.algorithms.geometry import Point3D, Dimensions, Placement
from recommendations.algorithms.collision import is_within_box, check_overlap, has_collision_with_existing


class CollisionTests(unittest.TestCase):
    def setUp(self):
        self.box_dims = Dimensions(Decimal("50.00"), Decimal("40.00"), Decimal("30.00"))

    def test_within_box_valid(self):
        pt = Point3D(Decimal("0.00"), Decimal("0.00"), Decimal("0.00"))
        dims = Dimensions(Decimal("20.00"), Decimal("15.00"), Decimal("10.00"))
        self.assertTrue(is_within_box(pt, dims, self.box_dims))

    def test_within_box_exact_match(self):
        pt = Point3D(Decimal("0.00"), Decimal("0.00"), Decimal("0.00"))
        dims = Dimensions(Decimal("50.00"), Decimal("40.00"), Decimal("30.00"))
        self.assertTrue(is_within_box(pt, dims, self.box_dims))

    def test_exceeds_box_length(self):
        pt = Point3D(Decimal("35.00"), Decimal("0.00"), Decimal("0.00"))
        dims = Dimensions(Decimal("20.00"), Decimal("10.00"), Decimal("10.00")) # 35 + 20 = 55 > 50
        self.assertFalse(is_within_box(pt, dims, self.box_dims))

    def test_exceeds_box_width(self):
        pt = Point3D(Decimal("0.00"), Decimal("35.00"), Decimal("0.00"))
        dims = Dimensions(Decimal("10.00"), Decimal("10.00"), Decimal("10.00")) # 35 + 10 = 45 > 40
        self.assertFalse(is_within_box(pt, dims, self.box_dims))

    def test_exceeds_box_height(self):
        pt = Point3D(Decimal("0.00"), Decimal("0.00"), Decimal("25.00"))
        dims = Dimensions(Decimal("10.00"), Decimal("10.00"), Decimal("10.00")) # 25 + 10 = 35 > 30
        self.assertFalse(is_within_box(pt, dims, self.box_dims))

    def test_negative_coordinate_invalid(self):
        pt = Point3D(Decimal("-1.00"), Decimal("0.00"), Decimal("0.00"))
        dims = Dimensions(Decimal("10.00"), Decimal("10.00"), Decimal("10.00"))
        self.assertFalse(is_within_box(pt, dims, self.box_dims))

    def test_al05_two_products_overlap(self):
        """AL-05: Two products overlap -> overlap detected."""
        p1 = Point3D(Decimal("0.00"), Decimal("0.00"), Decimal("0.00"))
        d1 = Dimensions(Decimal("10.00"), Decimal("10.00"), Decimal("10.00"))

        p2 = Point3D(Decimal("5.00"), Decimal("5.00"), Decimal("5.00"))
        d2 = Dimensions(Decimal("10.00"), Decimal("10.00"), Decimal("10.00"))

        self.assertTrue(check_overlap(p1, d1, p2, d2))

    def test_al06_two_products_touch_boundaries_no_overlap(self):
        """AL-06: Two products touch boundaries -> Valid placement, no overlap."""
        p1 = Point3D(Decimal("0.00"), Decimal("0.00"), Decimal("0.00"))
        d1 = Dimensions(Decimal("10.00"), Decimal("10.00"), Decimal("10.00"))

        # Touching along X axis: p2 starts right where p1 ends (x=10.00)
        p2_x = Point3D(Decimal("10.00"), Decimal("0.00"), Decimal("0.00"))
        d2 = Dimensions(Decimal("10.00"), Decimal("10.00"), Decimal("10.00"))
        self.assertFalse(check_overlap(p1, d1, p2_x, d2))

        # Touching along Y axis: p2 starts at y=10.00
        p2_y = Point3D(Decimal("0.00"), Decimal("10.00"), Decimal("0.00"))
        self.assertFalse(check_overlap(p1, d1, p2_y, d2))

        # Touching along Z axis (stacked): p2 starts at z=10.00
        p2_z = Point3D(Decimal("0.00"), Decimal("0.00"), Decimal("10.00"))
        self.assertFalse(check_overlap(p1, d1, p2_z, d2))

    def test_collision_with_existing_placements(self):
        placement = Placement(
            item_id=1,
            sku="SKU-1",
            name="Book",
            unit_index=1,
            position=Point3D(Decimal("0.00"), Decimal("0.00"), Decimal("0.00")),
            dimensions=Dimensions(Decimal("20.00"), Decimal("15.00"), Decimal("5.00"))
        )
        existing = [placement]

        # Overlapping point
        pt_overlap = Point3D(Decimal("10.00"), Decimal("5.00"), Decimal("2.00"))
        d = Dimensions(Decimal("10.00"), Decimal("10.00"), Decimal("5.00"))
        self.assertTrue(has_collision_with_existing(pt_overlap, d, existing))

        # Non-overlapping point (adjacent on top)
        pt_on_top = Point3D(Decimal("0.00"), Decimal("0.00"), Decimal("5.00"))
        self.assertFalse(has_collision_with_existing(pt_on_top, d, existing))


if __name__ == "__main__":
    unittest.main()
