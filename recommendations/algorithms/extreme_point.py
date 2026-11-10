"""
Deterministic 3D Bin Packing heuristic using the Extreme Point (EP) algorithm.
Accurately places rectangular cuboids inside a target box without overlapping,
validating 3D boundaries and considering all unique orientations.
"""
from decimal import Decimal
from typing import List, Set, Tuple, Optional
from recommendations.algorithms.geometry import (
    Point3D, Dimensions, ItemToPack, Placement, PackingResult
)
from recommendations.algorithms.orientation import get_all_orientations
from recommendations.algorithms.collision import is_within_box, has_collision_with_existing


def _is_point_inside_placed_item(point: Point3D, placements: List[Placement]) -> bool:
    """Check if point is strictly inside any already placed item cuboid."""
    for p in placements:
        if (p.x <= point.x < p.x_end and
            p.y <= point.y < p.y_end and
            p.z <= point.z < p.z_end):
            return True
    return False


def _generate_candidate_points(
    box_dims: Dimensions,
    new_placement: Placement,
    current_points: Set[Point3D],
    all_placements: List[Placement]
) -> Set[Point3D]:
    """
    Generate new extreme points after placing an item and filter out covered/invalid points.
    Based on the classical 3D Extreme Point method for Bin Packing (Crainic et al.).
    """
    candidate_points = set(current_points)

    # The point where the item was placed is now occupied
    candidate_points.discard(new_placement.position)

    # Placed bounding bounds
    nx, ny, nz = new_placement.x, new_placement.y, new_placement.z
    nx_end, ny_end, nz_end = new_placement.x_end, new_placement.y_end, new_placement.z_end

    # 1. Base extreme points generated directly by the 3 faces of the placed cuboid
    raw_new_points = [
        Point3D(nx_end, ny, nz),
        Point3D(nx, ny_end, nz),
        Point3D(nx, ny, nz_end),
    ]

    # 2. Projection extreme points aligned with other placed items and box edges
    # For every other placed item, project the new item's boundaries onto coordinate lines
    for p in all_placements:
        if p == new_placement:
            continue
        # Points along x = nx_end
        if p.y_end <= box_dims.width:
            raw_new_points.append(Point3D(nx_end, p.y_end, nz))
            raw_new_points.append(Point3D(nx_end, p.y, nz))
        if p.z_end <= box_dims.height:
            raw_new_points.append(Point3D(nx_end, ny, p.z_end))
            raw_new_points.append(Point3D(nx_end, ny, p.z))

        # Points along y = ny_end
        if p.x_end <= box_dims.length:
            raw_new_points.append(Point3D(p.x_end, ny_end, nz))
            raw_new_points.append(Point3D(p.x, ny_end, nz))
        if p.z_end <= box_dims.height:
            raw_new_points.append(Point3D(nx, ny_end, p.z_end))
            raw_new_points.append(Point3D(nx, ny_end, p.z))

        # Points along z = nz_end
        if p.x_end <= box_dims.length:
            raw_new_points.append(Point3D(p.x_end, ny, nz_end))
            raw_new_points.append(Point3D(p.x, ny, nz_end))
        if p.y_end <= box_dims.width:
            raw_new_points.append(Point3D(nx, p.y_end, nz_end))
            raw_new_points.append(Point3D(nx, p.y, nz_end))

    # Add valid new points
    for pt in raw_new_points:
        if (0 <= pt.x < box_dims.length and
            0 <= pt.y < box_dims.width and
            0 <= pt.z < box_dims.height):
            candidate_points.add(pt)

    # Filter all candidate points: must not be inside any placed item
    valid_points = set()
    for pt in candidate_points:
        if not _is_point_inside_placed_item(pt, all_placements):
            valid_points.add(pt)

    return valid_points


