from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from orders.models import Order, OrderStatus
from inventory.models import ShippingBox
from recommendations.models import Recommendation, BoxEvaluationResult, ProductPlacementRecord
from recommendations.services.recommendation_service import run_box_recommendation, RecommendationEngineError
from recommendations.serializers import RecommendationSerializer


def process_order_recommendation(order: Order, allow_rotation: bool = True) -> Recommendation:
    """
    Executes recommendation pipeline and stores immutable snapshots in DB within a transaction.
    """
    if order.status == OrderStatus.CANCELLED:
        raise RecommendationEngineError("Cancelled orders cannot receive new recommendations.")
    if not order.items.exists():
        raise RecommendationEngineError("Order must contain at least one item before generating recommendations.")

    items_data = order.get_items_payload_for_recommendation()
    available_boxes = list(ShippingBox.objects.all())

    # Run recommendation algorithm
    result_data = run_box_recommendation(
        items_data=items_data,
        available_boxes=available_boxes,
        order_id=order.id,
        order_number=order.order_number,
        allow_rotation=allow_rotation
    )

    with transaction.atomic():
        recommended_info = result_data.get("recommended_box")
        selected_box_instance = None
        selected_code = ""
        selected_name = ""
        selected_cost = None

        if recommended_info:
            selected_code = recommended_info["box"]["code"]
            selected_name = recommended_info["box"]["name"]
            selected_cost = Decimal(str(recommended_info["box"]["cost"]))
            # Match current DB instance if available (PROTECT on delete)
            selected_box_instance = ShippingBox.objects.filter(code=selected_code).first()

        rec = Recommendation.objects.create(
            order=order,
            selected_box=selected_box_instance,
            selected_box_code=selected_code,
            selected_box_name=selected_name,
            selected_cost=selected_cost,
            total_weight=Decimal(str(result_data["total_weight"])),
            algorithm_version=result_data["algorithm_version"],
            has_suitable_box=result_data["has_suitable_box"],
            input_snapshot={
                "items": items_data,
                "box_count_evaluated": len(available_boxes)
            },
            result_payload=result_data
        )

        # Persist eligible boxes and placements
        rank = 1
        if recommended_info:
            _persist_box_result(rec, recommended_info, is_eligible=True, rank=rank)
            rank += 1

        for alt in result_data.get("alternatives", []):
            _persist_box_result(rec, alt, is_eligible=True, rank=rank)
            rank += 1

        # Persist rejected boxes
        for rej in result_data.get("rejected_boxes", []):
            BoxEvaluationResult.objects.create(
                recommendation=rec,
                box_code=rej["box"]["code"],
                box_name=rej["box"]["name"],
                cost=Decimal(str(rej["box"]["cost"])),
                volume=Decimal(str(rej["box"]["volume"])),
                is_eligible=False,
                rejection_reason=rej["reason"]
            )

        # Update order status if suitable box found
        if rec.has_suitable_box:
            order.status = OrderStatus.RECOMMENDED
            order.save()

    return rec


def _persist_box_result(rec: Recommendation, box_eval: dict, is_eligible: bool, rank: int = 1):
    box_info = box_eval["box"]
    res = BoxEvaluationResult.objects.create(
        recommendation=rec,
        box_code=box_info["code"],
        box_name=box_info["name"],
        cost=Decimal(str(box_info["cost"])),
        volume=Decimal(str(box_info["volume"])),
        is_eligible=is_eligible,
        rejection_reason="",
        rank=rank,
        weight_utilization_pct=Decimal(str(box_eval.get("weight_utilization_pct", 0))),
        volume_utilization_pct=Decimal(str(box_eval.get("volume_utilization_pct", 0)))
    )

    for p in box_eval.get("placements", []):
        ProductPlacementRecord.objects.create(
            box_result=res,
            item_sku=p["sku"],
            item_name=p["name"],
            unit_index=p["unit_index"],
            x=Decimal(str(p["position"]["x"])),
            y=Decimal(str(p["position"]["y"])),
            z=Decimal(str(p["position"]["z"])),
            placed_length=Decimal(str(p["dimensions"]["length"])),
            placed_width=Decimal(str(p["dimensions"]["width"])),
            placed_height=Decimal(str(p["dimensions"]["height"]))
        )


# ---------------------------------
# Web Views: Recommendations
# ---------------------------------

