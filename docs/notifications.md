# Уведомления (`send_notifications`)

Команда `python manage.py send_notifications` шлёт напоминания за 30/14/7/3 дня до окончания аренды (`status='active'`) и письма о просрочке (каждые 30 дней после перевода в `overdue`). Отправка устойчива к сбоям SMTP.

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
(Lokálně — в консоль при отсутствии SMTP.)
