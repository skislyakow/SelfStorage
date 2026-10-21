from apps.notifications.models import Notification
from apps.users.models import User


def notify(user: User | None, text: str, url: str = "") -> Notification | None:
    if user is None:
        return None
    return Notification.objects.create(user=user, text=text, url=url)
