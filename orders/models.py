from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from inventory.models import Product


class OrderStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    PENDING = "PENDING", "Pending"
    READY_FOR_PACKAGING = "READY", "Ready for packaging"
    RECOMMENDED = "RECOMMENDED", "Recommended"
    PACKED = "PACKED", "Packed"
    COMPLETED = "COMPLETED", "Completed"
    CANCELLED = "CANCELLED", "Cancelled"


class Order(models.Model):
    order_number = models.CharField(max_length=64, unique=True, db_index=True)
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=32,
        choices=OrderStatus.choices,
        default=OrderStatus.PENDING,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.order_number} - {self.customer_name} ({self.get_status_display()})"

    @property
    def total_weight(self) -> Decimal:
        total = Decimal("0.00")
        for item in self.items.all():
            total += item.total_weight
        return total.quantize(Decimal("0.01"))

    @property
    def total_quantity(self) -> int:
        return sum(item.quantity for item in self.items.all())

    @property
    def can_recommend(self) -> bool:
        return self.status != OrderStatus.CANCELLED and self.items.exists()

    def get_items_payload_for_recommendation(self):
        """
        Returns list of item dicts using the immutable snapshots!
        Preserves historical dimensions & weight.
        """
        payload = []
        for item in self.items.all():
            payload.append({
                "id": item.id,
                "product_id": item.product_id,
                "sku": item.product_sku_snapshot or (item.product.sku if item.product else ""),
                "name": item.product_name_snapshot or (item.product.name if item.product else ""),
                "length": str(item.length_snapshot),
                "width": str(item.width_snapshot),
                "height": str(item.height_snapshot),
                "weight": str(item.weight_snapshot),
                "quantity": item.quantity,
            })
        return payload


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Quantity of product (must be >= 1)"
    )

    # Immutable historical snapshots
    product_sku_snapshot = models.CharField(max_length=64, blank=True)
    product_name_snapshot = models.CharField(max_length=255, blank=True)
    length_snapshot = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    width_snapshot = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    height_snapshot = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    weight_snapshot = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        ordering = ["id"]

    def __str__(self):
        return f"{self.quantity}x {self.product_sku_snapshot or self.product.sku} for {self.order.order_number}"

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        if self.product and not self.product.is_active and not self.pk:
            raise ValidationError(f"Cannot add inactive product {self.product.sku} to a new order.")

    def save(self, *args, **kwargs):
        # Automatically capture product snapshot on first creation or if snapshot is blank
        if self.product:
            if not self.product_sku_snapshot:
                self.product_sku_snapshot = self.product.sku
            if not self.product_name_snapshot:
                self.product_name_snapshot = self.product.name
            if self.length_snapshot == Decimal("0.00"):
                self.length_snapshot = self.product.length
            if self.width_snapshot == Decimal("0.00"):
                self.width_snapshot = self.product.width
            if self.height_snapshot == Decimal("0.00"):
                self.height_snapshot = self.product.height
            if self.weight_snapshot == Decimal("0.00"):
                self.weight_snapshot = self.product.weight
        super().save(*args, **kwargs)

    @property
    def unit_volume(self) -> Decimal:
        return (self.length_snapshot * self.width_snapshot * self.height_snapshot).quantize(Decimal("0.01"))

    @property
    def total_weight(self) -> Decimal:
        return (self.weight_snapshot * self.quantity).quantize(Decimal("0.01"))
