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
    avatar_base64 = models.TextField("Logo (Base64)", null=True, blank=True)
    label_servico = models.CharField("Nome para Serviço (singular)", max_length=50, default="Serviço")
    label_servico_plural = models.CharField("Nome para Serviço (plural)", max_length=50, default="Serviços")
    label_profissional = models.CharField("Nome para Profissional (singular)", max_length=50, default="Profissional")
    label_profissional_plural = models.CharField("Nome para Profissional (plural)", max_length=50, default="Profissionais")
    slot_interval_minutes = models.PositiveIntegerField(
        "Intervalo entre horários (min)",
        default=15,
        choices=[(5, "5 minutos"), (10, "10 minutos"), (15, "15 minutos"), (20, "20 minutos"), (30, "30 minutos"), (45, "45 minutos"), (60, "60 minutos")],
        help_text="Define de quantos em quantos minutos os horários aparecem no agendamento público.",
    )
    # Novos campos para página de landing do tenant
    about_us = models.TextField("Sobre nós", blank=True, help_text="Descrição sobre o seu negócio/salão")
    address = models.CharField("Endereço", max_length=300, blank=True)
    neighborhood = models.CharField("Bairro", max_length=100, blank=True)
    city = models.CharField("Cidade", max_length=100, blank=True)
    state = models.CharField("Estado", max_length=2, blank=True)
    zip_code = models.CharField("CEP", max_length=10, blank=True)
    instagram_url = models.URLField("URL Instagram", blank=True)
    facebook_url = models.URLField("URL Facebook", blank=True)
    payment_methods = models.TextField("Formas de pagamento", blank=True, help_text="Separadas por vírgula: Ex: Dinheiro, Cartão de Crédito, Cartão de Débito, PIX")
    amenities = models.TextField("Comodidades", blank=True, help_text="Separadas por vírgula: Ex: WiFi, Estacionamento, Acessibilidade")
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


class BusinessHours(models.Model):
    """Horários de funcionamento do tenant."""
    
    DAYS_OF_WEEK = [
        (0, "Segunda-feira"),
        (1, "Terça-feira"),
        (2, "Quarta-feira"),
        (3, "Quinta-feira"),
        (4, "Sexta-feira"),
        (5, "Sábado"),
        (6, "Domingo"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="business_hours")
    day_of_week = models.IntegerField("Dia da semana", choices=DAYS_OF_WEEK)
    is_closed = models.BooleanField("Fechado", default=False)
    opening_time = models.TimeField("Horário de abertura", null=True, blank=True)
    closing_time = models.TimeField("Horário de fechamento", null=True, blank=True)

    class Meta:
        verbose_name = "Horário de funcionamento"
        verbose_name_plural = "Horários de funcionamento"
        unique_together = ("tenant", "day_of_week")
        ordering = ("day_of_week",)

    def __str__(self) -> str:
        day_name = dict(self.DAYS_OF_WEEK)[self.day_of_week]
        if self.is_closed:
            return f"{day_name} - FECHADO"
        return f"{day_name} - {self.opening_time.strftime('%H:%M')} - {self.closing_time.strftime('%H:%M')}"
