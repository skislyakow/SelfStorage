from datetime import timedelta

from django.core import mail
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.notifications.models import Notification
from apps.notifications.services import notify
from apps.rentals.models import RentalOrder
from apps.users.models import User
from apps.warehouses.models import Box, Warehouse


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
            end_date=timezone.now().date() - timedelta(days=1),
            status="active",
        )
        call_command("send_notifications")
        order.refresh_from_db()
        self.assertEqual(order.status, "overdue")
        self.assertEqual(order.last_overdue_notified, timezone.now().date())
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Срок аренды просрочен!")
        self.assertIn("Привет Мария", mail.outbox[0].body)
        self.assertIn("6 месяцев", mail.outbox[0].body)
        self.assertIn("повышенному тарифу", mail.outbox[0].body)
        self.assertIn("1 день", mail.outbox[0].body)

    def test_overdue_monthly_sends(self):
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
        self.assertEqual(order.last_overdue_notified, timezone.now().date())
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("30 дней", mail.outbox[0].body)

    def test_overdue_already_overdue_day1_emailed(self):
        self.user.first_name = "Мария"
        self.user.save()
        order = RentalOrder.objects.create(
            user=self.user,
            box=self.box,
            start_date=timezone.now().date() - timedelta(days=60),
            end_date=timezone.now().date() - timedelta(days=1),
            status="overdue",
        )
        call_command("send_notifications")
        order.refresh_from_db()
        self.assertEqual(order.last_overdue_notified, timezone.now().date())
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Привет Мария", mail.outbox[0].body)

    def test_overdue_not_resends(self):
        RentalOrder.objects.create(
            user=self.user,
            box=self.box,
            start_date=timezone.now().date() - timedelta(days=60),
            end_date=timezone.now().date() - timedelta(days=1),
            status="active",
        )
        call_command("send_notifications")
        self.assertEqual(len(mail.outbox), 1)
        call_command("send_notifications")
        self.assertEqual(len(mail.outbox), 1)

    def test_overdue_resends_after_30_days(self):
        overdue_date = timezone.now().date() - timedelta(days=31)
        order = RentalOrder.objects.create(
            user=self.user,
            box=self.box,
            start_date=timezone.now().date() - timedelta(days=60),
            end_date=overdue_date,
            status="overdue",
            last_overdue_notified=overdue_date,
        )
        call_command("send_notifications")
        order.refresh_from_db()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(order.last_overdue_notified, timezone.now().date())


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class InAppNotificationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="bell@example.com", password="pass12345"
        )
        self.other = User.objects.create_user(
            email="other@example.com", password="pass12345"
        )
        warehouse = Warehouse.objects.create(city="Москва", address="Тверская 1")
        self.box = Box.objects.create(
            warehouse=warehouse, number="A1", area=2, price_per_month=1000
        )

    def test_notify_creates_unread_notification(self):
        note = notify(self.user, "Оплата получена", url="/orders/my-rent/")
        assert note is not None
        self.assertFalse(note.is_read)
        self.assertEqual(self.user.notifications.count(), 1)

    def test_notify_without_user_is_noop(self):
        self.assertIsNone(notify(None, "Никому"))
        self.assertEqual(Notification.objects.count(), 0)

    def test_anonymous_has_no_bell_counter(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.context["unread_notifications"], 0)
        self.assertNotContains(response, "notificationsBell")

    def test_bell_counter_counts_only_own_unread(self):
        notify(self.user, "Моё непрочитанное")
        read_note = notify(self.user, "Моё прочитанное", url="/x/")
        assert read_note is not None
        read_note.is_read = True
        read_note.save()
        notify(self.other, "Чужое непрочитанное")

        self.client.force_login(self.user)
        response = self.client.get(reverse("home"))
        self.assertEqual(response.context["unread_notifications"], 1)
        self.assertEqual(len(response.context["recent_notifications"]), 2)
        self.assertContains(response, "notificationsBell")

    def test_list_requires_login(self):
        response = self.client.get(reverse("notifications:list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.headers["Location"])

    def test_list_shows_only_own_notifications(self):
        notify(self.user, "Моё уведомление")
        notify(self.other, "Чужое уведомление")

        self.client.force_login(self.user)
        response = self.client.get(reverse("notifications:list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Моё уведомление")
        self.assertNotContains(response, "Чужое уведомление")

    def test_mark_all_read_marks_own_only(self):
        notify(self.user, "Моё")
        notify(self.other, "Чужое")

        self.client.force_login(self.user)
        response = self.client.post(reverse("notifications:read_all"))
        self.assertRedirects(response, reverse("notifications:list"))
        self.assertFalse(self.user.notifications.filter(is_read=False).exists())
        self.assertTrue(self.other.notifications.filter(is_read=False).exists())

    def test_mark_all_read_requires_post(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("notifications:read_all"))
        self.assertEqual(response.status_code, 405)

    def test_reminder_creates_in_app_notification(self):
        RentalOrder.objects.create(
            user=self.user,
            box=self.box,
            start_date=timezone.now().date() - timedelta(days=30),
            end_date=timezone.now().date() + timedelta(days=3),
            status="active",
        )
        call_command("send_notifications")
        note = self.user.notifications.get()
        self.assertIn(f"бокса №{self.box.number}", note.text)
        self.assertIn("3 дня", note.text)
        self.assertEqual(note.url, reverse("my_rent"))

    def test_overdue_creates_in_app_notification(self):
        RentalOrder.objects.create(
            user=self.user,
            box=self.box,
            start_date=timezone.now().date() - timedelta(days=60),
            end_date=timezone.now().date() - timedelta(days=1),
            status="active",
        )
        call_command("send_notifications")
        note = self.user.notifications.get()
        self.assertIn("просрочен", note.text)
