from django.conf import settings
from django.db import models

from tenants.models import Tenant


class Service(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=120, verbose_name="Servico")
    description = models.TextField(blank=True, verbose_name="Descricao")
    duration_minutes = models.PositiveIntegerField(default=30, verbose_name="Duracao (min)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preco")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    professionals = models.ManyToManyField(
        "Professional",
        through="ProfessionalService",
        related_name="services",
        verbose_name="Profissionais",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Servico"
        verbose_name_plural = "Servicos"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name

    def duration_for(self, professional=None) -> int:
        if professional:
            link = self.professional_links.filter(professional=professional).first()
            if link and link.duration_minutes:
                return link.duration_minutes
        return self.duration_minutes

    def price_for(self, professional=None):
        if professional:
            link = self.professional_links.filter(professional=professional).first()
            if link and link.price is not None:
                return link.price
        return self.price


class Professional(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="professionals")
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="professional_profile",
        null=True,
        blank=True,
        verbose_name="Usuario",
    )
    display_name = models.CharField(max_length=120, verbose_name="Nome de exibicao")
    test_field = models.CharField(max_length=50, blank=True, null=True, verbose_name="Campo de Teste")
    bio = models.TextField(blank=True, verbose_name="Bio")
    color = models.CharField(max_length=7, default="#2563EB", verbose_name="Cor na agenda")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profissional"
        verbose_name_plural = "Profissionais"
        ordering = ("display_name",)

    def __str__(self) -> str:
        return self.display_name or (self.user.get_full_name() if self.user else "")


class ProfessionalService(models.Model):
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name="service_links")
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name="professional_links")
    duration_minutes = models.PositiveIntegerField(null=True, blank=True, verbose_name="Duracao customizada (min)")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Preco customizado")

    class Meta:
        verbose_name = "Servico por profissional"
        verbose_name_plural = "Servicos por profissional"
        unique_together = ("professional", "service")


class AvailabilityRule(models.Model):
    WEEKDAYS = [
        (0, "Segunda"),
        (1, "Terca"),
        (2, "Quarta"),
        (3, "Quinta"),
        (4, "Sexta"),
        (5, "Sabado"),
        (6, "Domingo"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="availability_rules")
    professional = models.ForeignKey(
        Professional, on_delete=models.CASCADE, related_name="availability_rules", null=True, blank=True
    )
    weekday = models.IntegerField(choices=WEEKDAYS, verbose_name="Dia da semana")
    start_time = models.TimeField(verbose_name="Inicio")
    end_time = models.TimeField(verbose_name="Fim")
    break_start = models.TimeField(null=True, blank=True, verbose_name="Intervalo inicio")
    break_end = models.TimeField(null=True, blank=True, verbose_name="Intervalo fim")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")

    class Meta:
        verbose_name = "Disponibilidade"
        verbose_name_plural = "Disponibilidades"
        ordering = ("weekday", "start_time")


class TimeOff(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="time_offs")
    professional = models.ForeignKey(
        Professional, on_delete=models.CASCADE, related_name="time_offs", null=True, blank=True
    )
    name = models.CharField(max_length=120, verbose_name="Motivo")
    start = models.DateTimeField(verbose_name="Inicio")
    end = models.DateTimeField(verbose_name="Fim")

    class Meta:
        verbose_name = "Folga/Indisponibilidade"
        verbose_name_plural = "Folgas/Indisponibilidades"
        ordering = ("-start",)


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pendente"
        CONFIRMED = "confirmed", "Confirmado"
        CANCELLED = "cancelled", "Cancelado"
        NO_SHOW = "no_show", "Nao compareceu"
        COMPLETED = "completed", "Concluido"

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="bookings")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="bookings")
    professional = models.ForeignKey(Professional, on_delete=models.PROTECT, related_name="bookings")
    customer_name = models.CharField(max_length=150, verbose_name="Cliente")
    customer_phone = models.CharField(max_length=32, verbose_name="Telefone")
    customer_email = models.EmailField(blank=True, verbose_name="E-mail")
    scheduled_for = models.DateTimeField(verbose_name="Agendado para")
    duration_minutes = models.PositiveIntegerField(default=30, verbose_name="Duracao (min)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preco")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="Status")
    notes = models.TextField(blank=True, verbose_name="Observacoes")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="created_bookings",
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Agendamento"
        verbose_name_plural = "Agendamentos"
        ordering = ("-scheduled_for",)
        indexes = [
            models.Index(fields=("tenant", "scheduled_for")),
            models.Index(fields=("tenant", "professional", "scheduled_for")),
        ]

    def __str__(self) -> str:
        return f"{self.customer_name} - {self.service.name} ({self.scheduled_for:%d/%m %H:%M})"
