from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.promotions.models import PromoCode
from apps.rentals.models import RentalOrder
from apps.rentals.services import (
    add_months,
    calculate_amount,
    can_open_box,
    close_box,
    open_box,
)
from apps.users.models import User
from apps.warehouses.models import Box, Warehouse


class BoxAccessServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="renter@test.ru", password="pass1234"
        )
        self.wh = Warehouse.objects.create(city="Москва", address="ул. Тест, 1")
        self.box = Box.objects.create(
            warehouse=self.wh,
            number="9",
            area=3,
            price_per_month=2000,
            status="occupied",
        )
        self.order = RentalOrder.objects.create(
            user=self.user,
            box=self.box,
            start_date="2026-01-01",
            end_date="2027-01-01",
            status="active",
            amount=2000,
        )

    def test_can_open_box_only_when_active(self):
        self.assertTrue(can_open_box(self.order))
        self.order.status = "finished"
        self.assertFalse(can_open_box(self.order))

    def test_open_box_sets_open_and_reports_change(self):
        self.assertTrue(open_box(self.order))
        self.order.refresh_from_db()
        self.assertEqual(self.order.access_status, "open")

    def test_open_box_is_idempotent(self):
        self.assertTrue(open_box(self.order))
        self.assertFalse(open_box(self.order))

    def test_open_box_refuses_when_not_active(self):
        self.order.status = "overdue"
        self.assertFalse(open_box(self.order))
        self.order.refresh_from_db()
        self.assertEqual(self.order.access_status, "closed")

    def test_close_box_sets_closed(self):
        open_box(self.order)
        close_box(self.order)
        self.order.refresh_from_db()
        self.assertEqual(self.order.access_status, "closed")


class CalculateAmountTests(TestCase):
    def setUp(self):
        self.wh = Warehouse.objects.create(city="Москва", address="ул. Тест, 1")
        self.box = Box.objects.create(
            warehouse=self.wh,
            number="10",
            area=3,
            price_per_month=1000,
            status="free",
        )

    def test_add_months_clamps_to_short_month(self):
        self.assertEqual(add_months(date(2026, 1, 31), 1), date(2026, 2, 28))
        self.assertEqual(add_months(date(2026, 12, 15), 2), date(2027, 2, 15))

    def test_amount_without_promo_is_full_price(self):
        calc = calculate_amount(self.box, 3, date(2026, 1, 1), None)
        self.assertEqual(calc["total"], 3000)
        self.assertEqual(calc["full_months"], 3)
        self.assertEqual(calc["discounted_months"], 0)

    def test_amount_applies_promo_to_overlapping_months(self):
        promo = PromoCode.objects.create(
            code="SPRING",
            discount_percent=Decimal("10"),
            valid_from=date(2026, 2, 1),
            valid_to=date(2026, 2, 28),
        )
        calc = calculate_amount(self.box, 3, date(2026, 1, 1), promo)
        self.assertEqual(calc["total"], Decimal("2900.00"))
        self.assertEqual(calc["discounted_months"], 1)
        self.assertEqual(calc["full_months"], 2)
        self.assertEqual(calc["discounted_month_price"], Decimal("900.00"))
