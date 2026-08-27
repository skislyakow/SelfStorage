from django.urls import path

from apps.rentals import views

urlpatterns = [
    path("wizard/", views.OrderWizard.as_view(), name="order_wizard"),
]
