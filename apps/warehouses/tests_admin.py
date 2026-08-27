from django.test import TestCase, Client

from django.contrib.auth import get_user_model

User = get_user_model()


class BoxAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from apps.warehouses.management.commands.seed_demo import Command

        Command().handle()

    def test_box_list_shows_occupancy_status(self):
        admin = User.objects.get(email="admin@selfstorage.ru")
        self.client.force_login(admin)
        resp = self.client.get("/admin/warehouses/box/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Занят")
        self.assertContains(resp, "Свободен")
        self.assertContains(resp, "Зарезервирован")