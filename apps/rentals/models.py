from django.conf import settings
from django.db import models


class RentalOrder(models.Model):
    STATUS_CHOICES = [
        ("awaiting_payment", "Ожидает оплаты"),
        ("active", "Активна"),
        ("overdue", "Просрочена"),
        ("extended_6m", "Продлена на 6 мес"),
        ("finished", "Завершена"),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders", verbose_name="Пользователь")
    box = models.ForeignKey("warehouses.Box", on_delete=models.CASCADE, related_name="orders", verbose_name="Бокс")
    start_date = models.DateField("Дата начала")
    end_date = models.DateField("Дата окончания")
    items_text = models.TextField("Список вещей", blank=True, default="")
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default="awaiting_payment")
    promo = models.ForeignKey("promotions.PromoCode", on_delete=models.SET_NULL, null=True, blank=True, related_name="orders", verbose_name="Промокод")
    amount = models.DecimalField("Сумма, ₽", max_digits=10, decimal_places=2, null=True, blank=True)
    traffic_source = models.CharField("Метка источника трафика", max_length=100, blank=True, default="")

    class Meta:
        verbose_name = "Заказ аренды"
        verbose_name_plural = "Заказы аренды"

    def __str__(self):
        return f"Заказ #{self.pk} — {self.user}"


class DeliveryRequest(models.Model):
    STATUS_CHOICES = [
        ("new", "Новая"),
        ("in_progress", "В пути"),
        ("done", "Выполнена"),
        ("rejected", "Отклонена"),
    ]
    order = models.OneToOneField("rentals.RentalOrder", on_delete=models.CASCADE, related_name="delivery", verbose_name="Заказ")
    client_address = models.CharField("Адрес клиента", max_length=255, blank=True, default="")
    phone = models.CharField("Телефон", max_length=20, blank=True, default="")
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default="new")
    rejection_reason = models.TextField("Причина отказа доставщика", blank=True, default="")

    class Meta:
        verbose_name = "Заявка на доставку"
        verbose_name_plural = "Заявки на доставку"

    def __str__(self):
        return f"Доставка для заказа #{self.order_id}"
