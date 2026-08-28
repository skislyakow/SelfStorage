import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def send_notification(user, subject, message, fail_silently=True):
    """Отправка письма конкретному пользователю.

    Используется для уведомлений (приветствие при регистрации и т.п.).
    Возвращает False, если у пользователя нет email или отправка упала.
    Ошибки всегда логируются (видны в error.log), но при fail_silently=True
    они не ломают вызывающий код (например, регистрацию).
    """
    if not user or not getattr(user, "email", ""):
        return False
    try:
        return send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception("Failed to send notification to %s", user.email)
        if not fail_silently:
            raise
        return False
