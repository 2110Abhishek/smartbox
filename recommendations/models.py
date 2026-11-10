from django.db import models
from django.utils import timezone
from django.core.serializers.json import DjangoJSONEncoder
from decimal import Decimal
from orders.models import Order
from inventory.models import ShippingBox


class Recommendation(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="recommendations")
    selected_box = models.ForeignKey(ShippingBox, on_delete=models.SET_NULL, null=True, blank=True, related_name="recommendation_selections")

    # Snapshot of the recommended box at time of calculation
    selected_box_code = models.CharField(max_length=64, blank=True)
    selected_box_name = models.CharField(max_length=255, blank=True)
    selected_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    total_weight = models.DecimalField(max_digits=10, decimal_places=2)
    algorithm_version = models.CharField(max_length=64, default="extreme_point_v1")
    has_suitable_box = models.BooleanField(default=False)

    # Immutable historical snapshots
    input_snapshot = models.JSONField(default=dict, encoder=DjangoJSONEncoder, help_text="Snapshot of evaluated order items and box parameters")
    result_payload = models.JSONField(default=dict, encoder=DjangoJSONEncoder, help_text="Full recommendation result tree")

    # Confirmation & packaging lifecycle
    is_confirmed = models.BooleanField(default=False)
    confirmed_box_code = models.CharField(max_length=64, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        status_str = f"Recommended: {self.selected_box_code}" if self.has_suitable_box else "No suitable box"
        return f"Rec #{self.id} for {self.order.order_number} ({status_str})"

    def confirm_box(self, box_code: str):
        self.is_confirmed = True
        self.confirmed_box_code = box_code
        self.confirmed_at = timezone.now()
        self.save()


class BoxEvaluationResult(models.Model):
    recommendation = models.ForeignKey(Recommendation, on_delete=models.CASCADE, related_name="box_results")
    box_code = models.CharField(max_length=64)
    box_name = models.CharField(max_length=255)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.DecimalField(max_digits=14, decimal_places=4)
    is_eligible = models.BooleanField(default=False)
    rejection_reason = models.TextField(blank=True)
    rank = models.PositiveIntegerField(null=True, blank=True)
    weight_utilization_pct = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.00"))
    volume_utilization_pct = models.DecimalField(max_digits=6, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        ordering = ["cost", "volume", "box_code"]

    def __str__(self):
        elig = "Eligible" if self.is_eligible else f"Rejected: {self.rejection_reason}"
        return f"{self.box_code} ({elig})"


class ProductPlacementRecord(models.Model):
    box_result = models.ForeignKey(BoxEvaluationResult, on_delete=models.CASCADE, related_name="placements")
    item_sku = models.CharField(max_length=64)
    item_name = models.CharField(max_length=255)
    unit_index = models.PositiveIntegerField(default=1)

    # 3D placement coordinates (x, y, z)
    x = models.DecimalField(max_digits=10, decimal_places=2)
    y = models.DecimalField(max_digits=10, decimal_places=2)
    z = models.DecimalField(max_digits=10, decimal_places=2)

    # Oriented dimensions
    placed_length = models.DecimalField(max_digits=10, decimal_places=2)
    placed_width = models.DecimalField(max_digits=10, decimal_places=2)
    placed_height = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["z", "y", "x"]

    def __str__(self):
        return f"{self.item_sku} #{self.unit_index} at ({self.x}, {self.y}, {self.z})"
