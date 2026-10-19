# Деплой и переменные окружения

Проект использует uv. Деплой через GitHub Actions (`.github/workflows/deploy.yml`) по push в `main`: на VPS выполняется `deploy.sh` (в `/opt/selftorage/`), который делает `uv sync --frozen --no-dev`, `collectstatic`, `migrate`, `seed_demo`, перезапуск сервиса и установку systemd-таймера уведомлений.

## Демонстрационный стенд

Стенд демонстрационный, поэтому `deploy.sh` на каждом деплое вызывает `seed_demo`. Команда пересоздаёт склады, боксы, промокоды и пользователей, так что после любой выкатки сайт выглядит одинаково и предсказуемо.

Это ожидаемое поведение, а не потеря данных: регистрации и заказы, сделанные на стенде, при следующем деплое сбрасываются. Боевой контур потребовал бы убрать `seed_demo` из `deploy.sh` (или закрыть его условием на пустую базу).

## .env
Файл `.env` в корне через `django-environ`. `.env` не коммитится; шаблон — `.env.example`.

Обязательные для продакшена (и локально при текущих настройках — см. ниже):
- `SECRET_KEY` — уникальный секрет
- `DEBUG` — `False` на проде
- `ALLOWED_HOSTS` — через запятую
- `DB_PATH` — путь к SQLite
- `EMAIL_*` — SMTP-настройки (иначе письма в консоль)

Приём оплат YooKassa: `YOOKASSA_SHOP_ID`, `YOOKASSA_SECRET_KEY`, `SITE_URL`.

## Проверка после деплоя
```bash
curl -s -H "Host: selfstorage.kislyakov.pro" http://127.0.0.1:8003/orders/my-rent/ -o /dev/null -w "%{http_code}"
# ожидаем 302

curl -sI https://selfstorage.kislyakov.pro/ | grep -E 'Strict-Transport|Content-Security'
# ожидаем max-age=31536000 и default-src 'self' (HSTS и CSP)
```

## Если деплой упал на `git pull`

У сервера только одна задача — отдавать `origin/main`, своих коммитов там не
предполагается. Если историю в репозитории переписали (force-push/rebase),
`git pull` на сервере отказывается мержить разошедшиеся ветки и деплой падает.
Чинится одной командой с VPS:

```bash
cd /opt/selftorage && git reset --hard origin/main && bash deploy.sh
```

`.env`, `db.sqlite3` и `media/` под gitignore — reset их не трогает. В
workflow стоит `git pull --ff-only`: такая ситуация падает сразу с понятной
ошибкой, а не на слиянии.
