"""
Filtering service for shipping boxes based on status, dimensions, and payload weight capacity.
"""
from decimal import Decimal
from typing import List, Tuple, Dict, Any


def filter_boxes_by_weight(
    boxes: List[Any],
    total_order_weight: Decimal
) -> Tuple[List[Any], List[Dict[str, Any]]]:
    """
    Filters boxes:
    - Active status
    - Valid dimensions & weight
    - Maximum payload weight >= total_order_weight

    Returns (candidates, rejected_due_to_weight_or_status)
    """
    candidates = []
    rejected = []

    for box in boxes:
        # Check active status
        is_active = getattr(box, "is_active", True)
        code = getattr(box, "code", "UNKNOWN")
        name = getattr(box, "name", code)
        max_weight = Decimal(str(getattr(box, "max_weight", 0)))
        cost = Decimal(str(getattr(box, "cost", 0)))
        length = Decimal(str(getattr(box, "length", 0)))
        width = Decimal(str(getattr(box, "width", 0)))
        height = Decimal(str(getattr(box, "height", 0)))
        volume = length * width * height

        box_info = {
            "box_id": getattr(box, "id", None),
            "code": code,
            "name": name,
            "max_weight": str(max_weight),
            "cost": str(cost),
            "cost_val": cost,
            "length": str(length),
            "width": str(width),
            "height": str(height),
            "volume": str(volume),
            "volume_val": volume,
        }

        if not is_active:
            rejected.append({
                "box": box_info,
                "reason": "Box is inactive."
            })
            continue

        if length <= 0 or width <= 0 or height <= 0 or max_weight <= 0:
            rejected.append({
                "box": box_info,
                "reason": "Box has invalid non-positive dimensions or capacity."
            })
            continue

        if total_order_weight > max_weight:
            rejected.append({
                "box": box_info,
                "reason": f"Maximum payload weight exceeded (Order: {total_order_weight} kg, Box limit: {max_weight} kg)."
            })
            continue

        candidates.append(box_info)

    return candidates, rejected
