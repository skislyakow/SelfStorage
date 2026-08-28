from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from apps.rentals.models import RentalOrder
from apps.warehouses.models import Box, Warehouse

User = get_user_model()


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class SendNotificationsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="renter@example.com", password="pass12345"
        )
        warehouse = Warehouse.objects.create(city="Москва", address="Тверская 1")
        self.box = Box.objects.create(
            warehouse=warehouse, number="A1", area=2, price_per_month=1000
        )

    def test_reminder_sent_3_days_before_end(self):
        self.user.first_name = "Мария"
        self.user.save()
        RentalOrder.objects.create(
            user=self.user,
            box=self.box,
            start_date=timezone.now().date() - timedelta(days=30),
            end_date=timezone.now().date() + timedelta(days=3),
            status="active",
        )
        call_command("send_notifications")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Заканчивается срок аренды!")
        self.assertEqual(mail.outbox[0].to, ["renter@example.com"])
        self.assertIn("Привет Мария", mail.outbox[0].body)
        self.assertNotIn("Уважаемый", mail.outbox[0].body)

    def test_reminder_fallback_without_name(self):
        RentalOrder.objects.create(
            user=self.user,
            box=self.box,
            start_date=timezone.now().date() - timedelta(days=30),
            end_date=timezone.now().date() + timedelta(days=3),
            status="active",
        )
        call_command("send_notifications")
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Уважаемый клиент", mail.outbox[0].body)

    def test_no_reminder_when_far_away(self):
        RentalOrder.objects.create(
            user=self.user,
            box=self.box,
            start_date=timezone.now().date(),
            end_date=timezone.now().date() + timedelta(days=10),
            status="active",
        )
        call_command("send_notifications")
        self.assertEqual(len(mail.outbox), 0)

    def test_overdue_marked_and_notified(self):
        self.user.first_name = "Мария"
        self.user.save()
        order = RentalOrder.objects.create(
            user=self.user,
            box=self.box,
            start_date=timezone.now().date() - timedelta(days=60),
            end_date=timezone.now().date() - timedelta(days=30),
            status="active",
        )
        call_command("send_notifications")
        order.refresh_from_db()
        self.assertEqual(order.status, "overdue")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Срок аренды просрочен!")
        self.assertIn("Привет Мария", mail.outbox[0].body)
