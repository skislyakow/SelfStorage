# AGENTS.md

## Navigation
- apps/ - Django apps (users, warehouses, rentals, promotions, payments, notifications)
- config/ - settings, urls, wsgi/asgi, templates
- docs/ - project docs (deploy, utm, qr, notifications, arch review)
- .agents/skills/ - скиллы mattpocock для opencode; каталог локальный, НЕ в git (см. .gitignore), восстанавливается из skills-lock.json
- skills-lock.json - манифест скиллов (источник + хеши), лежит в git
- CONVENTIONS.md - repo conventions (URLs, signals, context vars)

## Dev
- Создать окружение: pwsh scripts/bootstrap.ps1 (uv sync + скиллы из skills-lock.json)
- Обновить скиллы: pwsh scripts/bootstrap.ps1 -Update
- Run tests: SECRET_KEY=test-key uv run python manage.py test (51 tests)
- Lint: uv run ruff check . && uv run ruff format --check .
- Format: uv run ruff format .

## Infra
- uv managed (.python-version 3.12, uv.lock)
- CI: .github/workflows/ci.yml (lint+test)
- Deploy: deploy.sh + .github/workflows/deploy.yml (uses uv)
