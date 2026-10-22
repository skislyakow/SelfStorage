import re
import tempfile
from io import BytesIO

from django.core import mail
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from PIL import Image

from apps.users.models import User


def png_bytes():
    buf = BytesIO()
    Image.new("RGB", (8, 8), "red").save(buf, "PNG")
    return buf.getvalue()


class RegistrationTests(TestCase):
    def setUp(self):
        self.client = Client(SERVER_NAME="localhost")

    def test_register_renders_form_on_get(self):
        response = self.client.get(reverse("users:register"))
        self.assertEqual(response.status_code, 200)

    def test_register_creates_user_and_redirects(self):
        data = {
            "email": "new@test.ru",
            "first_name": "Новый",
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
        self.assertEqual(user.first_name, "Новый")

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_register_sends_welcome_email(self):
        data = {
            "email": "welcome@test.ru",
            "first_name": "Привет",
            "phone": "+79990000000",
            "password1": "Str0ngPass!123",
            "password2": "Str0ngPass!123",
            "personal_data_consent": "on",
        }
        response = self.client.post(reverse("users:register"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["welcome@test.ru"])
        self.assertIn("Добро пожаловать", mail.outbox[0].subject)
        self.assertIn("Привет", mail.outbox[0].body)
        self.assertNotIn("Уважаемый(ая)", mail.outbox[0].body)
        self.assertEqual(User.objects.get(email="welcome@test.ru").first_name, "Привет")


class NextRedirectTests(TestCase):
    def setUp(self):
        self.client = Client(SERVER_NAME="localhost")

    @staticmethod
    def register_data(**overrides):
        data = {
            "email": "next@test.ru",
            "first_name": "Гость",
            "phone": "+79990000000",
            "password1": "Str0ngPass!123",
            "password2": "Str0ngPass!123",
            "personal_data_consent": "on",
        }
        data.update(overrides)
        return data

    def test_login_required_redirect_lands_on_real_page(self):
        response = self.client.get(reverse("my_rent"))
        login_url = f"{reverse('users:login')}?next={reverse('my_rent')}"

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], login_url)
        self.assertEqual(self.client.get(login_url).status_code, 200)

    def test_register_returns_to_next(self):
        response = self.client.post(
            reverse("users:register"),
            self.register_data(next=reverse("my_rent")),
        )
        self.assertRedirects(
            response, reverse("my_rent"), fetch_redirect_response=False
        )

    def test_register_without_next_goes_home(self):
        response = self.client.post(reverse("users:register"), self.register_data())
        self.assertEqual(response["Location"], reverse("home"))

    def test_register_ignores_next_on_another_host(self):
        response = self.client.post(
            reverse("users:register"),
            self.register_data(next="https://evil.example.com/phish"),
        )
        self.assertEqual(response["Location"], reverse("home"))

    def test_auth_forms_post_to_real_views(self):
        page = self.client.get(reverse("home")).content.decode()

        for url_name in ("users:login", "users:register", "users:password_reset"):
            self.assertIn(f'action="{reverse(url_name)}"', page)


class UserAdminTests(TestCase):
    def test_user_admin_list_and_change_minimal(self):
        User.objects.create_superuser(email="admin@test.ru", password="x1!aaaaA2")
        self.client.login(email="admin@test.ru", password="x1!aaaaA2")

        list_resp = self.client.get("/admin/users/user/")
        self.assertEqual(list_resp.status_code, 200)
        self.assertContains(list_resp, "Телефон")
        self.assertContains(list_resp, "Имя")

        user = User.objects.create_user(email="someone@test.ru", phone="+79990000000")
        change_resp = self.client.get(f"/admin/users/user/{user.pk}/change/")
        self.assertEqual(change_resp.status_code, 200)
        self.assertContains(change_resp, "Согласие ПД")
        self.assertContains(change_resp, "Имя")
        self.assertNotContains(change_resp, 'id="id_groups"')
        self.assertNotContains(change_resp, 'id="id_user_permissions"')
        self.assertNotContains(change_resp, "Важные даты")


