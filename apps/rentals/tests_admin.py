from django.test import TestCase, Client

from django.contrib.auth import get_user_model

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

    def test_dashboard_renders_for_staff(self):
        admin = User.objects.get(email="admin@selfstorage.ru")
        self.client.force_login(admin)
        resp = self.client.get("/admin/owner-dashboard/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Одинцово, ул. Победы")
        self.assertContains(resp, "Просроченные")

    def test_delivery_action_mark_done(self):
        admin = User.objects.get(email="admin@selfstorage.ru")
        self.client.force_login(admin)
        dr = DeliveryRequest.objects.filter(status="new").first()
        self.assertIsNotNone(dr)
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
