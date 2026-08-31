from calendar import monthrange
from datetime import date
from typing import cast

from decimal import Decimal
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import DetailView, ListView
from formtools.wizard.views import SessionWizardView

from apps.promotions.models import PromoCode
from apps.rentals.forms import BoxForm, ContactsForm, DeliveryForm
from apps.rentals.models import DeliveryRequest, RentalOrder
from apps.warehouses.models import Box
from apps.users.models import User


def add_months(start, months):
    total = start.month - 1 + months
    year = start.year + total // 12
    month = total % 12 + 1
    return date(year, month, min(start.day, monthrange(year, month)[1]))


def calculate_amount(box, rental_months, start_date, promo):
    full_price = box.price_per_month
    if promo is None:
        return {
            "total": full_price * rental_months,
            "discounted_months": 0,
            "full_months": rental_months,
            "discounted_month_price": full_price,
            "full_month_price": full_price,
        }
    discount = promo.discount_percent / Decimal("100")
    discounted_price = (full_price * (Decimal("1") - discount)).quantize(Decimal("0.01"))
    discounted_months = 0
    full_months = 0
    total = Decimal("0")
    for i in range(rental_months):
        m_start = add_months(start_date, i)
        m_end = add_months(start_date, i + 1)
        if m_start <= promo.valid_to and m_end > promo.valid_from:
            total += discounted_price
            discounted_months += 1
        else:
            total += full_price
            full_months += 1
    return {
        "total": total,
        "discounted_months": discounted_months,
        "full_months": full_months,
        "discounted_month_price": discounted_price,
        "full_month_price": full_price,
    }


class OrderWizard(LoginRequiredMixin, SessionWizardView):
    form_list = [BoxForm, DeliveryForm, ContactsForm]
    template_name = "rentals/wizard.html"

    def get_form_initial(self, step):
        initial = super().get_form_initial(step)
        if step == "0":
            box_id = self.request.GET.get("box")
            if box_id:
                initial["box"] = box_id
        elif step == "2":
            user = self.request.user
            initial["first_name"] = user.first_name
            initial["phone"] = user.phone
        return initial

    def get_form(self, step=None, data=None, files=None):
        form = super().get_form(step, data, files)
        if step == "0":
            box_id = self.request.GET.get("box")
            if box_id:
                form.fields["box"].queryset = Box.objects.filter(pk=box_id, status="free")
        return form

    def done(self, form_list, **kwargs):
        data = self.get_all_cleaned_data()
        months = int(data["rental_months"])
        start = date.today()
        end = add_months(start, months)

        box = data["box"]
        promo = None
        promo_code = data.get("promo_code")
        if promo_code:
            today = timezone.localdate()
            promo = PromoCode.objects.filter(
                code__iexact=promo_code, valid_from__lte=today, valid_to__gte=today
            ).first()
        calc = calculate_amount(box, months, start, promo)
        order = RentalOrder.objects.create(
            user=self.request.user,
            box=box,
            start_date=start,
            end_date=end,
            items_text="",
            status="awaiting_payment",
            promo=promo,
            amount=calc["total"],
            traffic_source=self.request.session.get("traffic_source", ""),
        )
        box.status = "reserved"
        box.save()

        if data["delivery_type"] in ("delivery", "measure"):
            DeliveryRequest.objects.create(
                order=order,
                client_address=data.get("address", ""),
                phone=data["phone"],
                status="new",
            )

        user = cast(User, self.request.user)
        user.first_name = data.get("first_name", "")
        user.phone = data["phone"]
        user.save()

        return render(
            self.request,
            "rentals/order_reserved.html",
            {"order": order, "promo": promo, "calc": calc},
        )


class MyRentView(LoginRequiredMixin, ListView):
    template_name = "rentals/my_rent.html"
    context_object_name = "orders"

    def get_queryset(self):
        return (
            RentalOrder.objects.filter(user=self.request.user)
            .select_related("box", "box__warehouse", "delivery")
            .order_by("-start_date")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        error = self.request.session.pop("box_access_error", None)
        if error:
            context["box_access_error"] = error
        return context


class BoxAccessView(DetailView):
    """QR-доступ: переход по QR открывает бокс (заглушка логики).

    Доступно по ссылке/QR любому, у кого есть QR (семья, охрана). Открытие
    возможно только при активной аренде (срок не вышел).
    """
    model = RentalOrder
    template_name = "rentals/qr_access.html"
    context_object_name = "order"

    def get(self, request, *args, **kwargs):
        order = self.get_object()
        if order.status == "active" and order.access_status != "open":
            order.access_status = "open"
            order.save(update_fields=["access_status"])
        return super().get(request, *args, **kwargs)


def box_close(request, pk):
    """Закрыть бокс (заглушка логики): любой, кому доступен бокс."""
    order = get_object_or_404(RentalOrder, pk=pk)
    order.access_status = "closed"
    order.save(update_fields=["access_status"])
    if request.user.is_authenticated:
        return redirect("my_rent")
    return redirect("qr_access", pk=pk)
