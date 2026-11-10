from django.urls import path
from inventory import views

app_name = "inventory"

urlpatterns = [
    # Products
    path("products/", views.product_list, name="product_list"),
    path("products/create/", views.product_create, name="product_create"),
    path("products/<int:pk>/edit/", views.product_update, name="product_update"),
    path("products/<int:pk>/toggle/", views.product_toggle_status, name="product_toggle"),

    # Shipping Boxes
    path("boxes/", views.box_list, name="box_list"),
    path("boxes/create/", views.box_create, name="box_create"),
    path("boxes/<int:pk>/edit/", views.box_update, name="box_update"),
    path("boxes/<int:pk>/toggle/", views.box_toggle_status, name="box_toggle"),
]
