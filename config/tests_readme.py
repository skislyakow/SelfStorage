"""Бейджи и таблица стека в README не должны врать о версиях.

Python, Django и Bootstrap сверяются с источниками правды в репозитории —
при бампе версии CI падает, пока README не обновят. У nginx версии в репо
нет (живёт на VPS), его бейдж обновляется вручную — см. AGENTS.md.
"""

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
    """Версия из shields-url вида ``.../badge/Django-5.2.17-092E20...``."""
    match = re.search(rf"badge/{name}-([0-9][0-9.]*)-", README)
    assert match is not None, f"бейдж {name} не найден в README"
    return match.group(1)


def django_pin() -> str:
    """Пин django из pyproject, напр. ``5.2.17``."""
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
        # CSS и JS Bootstrap в base.html — одной версии, и это та версия,
        # что в бейдже: набор из findall должен состоять из одного элемента.
        versions = set(re.findall(r"bootstrap@(\d+\.\d+\.\d+)", BASE_TEMPLATE))
        self.assertEqual(versions, {badge_version("Bootstrap")})

    def test_stack_table_states_same_versions(self):
        self.assertIn(f"Python {badge_version('Python')}", README)
        self.assertIn(f"Django {badge_version('Django')}", README)
        self.assertIn(f"Bootstrap {badge_version('Bootstrap')}", README)
