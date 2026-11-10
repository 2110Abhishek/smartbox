"""
Generates unique 3D axis-aligned orientations for a rectangular product.
"""
from typing import List
from itertools import permutations
from recommendations.algorithms.geometry import Dimensions


def get_all_orientations(dims: Dimensions, allow_rotation: bool = True) -> List[Dimensions]:
    """
    Generate all unique axis-aligned orientations for a 3D cuboid.
    If allow_rotation is False, only returns the original orientation.
    Filters out duplicates when dimensions are equal (e.g. cubes or square faces).
    """
    if not allow_rotation:
        return [dims]

    # Permutations of (length, width, height)
    raw_orientations = [
        (dims.length, dims.width, dims.height),
        (dims.length, dims.height, dims.width),
        (dims.width, dims.length, dims.height),
        (dims.width, dims.height, dims.length),
        (dims.height, dims.length, dims.width),
        (dims.height, dims.width, dims.length),
    ]

    seen = set()
    unique_orientations = []

    for l, w, h in raw_orientations:
        key = (l, w, h)
        if key not in seen:
            seen.add(key)
            unique_orientations.append(Dimensions(length=l, width=w, height=h))

    return unique_orientations

