from django.conf import settings
from django.db import models


class Tenant(models.Model):
    """Empresa (tenant) do sistema multi-cliente."""

    name = models.CharField("Nome", max_length=150)
    slug = models.SlugField("Slug", unique=True)
    document = models.CharField("CNPJ/CPF", max_length=32, blank=True)
    phone_number = models.CharField("Telefone", max_length=32, blank=True)
    whatsapp_number = models.CharField("WhatsApp", max_length=32, blank=True)
    email = models.EmailField("E-mail", blank=True)
    timezone = models.CharField("Fuso horario", max_length=64, default="America/Sao_Paulo")
    color_primary = models.CharField("Cor primaria", max_length=7, default="#D97706")
    color_secondary = models.CharField("Cor secundaria", max_length=7, default="#1F2937")
    avatar = models.ImageField("Logo", upload_to="tenants/logo/", blank=True)
    # Labels personalizáveis
    label_professional_singular = models.CharField("Label Profissional (singular)", max_length=50, default="Profissional")
    label_professional_plural = models.CharField("Label Profissional (plural)", max_length=50, default="Profissionais")
    label_service_singular = models.CharField("Label Serviço (singular)", max_length=50, default="Serviço")
    label_service_plural = models.CharField("Label Serviço (plural)", max_length=50, default="Serviços")
    is_active = models.BooleanField("Ativo", default=True)
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"

    def __str__(self) -> str:
        return self.name


class TenantMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Dono(a)"
        MANAGER = "manager", "Recepcao"
        PROFESSIONAL = "professional", "Profissional"
        STAFF = "staff", "Equipe"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tenant_memberships")
    role = models.CharField("Papel", max_length=32, choices=Role.choices, default=Role.MANAGER)
    is_active = models.BooleanField("Ativo", default=True)
    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="tenant_invites",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)

    class Meta:
        verbose_name = "Vinculo de usuario"
        verbose_name_plural = "Vinculos de usuarios"
        unique_together = ("tenant", "user")

    def __str__(self) -> str:
        return f"{self.user.full_name} @ {self.tenant.name}"
