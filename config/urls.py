"""
URL configuration for smartbox project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from inventory.views import ProductViewSet, ShippingBoxViewSet
from orders.views import OrderViewSet

# DRF Router
router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="api-products")
router.register(r"boxes", ShippingBoxViewSet, basename="api-boxes")
router.register(r"orders", OrderViewSet, basename="api-orders")

urlpatterns = [
    path("admin/", admin.site.urls),

    # Dashboard & Home
    path("", include("dashboard.urls")),

    # Auth
    path("accounts/", include("accounts.urls")),

    # Modules
    path("inventory/", include("inventory.urls")),
    path("orders/", include("orders.urls")),
    path("recommendations/", include("recommendations.urls")),

    # REST API endpoints
    path("api/v1/", include(router.urls)),
]
