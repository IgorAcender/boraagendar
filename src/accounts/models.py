from __future__ import annotations

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """User manager that stores credentials by e-mail address."""

    use_in_migrations = True

    def _create_user(self, email: str, password: str | None, **extra_fields):
        if not email:
            raise ValueError("O e-mail deve ser informado.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser precisa ter is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser precisa ter is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model with e-mail authentication only."""

    username = None
    email = models.EmailField("E-mail", unique=True)
    phone_number = models.CharField("Telefone", max_length=32, blank=True)
    locale = models.CharField("Idioma", max_length=10, default="pt-br")
    timezone = models.CharField("Fuso horario", max_length=64, default="America/Sao_Paulo")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    objects = UserManager()

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    @property
    def full_name(self) -> str:
        return self.get_full_name() or self.email

    def get_active_membership(self):
        from tenants.models import TenantMembership  # lazy import to avoid circular dependency

        return (
            TenantMembership.objects.filter(user=self, is_active=True, tenant__is_active=True)
            .select_related("tenant")
            .first()
        )
