from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("warehouses/", include("apps.warehouses.urls")),
    path("orders/", include("apps.rentals.urls")),
]
