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
        self.assertEqual(response["Location"], reverse("home"))
        user = User.objects.get(email="new@test.ru")
        self.assertTrue(user.check_password("Str0ngPass!123"))
        self.assertTrue(user.pd_consent)


class UserAdminTests(TestCase):
    def test_user_admin_list_and_change_minimal(self):
        User.objects.create_superuser(email="admin@test.ru", password="x1!aaaaA2")
        self.client.login(email="admin@test.ru", password="x1!aaaaA2")

        list_resp = self.client.get("/admin/users/user/")
        self.assertEqual(list_resp.status_code, 200)
        self.assertContains(list_resp, "Телефон")

        user = User.objects.create_user(email="someone@test.ru", phone="+79990000000")
        change_resp = self.client.get(f"/admin/users/user/{user.pk}/change/")
        self.assertEqual(change_resp.status_code, 200)
        self.assertContains(change_resp, "Согласие ПД")
        self.assertNotContains(change_resp, 'id="id_groups"')
        self.assertNotContains(change_resp, 'id="id_user_permissions"')
        self.assertNotContains(change_resp, "Важные даты")


class LoginLogoutTests(TestCase):
    def test_login_logs_in_user(self):
        User.objects.create_user(email="login@test.ru", password="Str0ngPass!123")
        response = self.client.post(reverse("users:login"), {
            "username": "login@test.ru",
            "password": "Str0ngPass!123",
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("home"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_logout_clears_session(self):
        User.objects.create_user(email="logout@test.ru", password="Str0ngPass!123")
        self.client.force_login(User.objects.get(email="logout@test.ru"))
        response = self.client.post(reverse("users:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)
