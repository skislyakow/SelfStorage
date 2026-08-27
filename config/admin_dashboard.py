from datetime import date

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse

from apps.rentals.models import DeliveryRequest, RentalOrder

NEED_CALL_STATUSES = ("overdue", "extended_6m")
DELIVERY_ACTIVE_STATUSES = ("new", "in_progress")


@staff_member_required
def owner_dashboard(request, *args, **kwargs):
    deliveries = (
        DeliveryRequest.objects.filter(status__in=DELIVERY_ACTIVE_STATUSES)
        .select_related("order__user", "order__box__warehouse")
        .order_by("status", "pk")
    )
    overdue = (
        RentalOrder.objects.filter(status__in=NEED_CALL_STATUSES)
        .select_related("user", "box__warehouse")
        .order_by("end_date")
    )

    today = date.today()
    overdue_rows = [
        {"order": order, "days": (today - order.end_date).days} for order in overdue
    ]

    context = dict(
        admin.site.each_context(request),
        title="Панель владельца",
        deliveries=deliveries,
        overdue=overdue_rows,
        deliveries_count=deliveries.count(),
        overdue_count=overdue.count(),
    )
    return TemplateResponse(request, "admin/owner_dashboard.html", context)


# Сделать «Панель владельца» главной страницей админки (вход по /admin/)
admin.site.index = owner_dashboard  # type: ignore[method-assign]
