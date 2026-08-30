import os
import qrcode
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from io import BytesIO

def generate_qr(order):
    data = f'Box{order.box.number}, Warehouse: {order.box.warehouse.id}, Order: {order.pk}'
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
    img_bytes = buffer.getvalue()

    filename = f"qr_{order.pk}.png"
    path = os.path.join('qr', filename)

    if default_storage.exists(path):
        default_storage.delete(path)

    default_storage.save(path, ContentFile(img_bytes))

    return default_storage.url(path)
