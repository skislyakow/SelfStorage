from django.db import models


class PromoCode(models.Model):
    code = models.CharField("Код", max_length=50, unique=True)
    discount_percent = models.DecimalField("Процент скидки", max_digits=5, decimal_places=2)
    valid_from = models.DateField("Действует с")
    valid_to = models.DateField("Действует по")

    class Meta:
        verbose_name = "Промокод"
        verbose_name_plural = "Промокоды"

    def __str__(self):
        return self.code
