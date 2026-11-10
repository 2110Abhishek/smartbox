"""
Geometry and 3D data structures for box packing.
Uses Decimal for precise dimensional calculations without floating-point artifacts.
"""
from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from typing import Any, List, Optional


def to_decimal(val: Any) -> Decimal:
    """Helper to convert float, int, str to Decimal with 2 decimal places."""
    if isinstance(val, Decimal):
        return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Point3D:
    x: Decimal
    y: Decimal
    z: Decimal

    def __post_init__(self):
        object.__setattr__(self, "x", to_decimal(self.x))
        object.__setattr__(self, "y", to_decimal(self.y))
        object.__setattr__(self, "z", to_decimal(self.z))

    def to_dict(self):
        return {"x": str(self.x), "y": str(self.y), "z": str(self.z)}

    def __repr__(self):
        return f"Point3D({self.x}, {self.y}, {self.z})"


@dataclass(frozen=True)
class Dimensions:
    length: Decimal
    width: Decimal
    height: Decimal

    def __post_init__(self):
        object.__setattr__(self, "length", to_decimal(self.length))
        object.__setattr__(self, "width", to_decimal(self.width))
        object.__setattr__(self, "height", to_decimal(self.height))

    @property
    def volume(self) -> Decimal:
        return (self.length * self.width * self.height).quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP)

    @property
    def longest_side(self) -> Decimal:
        return max(self.length, self.width, self.height)

    def to_dict(self):
        return {
            "length": str(self.length),
            "width": str(self.width),
            "height": str(self.height),
            "volume": str(self.volume),
        }

    def __repr__(self):
        return f"Dimensions(L={self.length}, W={self.width}, H={self.height})"


@dataclass
class ItemToPack:
    id: Any
    sku: str
    name: str
    dimensions: Dimensions
    weight: Decimal
    unit_index: int = 1

    def __post_init__(self):
        self.weight = to_decimal(self.weight)

    @property
    def volume(self) -> Decimal:
        return self.dimensions.volume

    @property
    def longest_side(self) -> Decimal:
        return self.dimensions.longest_side


@dataclass
class Placement:
    item_id: Any
    sku: str
    name: str
    unit_index: int
    position: Point3D
    dimensions: Dimensions

    @property
    def x(self) -> Decimal:
        return self.position.x

    @property
    def y(self) -> Decimal:
        return self.position.y

    @property
    def z(self) -> Decimal:
        return self.position.z

    @property
    def x_end(self) -> Decimal:
        return self.position.x + self.dimensions.length

    @property
    def y_end(self) -> Decimal:
        return self.position.y + self.dimensions.width

    @property
    def z_end(self) -> Decimal:
        return self.position.z + self.dimensions.height

    def to_dict(self):
        return {
            "item_id": self.item_id,
            "sku": self.sku,
            "name": self.name,
            "unit_index": self.unit_index,
            "position": self.position.to_dict(),
            "dimensions": self.dimensions.to_dict(),
            "bounding_box": {
                "x_start": str(self.x),
                "x_end": str(self.x_end),
                "y_start": str(self.y),
                "y_end": str(self.y_end),
                "z_start": str(self.z),
                "z_end": str(self.z_end),
            },
        }


@dataclass
class PackingResult:
    success: bool
    reason: str = ""
    placements: List[Placement] = field(default_factory=list)
    algorithm: str = "extreme_point_v1"
    box_code: Optional[str] = None
    placed_items_count: int = 0
    total_volume_used: Decimal = Decimal("0.00")
    volume_utilization_pct: Decimal = Decimal("0.00")

    def to_dict(self):
        return {
            "success": self.success,
            "reason": self.reason,
            "algorithm": self.algorithm,
            "box_code": self.box_code,
            "placed_items_count": self.placed_items_count,
            "total_volume_used": str(self.total_volume_used),
            "volume_utilization_pct": float(self.volume_utilization_pct),
            "placements": [p.to_dict() for p in self.placements],
        }
