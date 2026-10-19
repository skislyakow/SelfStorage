from apps.notifications.models import Notification
from apps.users.models import User


def notify(user: User | None, text: str, url: str = "") -> Notification | None:
    """Создать уведомление в кабинете.

    Вызывается рядом с отправкой письма: письмо может не дойти (нет SMTP,
    нет адреса), а уведомление в кабинете остаётся. Возвращает созданное
    уведомление или None, если пользователя нет.
    """
    if user is None:
        return None
    return Notification.objects.create(user=user, text=text, url=url)
