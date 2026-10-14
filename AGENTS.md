# AGENTS.md

## Navigation
- apps/ - Django apps (users, warehouses, rentals, promotions, payments, notifications)
- config/ - settings, urls, wsgi/asgi, templates
- docs/ - project docs (deploy, utm, qr, notifications, arch review)
- .agents/skills/ - скиллы mattpocock для opencode; каталог локальный, НЕ в git (см. .gitignore), восстанавливается из skills-lock.json
- skills-lock.json - манифест скиллов (источник + хеши), лежит в git
- CONVENTIONS.md - repo conventions (URLs, signals, context vars)

## Dev
- Создать окружение: .\scripts\bootstrap.ps1 (uv sync + хук pre-commit + скиллы из skills-lock.json)
- Обновить скиллы: .\scripts\bootstrap.ps1 -Update
- Run tests: SECRET_KEY=test-key uv run python manage.py test
- Lint: uv run ruff check . && uv run ruff format --check .
- Типы: uv run mypy .
- Format: uv run ruff format .

## Windows / PowerShell
- Секрет в env: PowerShell `$env:SECRET_KEY="test-key"`, bash `SECRET_KEY=test-key`.
- `pwsh` (PowerShell 7) может не стоять — хватит текущего `powershell`/`.\scripts\bootstrap.ps1`.
- У нативных команд (git, uv) `2>&1` даёт шумный NativeCommandError и путает вывод с ошибкой. Статус брать из `$LASTEXITCODE`, а вывод — через `cmd /c "команда > файл 2>&1"`.
- Кавычки внутри `git commit -m "..."` в PowerShell 5.1 теряются, и слова сообщения уезжают в pathspec. Надёжно — `git commit -F -` с here-string.
- `.ps1` без BOM PowerShell 5.1 читает как ANSI, кириллица бьётся: сохранять с BOM.

## Infra
- uv managed (.python-version 3.12, uv.lock)
- CI: .github/workflows/ci.yml
- Deploy: deploy.sh + .github/workflows/deploy.yml (uses uv)