@login_required
def generate_recommendation(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    try:
        rec = process_order_recommendation(order)
        if rec.has_suitable_box:
            messages.success(request, f"Recommended {rec.selected_box_code} for order {order.order_number}.")
        else:
            messages.warning(request, f"No suitable box could be found for order {order.order_number}. See rejection reasons.")
        return redirect("recommendations:recommendation_detail", pk=rec.pk)
    except RecommendationEngineError as e:
        messages.error(request, str(e))
        return redirect("orders:order_detail", pk=order.pk)


@login_required
def recommendation_detail(request, pk):
    rec = get_object_or_404(
        Recommendation.objects.select_related("order", "selected_box").prefetch_related("box_results__placements"),
        pk=pk
    )
    eligible_results = rec.box_results.filter(is_eligible=True).order_by("rank")
    rejected_results = rec.box_results.filter(is_eligible=False)
    primary_result = eligible_results.first()

    box_dims = {"length": 30.0, "width": 20.0, "height": 15.0}
    if rec.result_payload and "recommended_box" in rec.result_payload and rec.result_payload["recommended_box"]:
        b_info = rec.result_payload["recommended_box"]["box"]
        box_dims = {
            "length": float(b_info.get("length", 30)),
            "width": float(b_info.get("width", 20)),
            "height": float(b_info.get("height", 15)),
        }
    elif rec.selected_box:
        box_dims = {
            "length": float(rec.selected_box.length),
            "width": float(rec.selected_box.width),
            "height": float(rec.selected_box.height),
        }

    placements_data = []
    if primary_result:
        for p in primary_result.placements.all():
            placements_data.append({
                "sku": p.item_sku,
                "name": p.item_name,
                "unit_index": p.unit_index,
                "x": float(p.x),
                "y": float(p.y),
                "z": float(p.z),
                "length": float(p.placed_length),
                "width": float(p.placed_width),
                "height": float(p.placed_height),
            })

    import json
    return render(request, "recommendations/recommendation_detail.html", {
        "recommendation": rec,
        "order": rec.order,
        "primary_result": primary_result,
        "eligible_results": eligible_results,
        "rejected_results": rejected_results,
        "box_dims_json": json.dumps(box_dims),
        "placements_json": json.dumps(placements_data),
    })


@login_required
def confirm_box_selection(request, pk):
    rec = get_object_or_404(Recommendation, pk=pk)
    if request.method == "POST":
        selected_code = request.POST.get("box_code")
        # Ensure box is eligible
        eligible = rec.box_results.filter(is_eligible=True, box_code=selected_code).first()
        if not eligible:
            messages.error(request, f"Box {selected_code} is not an eligible box for this order.")
            return redirect("recommendations:recommendation_detail", pk=pk)

        rec.confirm_box(selected_code)
        rec.order.status = OrderStatus.READY_FOR_PACKAGING
        rec.order.save()
        messages.success(request, f"Box {selected_code} confirmed for packaging.")
    return redirect("recommendations:recommendation_detail", pk=pk)


@login_required
def mark_order_packed(request, pk):
    rec = get_object_or_404(Recommendation, pk=pk)
    if request.method == "POST":
        rec.order.status = OrderStatus.PACKED
        rec.order.save()
        messages.success(request, f"Order {rec.order.order_number} marked as PACKED.")
    return redirect("orders:order_detail", pk=rec.order.pk)


@login_required
def mark_order_completed(request, pk):
    rec = get_object_or_404(Recommendation, pk=pk)
    if request.method == "POST":
        rec.order.status = OrderStatus.COMPLETED
        rec.order.save()
        messages.success(request, f"Order {rec.order.order_number} marked as COMPLETED.")
    return redirect("orders:order_detail", pk=rec.order.pk)


@login_required
def recommendation_history(request):
    recommendations = Recommendation.objects.select_related("order").all()
    return render(request, "recommendations/recommendation_history.html", {
        "recommendations": recommendations
    })


# ---------------------------------
# REST API Endpoints
# ---------------------------------

@api_view(["POST"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def api_recommend_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    try:
        rec = process_order_recommendation(order)
        serializer = RecommendationSerializer(rec)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except RecommendationEngineError as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def api_order_recommendations(request, pk):
    order = get_object_or_404(Order, pk=pk)
    recs = order.recommendations.all()
    serializer = RecommendationSerializer(recs, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def api_recommendation_detail(request, pk):
    rec = get_object_or_404(Recommendation, pk=pk)
    serializer = RecommendationSerializer(rec)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def api_confirm_recommendation(request, pk):
    rec = get_object_or_404(Recommendation, pk=pk)
    box_code = request.data.get("box_code")
    if not box_code:
        return Response({"error": "box_code is required."}, status=status.HTTP_400_BAD_REQUEST)

    eligible = rec.box_results.filter(is_eligible=True, box_code=box_code).first()
    if not eligible:
        return Response({"error": f"Box {box_code} is not an eligible option."}, status=status.HTTP_400_BAD_REQUEST)

    rec.confirm_box(box_code)
    rec.order.status = OrderStatus.READY_FOR_PACKAGING
    rec.order.save()
    return Response({"message": f"Box {box_code} confirmed.", "recommendation_id": rec.id})


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticatedOrReadOnly])
def api_complete_packaging(request, pk):
    rec = get_object_or_404(Recommendation, pk=pk)
    rec.order.status = OrderStatus.COMPLETED
    rec.order.save()
    return Response({"message": f"Order {rec.order.order_number} packaging completed.", "order_status": "COMPLETED"})
