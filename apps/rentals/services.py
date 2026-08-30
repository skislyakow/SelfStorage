from io import BytesIO
import os

import qrcode
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.urls import reverse


def qr_payload(order):
    """Данные, которые кодирует QR: ссылка на страницу доступа к боксу."""
    url = settings.SITE_URL.rstrip("/") + reverse("qr_access", args=[order.pk])
    return url


def generate_qr(order):
    """Сгенерировать QR-код доступа к боксу заказа, сохранить в media/qr/ и вернуть FieldFile."""
    data = qr_payload(order)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")

    filename = f"qr_{order.pk}.png"
    path = os.path.join("qr", filename)
    if default_storage.exists(path):
        default_storage.delete(path)
    default_storage.save(path, ContentFile(buffer.getvalue()))

    order.qr_code = path
    order.save(update_fields=["qr_code"])
    return order.qr_code
