from django.urls import path

from apps.payments import views

urlpatterns = [
    path(
        "orders/<int:order_id>/pay/",
        views.create_payment,
        name="payment_create",
    ),
    path(
        "orders/payment-success/<int:order_id>/",
        views.payment_success,
        name="payment_success",
    ),
    path("payments/webhook/", views.yookassa_webhook, name="yookassa_webhook"),
]
