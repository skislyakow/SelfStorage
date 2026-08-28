import re

from django.test import TestCase, Client
from django.urls import reverse

from apps.rentals.models import DeliveryRequest, RentalOrder
from apps.warehouses.models import Box, Warehouse
from apps.users.models import User


class OrderWizardTests(TestCase):
    def setUp(self):
        wh = Warehouse.objects.create(city="Тест", address="ул. Тест, 1")
        self.box = Box.objects.create(
            warehouse=wh,
            number="1",
            area=5,
            price_per_month=3000,
            status="free",
        )
        self.user = User(email="wizard@test.ru")
        self.user.set_password("pass1234")
        self.user.save()
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
            },
            r,
        )
        r = self._post_step(
            {
                "2-first_name": "Имя",
                "2-phone": "79990000000",
                
            },
            r,
        )


        self.assertEqual(RentalOrder.objects.count(), 1)
        order = RentalOrder.objects.get()
        self.assertEqual(order.amount, self.box.price_per_month * 3)
        self.assertEqual(order.status, "awaiting_payment")
        self.assertEqual(DeliveryRequest.objects.count(), 1)
        self.assertEqual(RentalOrder.objects.filter(user=self.user).count(), 1)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Имя")

    def test_wizard_self_pickup_no_delivery(self):
        self.client.login(email="wizard@test.ru", password="pass1234")
        r = self.client.get(reverse("order_wizard"))
        r = self._post_step(
            {"0-box": str(self.box.pk), "0-rental_months": "1"}, r
        )
        r = self._post_step({"1-delivery_type": "self"}, r)
        r = self._post_step(
            {
                "2-first_name": "Имя",
                "2-phone": "79990000000",
                
            },
            r,
        )


        self.assertEqual(RentalOrder.objects.count(), 1)
        self.assertEqual(DeliveryRequest.objects.count(), 0)

    def test_wizard_prefills_box_from_query(self):
        self.client.login(email="wizard@test.ru", password="pass1234")
        r = self.client.get(reverse("order_wizard") + f"?box={self.box.pk}")
        content = r.content.decode()
        self.assertIn(f'value="{self.box.pk}"', content)
        self.assertIn("selected", content)

    def test_wizard_completes_with_confirmation_and_reserves(self):
        self.client.login(email="wizard@test.ru", password="pass1234")
        r = self.client.get(reverse("order_wizard") + f"?box={self.box.pk}")
        r = self._post_step(
            {"0-box": str(self.box.pk), "0-rental_months": "3"}, r
        )
        r = self._post_step(
            {"1-delivery_type": "delivery", "1-address": "ул. Тест"}, r
        )
        r = self._post_step(
            {
                "2-first_name": "Имя",
                "2-phone": "79990000000",
                
            },
            r,
        )


        self.assertEqual(r.status_code, 200)
        content = r.content.decode().lower()
        self.assertIn("забронирован", content)
        self.assertIn("оплат", content)
        order = RentalOrder.objects.get()
        self.assertEqual(order.status, "awaiting_payment")
        self.box.refresh_from_db()
        self.assertEqual(self.box.status, "reserved")

    def test_contacts_step_prefills_from_user(self):
        self.user.first_name = "Пётр"
        self.user.phone = "79991112233"
        self.user.save()
        self.client.login(email="wizard@test.ru", password="pass1234")
        r = self.client.get(reverse("order_wizard"))
        r = self._post_step(
            {"0-box": str(self.box.pk), "0-rental_months": "1"}, r
        )
        r = self._post_step({"1-delivery_type": "self"}, r)
        content = r.content.decode()
        self.assertIn('value="Пётр"', content)
        self.assertIn('value="79991112233"', content)
        self.assertNotIn("pd_consent", content)