def pack_products_3d(
    products: List[ItemToPack],
    box_dims: Dimensions,
    box_code: Optional[str] = None,
    allow_rotation: bool = True
) -> PackingResult:
    """
    3D bin packing using Extreme Point Heuristic.
    - Sorts products descending by volume, then longest side, then weight, then SKU.
    - Tests candidate extreme points sorted by min z (floor), then min y, then min x.
    - Tests all 6 axis-aligned orientations (deduplicated).
    - Checks boundary constraints and 3D collision with previously placed items.
    """
    if not products:
        return PackingResult(
            success=True,
            reason="No products to pack.",
            algorithm="extreme_point_v1",
            box_code=box_code
        )

    # 1. Check if any individual item exceeds box dimensions in all possible orientations
    origin = Point3D(Decimal("0.00"), Decimal("0.00"), Decimal("0.00"))
    for item in products:
        orientations = get_all_orientations(item.dimensions, allow_rotation=allow_rotation)
        fits_alone = any(is_within_box(origin, ori, box_dims) for ori in orientations)
        if not fits_alone:
            return PackingResult(
                success=False,
                reason=f"Product '{item.name}' exceeds box dimensions in all possible orientations.",
                algorithm="extreme_point_v1",
                box_code=box_code
            )

    # 2. Check total volume pre-filter
    total_product_volume = sum(p.volume for p in products)
    if total_product_volume > box_dims.volume:
        return PackingResult(
            success=False,
            reason="Total product volume exceeds box internal volume.",
            algorithm="extreme_point_v1",
            box_code=box_code
        )

    # Sort products: descending by volume, longest side, weight, and id
    sorted_products = sorted(
        products,
        key=lambda item: (item.volume, item.longest_side, item.weight, str(item.sku)),
        reverse=True
    )

    placements: List[Placement] = []
    extreme_points: Set[Point3D] = {Point3D(Decimal("0.00"), Decimal("0.00"), Decimal("0.00"))}

    for item in sorted_products:
        orientations = get_all_orientations(item.dimensions, allow_rotation=allow_rotation)
        placed = False

        # Sort candidate extreme points: prefer lowest z (gravity/floor), lowest y (back), lowest x (left)
        sorted_points = sorted(extreme_points, key=lambda pt: (pt.z, pt.y, pt.x))

        for pt in sorted_points:
            for ori in orientations:
                # 1. Boundary check
                if not is_within_box(pt, ori, box_dims):
                    continue

                # 2. Collision check
                if has_collision_with_existing(pt, ori, placements):
                    continue

                # Valid placement found!
                placement = Placement(
                    item_id=item.id,
                    sku=item.sku,
                    name=item.name,
                    unit_index=item.unit_index,
                    position=pt,
                    dimensions=ori
                )
                placements.append(placement)
                extreme_points = _generate_candidate_points(
                    box_dims, placement, extreme_points, placements
                )
                placed = True
                break

            if placed:
                break

        if not placed:
            # Check if product simply exceeds all box dimensions in any orientation
            fits_alone = any(
                is_within_box(Point3D(Decimal("0.00"), Decimal("0.00"), Decimal("0.00")), ori, box_dims)
                for ori in orientations
            )
            if not fits_alone:
                reason = f"Product '{item.name}' exceeds box dimensions in all possible orientations."
            else:
                reason = f"Product '{item.name}' cannot be placed within internal dimensions using the packing heuristic."

            return PackingResult(
                success=False,
                reason=reason,
                algorithm="extreme_point_v1",
                box_code=box_code,
                placements=placements
            )

    # Calculate utilization
    used_volume = sum(p.dimensions.volume for p in placements)
    utilization_pct = Decimal("0.00")
    if box_dims.volume > Decimal("0.00"):
        utilization_pct = ((used_volume / box_dims.volume) * Decimal("100.00")).quantize(Decimal("0.01"))

    return PackingResult(
        success=True,
        reason="All products successfully packed.",
        placements=placements,
        algorithm="extreme_point_v1",
        box_code=box_code,
        placed_items_count=len(placements),
        total_volume_used=used_volume,
        volume_utilization_pct=utilization_pct
    )
