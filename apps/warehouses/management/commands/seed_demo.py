import os
import shutil
from datetime import date
from decimal import Decimal

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.warehouses.models import Warehouse, Box
from apps.rentals.models import RentalOrder, DeliveryRequest
from apps.promotions.models import PromoCode
from apps.payments.models import Payment

User = get_user_model()

# Склады — точно по вёрстке boxes.html (город, адрес, t, потолок, база цены, картинка)
WAREHOUSES = [
    ("Москва", "ул. Рокотова, д. 15", "17 °С", 3.5, 3034, "image11.png"),
    ("Одинцово", "ул. Северная, д. 36", "18 °С", 3.5, 2264, "image9.png"),
    ("Пушкино", "ул. Строителей, д. 5", "20 °С", 5.5, 2154, "image15.png"),
    ("Люберцы", "ул. Советская, д. 88", "18 °С", 3.5, 1408, "image151.png"),
    ("Домодедово", "ул. Орджоникидзе, д. 29", "21 °С", 4.5, 2988, "image16.png"),
]

BOX_AREAS = [1, 2, 3, 4, 5, 6, 8, 10, 11]


class Command(BaseCommand):
    help = "Идемпотентное наполнение демо-данными (5 складов как в макете, боксы, кабинет Екатерины, промокод, платежи, фото)."

    def handle(self, *args, **options):
        # Идемпотентная очистка (каскад удаляет Box/Order/Payment/Delivery)
        Warehouse.objects.all().delete()
        PromoCode.objects.all().delete()
        User.objects.all().delete()

        media_wh = settings.MEDIA_ROOT / "warehouses"
        os.makedirs(media_wh, exist_ok=True)

        warehouses = {}
        for i, (city, address, temp, ceil, base, img) in enumerate(WAREHOUSES, start=1):
            src = settings.BASE_DIR / "layot" / "img" / img
            dst_name = f"wh_{i}.png"
            photo = ""
            if src.exists():
                shutil.copy(src, media_wh / dst_name)
                photo = f"warehouses/{dst_name}"

            wh = Warehouse.objects.create(
                city=city,
                address=address,
                temperature=temp,
                ceiling_height=ceil,
                description="Отапливаемое и сухое помещение индивидуального хранения SelfStorage.",
                contacts="8 (800) 000-00-00",
                photo=photo,
            )
            warehouses[city] = wh

            # Гибрид: ~12 боксов со случайно-детерминированными параметрами
            for j in range(1, 13):
                area = BOX_AREAS[(i + j) % len(BOX_AREAS)]
                width = round(area ** 0.5, 1)
                length = round(area / width, 1)
                height = 2.5
                price = base + (area - 1) * 150
                if j % 4 == 0:
                    status = "occupied"
                elif j % 5 == 0:
                    status = "reserved"
                else:
                    status = "free"
                Box.objects.create(
                    warehouse=wh,
                    number=f"{i}-{j}",
                    floor=(j % 3) + 1,
                    area=area,
                    length=length,
                    width=width,
                    height=height,
                    price_per_month=price,
                    status=status,
                )

        # Фиксированные боксы под личный кабинет (my-rent.html)
        odintsovo = warehouses["Одинцово"]
        lyubertsi = warehouses["Люберцы"]
        box_ekat1, _ = Box.objects.get_or_create(
            warehouse=odintsovo, number="2389-12",
            defaults=dict(floor=2, area=3, length=2, width=2, height=2.5, price_per_month=2561, status="occupied"),
        )
        box_ekat2, _ = Box.objects.get_or_create(
            warehouse=lyubertsi, number="2335-10",
            defaults=dict(floor=1, area=2, length=2, width=1, height=2.5, price_per_month=1408, status="occupied"),
        )

        # Пользователи: Екатерина (как в макете) + суперюзер для админки
        user = User.objects.create_user(
            email="ekatyusha89@yandex.ru",
            phone="+7-909-000-00-00",
            password="111111111",
            pd_consent_date=date.today(),
        )
        User.objects.create_superuser(email="admin@selfstorage.ru", password="admin12345")

        promo = PromoCode.objects.create(
            code="storage15",
            discount_percent=15,
            valid_from=date(2026, 1, 1),
            valid_to=date(2026, 12, 31),
        )

        # Две активные аренды Екатерины
        order1 = RentalOrder.objects.create(
            user=user, box=box_ekat1,
            start_date=date(2022, 3, 15), end_date=date(2022, 6, 28),
            items_text="Сезонные вещи: лыжи, сноуборд, коробки с книгами.",
            status="active", promo=promo,
            amount=box_ekat1.price_per_month * Decimal("0.85"),
            traffic_source="vk",
        )
        order2 = RentalOrder.objects.create(
            user=user, box=box_ekat2,
            start_date=date(2022, 3, 18), end_date=date(2022, 9, 21),
            items_text="Мебель и документы на хранение.",
            status="active", amount=box_ekat2.price_per_month,
            traffic_source="google",
        )

        Payment.objects.create(order=order1, yookassa_id=f"test_{order1.pk}", status="succeeded", amount=order1.amount)
        Payment.objects.create(order=order2, yookassa_id=f"test_{order2.pk}", status="succeeded", amount=order2.amount)

        DeliveryRequest.objects.create(
            order=order1,
            client_address="Одинцово, ул. Северная, д. 36",
            phone="+7-909-000-00-00",
            status="done",
        )

        self.stdout.write(self.style.SUCCESS("Демо-данные обновлены (idempotent, гибрид + фото)."))
