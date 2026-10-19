import os
from calendar import monthrange
from datetime import date
from decimal import Decimal
from io import BytesIO

import qrcode
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.urls import reverse
from qrcode import constants

from apps.promotions.models import PromoCode
from apps.rentals.models import RentalOrder
from apps.warehouses.models import Box


def qr_payload(order):
    """Данные, которые кодирует QR: ссылка на страницу доступа к боксу."""
    url = settings.SITE_URL.rstrip("/") + reverse("qr_access", args=[order.pk])
    return url


def generate_qr(order):
    """Сгенерировать QR-код доступа, сохранить файл в media/qr/ и вернуть FieldFile."""
    data = qr_payload(order)
    qr = qrcode.QRCode(
        version=1,
        error_correction=constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    # qrcode без py.typed: BaseImage.save объявлен как save(stream, kind=None),
    # а у PIL-реализации есть аргумент format — ложное срабатывание pyright.
    img.save(buffer, format="PNG")  # type: ignore

    filename = f"qr_{order.pk}.png"
    path = os.path.join("qr", filename)
    if default_storage.exists(path):
        default_storage.delete(path)
    default_storage.save(path, ContentFile(buffer.getvalue()))

    order.qr_code = path
    order.save(update_fields=["qr_code"])
    return order.qr_code


def add_months(start, months):
    """Дата начала плюс N месяцев с учётом разной длины месяцев."""
    total = start.month - 1 + months
    year = start.year + total // 12
    month = total % 12 + 1
    return date(year, month, min(start.day, monthrange(year, month)[1]))


def calculate_amount(box: Box, rental_months, start_date, promo: PromoCode | None):
    """Сумма заказа: по месяцам раскладывает скидку промокода по периодам её
    действия (месяц со скидкой, если он пересекается с окном промо)."""
    full_price = box.price_per_month
    if promo is None:
        return {
            "total": full_price * rental_months,
            "discounted_months": 0,
            "full_months": rental_months,
            "discounted_month_price": full_price,
            "full_month_price": full_price,
        }
    discount = promo.discount_percent / Decimal("100")
    discounted_price = (full_price * (Decimal("1") - discount)).quantize(
        Decimal("0.01")
    )
    discounted_months = 0
    full_months = 0
    total = Decimal("0")
    for i in range(rental_months):
        m_start = add_months(start_date, i)
        m_end = add_months(start_date, i + 1)
        if m_start <= promo.valid_to and m_end > promo.valid_from:
            total += discounted_price
            discounted_months += 1
        else:
            total += full_price
            full_months += 1
    return {
        "total": total,
        "discounted_months": discounted_months,
        "full_months": full_months,
        "discounted_month_price": discounted_price,
        "full_month_price": full_price,
    }


def can_open_box(order: RentalOrder) -> bool:
    """Правило доступа: бокс открывается только при активной аренде."""
    return order.status == "active"


def open_box(order: RentalOrder) -> bool:
    """Открыть бокс по QR. True — если статус изменился (открыл сейчас)."""
    if not can_open_box(order) or order.access_status == "open":
        return False
    order.access_status = "open"
    order.save(update_fields=["access_status"])
    return True


def close_box(order: RentalOrder) -> None:
    """Закрыть бокс: вправе любой, кому выдан QR-доступ."""
    order.access_status = "closed"
    order.save(update_fields=["access_status"])
