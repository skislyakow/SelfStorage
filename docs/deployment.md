# Деплой и переменные окружения

Проект использует uv. Деплой через GitHub Actions (`.github/workflows/deploy.yml`) по push в `main`: на VPS выполняется `deploy.sh` (в `/opt/selftorage/`), который делает `uv sync --frozen --no-dev`, `collectstatic`, `migrate`, `seed_demo`, перезапуск сервиса и установку systemd-таймера уведомлений.

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
```
