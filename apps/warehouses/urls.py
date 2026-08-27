from django.urls import path
from django.urls import include

from apps.warehouses import views

urlpatterns = [
    path("", views.warehouse_list, name="warehouse_list"),
    path("<int:pk>/", views.warehouse_detail, name="warehouse_detail"),
    path("boxes/", include("apps.warehouses.urls")),
]
