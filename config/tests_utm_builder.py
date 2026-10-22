from urllib.parse import urlencode

from django.contrib.staticfiles import finders
from django.test import SimpleTestCase, TestCase

from apps.users.models import User


class UtmBuilderTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.staff = User.objects.create_user(
            email="builder@test.ru", password="Str0ngPass!123", is_staff=True
        )

    def test_requires_staff(self):
        resp = self.client.get("/admin/utm-builder/")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/admin/login/", resp["Location"])

    def test_renders_form_for_staff(self):
        self.client.force_login(self.staff)
        resp = self.client.get("/admin/utm-builder/")
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Конструктор UTM-ссылок")
        self.assertContains(resp, "utm_source — источник")
        self.assertContains(resp, "utm-source-list")

    def test_dashboard_links_to_builder(self):
        self.client.force_login(self.staff)
        resp = self.client.get("/admin/")
        self.assertContains(resp, "/admin/utm-builder/")

    def test_builds_link_with_all_params(self):
        self.client.force_login(self.staff)
        resp = self.client.post(
            "/admin/utm-builder/",
            {
                "target": "/",
                "custom_path": "",
                "source": "vk",
                "medium": "social",
                "campaign": "весна 2026",
                "content": "banner_a",
            },
        )
        expected = "http://testserver/?" + urlencode(
            {
                "utm_source": "vk",
                "utm_medium": "social",
                "utm_campaign": "весна 2026",
                "utm_content": "banner_a",
            }
        )
        self.assertEqual(resp.context["result"], expected)
        self.assertContains(resp, "Готовая ссылка")

    def test_source_required(self):
        self.client.force_login(self.staff)
        resp = self.client.post("/admin/utm-builder/", {"target": "/", "source": ""})
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.context["result"])
        self.assertIn("source", resp.context["form"].errors)

    def test_custom_path(self):
        self.client.force_login(self.staff)
        resp = self.client.post(
            "/admin/utm-builder/",
            {"target": "custom", "custom_path": "/faq/", "source": "email"},
        )
        self.assertEqual(
            resp.context["result"], "http://testserver/faq/?utm_source=email"
        )

    def test_custom_path_requires_leading_slash(self):
        self.client.force_login(self.staff)
        resp = self.client.post(
            "/admin/utm-builder/",
            {"target": "custom", "custom_path": "faq/", "source": "email"},
        )
        self.assertIsNone(resp.context["result"])
        self.assertIn("custom_path", resp.context["form"].errors)

    def test_omitted_optional_params_not_in_url(self):
        self.client.force_login(self.staff)
        resp = self.client.post(
            "/admin/utm-builder/", {"target": "/", "source": "direct"}
        )
        self.assertEqual(resp.context["result"], "http://testserver/?utm_source=direct")


class UtmBuilderStaticTests(SimpleTestCase):
    def test_copy_button_js_is_findable(self):
        self.assertIsNotNone(finders.find("js/utm-builder.js"))
