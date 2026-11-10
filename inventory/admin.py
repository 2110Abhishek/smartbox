from django.contrib import admin
from inventory.models import Product, ShippingBox


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["sku", "name", "length", "width", "height", "weight", "volume", "is_active", "updated_at"]
    search_fields = ["sku", "name"]
    list_filter = ["is_active"]


@admin.register(ShippingBox)
class ShippingBoxAdmin(admin.ModelAdmin):
    list_display = ["code", "name", "length", "width", "height", "max_weight", "cost", "volume", "is_active", "updated_at"]
    search_fields = ["code", "name"]
    list_filter = ["is_active"]
