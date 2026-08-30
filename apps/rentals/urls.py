from django.urls import path

from apps.rentals import views

urlpatterns = [
    path("wizard/", views.OrderWizard.as_view(), name="order_wizard"),
    path("my-rent/", views.MyRentView.as_view(), name="my_rent"),
    path("box-access/<int:pk>/", views.BoxAccessView.as_view(), name="qr_access"),
]
