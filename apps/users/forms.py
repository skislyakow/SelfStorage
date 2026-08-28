from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    AuthenticationForm,
    PasswordResetForm,
    SetPasswordForm,
)
from .models import User


class CustomUserCreationForm(UserCreationForm):
    personal_data_consent = forms.BooleanField(
        label='Согласие на обработку персональных данных',
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
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
            if name == 'username':
                field.label = 'Email'


class CustomPasswordResetForm(PasswordResetForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'phone', 'is_active', 'is_superuser', 'pd_consent', 'password')
