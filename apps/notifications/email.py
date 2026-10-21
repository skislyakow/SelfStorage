import logging

from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


def greeting(user):
    first_name = getattr(user, "first_name", "") or ""
    return f"Привет {first_name}," if first_name else "Уважаемый клиент,"


def plural_days(n):
    n = abs(int(n)) % 100
    if 10 <= n <= 20:
        return "дней"
    n %= 10
    if n == 1:
        return "день"
    if 2 <= n <= 4:
        return "дня"
    return "дней"


def send_notification(user, subject, message, fail_silently=True):
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
