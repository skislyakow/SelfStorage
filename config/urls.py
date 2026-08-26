from django.contrib import admin
from django.urls import path
from config import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.HomeView.as_view(), name="home"),
    path("faq/", views.FaqView.as_view(), name="faq"),
    path("storage-rules/", views.StorageRulesView.as_view(), name="storage_rules"),
]
