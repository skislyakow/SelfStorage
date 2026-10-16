# Уведомления

## In-app уведомления (колокольчик в шапке)

Модель `apps.notifications.models.Notification` хранит уведомления в личном кабинете: пользователь, текст, ссылка `url`, флаг `is_read`, дата создания. 

- Колокольчик в шапке показывает счётчик непрочитанных (`unread_notifications`) и 5 последних (`recent_notifications`) — реализовано через контекст-процессор `apps.notifications.context_processors.notifications`.
- Страница `/notifications/` (`notifications:list`) — список всех уведомлений пользователя.
- Кнопка «Отметить все прочитанными» (`notifications:read_all`, POST) помечает только свои уведомления.
- Создаются при оплате (`_mark_paid`), а также в команде `send_notifications` для напоминаний и просрочек.

## Email-уведомления (`send_notifications`)

Команда `python manage.py send_notifications` шлёт напоминания за 30/14/7/3 дня до окончания аренды (`status='active'`) и письма о просрочке (каждые 30 дней после перевода в `overdue`). Отправка устойчива к сбоям SMTP. Отдельно создаются in-app уведомления в кабинете.

## Автозапуск (systemd timer)
Юниты `selfstorage-notify.service` и `selfstorage-notify.timer` — копируются `deploy.sh` в `/etc/systemd/system/`, включаются автоматически. Проект: `/opt/selftorage`, venv `/opt/selftorage/.venv`, лог `/var/log/selftorage/send_notifications.log`.

## Проверка
```bash
systemctl list-timers selfstorage-notify.timer
journalctl -u selfstorage-notify.service -n 50
cat /var/log/selftorage/send_notifications.log
```

## Быстрая проверка вручную
На сервере:
```bash
cd /opt/selftorage
/opt/selftorage/.venv/bin/python manage.py send_notifications
```
(Локально — в консоль при отсутствии SMTP.)