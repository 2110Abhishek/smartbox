"""
Service to expand order items into individual 3D packable items and run packing validation.
"""
from decimal import Decimal
from typing import List, Dict, Any
from recommendations.algorithms.geometry import Dimensions, ItemToPack, PackingResult
from recommendations.algorithms.extreme_point import pack_products_3d


def expand_order_items(items: List[Dict[str, Any]]) -> List[ItemToPack]:
    """
    Expands an order's items list into individual item instances based on quantity.
    Each instance gets a unit_index from 1 to quantity.
    """
    expanded: List[ItemToPack] = []

    for item in items:
        item_id = item.get("id") or item.get("product_id")
        sku = str(item.get("sku", ""))
        name = str(item.get("name", sku))
        qty = int(item.get("quantity", 1))

        length = Decimal(str(item.get("length", 0)))
        width = Decimal(str(item.get("width", 0)))
        height = Decimal(str(item.get("height", 0)))
        weight = Decimal(str(item.get("weight", 0)))

        dims = Dimensions(length=length, width=width, height=height)

        for unit_idx in range(1, qty + 1):
            expanded.append(
                ItemToPack(
                    id=item_id,
                    sku=sku,
                    name=name,
                    dimensions=dims,
                    weight=weight,
                    unit_index=unit_idx
                )
            )

    return expanded


def evaluate_box_packing(
    products: List[ItemToPack],
    box_info: Dict[str, Any],
    allow_rotation: bool = True
) -> PackingResult:
    """
    Packs the expanded list of products into a candidate box using 3D extreme-point algorithm.
    """
    box_dims = Dimensions(
        length=Decimal(str(box_info["length"])),
        width=Decimal(str(box_info["width"])),
        height=Decimal(str(box_info["height"]))
    )
    return pack_products_3d(
        products=products,
        box_dims=box_dims,
        box_code=box_info.get("code"),
        allow_rotation=allow_rotation
    )

