from django.contrib import admin

from .models import Warehouse, Box


@admin.register(Box)
class BoxAdmin(admin.ModelAdmin):
    list_display = ("warehouse", "number", "area", "price_per_month", "status")
    list_filter = ("status",)
    search_fields = ("number", "warehouse__city", "warehouse__address")


admin.site.register(Warehouse)
