from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model com campos de telefone e preferencias regionais."""

    phone_number = models.CharField("Telefone", max_length=32, blank=True)
    locale = models.CharField("Idioma", max_length=10, default="pt-br")
    timezone = models.CharField("Fuso horario", max_length=64, default="America/Sao_Paulo")

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    @property
    def full_name(self) -> str:
        return self.get_full_name() or self.username

    def get_active_membership(self):
        from tenants.models import TenantMembership  # lazy import to avoid circular dependency

        return (
            TenantMembership.objects.filter(user=self, is_active=True, tenant__is_active=True)
            .select_related("tenant")
            .first()
        )
