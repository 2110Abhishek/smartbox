"""
Tests for Recommendation Engine (RT-01 to RT-07, RT-09, RT-10).
"""
import unittest
from decimal import Decimal
from dataclasses import dataclass
from recommendations.services.recommendation_service import run_box_recommendation, RecommendationEngineError


@dataclass
class DummyBox:
    id: int
    code: str
    name: str
    length: Decimal
    width: Decimal
    height: Decimal
    max_weight: Decimal
    cost: Decimal
    is_active: bool = True


class RecommendationServiceTests(unittest.TestCase):
    def setUp(self):
        self.item = {
            "id": 1,
            "sku": "ITEM-1",
            "name": "Standard Item",
            "length": "20.00",
            "width": "15.00",
            "height": "10.00",
            "weight": "2.00",
            "quantity": 1
        }

    def test_rt01_one_suitable_box(self):
        """RT-01: One suitable box -> That box recommended."""
        box = DummyBox(
            id=1, code="BOX-A", name="Box A",
            length=Decimal("30.00"), width=Decimal("20.00"), height=Decimal("15.00"),
            max_weight=Decimal("5.00"), cost=Decimal("15.00")
        )
        res = run_box_recommendation([self.item], [box])
        self.assertTrue(res["has_suitable_box"])
        self.assertEqual(res["recommended_box"]["box"]["code"], "BOX-A")
        self.assertEqual(len(res["alternatives"]), 0)

    def test_rt02_multiple_suitable_boxes_cheapest_recommended(self):
        """RT-02: Multiple suitable boxes -> Cheapest box recommended."""
        expensive_box = DummyBox(
            id=1, code="EXPENSIVE", name="Expensive Box",
            length=Decimal("40.00"), width=Decimal("30.00"), height=Decimal("20.00"),
            max_weight=Decimal("10.00"), cost=Decimal("45.00")
        )
        cheap_box = DummyBox(
            id=2, code="CHEAP", name="Cheap Box",
            length=Decimal("30.00"), width=Decimal("20.00"), height=Decimal("15.00"),
            max_weight=Decimal("5.00"), cost=Decimal("20.00")
        )
        res = run_box_recommendation([self.item], [expensive_box, cheap_box])
        self.assertTrue(res["has_suitable_box"])
        self.assertEqual(res["recommended_box"]["box"]["code"], "CHEAP")
        self.assertEqual(len(res["alternatives"]), 1)
        self.assertEqual(res["alternatives"][0]["box"]["code"], "EXPENSIVE")

    def test_rt03_equal_box_costs_smaller_volume_preferred(self):
        """RT-03: Equal box costs -> Smaller volume preferred."""
        larger_volume_box = DummyBox(
            id=1, code="BOX-LARGE-VOL", name="Large Vol Box",
            length=Decimal("50.00"), width=Decimal("40.00"), height=Decimal("30.00"), # Vol = 60,000
            max_weight=Decimal("10.00"), cost=Decimal("25.00")
        )
        smaller_volume_box = DummyBox(
            id=2, code="BOX-SMALL-VOL", name="Small Vol Box",
            length=Decimal("30.00"), width=Decimal("20.00"), height=Decimal("15.00"), # Vol = 9,000
            max_weight=Decimal("10.00"), cost=Decimal("25.00")
        )
        res = run_box_recommendation([self.item], [larger_volume_box, smaller_volume_box])
        self.assertEqual(res["recommended_box"]["box"]["code"], "BOX-SMALL-VOL")

    def test_rt04_equal_costs_and_volumes_code_determines_order(self):
        """RT-04: Equal costs and volumes -> Box code determines order."""
        box_z = DummyBox(
            id=1, code="BOX-Z", name="Box Z",
            length=Decimal("30.00"), width=Decimal("20.00"), height=Decimal("15.00"),
            max_weight=Decimal("10.00"), cost=Decimal("20.00")
        )
        box_a = DummyBox(
            id=2, code="BOX-A", name="Box A",
            length=Decimal("30.00"), width=Decimal("20.00"), height=Decimal("15.00"),
            max_weight=Decimal("10.00"), cost=Decimal("20.00")
        )
        res = run_box_recommendation([self.item], [box_z, box_a])
        self.assertEqual(res["recommended_box"]["box"]["code"], "BOX-A")

    def test_rt05_weight_capacity_exceeded(self):
        """RT-05: Weight capacity exceeded -> Box rejected."""
        heavy_item = dict(self.item, weight="10.00") # 10 kg
        light_box = DummyBox(
            id=1, code="LIGHT-BOX", name="Light Box",
            length=Decimal("50.00"), width=Decimal("50.00"), height=Decimal("50.00"),
            max_weight=Decimal("5.00"), cost=Decimal("10.00")
        )
        res = run_box_recommendation([heavy_item], [light_box])
        self.assertFalse(res["has_suitable_box"])
        self.assertEqual(len(res["rejected_boxes"]), 1)
        self.assertIn("Maximum payload weight exceeded", res["rejected_boxes"][0]["reason"])

    def test_rt06_no_suitable_box(self):
        """RT-06: No suitable box -> No recommendation returned."""
        tiny_box = DummyBox(
            id=1, code="TINY-BOX", name="Tiny Box",
            length=Decimal("5.00"), width=Decimal("5.00"), height=Decimal("5.00"),
            max_weight=Decimal("5.00"), cost=Decimal("5.00")
        )
        res = run_box_recommendation([self.item], [tiny_box])
        self.assertFalse(res["has_suitable_box"])
        self.assertIsNone(res["recommended_box"])

    def test_rt07_inactive_box_excluded(self):
        """RT-07: Inactive box -> Box excluded."""
        inactive_box = DummyBox(
            id=1, code="INACTIVE", name="Inactive Box",
            length=Decimal("30.00"), width=Decimal("20.00"), height=Decimal("15.00"),
            max_weight=Decimal("10.00"), cost=Decimal("5.00"), is_active=False
        )
        res = run_box_recommendation([self.item], [inactive_box])
        self.assertFalse(res["has_suitable_box"])
        self.assertEqual(res["rejected_boxes"][0]["reason"], "Box is inactive.")

    def test_rt09_repeated_identical_request_is_deterministic(self):
        """RT-09: Repeated identical request -> Same result."""
        boxes = [
            DummyBox(id=1, code="B1", name="Box 1", length=Decimal("30"), width=Decimal("20"), height=Decimal("15"), max_weight=Decimal("5"), cost=Decimal("15")),
            DummyBox(id=2, code="B2", name="Box 2", length=Decimal("40"), width=Decimal("30"), height=Decimal("20"), max_weight=Decimal("10"), cost=Decimal("25")),
        ]
        res1 = run_box_recommendation([self.item], boxes)
        res2 = run_box_recommendation([self.item], boxes)
        self.assertEqual(res1["recommended_box"]["box"]["code"], res2["recommended_box"]["box"]["code"])
        self.assertEqual(res1["recommended_box"]["placements"], res2["recommended_box"]["placements"])

    def test_rt10_all_candidate_boxes_rejected_reasons_displayed(self):
        """RT-10: All candidate boxes rejected -> Explanations displayed."""
        box_small = DummyBox(id=1, code="SMALL", name="Small", length=Decimal("5"), width=Decimal("5"), height=Decimal("5"), max_weight=Decimal("10"), cost=Decimal("5"))
        box_light = DummyBox(id=2, code="LIGHT", name="Light", length=Decimal("50"), width=Decimal("50"), height=Decimal("50"), max_weight=Decimal("1"), cost=Decimal("10"))
        res = run_box_recommendation([self.item], [box_small, box_light])
        self.assertFalse(res["has_suitable_box"])
        self.assertEqual(len(res["rejected_boxes"]), 2)
        reasons = [r["reason"] for r in res["rejected_boxes"]]
        self.assertTrue(any("Maximum payload weight exceeded" in r for r in reasons))
        self.assertTrue(any("cannot be placed" in r or "exceeds" in r for r in reasons))

    def test_empty_order_raises_validation_error(self):
        box = DummyBox(id=1, code="B1", name="B1", length=Decimal("30"), width=Decimal("20"), height=Decimal("15"), max_weight=Decimal("5"), cost=Decimal("10"))
        with self.assertRaises(RecommendationEngineError):
            run_box_recommendation([], [box])


if __name__ == "__main__":
    unittest.main()

