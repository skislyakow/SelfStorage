from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from apps.notifications.models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    """Список уведомлений пользователя (только свои)."""

    template_name = "notifications/list.html"
    context_object_name = "notifications"

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user)


@login_required
@require_POST
def mark_all_read(request):
    """Отметить все уведомления пользователя прочитанными."""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    return redirect("notifications:list")
