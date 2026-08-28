# SelfStorage

Сервис аренды складских боксов (MVP). Стек: `Python 3.12` + `Django 5.2` + `SQLite`.

## Запуск

```bash
# Создать виртуальное окружение
python -m venv venv
```

### Активировать (Windows)
```bash
.\venv\Scripts\Activate.ps1
```

### Активировать (Linux/Mac)
```bash
source venv/bin/activate
```

### Установить зависимости
```bash
pip install -r requirements.txt
```
### Применить миграции
```bash
python manage.py migrate
```
### Наполнить тестовыми данными
```bash
python manage.py seed_demo
```
### Запустить сервер
```bash
python manage.py runserver
```
## Демо-данные для входа

После `seed_demo` в базе есть тестовые аккаунты:

| Роль | E-mail | Пароль |
|------|--------|--------|
| Администратор (панель `/admin/`) | `admin@selfstorage.ru` | `admin12345` |
| Пользователь (кабинет Екатерины, `my-rent`) | `ekatyusha89@yandex.ru` | `111111111` |

Прочие демо-данные: 5 складов (Москва, Одинцово, Пушкино, Люберцы, Домодедово) с фото, боксы, 2 активные аренды, промокоды `storage15` (скидка 15%, ноябрь–апрель) и `storage2022` (скидка 22%, март).

## Команды управления
### Наполнение тестовыми данными
``` bash
python manage.py seed_demo
```
### Отправка уведомлений (напоминания об аренде)
```bash
python manage.py send_notifications
```
### Что делает команда:

Напоминания за 30, 14, 7 и 3 дня до окончания аренды

Перевод заказов в статус `overdue` при просрочке

Ежемесячные напоминания для просроченных заказов

Завершение заказов и предупреждение о потере вещей через 6 месяцев

## Настройка почты
### Для разработки (письма в консоль)
В файле `.env`:

```text
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```
### Для продакшена (реальная отправка)

В файле `.env`:

```text
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.yandex.ru
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=info@selfstorage.ru
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=info@selfstorage.ru
```
### Структура проекта
```text
SelfStorage/
├── config/               # Настройки проекта
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/                 # Приложения
│   ├── users/            # Пользователи (email = логин)
│   ├── warehouses/       # Склады и боксы
│   ├── rentals/          # Заказы аренды и доставка
│   ├── promotions/       # Промокоды
│   ├── payments/         # Платежи ЮKassa
│   └── notifications/    # Письма и команда send_notifications
├── layot/                # Исходная вёрстка (не редактируется)
├── static/               # Статические файлы
├── media/                # Загрузки (фото, QR)
├── manage.py
├── requirements.txt
├── .env                  # Переменные окружения (создать из .env.example)
└── README.md
```
Переменные окружения (`.env`)
Создай файл `.env` в корне проекта:

```text
DEBUG=True
SECRET_KEY=django-insecure-change-me-in-production
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Договорённости
Общие контракты (имена `URL`, переменные шаблонов, сигналы) зафиксированы в `CONVENTIONS.md`.
Перед добавлением нового URL/сигнала/переменной — обнови этот файл.

