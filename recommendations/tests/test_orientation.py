"""
Unit tests for 3D cuboid orientations (PRD Stage 4 & AL-01, AL-02).
"""
import unittest
from decimal import Decimal
from recommendations.algorithms.geometry import Dimensions
from recommendations.algorithms.orientation import get_all_orientations


class OrientationTests(unittest.TestCase):
    def test_cube_has_single_unique_orientation(self):
        cube = Dimensions(Decimal("10.00"), Decimal("10.00"), Decimal("10.00"))
        orientations = get_all_orientations(cube)
        self.assertEqual(len(orientations), 1)
        self.assertEqual(orientations[0], cube)

    def test_square_cuboid_has_three_orientations(self):
        # Two sides equal, one different
        cuboid = Dimensions(Decimal("10.00"), Decimal("10.00"), Decimal("20.00"))
        orientations = get_all_orientations(cuboid)
        self.assertEqual(len(orientations), 3)

    def test_irregular_cuboid_has_six_orientations(self):
        # All three sides different
        cuboid = Dimensions(Decimal("10.00"), Decimal("20.00"), Decimal("30.00"))
        orientations = get_all_orientations(cuboid)
        self.assertEqual(len(orientations), 6)

        expected_tuples = {
            (Decimal("10.00"), Decimal("20.00"), Decimal("30.00")),
            (Decimal("10.00"), Decimal("30.00"), Decimal("20.00")),
            (Decimal("20.00"), Decimal("10.00"), Decimal("30.00")),
            (Decimal("20.00"), Decimal("30.00"), Decimal("10.00")),
            (Decimal("30.00"), Decimal("10.00"), Decimal("20.00")),
            (Decimal("30.00"), Decimal("20.00"), Decimal("10.00")),
        }
        actual_tuples = {(o.length, o.width, o.height) for o in orientations}
        self.assertEqual(actual_tuples, expected_tuples)

    def test_rotation_disabled_returns_single_orientation(self):
        cuboid = Dimensions(Decimal("10.00"), Decimal("20.00"), Decimal("30.00"))
        orientations = get_all_orientations(cuboid, allow_rotation=False)
        self.assertEqual(len(orientations), 1)
        self.assertEqual(orientations[0], cuboid)


if __name__ == "__main__":
    unittest.main()

