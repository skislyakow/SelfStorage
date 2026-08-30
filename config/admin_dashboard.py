import logging
from datetime import date

from django.contrib import admin
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from django.db.models import Count, Sum
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from apps.rentals.models import DeliveryRequest, RentalOrder

logger = logging.getLogger(__name__)

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

    rejected = (
        DeliveryRequest.objects.filter(status="rejected")
        .select_related("order__user", "order__box__warehouse")
        .order_by("pk")
    )

    today = date.today()
    overdue_rows = [
        {"order": order, "days": (today - order.end_date).days} for order in overdue
    ]

    raw_sources = (
        RentalOrder.objects.values("traffic_source")
        .annotate(orders=Count("id"), clients=Count("user", distinct=True), revenue=Sum("amount"))
        .order_by("-orders")
    )
    traffic_sources = []
    traffic_total = {"orders": 0, "clients": 0, "revenue": 0}
    for row in raw_sources:
        label = row["traffic_source"] or "(без метки)"
        revenue = row["revenue"] or 0
        traffic_sources.append(
            {"source": label, "orders": row["orders"], "clients": row["clients"], "revenue": revenue}
        )
        traffic_total["orders"] += row["orders"]
        traffic_total["clients"] += row["clients"]
        traffic_total["revenue"] += revenue

    context = dict(
        admin.site.each_context(request),
        title="Панель владельца",
        deliveries=deliveries,
        overdue=overdue_rows,
        rejected=rejected,
        deliveries_count=deliveries.count(),
        overdue_count=overdue.count(),
        rejected_count=rejected.count(),
        traffic_sources=traffic_sources,
        traffic_total=traffic_total,
    )
    return TemplateResponse(request, "admin/owner_dashboard.html", context)


@staff_member_required
def send_notifications_now(request, *args, **kwargs):
    if request.method == "POST":
        try:
            call_command("send_notifications")
            messages.success(request, "Уведомления об окончании аренды разосланы.")
        except Exception:
            logger.exception("Ручная рассылка уведомлений упала")
            messages.error(request, "Не удалось разослать уведомления.")
    return redirect("owner-dashboard")


# Сделать «Панель владельца» главной страницей админки (вход по /admin/)
admin.site.index = owner_dashboard  # type: ignore[method-assign]