class LoginLogoutTests(TestCase):
    def test_login_logs_in_user(self):
        User.objects.create_user(email="login@test.ru", password="Str0ngPass!123")
        response = self.client.post(
            reverse("users:login"),
            {
                "username": "login@test.ru",
                "password": "Str0ngPass!123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], reverse("home"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_logout_clears_session(self):
        User.objects.create_user(email="logout@test.ru", password="Str0ngPass!123")
        self.client.force_login(User.objects.get(email="logout@test.ru"))
        response = self.client.post(reverse("users:logout"))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("_auth_user_id", self.client.session)


class PasswordResetTests(TestCase):
    def test_password_reset_sends_email_and_changes_password(self):
        User.objects.create_user(email="reset@test.ru", password="OldPass!123")
        client = Client(SERVER_NAME="localhost")

        resp = client.post(reverse("users:password_reset"), {"email": "reset@test.ru"})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp["Location"], reverse("users:password_reset_done"))

        self.assertEqual(len(mail.outbox), 1)
        body = str(mail.outbox[0].body)
        match = re.search(r"/accounts/password-reset/([^/]+)/([^/]+)/", body)
        assert match is not None
        uidb64, token = match.group(1), match.group(2)

        confirm_url = reverse(
            "users:password_reset_confirm", kwargs={"uidb64": uidb64, "token": token}
        )
        resp_get = client.get(confirm_url)
        self.assertEqual(resp_get.status_code, 302)
        set_password_url = resp_get["Location"]

        resp_form = client.get(set_password_url)
        self.assertEqual(resp_form.status_code, 200)

        resp_post = client.post(
            set_password_url,
            {
                "new_password1": "NewStr0ng!456",
                "new_password2": "NewStr0ng!456",
            },
        )
        self.assertEqual(resp_post.status_code, 302)
        self.assertEqual(
            resp_post["Location"], reverse("users:password_reset_complete")
        )

        user = User.objects.get(email="reset@test.ru")
        self.assertTrue(user.check_password("NewStr0ng!456"))


@override_settings(MEDIA_ROOT=tempfile.mkdtemp(prefix="selfstorage-tests-"))
class ProfileTests(TestCase):
    def setUp(self):
        self.client = Client(SERVER_NAME="localhost")
        self.user = User.objects.create_user(
            email="profile@test.ru", password="Str0ngPass!123", first_name="Пётр"
        )
        self.client.force_login(self.user)

    @staticmethod
    def profile_data(**overrides):
        data = {
            "first_name": "Пётр",
            "email": "profile@test.ru",
            "phone": "+79990001122",
        }
        data.update(overrides)
        return data

    def test_profile_requires_login(self):
        self.client.logout()
        response = self.client.post(reverse("users:profile"), self.profile_data())
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("users:login"), response["Location"])

    def test_profile_get_not_allowed(self):
        response = self.client.get(reverse("users:profile"))
        self.assertEqual(response.status_code, 405)

    def test_profile_updates_first_name(self):
        response = self.client.post(
            reverse("users:profile"),
            self.profile_data(first_name="Сергей"),
            follow=True,
        )
        self.assertContains(response, "Профиль сохранён")
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Сергей")

    def test_profile_invalid_email_keeps_old_value(self):
        response = self.client.post(
            reverse("users:profile"), self.profile_data(email="не-почта"), follow=True
        )
        self.assertContains(response, "Email:")
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "profile@test.ru")

    def test_profile_uploads_avatar(self):
        avatar = SimpleUploadedFile("avatar.png", png_bytes(), content_type="image/png")
        self.client.post(reverse("users:profile"), self.profile_data(avatar=avatar))
        self.user.refresh_from_db()
        self.assertTrue(self.user.avatar.name.startswith("avatars/"))
        self.assertTrue(self.user.avatar.storage.exists(self.user.avatar.name))

    def test_profile_rejects_oversized_avatar(self):
        big = png_bytes() + b"\x00" * (2 * 1024 * 1024 + 1)
        avatar = SimpleUploadedFile("big.png", big, content_type="image/png")
        response = self.client.post(
            reverse("users:profile"), self.profile_data(avatar=avatar), follow=True
        )
        self.assertContains(response, "не больше 2 МБ")
        self.user.refresh_from_db()
        self.assertEqual(self.user.avatar, "")

    def test_profile_rejects_non_image_avatar(self):
        avatar = SimpleUploadedFile("doc.txt", b"hello", content_type="text/plain")
        response = self.client.post(
            reverse("users:profile"), self.profile_data(avatar=avatar), follow=True
        )
        self.assertContains(response, "Аватар:")
        self.user.refresh_from_db()
        self.assertEqual(self.user.avatar, "")

    def test_header_shows_avatar_when_set(self):
        self.user.avatar.save("a.png", ContentFile(png_bytes()), save=True)
        response = self.client.get(reverse("home"))
        self.assertContains(response, "media/avatars/")

    def test_header_shows_placeholder_without_avatar(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "bi-person")
        self.assertNotContains(response, "media/avatars/")

    def test_cabinet_form_posts_to_profile(self):
        response = self.client.get(reverse("my_rent"))
        self.assertContains(response, f'action="{reverse("users:profile")}"')
        self.assertContains(response, 'enctype="multipart/form-data"')
