"""
Collision detection and boundary validation for 3D packaging.
"""
from typing import List
from recommendations.algorithms.geometry import Point3D, Dimensions, Placement


def is_within_box(point: Point3D, dims: Dimensions, box_dims: Dimensions) -> bool:
    """
    Check if a placed cuboid with position and dimensions fits entirely inside the box boundaries:
    0 <= x, x + l <= L
    0 <= y, y + w <= W
    0 <= z, z + h <= H
    """
    if point.x < 0 or point.y < 0 or point.z < 0:
        return False
    if (point.x + dims.length) > box_dims.length:
        return False
    if (point.y + dims.width) > box_dims.width:
        return False
    if (point.z + dims.height) > box_dims.height:
        return False
    return True


def check_overlap(
    p1: Point3D, d1: Dimensions,
    p2: Point3D, d2: Dimensions
) -> bool:
    """
    Check if two 3D cuboids overlap.
    Non-overlap condition (Separating Axis Theorem for axis-aligned bounding boxes):
    Separated if one is completely to the left/right, front/back, or bottom/top of the other.
    Touching surfaces (e.g. p1.x + d1.length == p2.x) are ALLOWED and do not count as overlap.
    Returns True if they overlap, False if they are separated.
    """
    p1_x_end = p1.x + d1.length
    p1_y_end = p1.y + d1.width
    p1_z_end = p1.z + d1.height

    p2_x_end = p2.x + d2.length
    p2_y_end = p2.y + d2.width
    p2_z_end = p2.z + d2.height

    # If any axis is separated, there is no collision
    if p1_x_end <= p2.x or p2_x_end <= p1.x:
        return False
    if p1_y_end <= p2.y or p2_y_end <= p1.y:
        return False
    if p1_z_end <= p2.z or p2_z_end <= p1.z:
        return False

    # Overlaps in all 3 dimensions
    return True


def has_collision_with_existing(
    point: Point3D,
    dims: Dimensions,
    existing_placements: List[Placement]
) -> bool:
    """
    Check if placing an item at the given point with dimensions collides with any already placed item.
    """
    for placed in existing_placements:
        if check_overlap(point, dims, placed.position, placed.dimensions):
            return True
    return False
