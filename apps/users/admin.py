from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    list_display = ("email", "phone", "is_active", "is_superuser")
    list_filter = ("is_active", "is_superuser")
    search_fields = ("email", "phone")
    ordering = ("email",)
    readonly_fields = ("pd_consent",)

    fieldsets = (
        ("Основное", {"fields": ("email", "phone")}),
        ("Пароль", {"fields": ("password",)}),
        ("Доступ", {"fields": ("is_active", "is_superuser")}),
        ("Согласие ПД", {"fields": ("pd_consent",)}),
    )
    add_fieldsets = (
        ("Основное", {"fields": ("email", "phone", "password1", "password2")}),
    )
