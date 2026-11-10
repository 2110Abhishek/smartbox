"""
Comprehensive tests for 3D Bin Packing Algorithm (AL-01 to AL-10).
"""
import unittest
from decimal import Decimal
from recommendations.algorithms.geometry import Dimensions, ItemToPack, Point3D
from recommendations.algorithms.extreme_point import pack_products_3d


class PackingAlgorithmTests(unittest.TestCase):
    def setUp(self):
        # Standard box: 30 x 20 x 15 cm
        self.box_dims = Dimensions(Decimal("30.00"), Decimal("20.00"), Decimal("15.00"))

    def test_al01_product_fits_without_rotation(self):
        """AL-01: Product fits without rotation -> Successful placement."""
        # Item: 25 x 15 x 10 cm inside 30 x 20 x 15 cm
        item = ItemToPack(
            id=1,
            sku="ITEM-1",
            name="Keyboard",
            dimensions=Dimensions(Decimal("25.00"), Decimal("15.00"), Decimal("10.00")),
            weight=Decimal("1.50")
        )
        result = pack_products_3d([item], self.box_dims, allow_rotation=False)
        self.assertTrue(result.success)
        self.assertEqual(len(result.placements), 1)
        self.assertEqual(result.placements[0].position, Point3D(Decimal("0.00"), Decimal("0.00"), Decimal("0.00")))
        self.assertEqual(result.placements[0].dimensions, item.dimensions)

    def test_al02_product_fits_only_after_rotation(self):
        """AL-02: Product fits only after rotation -> Successful placement."""
        # Item: 10 x 25 x 15 cm does NOT fit into 30 x 20 x 15 if width must be <= 20,
        # but rotated to 25 x 10 x 15 cm it fits perfectly!
        item = ItemToPack(
            id=2,
            sku="ITEM-ROT",
            name="Long Device",
            dimensions=Dimensions(Decimal("10.00"), Decimal("25.00"), Decimal("15.00")),
            weight=Decimal("2.00")
        )

        # Without rotation it must fail because width 25 > box width 20
        res_no_rot = pack_products_3d([item], self.box_dims, allow_rotation=False)
        self.assertFalse(res_no_rot.success)

        # With rotation it must succeed
        res_rot = pack_products_3d([item], self.box_dims, allow_rotation=True)
        self.assertTrue(res_rot.success)
        self.assertEqual(len(res_rot.placements), 1)
        # Verify placed orientation fits within 30 x 20 x 15
        placed_dim = res_rot.placements[0].dimensions
        self.assertLessEqual(placed_dim.length, self.box_dims.length)
        self.assertLessEqual(placed_dim.width, self.box_dims.width)
        self.assertLessEqual(placed_dim.height, self.box_dims.height)

    def test_al03_product_exceeds_box_length(self):
        """AL-03: Product exceeds box length in given orientation without rotation."""
        item = ItemToPack(
            id=3,
            sku="ITEM-LONG",
            name="Long Pole",
            dimensions=Dimensions(Decimal("35.00"), Decimal("10.00"), Decimal("10.00")),
            weight=Decimal("1.00")
        )
        # Even with rotation, 35 exceeds all box dimensions (30, 20, 15)
        result = pack_products_3d([item], self.box_dims)
        self.assertFalse(result.success)
        self.assertIn("exceeds box dimensions", result.reason)

    def test_al04_product_exceeds_all_possible_orientations(self):
        """AL-04: Product exceeds all possible orientations -> Placement failure."""
        # Dimensions 22 x 22 x 22 cm inside 30 x 20 x 15 cm (no orientation can fit into height 15 or width 20)
        item = ItemToPack(
            id=4,
            sku="ITEM-HUGE-CUBE",
            name="Large Cube",
            dimensions=Dimensions(Decimal("22.00"), Decimal("22.00"), Decimal("22.00")),
            weight=Decimal("3.00")
        )
        result = pack_products_3d([item], self.box_dims)
        self.assertFalse(result.success)
        self.assertIn("exceeds box dimensions in all possible orientations", result.reason)

    def test_al05_two_products_overlap_prevented(self):
        """AL-05: Algorithm ensures placed items never overlap."""
        item1 = ItemToPack(
            id=5,
            sku="ITEM-A",
            name="Item A",
            dimensions=Dimensions(Decimal("15.00"), Decimal("10.00"), Decimal("10.00")),
            weight=Decimal("1.00")
        )
        item2 = ItemToPack(
            id=6,
            sku="ITEM-B",
            name="Item B",
            dimensions=Dimensions(Decimal("15.00"), Decimal("10.00"), Decimal("10.00")),
            weight=Decimal("1.00")
        )
        result = pack_products_3d([item1, item2], self.box_dims)
        self.assertTrue(result.success)
        self.assertEqual(len(result.placements), 2)
        p1 = result.placements[0]
        p2 = result.placements[1]

        # Verify separation in at least one axis
        sep_x = (p1.x_end <= p2.x) or (p2.x_end <= p1.x)
        sep_y = (p1.y_end <= p2.y) or (p2.y_end <= p1.y)
        sep_z = (p1.z_end <= p2.z) or (p2.z_end <= p1.z)
        self.assertTrue(sep_x or sep_y or sep_z, "Items must not overlap in 3D space")

    def test_al06_two_products_touch_boundaries_valid(self):
        """AL-06: Two products touch boundaries -> Valid placement."""
        # Box: 30 x 20 x 15. Two items: 15 x 20 x 15 each. They fit side-by-side touching at x=15.
        item1 = ItemToPack(
            id=7, sku="HALF-1", name="Block 1",
            dimensions=Dimensions(Decimal("15.00"), Decimal("20.00"), Decimal("15.00")),
            weight=Decimal("1.00"), unit_index=1
        )
        item2 = ItemToPack(
            id=8, sku="HALF-2", name="Block 2",
            dimensions=Dimensions(Decimal("15.00"), Decimal("20.00"), Decimal("15.00")),
            weight=Decimal("1.00"), unit_index=1
        )
        result = pack_products_3d([item1, item2], self.box_dims)
        self.assertTrue(result.success)
        self.assertEqual(len(result.placements), 2)
        # Total volume used should be 100%
        self.assertEqual(result.volume_utilization_pct, Decimal("100.00"))

    def test_al07_multiple_products_fit(self):
        """AL-07: Multiple different products fit -> All products placed."""
        items = [
            ItemToPack(id=1, sku="P1", name="Book", dimensions=Dimensions(Decimal("20.00"), Decimal("10.00"), Decimal("5.00")), weight=Decimal("0.5")),
            ItemToPack(id=2, sku="P2", name="Mouse", dimensions=Dimensions(Decimal("10.00"), Decimal("6.00"), Decimal("4.00")), weight=Decimal("0.2")),
            ItemToPack(id=3, sku="P3", name="Headphones", dimensions=Dimensions(Decimal("15.00"), Decimal("10.00"), Decimal("5.00")), weight=Decimal("0.4")),
        ]
        result = pack_products_3d(items, self.box_dims)
        self.assertTrue(result.success)
        self.assertEqual(len(result.placements), 3)

    def test_al08_product_quantity_greater_than_one(self):
        """AL-08: Product quantity > 1 -> Each instance placed."""
        # 4 identical small boxes of 10 x 10 x 7 cm
        items = [
            ItemToPack(id=10, sku="MUG", name="Coffee Mug", dimensions=Dimensions(Decimal("10.00"), Decimal("10.00"), Decimal("7.00")), weight=Decimal("0.4"), unit_index=i+1)
            for i in range(4)
        ]
        result = pack_products_3d(items, self.box_dims)
        self.assertTrue(result.success)
        self.assertEqual(len(result.placements), 4)

    def test_al09_product_extends_beyond_box_height(self):
        """AL-09: Product extends beyond box height -> Placement rejected."""
        # Box height is 15. Item height is 16 and other dimensions are also > 15
        item = ItemToPack(
            id=11, sku="TALL", name="Tall Vase",
            dimensions=Dimensions(Decimal("16.00"), Decimal("16.00"), Decimal("16.00")),
            weight=Decimal("1.00")
        )
        result = pack_products_3d([item], self.box_dims)
        self.assertFalse(result.success)

    def test_al10_no_valid_candidate_point_remains(self):
        """AL-10: No valid candidate point remains when box is full -> Packing failure."""
        # Fill box with 2 large halves, then try to add 1 small item
        item1 = ItemToPack(id=12, sku="HALF-A", name="Block A", dimensions=Dimensions(Decimal("15.00"), Decimal("20.00"), Decimal("15.00")), weight=Decimal("1.0"))
        item2 = ItemToPack(id=13, sku="HALF-B", name="Block B", dimensions=Dimensions(Decimal("15.00"), Decimal("20.00"), Decimal("15.00")), weight=Decimal("1.0"))
        item3 = ItemToPack(id=14, sku="EXTRA", name="Extra Item", dimensions=Dimensions(Decimal("5.00"), Decimal("5.00"), Decimal("5.00")), weight=Decimal("0.2"))

        result = pack_products_3d([item1, item2, item3], self.box_dims)
        self.assertFalse(result.success)


if __name__ == "__main__":
    unittest.main()

