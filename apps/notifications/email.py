from django.conf import settings
from django.core.mail import send_mail


def send_notification(user, subject, message, fail_silently=True):
    """Отправка письма конкретному пользователю.

    Используется для уведомлений (приветствие при регистрации и т.п.).
    Возвращает False, если у пользователя нет email.
    """
    if not user or not getattr(user, "email", ""):
        return False
    return send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=fail_silently,
    )
