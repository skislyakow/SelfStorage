from django.conf import settings
from django.db import models


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Пользователь",
    )
    text = models.TextField("Текст")
    url = models.CharField(
        "Ссылка",
        max_length=200,
        blank=True,
        default="",
        help_text="Куда ведёт уведомление (например, личный кабинет)",
    )
    is_read = models.BooleanField("Прочитано", default=False)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомления"
        ordering = ("-created_at",)
        indexes = (models.Index(fields=("user", "is_read")),)

    def __str__(self):
        return f"Уведомление для {self.user}: {self.text[:40]}"
