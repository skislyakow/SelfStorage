from django.test import TestCase


class PrivacyPageTests(TestCase):
    def test_privacy_page_returns_200(self):
        response = self.client.get("/privacy/")
        self.assertEqual(response.status_code, 200)

    def test_privacy_page_contains_title_and_legal_anchor_target(self):
        response = self.client.get("/privacy/")
        content = response.content.decode()
        self.assertIn("Политика конфиденциальности", content)
        self.assertIn("Правовые документы", content)

    def test_registration_form_links_to_privacy_policy(self):
        response = self.client.get("/")
        self.assertContains(response, "/privacy/")
