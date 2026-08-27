from calendar import monthrange
from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from formtools.wizard.views import SessionWizardView

from apps.rentals.forms import BoxForm, ContactsForm, DeliveryForm, SummaryForm
from apps.rentals.models import DeliveryRequest, RentalOrder


def add_months(start, months):
    total = start.month - 1 + months
    year = start.year + total // 12
    month = total % 12 + 1
    return date(year, month, min(start.day, monthrange(year, month)[1]))


class OrderWizard(LoginRequiredMixin, SessionWizardView):
    form_list = [BoxForm, DeliveryForm, ContactsForm, SummaryForm]
    template_name = "rentals/wizard.html"

    def done(self, form_list, **kwargs):
        data = self.get_all_cleaned_data()
        months = int(data["rental_months"])
        start = date.today()
        end = add_months(start, months)

        order = RentalOrder.objects.create(
            user=self.request.user,
            box=data["box"],
            start_date=start,
            end_date=end,
            items_text="",
            status="awaiting_payment",
            amount=data["box"].price_per_month * months,
        )

        if data["delivery_type"] in ("delivery", "measure"):
            DeliveryRequest.objects.create(
                order=order,
                client_address=data.get("address", ""),
                phone=data["phone"],
                status="new",
            )

        user = self.request.user
        user.first_name = data.get("first_name", "")
        user.phone = data["phone"]
        user.pd_consent_date = date.today()
        user.save()

        return redirect("warehouse_list")
