from django import forms

from apps.warehouses.models import Box

INPUT_CLASS = "form-control border-8 py-3 px-5 border-0 fs_24 SelfStorage__bg_lightgrey"

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
    box = forms.ModelChoiceField(
        queryset=Box.objects.filter(status="free"),
        label="Бокс",
        widget=forms.Select(attrs={"class": INPUT_CLASS}),
    )
    rental_months = forms.ChoiceField(
        choices=MONTHS,
        initial=1,
        label="Срок аренды, мес.",
        widget=forms.Select(attrs={"class": INPUT_CLASS}),
    )


class DeliveryForm(forms.Form):
    delivery_type = forms.ChoiceField(
        choices=DELIVERY_TYPES,
        widget=forms.RadioSelect(attrs={"class": "form-check-input"}),
        label="Способ получения",
    )
    address = forms.CharField(
        required=False,
        label="Адрес доставки",
        widget=forms.TextInput(attrs={"class": INPUT_CLASS}),
    )


class ContactsForm(forms.Form):
    first_name = forms.CharField(
        label="Имя",
        widget=forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "Имя"}),
    )
    phone = forms.CharField(
        label="Телефон",
        widget=forms.TextInput(attrs={"class": INPUT_CLASS, "placeholder": "Телефон"}),
    )
