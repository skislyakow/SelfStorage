from django.db import models


class Payment(models.Model):
    STATUS_CHOICES = [
        ("pending", "Ожидает"),
        ("succeeded", "Успешно"),
        ("canceled", "Отменён"),
    ]
    order = models.OneToOneField("rentals.RentalOrder", on_delete=models.CASCADE, related_name="payment", verbose_name="Заказ")
    yookassa_id = models.CharField("Идентификатор платежа ЮKassa", max_length=100, blank=True, default="")
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default="pending")
    amount = models.DecimalField("Сумма, ₽", max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        return f"Платёж {self.yookassa_id} ({self.status})"
