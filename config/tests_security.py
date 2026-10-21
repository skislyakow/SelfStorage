from django.test import TestCase


class SecurityHeadersTests(TestCase):
    """HSTS и CSP — два заголовка, которых не было на стенде (см. TODO)."""

    def test_csp_header_on_home_page(self):
        response = self.client.get("/")
        csp = response.headers.get("Content-Security-Policy", "")
        self.assertIn("default-src 'self'", csp)
        self.assertIn("script-src 'self' https://cdn.jsdelivr.net", csp)
        self.assertIn("frame-ancestors 'none'", csp)

    def test_csp_header_on_admin_login(self):
        response = self.client.get("/admin/login/")
        self.assertIn("Content-Security-Policy", response.headers)

    def test_hsts_set_behind_proxy(self):
        response = self.client.get("/", headers={"X-Forwarded-Proto": "https"})
        self.assertEqual(
            response.headers.get("Strict-Transport-Security"), "max-age=31536000"
        )

    def test_hsts_set_for_secure_request(self):
        response = self.client.get("/", secure=True)
        self.assertIn("Strict-Transport-Security", response.headers)

    def test_hsts_absent_over_plain_http(self):
        response = self.client.get("/")
        self.assertNotIn("Strict-Transport-Security", response.headers)
