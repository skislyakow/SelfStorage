from datetime import date

from django.contrib import admin
from django.template.defaultfilters import urlencode
from django.urls import reverse
from django.utils.html import format_html

from .models import RentalOrder, DeliveryRequest


@admin.register(DeliveryRequest)
class DeliveryRequestAdmin(admin.ModelAdmin):
    list_display = (
        "order_link",
        "warehouse",
        "box",
        "client_address_link",
        "phone_link",
        "status",
        "rejection_reason_short",
    )
    list_filter = ("status",)
    search_fields = ("client_address", "phone", "order__user__email", "order__user__phone")
    readonly_fields = ("warehouse", "box")
    autocomplete_fields = ("order",)
    list_select_related = ("order__box__warehouse", "order__user")

    @admin.display(description="Заказ", ordering="order__pk")
    def order_link(self, obj):
        url = reverse("admin:rentals_rentalorder_change", args=[obj.order_id])
        return format_html('<a href="{}">#{}</a>', url, obj.order_id)

    @admin.display(description="Склад (откуда)")
    def warehouse(self, obj):
        return obj.order.box.warehouse

    @admin.display(description="Бокс")
    def box(self, obj):
        return obj.order.box.number

    @admin.display(description="Куда ехать")
    def client_address_link(self, obj):
        if not obj.client_address:
            return "—"
        link = f"https://yandex.ru/maps/?text={urlencode(obj.client_address)}"
        return format_html('<a href="{}" target="_blank">{}</a>', link, obj.client_address)

    @admin.display(description="Телефон")
    def phone_link(self, obj):
        if not obj.phone:
            return "—"
        return format_html('<a href="tel:{}">{}</a>', obj.phone, obj.phone)

    @admin.display(description="Причина отказа")
    def rejection_reason_short(self, obj):
        return obj.rejection_reason[:40] or "—"

    actions = ("mark_in_progress", "mark_done", "mark_rejected")

    @admin.action(description="Отметить «В пути»")
    def mark_in_progress(self, request, queryset):
        updated = queryset.update(status="in_progress")
        self.message_user(request, f"Переведено «В пути»: {updated}")

    @admin.action(description="Отметить «Выполнена»")
    def mark_done(self, request, queryset):
        updated = queryset.update(status="done")
        self.message_user(request, f"Отмечено «Выполнена»: {updated}")

    @admin.action(description="Отклонить")
    def mark_rejected(self, request, queryset):
        updated = queryset.update(status="rejected")
        self.message_user(request, f"Отклонено: {updated}")


class OverdueCallFilter(admin.SimpleListFilter):
    title = "нужно позвонить"
    parameter_name = "need_call"

    def lookups(self, request, model_admin):
        return (("yes", "Просроченные и продлённые"),)

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(status__in=["overdue", "extended_6m"])
        return queryset


@admin.register(RentalOrder)
class RentalOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "box_info", "status", "end_date", "days_overdue")
    list_filter = ("status", OverdueCallFilter)
    search_fields = ("user__email", "user__phone", "box__number")
    list_select_related = ("user", "box__warehouse")

    @admin.display(description="Клиент", ordering="user__email")
    def client(self, obj):
        phone = obj.user.phone
        return format_html(
            "{}<br><a href=\"tel:{}\">{}</a>", obj.user.email, phone, phone
        )

    @admin.display(description="Бокс", ordering="box__number")
    def box_info(self, obj):
        return format_html("{} — бокс {}", obj.box.warehouse, obj.box.number)

    @admin.display(description="Дней просрочено")
    def days_overdue(self, obj):
        if obj.status not in ("overdue", "extended_6m"):
            return "—"
        return (date.today() - obj.end_date).days
