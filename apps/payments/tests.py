import json
import os
import shutil
import tempfile
from decimal import Decimal
from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings
from django.urls import reverse

from apps.payments.models import Payment
from apps.payments.views import _mark_paid
from apps.rentals.models import RentalOrder
from apps.rentals.services import qr_payload
from apps.users.models import User
from apps.warehouses.models import Box, Warehouse


@override_settings(
    YOOKASSA_SHOP_ID="shop-1",
    YOOKASSA_SECRET_KEY="secret-1",
    SITE_URL="https://selfstorage.kislyakov.pro",
)
class PaymentFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="pay@test.ru", password="pass1234", phone="+79990000000"
        )
        warehouse = Warehouse.objects.create(city="Москва", address="ул. Тест, 1")
        self.box = Box.objects.create(
            warehouse=warehouse,
            number=1256,
            area=3,
            price_per_month=Decimal("2000.00"),
            status="reserved",
        )
        self.order = RentalOrder.objects.create(
            user=self.user,
            box=self.box,
            start_date="2026-09-01",
            end_date="2027-03-01",
            status="awaiting_payment",
            amount=Decimal("2000.00"),
        )
        self.client.force_login(self.user)

    def test_create_payment_redirects_to_confirmation(self):
        with patch("apps.payments.views.YooPayment") as MockYoo:
            mock_pay = MagicMock()
            mock_pay.id = "yoo_123"
            mock_pay.confirmation.confirmation_url = "https://yookassa.ru/pay/yoo_123"
            MockYoo.create.return_value = mock_pay

            resp = self.client.get(reverse("payment_create", args=[self.order.id]))

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.url, "https://yookassa.ru/pay/yoo_123")
            payment = Payment.objects.get(order=self.order)
            self.assertEqual(payment.yookassa_id, "yoo_123")
            self.assertEqual(payment.status, "pending")

    def test_create_payment_requires_owner(self):
        other = User.objects.create_user(email="other@test.ru", password="x")
        self.client.force_login(other)
        resp = self.client.get(reverse("payment_create", args=[self.order.id]))
        self.assertEqual(resp.status_code, 302)

    def test_create_payment_disabled_without_credentials(self):
        with override_settings(YOOKASSA_SHOP_ID="", YOOKASSA_SECRET_KEY=""):
            resp = self.client.get(reverse("payment_create", args=[self.order.id]))
            self.assertEqual(resp.status_code, 400)
            data = json.loads(resp.content)
            self.assertEqual(data["status"], "error")

    @patch("apps.payments.views.send_notification")
    def test_webhook_marks_order_active_and_box_occupied(self, mock_mail):
        with patch("apps.payments.views.generate_qr"):
            self.user.first_name = "Мария"
            self.user.save()
            Payment.objects.create(
                order=self.order,
                yookassa_id="yoo_webhook_1",
                status="pending",
                amount=self.order.amount,
            )
            payload = {
                "event": "payment.succeeded",
                "object": {"id": "yoo_webhook_1", "status": "succeeded"},
            }
            resp = self.client.post(
                reverse("yookassa_webhook"),
                data=json.dumps(payload),
                content_type="application/json",
            )
            self.assertEqual(resp.status_code, 200)
        self.order.refresh_from_db()
        self.box.refresh_from_db()
        self.assertEqual(self.order.status, "active")
        self.assertEqual(self.box.status, "occupied")
        self.assertEqual(
            Payment.objects.get(yookassa_id="yoo_webhook_1").status, "succeeded"
        )
        mock_mail.assert_called_once()
        _, _, message = mock_mail.call_args[0]
        self.assertIn("Привет Мария", message)

    @patch("apps.payments.views.send_notification")
    def test_payment_success_updates_status(self, mock_mail):
        with patch("apps.payments.views.generate_qr"):
            payment = Payment.objects.create(
                order=self.order,
                yookassa_id="yoo_success_1",
                status="pending",
                amount=self.order.amount,
            )
            with patch("apps.payments.views.YooPayment") as MockYoo:
                mock_pay = MagicMock()
                mock_pay.status = "succeeded"
                MockYoo.find_one.return_value = mock_pay

                resp = self.client.get(reverse("payment_success", args=[self.order.id]))

                self.assertEqual(resp.status_code, 302)
        self.order.refresh_from_db()
        self.box.refresh_from_db()
        payment.refresh_from_db()
        self.assertEqual(self.order.status, "active")
        self.assertEqual(self.box.status, "occupied")
        self.assertEqual(payment.status, "succeeded")
        mock_mail.assert_called_once()

    @patch("apps.payments.views.send_notification")
    def test_mark_paid_generates_qr_code(self, mock_mail):
        tmp = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, tmp, True)
        payment = Payment.objects.create(
            order=self.order, status="pending", amount=self.order.amount
        )
        self.order.refresh_from_db()
        with override_settings(MEDIA_ROOT=tmp):
            _mark_paid(payment, self.order)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "active")
        self.assertTrue(self.order.qr_code)
        full = os.path.join(tmp, self.order.qr_code.name)
        self.assertTrue(os.path.exists(full))
        self.assertEqual(self.order.qr_code.name, f"qr/qr_{self.order.pk}.png".replace("/", os.sep))
        self.assertIn(f"qr/qr_{self.order.pk}.png", self.order.qr_code.url)
        self.assertIn(
            reverse("qr_access", args=[self.order.pk]), qr_payload(self.order)
        )

    @patch("apps.payments.views.send_notification")
    def test_mark_paid_tolerates_qr_failure(self, mock_mail):
        payment = Payment.objects.create(
            order=self.order, status="pending", amount=self.order.amount
        )
        self.order.refresh_from_db()
        with patch("apps.payments.views.generate_qr", side_effect=RuntimeError("boom")):
            _mark_paid(payment, self.order)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, "active")
