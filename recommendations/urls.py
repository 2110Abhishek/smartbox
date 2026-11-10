from django.urls import path
from recommendations import views

app_name = "recommendations"

urlpatterns = [
    # Web views
    path("history/", views.recommendation_history, name="history"),
    path("orders/<int:order_id>/generate/", views.generate_recommendation, name="generate"),
    path("<int:pk>/", views.recommendation_detail, name="recommendation_detail"),
    path("<int:pk>/confirm/", views.confirm_box_selection, name="confirm_box"),
    path("<int:pk>/packed/", views.mark_order_packed, name="mark_packed"),
    path("<int:pk>/complete/", views.mark_order_completed, name="mark_complete"),

    # REST API endpoints (/api/v1/...)
    path("api/v1/orders/<int:pk>/recommend/", views.api_recommend_order, name="api_recommend_order"),
    path("api/v1/orders/<int:pk>/recommendations/", views.api_order_recommendations, name="api_order_recommendations"),
    path("api/v1/recommendations/<int:pk>/", views.api_recommendation_detail, name="api_recommendation_detail"),
    path("api/v1/recommendations/<int:pk>/confirm/", views.api_confirm_recommendation, name="api_confirm_recommendation"),
    path("api/v1/recommendations/<int:pk>/complete/", views.api_complete_packaging, name="api_complete_packaging"),
]
