"""
Ranking service for eligible packaging boxes.
Ranks boxes by:
1. Lowest packaging material cost
2. Lowest internal box volume
3. Stable box code alphabetical ordering
"""
from decimal import Decimal
from typing import List, Dict, Any


def rank_eligible_boxes(eligible_boxes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Ranks eligible packaging boxes deterministically:
    Key: (cost, volume, code)
    """
    return sorted(
        eligible_boxes,
        key=lambda item: (
            Decimal(str(item["box"]["cost"])),
            Decimal(str(item["box"]["volume"])),
            str(item["box"]["code"])
        )
    )
