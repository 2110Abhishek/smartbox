from django.urls import path
from dashboard import views

app_name = "dashboard"

urlpatterns = [
    path("", views.dashboard_index, name="index"),
    path("analytics/", views.analytics_view, name="analytics"),
]

