import re
from datetime import timedelta
from decimal import Decimal

from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone

from apps.promotions.models import PromoCode
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

    def test_wizard_applies_promo(self):
        promo = PromoCode.objects.create(
            code="TEST20",
            discount_percent=20,
            valid_from=timezone.localdate(),
            valid_to=timezone.localdate() + timedelta(days=90),
        )
        self.client.login(email="wizard@test.ru", password="pass1234")
        r = self.client.get(reverse("order_wizard") + f"?box={self.box.pk}")
        r = self._post_step(
            {"0-box": str(self.box.pk), "0-rental_months": "3"}, r
        )
        r = self._post_step({"1-delivery_type": "self"}, r)
        r = self._post_step(
            {
                "2-first_name": "Имя",
                "2-phone": "79990000000",
                "2-promo_code": "TEST20",
            },
            r,
        )
        self.assertEqual(r.status_code, 200)
        order = RentalOrder.objects.get()
        self.assertEqual(order.promo, promo)
        self.assertEqual(order.amount, Decimal("7200"))
        content = r.content.decode().lower()
        self.assertIn("test20", content)
        self.assertIn("7200", content)

    def test_wizard_invalid_promo_blocks(self):
        self.client.login(email="wizard@test.ru", password="pass1234")
        r = self.client.get(reverse("order_wizard") + f"?box={self.box.pk}")
        r = self._post_step(
            {"0-box": str(self.box.pk), "0-rental_months": "1"}, r
        )
        r = self._post_step({"1-delivery_type": "self"}, r)
        r = self._post_step(
            {
                "2-first_name": "Имя",
                "2-phone": "79990000000",
                "2-promo_code": "NOPE",
            },
            r,
        )
        self.assertEqual(RentalOrder.objects.count(), 0)
        self.assertIn("Промокод истёк или неверен", r.content.decode())

    def test_wizard_captures_traffic_source(self):
        self.client.login(email="wizard@test.ru", password="pass1234")
        r = self.client.get(reverse("order_wizard") + "?utm_source=facebook")
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
        order = RentalOrder.objects.get()
        self.assertEqual(order.traffic_source, "facebook")

    def test_wizard_without_traffic_source_is_empty(self):
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
        order = RentalOrder.objects.get()
        self.assertEqual(order.traffic_source, "")


class TrafficSourceMiddlewareTests(TestCase):
    def test_middleware_sets_session_from_utm_source(self):
        c = Client()
        c.get(reverse("order_wizard") + "?utm_source=vk")
        self.assertEqual(c.session.get("traffic_source"), "vk")

    def test_middleware_sets_session_from_src_alias(self):
        c = Client()
        c.get(reverse("order_wizard") + "?src=instagram")
        self.assertEqual(c.session.get("traffic_source"), "instagram")

    def test_middleware_ignores_without_param(self):
        c = Client()
        c.get(reverse("order_wizard"))
        self.assertNotIn("traffic_source", c.session)


class BoxAccessTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@test.ru", password="pass1234"
        )
        self.staff = User.objects.create_user(
            email="staff@test.ru", password="pass1234", is_staff=True
        )
        self.other = User.objects.create_user(
            email="other@test.ru", password="pass1234"
        )
        self.wh = Warehouse.objects.create(city="Москва", address="ул. Тест, 1")
        self.box = Box.objects.create(
            warehouse=self.wh,
            number="5",
            area=5,
            price_per_month=3000,
            status="occupied",
        )
        self.order = RentalOrder.objects.create(
            user=self.owner,
            box=self.box,
            start_date="2026-01-01",
            end_date="2027-01-01",
            status="active",
            amount=3000,
        )

    def test_access_page_requires_login(self):
        resp = self.client.get(reverse("qr_access", args=[self.order.pk]))
        self.assertEqual(resp.status_code, 302)

    def test_access_page_for_owner(self):
        self.client.force_login(self.owner)
        resp = self.client.get(reverse("qr_access", args=[self.order.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, f"Бокс №{self.box.number}")

    def test_access_page_for_staff(self):
        self.client.force_login(self.staff)
        resp = self.client.get(reverse("qr_access", args=[self.order.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "QR-пропуск")

    def test_access_page_forbidden_for_other(self):
        self.client.force_login(self.other)
        resp = self.client.get(reverse("qr_access", args=[self.order.pk]))
        self.assertEqual(resp.status_code, 404)

    def test_my_rent_shows_qr_when_present(self):
        self.order.qr_code = "qr/qr_x.png"
        self.order.access_status = "open"
        self.order.save()
        self.client.force_login(self.owner)
        resp = self.client.get(reverse("my_rent"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Закрыть бокс")
        self.assertContains(resp, "/media/qr/qr_x.png")

    def test_my_rent_hides_qr_when_absent(self):
        self.client.force_login(self.owner)
        resp = self.client.get(reverse("my_rent"))
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, "/media/qr/")

    def test_box_open_requires_login(self):
        resp = self.client.post(reverse("box_open", args=[self.order.pk]))
        self.assertEqual(resp.status_code, 302)

    def test_box_open_for_owner_sets_open(self):
        self.client.force_login(self.owner)
        resp = self.client.post(reverse("box_open", args=[self.order.pk]))
        self.assertEqual(resp.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.access_status, "open")

    def test_box_close_for_owner_sets_closed(self):
        self.order.access_status = "open"
        self.order.save()
        self.client.force_login(self.owner)
        resp = self.client.post(reverse("box_close", args=[self.order.pk]))
        self.assertEqual(resp.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.access_status, "closed")

    def test_box_open_forbidden_for_other(self):
        self.client.force_login(self.other)
        resp = self.client.post(reverse("box_open", args=[self.order.pk]))
        self.assertEqual(resp.status_code, 404)
        self.order.refresh_from_db()
        self.assertEqual(self.order.access_status, "closed")

    def test_box_open_blocked_when_not_active(self):
        self.order.status = "finished"
        self.order.save()
        self.client.force_login(self.owner)
        resp = self.client.post(reverse("box_open", args=[self.order.pk]))
        self.assertEqual(resp.status_code, 302)
        self.order.refresh_from_db()
        self.assertEqual(self.order.access_status, "closed")

    def test_my_rent_shows_close_when_open(self):
        self.order.access_status = "open"
        self.order.save()
        self.client.force_login(self.owner)
        resp = self.client.get(reverse("my_rent"))
        self.assertContains(resp, "Закрыть бокс")

    def test_my_rent_hides_open_when_not_active(self):
        self.order.status = "overdue"
        self.order.save()
        self.client.force_login(self.owner)
        resp = self.client.get(reverse("my_rent"))
        self.assertNotContains(resp, "Открыть бокс")
