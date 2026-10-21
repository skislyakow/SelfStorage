# AGENTS.md

## Navigation
- apps/ - Django apps (users, warehouses, rentals, promotions, payments, notifications)
- config/ - settings, urls, wsgi/asgi, templates
- docs/ - project docs (deploy, utm, qr, notifications, arch review, TODO)
- docs/agent-skills.md - скиллы агентов (.agents/skills, skills-lock.json, установка и обновление)
- docs/TODO.md - открытые задачи проекта: продолжать работу отсюда, дописывать туда же
- .agents/skills/ - скиллы mattpocock для opencode; каталог локальный, НЕ в git (см. .gitignore), восстанавливается из skills-lock.json
- skills-lock.json - манифест скиллов (источник + хеши), лежит в git
- CONVENTIONS.md - repo conventions (URLs, signals, context vars)
- GitHub owner - skislyakow (в URL репозитория и бейджей); домен проекта kislyakov.pro - не путать, в аккаунте есть «w»

## Dev
- Создать окружение: .\scripts\bootstrap.ps1 (uv sync + хук pre-commit + скиллы из skills-lock.json)
- Обновить скиллы: .\scripts\bootstrap.ps1 -Update
- Run tests: SECRET_KEY=test-key uv run python manage.py test
- Lint: uv run ruff check . && uv run ruff format --check .
- Типы: uv run mypy .
- Format: uv run ruff format .
- Коммиты в `main` — через PR: прямой push отклоняется защитой ветки (PR обязателен, чеки `lint`/`types`/`test` должны пройти, force-push запрещён, правила действуют и на админа). Схема: ветка → push → PR → merge после зелёного CI.
- Бейджи версий в README: Python/Django/Bootstrap сверяет тест `config/tests_readme.py` (с `.python-version`, `pyproject`, `base.html`) — при бампе версии README правится в том же PR. nginx-бейдж обновлять вручную: версии в репо нет, она живёт на VPS.

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
