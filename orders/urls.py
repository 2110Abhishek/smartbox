from django.urls import path
from orders import views

app_name = "orders"

urlpatterns = [
    path("", views.order_list, name="order_list"),
    path("pending/", views.pending_orders, name="pending_orders"),
    path("create/", views.order_create, name="order_create"),
    path("<int:pk>/", views.order_detail, name="order_detail"),
    path("<int:pk>/add-item/", views.order_add_item, name="order_add_item"),
    path("<int:pk>/cancel/", views.order_cancel, name="order_cancel"),
]

