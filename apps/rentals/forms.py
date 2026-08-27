from django import forms

from apps.warehouses.models import Box

MONTHS = [
    (1, "1 месяц"),
    (3, "3 месяца"),
    (6, "6 месяцев"),
    (12, "12 месяцев"),
]
DELIVERY_TYPES = [
    ("self", "Самопривоз"),
    ("delivery", "Доставка"),
    ("measure", "Замерим сами"),
]


class BoxForm(forms.Form):
    box = forms.ModelChoiceField(queryset=Box.objects.all(), label="Бокс")
    rental_months = forms.ChoiceField(choices=MONTHS, initial=1, label="Срок аренды, мес.")


class DeliveryForm(forms.Form):
    delivery_type = forms.ChoiceField(
        choices=DELIVERY_TYPES, widget=forms.RadioSelect, label="Способ получения"
    )
    address = forms.CharField(required=False, label="Адрес доставки")
    phone = forms.CharField(label="Телефон")


class ContactsForm(forms.Form):
    first_name = forms.CharField(label="Имя")
    phone = forms.CharField(label="Телефон")
    pd_consent = forms.BooleanField(label="Согласие на обработку персональных данных")


class SummaryForm(forms.Form):
    pass
