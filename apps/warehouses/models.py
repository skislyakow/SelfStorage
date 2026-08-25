from django.db import models


class Warehouse(models.Model):
    city = models.CharField("Город", max_length=100)
    address = models.CharField("Адрес", max_length=255)
    photo = models.ImageField("Фото", upload_to="warehouses/", blank=True, null=True)
    temperature = models.CharField("Температура", max_length=50, blank=True, default="")
    ceiling_height = models.DecimalField("Высота потолков, м", max_digits=5, decimal_places=2, null=True, blank=True)
    description = models.TextField("Описание", blank=True, default="")
    contacts = models.CharField("Контакты", max_length=255, blank=True, default="")

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склады"

    def __str__(self):
        return f"{self.city}, {self.address}"


class Box(models.Model):
    STATUS_CHOICES = [
        ("free", "Свободен"),
        ("reserved", "Зарезервирован"),
        ("occupied", "Занят"),
    ]
    warehouse = models.ForeignKey("warehouses.Warehouse", on_delete=models.CASCADE, related_name="boxes", verbose_name="Склад")
    number = models.CharField("Номер", max_length=20)
    floor = models.PositiveIntegerField("Этаж", default=1)
    area = models.DecimalField("Площадь, м²", max_digits=6, decimal_places=2)
    length = models.DecimalField("Длина, м", max_digits=6, decimal_places=2, null=True, blank=True)
    width = models.DecimalField("Ширина, м", max_digits=6, decimal_places=2, null=True, blank=True)
    height = models.DecimalField("Высота, м", max_digits=6, decimal_places=2, null=True, blank=True)
    price_per_month = models.DecimalField("Цена в месяц, ₽", max_digits=10, decimal_places=2)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default="free")

    class Meta:
        verbose_name = "Бокс"
        verbose_name_plural = "Боксы"

    def __str__(self):
        return f"Бокс {self.number} ({self.warehouse})"
