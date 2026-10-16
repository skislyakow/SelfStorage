from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "short_text", "is_read", "created_at")
    list_filter = ("is_read", "created_at")
    search_fields = ("user__email", "text")
    list_select_related = ("user",)
    actions = ("mark_read", "mark_unread")

    @admin.display(description="Текст")
    def short_text(self, obj):
        return obj.text[:60]

    @admin.action(description="Отметить прочитанными")
    def mark_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"Отмечено прочитанными: {updated}")

    @admin.action(description="Отметить непрочитанными")
    def mark_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f"Отмечено непрочитанными: {updated}")
