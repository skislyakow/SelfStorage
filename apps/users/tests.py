from django.test import TestCase, Client
from django.urls import reverse

from apps.users.models import User


class RegistrationTests(TestCase):
    def setUp(self):
        self.client = Client(SERVER_NAME="localhost")

    def test_register_renders_form_on_get(self):
        response = self.client.get(reverse("users:register"))
        self.assertEqual(response.status_code, 200)

    def test_register_creates_user_and_redirects(self):
        data = {
            "email": "new@test.ru",
            "phone": "+79990000000",
            "password1": "Str0ngPass!123",
            "password2": "Str0ngPass!123",
            "personal_data_consent": "on",
        }
        response = self.client.post(reverse("users:register"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("warehouse_list"))
        user = User.objects.get(email="new@test.ru")
        self.assertTrue(user.check_password("Str0ngPass!123"))
        self.assertIsNotNone(user.pd_consent_date)
