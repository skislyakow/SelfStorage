from datetime import date

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

    def test_seed_creates_two_promo_codes(self):
        from apps.promotions.models import PromoCode

        self.assertEqual(PromoCode.objects.count(), 2)
        s15 = PromoCode.objects.get(code="storage15")
        self.assertEqual(s15.discount_percent, 15)
        self.assertEqual(s15.valid_from, date(2026, 11, 1))
        self.assertEqual(s15.valid_to, date(2027, 4, 30))
        s22 = PromoCode.objects.get(code="storage2022")
        self.assertEqual(s22.discount_percent, 22)
        self.assertEqual(s22.valid_from, date(2026, 3, 1))
        self.assertEqual(s22.valid_to, date(2026, 3, 31))