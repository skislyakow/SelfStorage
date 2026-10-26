# Архитектура и стек

## Стек технологий

| Слой | Технологии |
|---|---|
| Backend | Python 3.12, Django 5.2.17 — кастомная модель пользователя, class-based views, ORM и миграции, Django Admin, signals, middleware, management-команды |
| Данные | SQLite (осознанный выбор для демо-стенда: база — один файл, отдельный сервер БД не нужен) |
| Фронтенд | Django Templates, Bootstrap 5.0.2, собственный CSS, vanilla JS |
| Оформление заказа | django-formtools (`SessionWizardView`), валидация через Django Forms |
| Платежи | API ЮKassa: создание платежа, `return_url`, webhook |
| Почта и уведомления | Django email backend, SMTP REG.RU, management-команда `send_notifications`, systemd timer |
| QR-доступ | `qrcode` + Pillow |
| Конфигурация | django-environ, 12-факторный `.env` (шаблон — `.env.example`) |
| Продакшен | nginx 1.24 + gunicorn под systemd на VPS (Ubuntu); приложение и таймер уведомлений — отдельные юниты |
| CI/CD | GitHub Actions: CI (lint, типы, тесты, проверка миграций) и деплой на сервер по SSH |
| Качество кода | uv (зависимости и Python), ruff (lint и формат), mypy + django-stubs, pre-commit, Django TestCase |

## Структура проекта

```
apps/        Django-приложения: users, warehouses, rentals, promotions, payments, notifications
config/      настройки, роутинг, базовые шаблоны, дашборд владельца и конструктор UTM-ссылок
docs/        деплой, UTM-метки, QR-доступ, уведомления, архитектура
scripts/     bootstrap окружения (PowerShell и sh)
static/      исходные CSS и изображения
deploy.sh    шаги деплоя на сервере
```
