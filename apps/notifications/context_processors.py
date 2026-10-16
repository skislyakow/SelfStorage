from apps.notifications.models import Notification

RECENT_NOTIFICATIONS_LIMIT = 5


def notifications(request):
    """Данные для колокольчика в шапке (шаблон подключается везде).

    Для анонимных пользователей возвращает пустые значения, поэтому
    лишних запросов к БД нет.
    """
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return {"unread_notifications": 0, "recent_notifications": []}

    own = Notification.objects.filter(user=user)
    return {
        "unread_notifications": own.filter(is_read=False).count(),
        "recent_notifications": list(own[:RECENT_NOTIFICATIONS_LIMIT]),
    }
