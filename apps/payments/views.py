import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt

from yookassa import Configuration, Payment as YooPayment

from apps.notifications.email import greeting, send_notification
from apps.payments.models import Payment
from apps.rentals.models import RentalOrder
from apps.rentals.services import generate_qr
from apps.warehouses.models import Box


logger = logging.getLogger(__name__)


def _configure_yookassa():
    if not settings.YOOKASSA_SHOP_ID or not settings.YOOKASSA_SECRET_KEY:
        return False
    Configuration.account_id = settings.YOOKASSA_SHOP_ID
    Configuration.secret_key = settings.YOOKASSA_SECRET_KEY
    return True


@login_required
def create_payment(request, order_id):
    """Создать платёж в Юмани и перенаправить пользователя на оплату."""
    order = get_object_or_404(RentalOrder, pk=order_id)
    if order.user != request.user:
        return redirect("warehouse_list")
    if order.status != "awaiting_payment":
        return redirect("warehouse_list")

    if not _configure_yookassa():
        return JsonResponse(
            {
                "status": "error",
                "message": "Оплата временно недоступна: не настроен приём платежей",
            },
            status=400,
        )

    payment, _ = Payment.objects.get_or_create(
        order=order, defaults={"amount": order.amount}
    )

    try:
        yoo_payment = YooPayment.create(
            {
                "amount": {
                    "value": f"{float(order.amount):.2f}",
                    "currency": "RUB",
                },
                "capture": True,
                "confirmation": {
                    "type": "redirect",
                    "return_url": f"{settings.SITE_URL}/orders/payment-success/{order.id}/",
                },
                "description": f"Аренда бокса №{order.box.number} — заказ #{order.id}",
                "metadata": {
                    "order_id": order.id,
                    "user_email": order.user.email,
                },
            }
        )
    except Exception as exc:
        return JsonResponse(
            {"status": "error", "message": f"Ошибка при создании платежа: {exc}"},
            status=502,
        )

    payment.yookassa_id = yoo_payment.id
    payment.status = "pending"
    if payment.amount is None:
        payment.amount = order.amount
    payment.save()

    return redirect(yoo_payment.confirmation.confirmation_url)


@login_required
def payment_success(request, order_id):
    """Возврат из Юмани — проверяем статус и завершаем заказ."""
    order = get_object_or_404(RentalOrder, pk=order_id)
    if order.user != request.user:
        return redirect("warehouse_list")

    payment = getattr(order, "payment", None)
    if payment and payment.yookassa_id and _configure_yookassa():
        try:
            yoo_payment = YooPayment.find_one(payment.yookassa_id)
            if yoo_payment.status == "succeeded":
                _mark_paid(payment, order)
        except Exception:
            pass

    if order.status == "active":
        return redirect("warehouse_list")
    return redirect("warehouse_list")


def _mark_paid(payment, order):
    """Отметить платёж и заказ оплаченными, занять бокс, уведомить клиента."""
    if payment.status != "succeeded":
        payment.status = "succeeded"
        payment.save()
    if order.status != "active":
        order.status = "active"
        order.save()
        try:
            generate_qr(order)
        except Exception:
            logger.exception("Не удалось сгенерировать QR-код для заказа %s", order.id)
        box = order.box
        if box.status != "occupied":
            box.status = "occupied"
            box.save()
        send_notification(
            order.user,
            "Оплата получена — SelfStorage",
            (
                f"{greeting(order.user)} Спасибо! Оплата заказа #{order.id} "
                f"(бокс №{order.box.number}, {order.box.area} м²) получена.\n"
                f"Сумма: {order.amount} ₽.\n"
                f"Забронированный срок: с {order.start_date:%d.%m.%Y} по {order.end_date:%d.%m.%Y}."
            ),
        )


@csrf_exempt
def yookassa_webhook(request):
    """Уведомление от Юмани о смене статуса платежа."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            payment_id = data.get("object", {}).get("id")
            status = data.get("object", {}).get("status")
            if status == "succeeded" and payment_id:
                payment = Payment.objects.filter(yookassa_id=payment_id).first()
                if payment is not None:
                    order = payment.order
                    _mark_paid(payment, order)
                else:
                    print(f"Платёж Юмани {payment_id} не найден в SelfStorage")
            return JsonResponse({"status": "ok"})
        except Exception as e:
            print(f"Ошибка webhook Юмани: {e}")
            return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"error": "POST required"}, status=400)
