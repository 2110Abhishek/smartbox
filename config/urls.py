"""
URL configuration for smartbox project.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from inventory.views import ProductViewSet, ShippingBoxViewSet
from orders.views import OrderViewSet
from recommendations import views as rec_views

# DRF Router
router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="api-products")
router.register(r"boxes", ShippingBoxViewSet, basename="api-boxes")
router.register(r"orders", OrderViewSet, basename="api-orders")

# API v1 routes specified in PRD Section 10
api_v1_patterns = [
    path("orders/<int:pk>/recommend/", rec_views.api_recommend_order, name="api-order-recommend"),
    path("orders/<int:pk>/recommendations/", rec_views.api_order_recommendations, name="api-order-recommendations"),
    path("recommendations/<int:pk>/", rec_views.api_recommendation_detail, name="api-recommendation-detail"),
    path("recommendations/<int:pk>/confirm/", rec_views.api_confirm_recommendation, name="api-recommendation-confirm"),
    path("recommendations/<int:pk>/complete/", rec_views.api_complete_packaging, name="api-recommendation-complete"),
]

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

    # REST API endpoints (/api/v1/...)
    path("api/v1/", include(router.urls)),
    path("api/v1/", include(api_v1_patterns)),
]
