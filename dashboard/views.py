from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg
from decimal import Decimal

from inventory.models import Product, ShippingBox
from orders.models import Order, OrderStatus
from recommendations.models import Recommendation, BoxEvaluationResult


@login_required
def dashboard_index(request):
    # Counts
    active_products_count = Product.objects.filter(is_active=True).count()
    available_boxes_count = ShippingBox.objects.filter(is_active=True).count()
    total_orders_count = Order.objects.count()
    pending_orders_count = Order.objects.filter(
        status__in=[OrderStatus.PENDING, OrderStatus.READY_FOR_PACKAGING, OrderStatus.RECOMMENDED]
    ).count()
    completed_orders_count = Order.objects.filter(
        status__in=[OrderStatus.PACKED, OrderStatus.COMPLETED]
    ).count()

    # Cost statistics from recommendations
    successful_recs = Recommendation.objects.filter(has_suitable_box=True)
    total_cost_agg = successful_recs.aggregate(total_cost=Sum("selected_cost"))
    total_packaging_cost = total_cost_agg["total_cost"] or Decimal("0.00")

    avg_cost_agg = successful_recs.aggregate(avg_cost=Avg("selected_cost"))
    avg_packaging_cost = (avg_cost_agg["avg_cost"] or Decimal("0.00")).quantize(Decimal("0.01")) if avg_cost_agg["avg_cost"] else Decimal("0.00")

    # Most frequently recommended box
    most_common_box_data = (
        successful_recs.values("selected_box_code", "selected_box_name")
        .annotate(usage_count=Count("id"))
        .order_by("-usage_count")
        .first()
    )

    # Recent orders
    recent_orders = Order.objects.prefetch_related("items").all()[:8]

    # Recent recommendations
    recent_recommendations = Recommendation.objects.select_related("order").all()[:6]

    # Orders awaiting packaging
    awaiting_packaging = Order.objects.filter(
        status__in=[OrderStatus.PENDING, OrderStatus.READY_FOR_PACKAGING]
    ).prefetch_related("items")[:6]

    context = {
        "active_products_count": active_products_count,
        "available_boxes_count": available_boxes_count,
        "total_orders_count": total_orders_count,
        "pending_orders_count": pending_orders_count,
        "completed_orders_count": completed_orders_count,
        "total_packaging_cost": total_packaging_cost,
        "avg_packaging_cost": avg_packaging_cost,
        "most_common_box": most_common_box_data,
        "recent_orders": recent_orders,
        "recent_recommendations": recent_recommendations,
        "awaiting_packaging": awaiting_packaging,
    }
    return render(request, "dashboard/index.html", context)


@login_required
def analytics_view(request):
    total_recs = Recommendation.objects.count()
    successful_recs = Recommendation.objects.filter(has_suitable_box=True).count()
    unsuitable_recs = total_recs - successful_recs

    # Box usage distribution
    box_usage = (
        Recommendation.objects.filter(has_suitable_box=True)
        .values("selected_box_code", "selected_box_name")
        .annotate(count=Count("id"), total_cost=Sum("selected_cost"))
        .order_by("-count")
    )

    # Box rejection frequency
    rejection_reasons = (
        BoxEvaluationResult.objects.filter(is_eligible=False)
        .values("rejection_reason")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )

    # Packaging cost totals
    total_cost = Recommendation.objects.filter(has_suitable_box=True).aggregate(Sum("selected_cost"))["selected_cost__sum"] or Decimal("0.00")
    avg_cost = Recommendation.objects.filter(has_suitable_box=True).aggregate(Avg("selected_cost"))["selected_cost__avg"] or Decimal("0.00")
    if avg_cost:
        avg_cost = avg_cost.quantize(Decimal("0.01"))

    context = {
        "total_recs": total_recs,
        "successful_recs": successful_recs,
        "unsuitable_recs": unsuitable_recs,
        "box_usage": box_usage,
        "rejection_reasons": rejection_reasons,
        "total_cost": total_cost,
        "avg_cost": avg_cost,
    }
    return render(request, "dashboard/analytics.html", context)
