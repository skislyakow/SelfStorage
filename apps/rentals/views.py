from calendar import monthrange
from datetime import date
from typing import cast

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from formtools.wizard.views import SessionWizardView

from apps.rentals.forms import BoxForm, ContactsForm, DeliveryForm
from apps.rentals.models import DeliveryRequest, RentalOrder
from apps.warehouses.models import Box
from apps.users.models import User


def add_months(start, months):
    total = start.month - 1 + months
    year = start.year + total // 12
    month = total % 12 + 1
    return date(year, month, min(start.day, monthrange(year, month)[1]))


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
        order = RentalOrder.objects.create(
            user=self.request.user,
            box=box,
            start_date=start,
            end_date=end,
            items_text="",
            status="awaiting_payment",
            amount=box.price_per_month * months,
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

        return render(self.request, "rentals/order_reserved.html", {"order": order})
