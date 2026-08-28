from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from config import views
from config.admin_dashboard import owner_dashboard

urlpatterns = [
    path("admin/owner-dashboard/", owner_dashboard, name="owner-dashboard"),
    path("admin/", admin.site.urls),
    path("", views.HomeView.as_view(), name="home"),
    path("faq/", views.FaqView.as_view(), name="faq"),
    path("storage-rules/", views.StorageRulesView.as_view(), name="storage_rules"),
    path("warehouses/", include("apps.warehouses.urls")),
    path("orders/", include("apps.rentals.urls")),
    path("accounts/", include("apps.users.urls")),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
