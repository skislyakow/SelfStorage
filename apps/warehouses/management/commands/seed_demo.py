from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.warehouses.models import Warehouse, Box
from apps.rentals.models import RentalOrder, DeliveryRequest
from apps.promotions.models import PromoCode
from datetime import date, timedelta
from decimal import Decimal

User = get_user_model()


class Command(BaseCommand):
    help = "Идемпотентное наполнение демо-данными (склады, боксы, пользователь, заказ, промокод)."

    def handle(self, *args, **options):
        Warehouse.objects.all().delete()
        PromoCode.objects.all().delete()
        User.objects.all().delete()

        user = User.objects.create_user(
            email="demo@selfstorage.ru",
            phone="+79990000000",
            password="demo12345",
            pd_consent_date=date.today(),
        )

        promo = PromoCode.objects.create(
            code="storage15",
            discount_percent=15,
            valid_from=date(2021, 11, 1),
            valid_to=date(2022, 4, 30),
        )

        cities = [
            ("Москва", "ул. Ленина, 1", 6),
            ("Москва", "пр. Мира, 10", 5),
            ("Санкт-Петербург", "ул. Гагарина, 5", 4),
        ]
        for i, (city, address, count) in enumerate(cities, start=1):
            wh = Warehouse.objects.create(
                city=city,
                address=address,
                temperature="от +5 до +15",
                ceiling_height=3.0,
                description="Склад SelfStorage для физических лиц.",
                contacts="+79990000000",
            )
            for j in range(1, count + 1):
                Box.objects.create(
                    warehouse=wh,
                    number=f"{i}-{j}",
                    floor=(j % 3) + 1,
                    area=2 + j,
                    length=1.5,
                    width=1.5,
                    height=2.5,
                    price_per_month=2000 + j * 100,
                    status="free" if j % 2 else "occupied",
                )

        box = Box.objects.filter(status="free").first()
        if box:
            order = RentalOrder.objects.create(
                user=user,
                box=box,
                start_date=date.today(),
                end_date=date.today() + timedelta(days=30),
                items_text="Сноуборд, лыжи",
                status="active",
                promo=promo,
                amount=box.price_per_month * Decimal("0.85"),
                traffic_source="google",
            )
            DeliveryRequest.objects.create(
                order=order,
                client_address="Москва, ул. Демо, 1",
                phone="+79990000000",
                status="new",
            )

        self.stdout.write(self.style.SUCCESS("Демо-данные обновлены (idempotent)."))
