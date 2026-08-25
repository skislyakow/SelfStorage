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

Наполнение примерами — команда `seed_demo` (появится на этапе моделей).

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
