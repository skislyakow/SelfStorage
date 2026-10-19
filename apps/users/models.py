from typing import ClassVar

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra):
        extra.setdefault("is_staff", False)
        extra.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra)

    def create_superuser(self, email, password=None, **extra):
        extra.setdefault("is_staff", True)
        extra.setdefault("is_superuser", True)
        return self._create_user(email, password, **extra)


class User(AbstractUser):
    # Вход по email: поле username убрано, поэтому тип из AbstractUser не подходит.
    username = None  # type: ignore[assignment]
    email = models.EmailField("Email", unique=True)
    phone = models.CharField("Телефон", max_length=20, blank=True, default="")
    pd_consent = models.BooleanField("Согласие на обработку ПД", default=False)

    # Свой менеджер вместо django.contrib.auth.models.UserManager.
    # Аннотация обязательна: без неё Pylance берёт ClassVar[UserManager[Self]]
    # из стабов AbstractUser и требует username в create_user().
    objects: ClassVar[UserManager] = UserManager()  # type: ignore[assignment,misc]
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: ClassVar[list[str]] = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email
