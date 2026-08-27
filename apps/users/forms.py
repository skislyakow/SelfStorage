from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    personal_data_consent = forms.BooleanField(
        required=True,
        error_messages={
            'required': 'Для регистрации необходимо согласие на обработку персональных данных'
        },
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'personalDataConsent'
        })
    )
    class Meta:
        model = User
        fields = ('email', 'phone', 'password1', 'password2')


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'phone', 'is_active', 'is_superuser', 'pd_consent', 'password')
