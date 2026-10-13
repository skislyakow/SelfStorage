# SelfStorage

Сервис аренды складских боксов. Клиент выбирает склад и бокс, оформляет аренду онлайн, оплачивает через ЮKassa и получает QR-доступ к боксу.

## Как запустить

```powershell
# 1. Клонируем репозиторий
cd SelfStorage

# 2. Устанавливаем зависимости через uv
uv sync

# 3. Создаём и заполняем .env (локальный запуск)
Copy-Item .env.example .env

# 4. Применяем миграции
uv run python manage.py migrate

# 5. Заполняем демо-данными
uv run python manage.py seed_demo

# 6. Запускаем сервер
uv run python manage.py runserver
```

## Примеры работы

Демо-аккаунты (после `seed_demo`):

| Роль | E-mail | Пароль |
|---|---|---|
| Администратор (`/admin/`) | `admin@selfstorage.ru` | `admin12345` |
| Пользователь (кабинет Екатерины, `my-rent`) | `ekatyusha89@yandex.ru` | `111111111` |

Живой сайт: [https://selfstorage.kislyakov.pro](https://selfstorage.kislyakov.pro)

## Документация

- [CONVENTIONS.md](CONVENTIONS.md) — договорённости проекта (URL, сигналы, переменные шаблонов)
- [docs/deployment.md](docs/deployment.md) — деплой, переменные окружения
- [docs/utm.md](docs/utm.md) — UTM-метки и источники трафика
- [docs/qr-access.md](docs/qr-access.md) — QR-доступ и статус бокса
- [docs/notifications.md](docs/notifications.md) — напоминания и просрочки (systemd)

## Лицензия

MIT



