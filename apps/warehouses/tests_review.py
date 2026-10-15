from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.warehouses.models import Review

User = get_user_model()


class ReviewModelTests(TestCase):
    def test_str_includes_author_and_city(self):
        review = Review.objects.create(
            title="Заголовок",
            author_name="Катерина",
            city="Одинцово",
            text="Текст отзыва",
        )
        self.assertEqual(str(review), "Отзыв Катерина (Одинцово)")

    def test_review_without_city_str(self):
        review = Review.objects.create(
            title="Заголовок", author_name="Пётр", text="Текст отзыва"
        )
        self.assertEqual(str(review), "Отзыв Пётр (без города)")


class HomeReviewCarouselTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from apps.warehouses.management.commands.seed_demo import Command

        Command().handle()

    def test_home_shows_published_reviews(self):
        response = self.client.get("/")
        self.assertContains(response, "Теперь могу хранить вещи по-умному!")
        self.assertContains(response, "Катерина Петрова")
        self.assertContains(response, "Читать отзыв полностью")

    def test_home_hides_unpublished_review(self):
        response = self.client.get("/")
        self.assertNotContains(response, "Отзыв на модерации")
        self.assertNotContains(response, "Тестовый Автор")

    def test_home_review_opens_modal_with_full_text(self):
        response = self.client.get("/")
        self.assertContains(response, 'data-bs-target="#reviewModal')
        self.assertContains(response, "Быстро собрали вещи и бесплатно доставили")


class ReviewAdminTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        from apps.warehouses.management.commands.seed_demo import Command

        Command().handle()

    def setUp(self):
        admin = User.objects.get(email="admin@selfstorage.ru")
        self.client.force_login(admin)

    def test_admin_review_list_renders(self):
        response = self.client.get("/admin/warehouses/review/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Катерина Петрова")
        self.assertContains(response, "Отзыв на модерации")

    def test_admin_action_unpublish(self):
        review = Review.objects.get(author_name="Катерина Петрова")
        response = self.client.post(
            "/admin/warehouses/review/",
            data={
                "action": "unpublish",
                "_selected_action": [review.pk],
            },
        )
        self.assertEqual(response.status_code, 302)
        review.refresh_from_db()
        self.assertFalse(review.is_published)

    def test_unpublished_review_disappears_from_home(self):
        Review.objects.filter(is_published=True).update(is_published=False)
        response = self.client.get("/")
        self.assertNotContains(response, "Читать отзыв полностью")


class SeedReviewsTests(TestCase):
    def test_seed_creates_two_published_and_one_moderation(self):
        from apps.warehouses.management.commands.seed_demo import Command

        Command().handle()
        self.assertEqual(Review.objects.filter(is_published=True).count(), 2)
        self.assertEqual(Review.objects.filter(is_published=False).count(), 1)
        first = Review.objects.order_by("created_at").first()
        self.assertTrue(first.photo)

    def test_seed_is_idempotent(self):
        from apps.warehouses.management.commands.seed_demo import Command

        Command().handle()
        Command().handle()
        self.assertEqual(Review.objects.count(), 3)
