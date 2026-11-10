from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from rest_framework import viewsets, permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from orders.models import Order, OrderItem, OrderStatus
from orders.forms import OrderForm, OrderItemFormSet
from inventory.models import Product


# ---------------------------------
# Web Views: Orders
# ---------------------------------

@login_required
def order_list(request):
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "")

    orders = Order.objects.prefetch_related("items").all()
    if query:
        orders = orders.filter(
            Q(order_number__icontains=query) |
            Q(customer_name__icontains=query) |
            Q(customer_email__icontains=query)
        )
    if status_filter:
        orders = orders.filter(status=status_filter)

    return render(request, "orders/order_list.html", {
        "orders": orders,
        "query": query,
        "status_filter": status_filter,
        "statuses": OrderStatus.choices,
    })


@login_required
def pending_orders(request):
    """View specifically for orders awaiting packaging."""
    orders = Order.objects.filter(
        status__in=[OrderStatus.PENDING, OrderStatus.READY_FOR_PACKAGING, OrderStatus.RECOMMENDED]
    ).prefetch_related("items")
    return render(request, "orders/pending_orders.html", {"orders": orders})


@login_required
def order_create(request):
    if request.method == "POST":
        form = OrderForm(request.POST)
        formset = OrderItemFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            order = form.save(commit=False)
            order.created_by = request.user
            order.save()
            formset.instance = order
            formset.save()
            messages.success(request, f"Order {order.order_number} created successfully.")
            return redirect("orders:order_detail", pk=order.pk)
    else:
        # Pre-generate unique order number
        import uuid
        order_num = f"ORD-{uuid.uuid4().hex[:6].upper()}"
        form = OrderForm(initial={"order_number": order_num, "status": OrderStatus.PENDING})
        formset = OrderItemFormSet()

    return render(request, "orders/order_form.html", {
        "form": form,
        "formset": formset,
        "title": "Create New Order"
    })


@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order.objects.prefetch_related("items", "recommendations"), pk=pk)
    latest_rec = order.recommendations.first()
    return render(request, "orders/order_detail.html", {
        "order": order,
        "items": order.items.all(),
        "latest_rec": latest_rec,
    })


@login_required
def order_cancel(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.status == OrderStatus.COMPLETED:
        messages.error(request, "Completed orders cannot be cancelled.")
    else:
        order.status = OrderStatus.CANCELLED
        order.save()
        messages.warning(request, f"Order {order.order_number} has been cancelled.")
    return redirect("orders:order_detail", pk=pk)


# ---------------------------------
# REST API Serializers & ViewSets
# ---------------------------------

class OrderItemSerializer(serializers.ModelSerializer):
    unit_volume = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_weight = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            "id", "product", "quantity",
            "product_sku_snapshot", "product_name_snapshot",
            "length_snapshot", "width_snapshot", "height_snapshot", "weight_snapshot",
            "unit_volume", "total_weight"
        ]
        read_only_fields = [
            "product_sku_snapshot", "product_name_snapshot",
            "length_snapshot", "width_snapshot", "height_snapshot", "weight_snapshot"
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_weight = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_quantity = serializers.IntegerField(read_only=True)

    class Meta:
        model = Order
        fields = [
            "id", "order_number", "customer_name", "customer_email",
            "status", "created_by", "created_at", "updated_at",
            "total_weight", "total_quantity", "items"
        ]


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.prefetch_related("items").all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=["post"])
    def add_item(self, request, pk=None):
        order = self.get_object()
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        if quantity <= 0:
            return Response({"error": "Quantity must be positive."}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, pk=product_id)
        if not product.is_active:
            return Response({"error": "Product is inactive."}, status=status.HTTP_400_BAD_REQUEST)

        item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity
        )
        return Response(OrderItemSerializer(item).data, status=status.HTTP_201_CREATED)
