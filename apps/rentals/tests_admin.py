from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.rentals.models import DeliveryRequest

User = get_user_model()


class OwnerDashboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from apps.warehouses.management.commands.seed_demo import Command

        Command().handle()

    def test_dashboard_requires_staff(self):
        resp = self.client.get("/admin/owner-dashboard/")
        self.assertEqual(resp.status_code, 302)

    def test_admin_index_is_dashboard(self):
        admin = User.objects.get(email="admin@selfstorage.ru")
        self.client.force_login(admin)
        resp = self.client.get("/admin/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Панель владельца")

    def test_dashboard_loads_admin_theme_css(self):
        admin = User.objects.get(email="admin@selfstorage.ru")
        self.client.force_login(admin)
        resp = self.client.get("/admin/")
        self.assertContains(resp, "css/admin.css")

    def test_dashboard_renders_for_staff(self):
        admin = User.objects.get(email="admin@selfstorage.ru")
        self.client.force_login(admin)
        resp = self.client.get("/admin/owner-dashboard/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Одинцово, ул. Победы")
        self.assertContains(resp, "Просроченные")
        self.assertContains(resp, "Отказ принять на доставку")
        self.assertContains(resp, "Екатерина")
        self.assertContains(resp, "Ира")

    def test_delivery_action_mark_done(self):
        admin = User.objects.get(email="admin@selfstorage.ru")
        self.client.force_login(admin)
        dr = DeliveryRequest.objects.filter(status="new").first()
        assert dr is not None
        url = "/admin/rentals/deliveryrequest/"
        resp = self.client.post(
            url,
            {
                "action": "mark_done",
                "_selected_action": [str(dr.pk)],
                "index": "0",
            },
        )
        self.assertEqual(resp.status_code, 302)
        dr.refresh_from_db()
        self.assertEqual(dr.status, "done")

    def test_send_notifications_button_runs_command(self):
        from unittest.mock import patch

        admin = User.objects.get(email="admin@selfstorage.ru")
        self.client.force_login(admin)
        with patch("config.admin_dashboard.call_command") as mock_cc:
            resp = self.client.post("/admin/send-notifications/")
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], "/admin/owner-dashboard/")
        mock_cc.assert_called_once_with("send_notifications")

    def test_dashboard_shows_traffic_sources(self):
        admin = User.objects.get(email="admin@selfstorage.ru")
        self.client.force_login(admin)
        resp = self.client.get("/admin/owner-dashboard/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Источники трафика")
        self.assertContains(resp, "vk")
        self.assertContains(resp, "google")
        self.assertContains(resp, "direct")

    def test_dashboard_breaks_down_by_campaign(self):
        admin = User.objects.get(email="admin@selfstorage.ru")
        self.client.force_login(admin)
        resp = self.client.get("/admin/owner-dashboard/")
        self.assertContains(resp, "Кампания")
        self.assertContains(resp, "vesna")
        self.assertContains(resp, "lyto")
        self.assertContains(resp, "(без кампании)")

    def test_dashboard_revenues_have_no_float_noise(self):
        admin = User.objects.get(email="admin@selfstorage.ru")
        self.client.force_login(admin)
        resp = self.client.get("/admin/owner-dashboard/")
        sources = resp.context["traffic_sources"]
        self.assertTrue(sources)
        for row in sources:
            self.assertRegex(str(row["revenue"]), r"^\d+(\.\d{1,2})?$")
        total = resp.context["traffic_total"]["revenue"]
        self.assertRegex(str(total), r"^\d+(\.\d{1,2})?$")

    def test_delivery_add_requires_order(self):
        admin = User.objects.get(email="admin@selfstorage.ru")
        self.client.force_login(admin)
        url = "/admin/rentals/deliveryrequest/add/"
        resp = self.client.post(
            url,
            {
                "client_address": "Москва, ул. Тестовая, д. 1",
                "phone": "+7-900-000-00-00",
                "status": "new",
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(
            DeliveryRequest.objects.filter(
                client_address="Москва, ул. Тестовая, д. 1"
            ).exists()
        )
