from rest_framework import serializers
from recommendations.models import Recommendation, BoxEvaluationResult, ProductPlacementRecord


class ProductPlacementSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPlacementRecord
        fields = [
            "id", "item_sku", "item_name", "unit_index",
            "x", "y", "z",
            "placed_length", "placed_width", "placed_height"
        ]


class BoxEvaluationResultSerializer(serializers.ModelSerializer):
    placements = ProductPlacementSerializer(many=True, read_only=True)

    class Meta:
        model = BoxEvaluationResult
        fields = [
            "id", "box_code", "box_name", "cost", "volume",
            "is_eligible", "rejection_reason", "rank",
            "weight_utilization_pct", "volume_utilization_pct", "placements"
        ]


class RecommendationSerializer(serializers.ModelSerializer):
    box_results = BoxEvaluationResultSerializer(many=True, read_only=True)

    class Meta:
        model = Recommendation
        fields = [
            "id", "order", "selected_box_code", "selected_box_name",
            "selected_cost", "total_weight", "algorithm_version",
            "has_suitable_box", "is_confirmed", "confirmed_box_code",
            "confirmed_at", "created_at", "result_payload", "box_results"
        ]

