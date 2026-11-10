"""
Main recommendation service coordinating the box recommendation pipeline.
"""
from decimal import Decimal
from typing import List, Dict, Any, Optional
from recommendations.services.weight_calculator import calculate_order_weight
from recommendations.services.box_filter import filter_boxes_by_weight
from recommendations.services.packing_service import expand_order_items, evaluate_box_packing
from recommendations.services.ranking_service import rank_eligible_boxes


class RecommendationEngineError(Exception):
    """Base error for recommendation engine validation failures."""
    pass


def run_box_recommendation(
    items_data: List[Dict[str, Any]],
    available_boxes: List[Any],
    order_id: Optional[Any] = None,
    order_number: Optional[str] = None,
    allow_rotation: bool = True
) -> Dict[str, Any]:
    """
    Executes the intelligent box recommendation pipeline:
    Stage 1: Validate items
    Stage 2: Calculate total weight
    Stage 3: Filter by status, dimensions and weight capacity
    Stage 4: Expand items and test 3D geometric packing
    Stage 5: Rank eligible boxes by (cost, volume, code)
    Stage 6: Assemble transparent output
    """
    # Stage 1: Validation
    if not items_data:
        raise RecommendationEngineError("Order must contain at least one item before generating recommendations.")

    for idx, it in enumerate(items_data):
        qty = it.get("quantity", 0)
        if not isinstance(qty, int) or qty <= 0:
            raise RecommendationEngineError(f"Item {it.get('sku', idx)} has invalid quantity {qty}. Must be positive integer.")

        length = Decimal(str(it.get("length", 0)))
        width = Decimal(str(it.get("width", 0)))
        height = Decimal(str(it.get("height", 0)))
        weight = Decimal(str(it.get("weight", 0)))

        if length <= 0 or width <= 0 or height <= 0:
            raise RecommendationEngineError(f"Item {it.get('sku', idx)} has non-positive dimensions ({length}x{width}x{height}).")
        if weight <= 0:
            raise RecommendationEngineError(f"Item {it.get('sku', idx)} has non-positive weight ({weight} kg).")

    # Stage 2: Calculate total weight
    total_weight = calculate_order_weight(items_data)

    # Stage 3: Filter boxes by weight & status
    candidates, rejected_boxes = filter_boxes_by_weight(available_boxes, total_weight)

    # Stage 4: Expand items into 3D packable items
    products_to_pack = expand_order_items(items_data)
    total_items_count = len(products_to_pack)

    eligible_boxes = []

    # Stage 5: Evaluate 3D packing for each candidate
    for box_info in candidates:
        pack_res = evaluate_box_packing(products_to_pack, box_info, allow_rotation=allow_rotation)
        if pack_res.success:
            # Weight utilization
            weight_util = Decimal("0.00")
            max_wt = Decimal(str(box_info["max_weight"]))
            if max_wt > Decimal("0.00"):
                weight_util = ((total_weight / max_wt) * Decimal("100.00")).quantize(Decimal("0.01"))

            eligible_boxes.append({
                "box": box_info,
                "packing": pack_res.to_dict(),
                "weight_utilization_pct": float(weight_util),
                "volume_utilization_pct": float(pack_res.volume_utilization_pct),
                "total_volume_used": str(pack_res.total_volume_used),
                "placements": [p.to_dict() for p in pack_res.placements],
            })
        else:
            rejected_boxes.append({
                "box": box_info,
                "reason": pack_res.reason
            })

    # Stage 6: Rank eligible boxes
    ranked_eligible = rank_eligible_boxes(eligible_boxes)

    recommended = ranked_eligible[0] if ranked_eligible else None
    alternatives = ranked_eligible[1:] if len(ranked_eligible) > 1 else []

    return {
        "success": True,
        "order_id": order_id,
        "order_number": order_number,
        "total_weight": str(total_weight),
        "total_items_count": total_items_count,
        "algorithm_version": "extreme_point_v1",
        "recommended_box": recommended,
        "alternatives": alternatives,
        "rejected_boxes": rejected_boxes,
        "has_suitable_box": recommended is not None,
    }
