import logging
from datetime import date
from urllib.parse import urlencode

from django import forms
from django.contrib import admin, messages
from django.contrib.admin.views.decorators import staff_member_required
from django.core.management import call_command
from django.db.models import Count, Sum
from django.shortcuts import redirect
from django.template.response import TemplateResponse

from apps.rentals.models import DeliveryRequest, RentalOrder

logger = logging.getLogger(__name__)

NEED_CALL_STATUSES = ("overdue", "extended_6m")
DELIVERY_ACTIVE_STATUSES = ("new", "in_progress")

TARGET_CHOICES = (
    ("/", "Главная"),
    ("/warehouses/", "Каталог складов"),
    ("/rentals/wizard/", "Оформление аренды (визард)"),
    ("custom", "Своя страница"),
)
SOURCE_SUGGESTIONS = (
    "vk",
    "telegram",
    "google",
    "yandex",
    "direct",
    "facebook",
    "instagram",
    "email",
    "whatsapp",
)
MEDIUM_SUGGESTIONS = ("social", "cpc", "email", "banner", "messengers")


class UtmBuilderForm(forms.Form):
    target = forms.ChoiceField(choices=TARGET_CHOICES, label="Целевая страница")
    custom_path = forms.CharField(
        required=False,
        max_length=200,
        label="Путь (для «Своя страница»)",
        widget=forms.TextInput(attrs={"placeholder": "/faq/"}),
    )
    source = forms.CharField(
        max_length=100,
        label="utm_source — источник",
        widget=forms.TextInput(attrs={"list": "utm-source-list", "placeholder": "vk"}),
    )
    medium = forms.CharField(
        required=False,
        max_length=100,
        label="utm_medium — канал",
        widget=forms.TextInput(
            attrs={"list": "utm-medium-list", "placeholder": "social"}
        ),
    )
    campaign = forms.CharField(
        required=False,
        max_length=100,
        label="utm_campaign — кампания/акция",
        widget=forms.TextInput(attrs={"placeholder": "vesna_2026"}),
    )
    content = forms.CharField(
        required=False,
        max_length=100,
        label="utm_content — вариант креатива",
    )

    def clean_custom_path(self):
        path = (self.cleaned_data.get("custom_path") or "").strip()
        if self.cleaned_data.get("target") == "custom":
            if not path.startswith("/") or "?" in path or "#" in path:
                raise forms.ValidationError(
                    "Укажите путь, начинающийся с «/», без «?» и «#»."
                )
        return path


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
        .annotate(
            orders=Count("id"),
            clients=Count("user", distinct=True),
            revenue=Sum("amount"),
        )
        .order_by("-orders")
    )
    traffic_sources = []
    traffic_total = {"orders": 0, "clients": 0, "revenue": 0}
    for row in raw_sources:
        label = row["traffic_source"] or "(без метки)"
        revenue = row["revenue"] or 0
        traffic_sources.append(
            {
                "source": label,
                "orders": row["orders"],
                "clients": row["clients"],
                "revenue": revenue,
            }
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


@staff_member_required
def utm_builder(request, *args, **kwargs):
    result = None
    if request.method == "POST":
        form = UtmBuilderForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            path = data["custom_path"] if data["target"] == "custom" else data["target"]
            params = {"utm_source": data["source"].strip()}
            for key, field in (
                ("utm_medium", "medium"),
                ("utm_campaign", "campaign"),
                ("utm_content", "content"),
            ):
                value = (data[field] or "").strip()
                if value:
                    params[key] = value
            result = request.build_absolute_uri(path) + "?" + urlencode(params)
    else:
        form = UtmBuilderForm()

    context = dict(
        admin.site.each_context(request),
        title="Конструктор UTM-ссылок",
        form=form,
        result=result,
        source_suggestions=SOURCE_SUGGESTIONS,
        medium_suggestions=MEDIUM_SUGGESTIONS,
    )
    return TemplateResponse(request, "admin/utm_builder.html", context)


admin.site.index = owner_dashboard  # type: ignore[method-assign]
