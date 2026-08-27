import re

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from apps.rentals.models import DeliveryRequest, RentalOrder
from apps.warehouses.models import Box, Warehouse

User = get_user_model()


class OrderWizardTests(TestCase):
    def setUp(self):
        wh = Warehouse.objects.create(city="Тест", address="ул. Тест, 1")
        self.box = Box.objects.create(
            warehouse=wh, number="1", area=5, price_per_month=3000, status="free"
        )
        self.user = User.objects.create_user(email="wizard@test.ru", password="pass1234")
        self.client = Client(SERVER_NAME="localhost")

    def _management(self, html):
        m = re.search(
            r'name="order_wizard-current_step" value="([^"]*)"', html
        )
        return {"order_wizard-current_step": m.group(1) if m else ""}

    def _post_step(self, data, prev_response):
        fields = self._management(prev_response.content.decode())
        fields.update(data)
        return self.client.post(reverse("order_wizard"), fields)

    def test_wizard_creates_order_and_delivery(self):
        self.client.login(email="wizard@test.ru", password="pass1234")
        r = self.client.get(reverse("order_wizard"))
        r = self._post_step(
            {"0-box": str(self.box.pk), "0-rental_months": "3"}, r
        )
        r = self._post_step(
            {
                "1-delivery_type": "delivery",
                "1-address": "ул. Тест",
                "1-phone": "79990000000",
            },
            r,
        )
        r = self._post_step(
            {
                "2-first_name": "Имя",
                "2-phone": "79990000000",
                "2-pd_consent": "on",
            },
            r,
        )
        r = self._post_step({}, r)

        self.assertEqual(RentalOrder.objects.count(), 1)
        order = RentalOrder.objects.first()
        self.assertEqual(order.amount, self.box.price_per_month * 3)
        self.assertEqual(order.status, "awaiting_payment")
        self.assertEqual(DeliveryRequest.objects.count(), 1)
        self.assertEqual(self.user.orders.count(), 1)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Имя")
        self.assertTrue(self.user.pd_consent_date)

    def test_wizard_self_pickup_no_delivery(self):
        self.client.login(email="wizard@test.ru", password="pass1234")
        r = self.client.get(reverse("order_wizard"))
        r = self._post_step(
            {"0-box": str(self.box.pk), "0-rental_months": "1"}, r
        )
        r = self._post_step(
            {"1-delivery_type": "self", "1-phone": "79990000000"}, r
        )
        r = self._post_step(
            {
                "2-first_name": "Имя",
                "2-phone": "79990000000",
                "2-pd_consent": "on",
            },
            r,
        )
        r = self._post_step({}, r)

        self.assertEqual(RentalOrder.objects.count(), 1)
        self.assertEqual(DeliveryRequest.objects.count(), 0)
