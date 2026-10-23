from pathlib import Path

from django.contrib.staticfiles import finders
from django.test import SimpleTestCase

BASE_DIR = Path(__file__).resolve().parent.parent
ADMIN_CSS = (BASE_DIR / "static" / "css" / "admin.css").read_text(encoding="utf-8")
BASE_SITE = (BASE_DIR / "config" / "templates" / "admin" / "base_site.html").read_text(
    encoding="utf-8"
)


class AdminThemeTemplateTests(SimpleTestCase):
    def test_login_page_has_branding_font_and_theme(self):
        response = self.client.get("/admin/login/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SelfStorage")
        self.assertContains(response, "img/SelfStorage.svg")
        self.assertContains(response, "css/admin.css")
        self.assertContains(response, "Commissioner")

    def test_base_site_declares_branding(self):
        self.assertIn("block branding", BASE_SITE)
        self.assertIn("admin-logo", BASE_SITE)
        self.assertIn('alt="SelfStorage"', BASE_SITE)
        self.assertNotIn('admin-logo">SelfStorage', BASE_SITE)


class AdminThemeCssTests(SimpleTestCase):
    def test_css_is_findable_by_staticfiles(self):
        self.assertIsNotNone(finders.find("css/admin.css"))

    def test_light_theme_uses_site_palette(self):
        self.assertIn("--primary: #579586", ADMIN_CSS)
        self.assertIn("--accent: #F28A4F", ADMIN_CSS)
        self.assertIn('"Commissioner"', ADMIN_CSS)

    def test_dark_theme_overrides_present(self):
        self.assertIn("@media (prefers-color-scheme: dark)", ADMIN_CSS)
        self.assertIn('html[data-theme="dark"]', ADMIN_CSS)
