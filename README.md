# SelfStorage

Сервис аренды складских боксов (MVP). Стек: Python 3.12 + Django 5.2 + SQLite.

## Запуск

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Наполнение примерами — команда `python manage.py seed_demo` (идемпотентна: пересоздаёт склады, боксы, кабинет и промокод при каждом запуске).

## Демо-данные для входа

После `seed_demo` в базе есть тестовые аккаунты:

| Роль | E-mail | Пароль |
|------|--------|--------|
| Администратор (панель `/admin/`) | `admin@selfstorage.ru` | `admin12345` |
| Пользователь (кабинет Екатерины, `my-rent`) | `ekatyusha89@yandex.ru` | `111111111` |

Прочие демо-данные: 5 складов (Москва, Одинцово, Пушкино, Люберцы, Домодедово) с фото, боксы, 2 активные аренды, промокоды `storage15` (скидка 15%, ноябрь–апрель) и `storage2022` (скидка 22%, март).

## Структура

- `config/` — настройки проекта (settings, urls, wsgi/asgi).
- `apps/` — приложения по доменам:
  - `users` — пользователи (email = логин, телефон, согласие на ПД).
  - `warehouses` — склады и боксы.
  - `rentals` — заказы аренды и заявки на доставку.
  - `promotions` — промокоды.
  - `payments` — платежи ЮKassa.
  - `notifications` — письма и команда `send_notifications`.
- `layot/` — исходная вёрстка (берётся как есть, не редактируется; адаптируется в шаблоны).
- `static/` — статические файлы (css/img после адаптации вёрстки).
- `media/` — загрузки (фото складов, qr.png); в `.gitignore`.

## Договорённости

Общие контракты (имена URL, переменные шаблонов, сигналы) зафиксированы в `CONVENTIONS.md`. Перед добавлением нового URL/сигнала/переменной — обнови этот файл.

## Переменные окружения / VPS

Проект читает `.env` в корне через `django-environ` (`env.read_env`). Файл `.env` находится в `.gitignore` — **не коммитится**. Шаблон всех переменных — в `.env.example`.

Локально (dev) `.env` необязателен: по умолчанию `DEBUG` берётся из окружения, а почта уходит в **консоль** (`console.EmailBackend`). На продакшене в `.env` на VPS нужно задать реальные значения, которых нет локально:

- `SECRET_KEY` — уникальный секрет (обязательно отличный от дефолта).
- `DEBUG=False`
- `ALLOWED_HOSTS` — через запятую, напр. `selftorage.kislyakov.pro`.
- `DB_PATH` — путь к sqlite, напр. `/opt/selftorage/db.sqlite3`.
- `EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend`
- `EMAIL_HOST`, `EMAIL_PORT` (587), `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS=True`, `DEFAULT_FROM_EMAIL`.

Без SMTP-настроек письма не дойдут (упадут в консоль), но сайт продолжает работать.

### Уведомления (`send_notifications`)

Команда `python manage.py send_notifications` шлёт напоминания за 30/14/7/3 дня до окончания аренды (`status='active'`) и письма о просрочке (каждые 30 дней после перевода в `overdue`). Чтобы письма реально уходили, запускайте её по расписанию, например cron раз в сутки на VPS:

```
0 9 * * * cd /opt/selftorage && /opt/selftorage/venv/bin/python manage.py send_notifications >> /opt/selftorage/notifications.log 2>&1
```

