from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from rest_framework import viewsets, permissions
from rest_framework import serializers

from inventory.models import Product, ShippingBox
from inventory.forms import ProductForm, ShippingBoxForm


# ---------------------------------
# Web Views: Products
# ---------------------------------

@login_required
def product_list(request):
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "")

    products = Product.objects.all()
    if query:
        products = products.filter(Q(sku__icontains=query) | Q(name__icontains=query))
    if status_filter == "active":
        products = products.filter(is_active=True)
    elif status_filter == "inactive":
        products = products.filter(is_active=False)

    return render(request, "inventory/product_list.html", {
        "products": products,
        "query": query,
        "status_filter": status_filter,
    })


@login_required
def product_create(request):
    if request.method == "POST":
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save()
            messages.success(request, f"Product {product.sku} created successfully.")
            return redirect("inventory:product_list")
    else:
        form = ProductForm()
    return render(request, "inventory/product_form.html", {"form": form, "title": "Add New Product"})


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == "POST":
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Product {product.sku} updated successfully.")
            return redirect("inventory:product_list")
    else:
        form = ProductForm(instance=product)
    return render(request, "inventory/product_form.html", {
        "form": form,
        "product": product,
        "title": f"Edit Product: {product.sku}"
    })


@login_required
def product_toggle_status(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.is_active = not product.is_active
    product.save()
    status_str = "activated" if product.is_active else "deactivated"
    messages.info(request, f"Product {product.sku} {status_str}.")
    return redirect("inventory:product_list")


# ---------------------------------
# Web Views: Shipping Boxes
# ---------------------------------

@login_required
def box_list(request):
    query = request.GET.get("q", "").strip()
    status_filter = request.GET.get("status", "")

    boxes = ShippingBox.objects.all()
    if query:
        boxes = boxes.filter(Q(code__icontains=query) | Q(name__icontains=query))
    if status_filter == "active":
        boxes = boxes.filter(is_active=True)
    elif status_filter == "inactive":
        boxes = boxes.filter(is_active=False)

    return render(request, "inventory/box_list.html", {
        "boxes": boxes,
        "query": query,
        "status_filter": status_filter,
    })


@login_required
def box_create(request):
    if request.method == "POST":
        form = ShippingBoxForm(request.POST)
        if form.is_valid():
            box = form.save()
            messages.success(request, f"Shipping box {box.code} created successfully.")
            return redirect("inventory:box_list")
    else:
        form = ShippingBoxForm()
    return render(request, "inventory/box_form.html", {"form": form, "title": "Add New Shipping Box"})


@login_required
def box_update(request, pk):
    box = get_object_or_404(ShippingBox, pk=pk)
    if request.method == "POST":
        form = ShippingBoxForm(request.POST, instance=box)
        if form.is_valid():
            form.save()
            messages.success(request, f"Shipping box {box.code} updated successfully.")
            return redirect("inventory:box_list")
    else:
        form = ShippingBoxForm(instance=box)
    return render(request, "inventory/box_form.html", {
        "form": form,
        "box": box,
        "title": f"Edit Shipping Box: {box.code}"
    })


@login_required
def box_toggle_status(request, pk):
    box = get_object_or_404(ShippingBox, pk=pk)
    box.is_active = not box.is_active
    box.save()
    status_str = "activated" if box.is_active else "deactivated"
    messages.info(request, f"Shipping box {box.code} {status_str}.")
    return redirect("inventory:box_list")


# ---------------------------------
# REST API Serializers & ViewSets
# ---------------------------------

class ProductSerializer(serializers.ModelSerializer):
    volume = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Product
        fields = "__all__"


class ShippingBoxSerializer(serializers.ModelSerializer):
    volume = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = ShippingBox
        fields = "__all__"


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ShippingBoxViewSet(viewsets.ModelViewSet):
    queryset = ShippingBox.objects.all()
    serializer_class = ShippingBoxSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
