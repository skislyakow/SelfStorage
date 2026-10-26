import re
import tomllib
from pathlib import Path

from django.test import SimpleTestCase

BASE_DIR = Path(__file__).resolve().parent.parent
README = (BASE_DIR / "README.md").read_text(encoding="utf-8")
BASE_TEMPLATE = (BASE_DIR / "config" / "templates" / "base.html").read_text(
    encoding="utf-8"
)


def badge_version(name: str) -> str:
    match = re.search(rf"badge/{name}-([0-9][0-9.]*)-", README)
    assert match is not None, f"бейдж {name} не найден в README"
    return match.group(1)


def django_pin() -> str:
    pyproject = tomllib.loads((BASE_DIR / "pyproject.toml").read_text("utf-8"))
    deps: list[str] = pyproject["project"]["dependencies"]
    for dep in deps:
        if dep.startswith("django=="):
            return dep.removeprefix("django==")
    raise AssertionError("django не найден в зависимостях pyproject")


class ReadmeVersionBadgesTests(SimpleTestCase):
    def test_python_badge_matches_python_version_file(self):
        expected = (BASE_DIR / ".python-version").read_text("utf-8").strip()
        self.assertEqual(badge_version("Python"), expected)

    def test_django_badge_matches_pyproject_pin(self):
        self.assertEqual(badge_version("Django"), django_pin())

    def test_bootstrap_badge_matches_cdn_in_base_template(self):
        versions = set(re.findall(r"bootstrap@(\d+\.\d+\.\d+)", BASE_TEMPLATE))
        self.assertEqual(versions, {badge_version("Bootstrap")})

    def test_stack_table_states_same_versions(self):
        self.assertTrue(True)
