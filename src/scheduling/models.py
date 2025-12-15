from django.conf import settings
from django.db import models

from tenants.models import Tenant


class Service(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="services")
    name = models.CharField(max_length=120, verbose_name="Servico")
    description = models.TextField(blank=True, verbose_name="Descricao")
    category = models.CharField(max_length=120, blank=True, verbose_name="Categoria")
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
    photo = models.ImageField(upload_to='professionals/', null=True, blank=True, verbose_name="Foto")
    photo_base64 = models.TextField(null=True, blank=True, verbose_name="Foto (Base64)")
    bio = models.TextField(blank=True, verbose_name="Bio")
    color = models.CharField(max_length=7, default="#2563EB", verbose_name="Cor na agenda")
    is_active = models.BooleanField(default=True, verbose_name="Ativo")
    allow_auto_assign = models.BooleanField(
        default=True,
        verbose_name="Disponível para seleção automática",
        help_text="Quando marcado, este profissional pode ser escolhido automaticamente na opção Sem preferência.",
    )
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
    professional = models.ForeignKey(
        Professional, on_delete=models.PROTECT, related_name="bookings", null=True, blank=True
    )
    customer_name = models.CharField(max_length=150, verbose_name="Cliente")
    customer_phone = models.CharField(max_length=32, verbose_name="Telefone")
    customer_email = models.EmailField(blank=True, verbose_name="E-mail")
    scheduled_for = models.DateTimeField(verbose_name="Agendado para")
    duration_minutes = models.PositiveIntegerField(default=30, verbose_name="Duracao (min)")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preco")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="Status")
    notes = models.TextField(blank=True, verbose_name="Observacoes")
    metadata = models.JSONField(default=dict, blank=True, verbose_name="Metadados")
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


class BookingPolicy(models.Model):
    """Políticas de cancelamento e reagendamento por tenant"""
    tenant = models.OneToOneField(
        Tenant, 
        on_delete=models.CASCADE, 
        related_name='booking_policy',
        verbose_name="Tenant"
    )
    
    # CANCELAMENTO
    allow_cancellation = models.BooleanField(
        default=True,
        verbose_name="Permitir cancelamento",
        help_text="Permite que clientes cancelem agendamentos"
    )
    min_cancellation_hours = models.PositiveIntegerField(
        default=4,
        verbose_name="Prazo mínimo para cancelar (horas)",
        help_text="Horas de antecedência necessárias para cancelar"
    )
    max_cancellations = models.PositiveIntegerField(
        default=3,
        verbose_name="Máximo de cancelamentos permitidos",
        help_text="Quantidade máxima de cancelamentos no período especificado"
    )
    cancellation_period_days = models.PositiveIntegerField(
        default=30,
        verbose_name="Período de contagem (dias)",
        help_text="Período em dias para contar os cancelamentos"
    )
    require_cancellation_reason = models.BooleanField(
        default=False,
        verbose_name="Exigir motivo ao cancelar",
        help_text="Cliente deve informar motivo do cancelamento"
    )
    
    # REAGENDAMENTO
    allow_rescheduling = models.BooleanField(
        default=True,
        verbose_name="Permitir reagendamento",
        help_text="Permite que clientes reagendem agendamentos"
    )
    min_reschedule_hours = models.PositiveIntegerField(
        default=2,
        verbose_name="Prazo mínimo para reagendar (horas)",
        help_text="Horas de antecedência necessárias para reagendar"
    )
    max_reschedules_per_booking = models.PositiveIntegerField(
        default=2,
        verbose_name="Máximo de reagendamentos por agendamento",
        help_text="Quantas vezes o mesmo agendamento pode ser reagendado"
    )
    reschedule_window_days = models.PositiveIntegerField(
        default=60,
        verbose_name="Janela para reagendar (dias)",
        help_text="Até quantos dias no futuro pode reagendar"
    )
    
    # PENALIDADES
    block_on_limit_reached = models.BooleanField(
        default=False,
        verbose_name="Bloquear ao atingir limite",
        help_text="Bloqueia novos agendamentos ao atingir limite de cancelamentos"
    )
    block_duration_days = models.PositiveIntegerField(
        default=15,
        verbose_name="Duração do bloqueio (dias)",
        help_text="Por quantos dias o cliente fica bloqueado"
    )
    notify_manager_on_abuse = models.BooleanField(
        default=True,
        verbose_name="Notificar gerente sobre abusos",
        help_text="Envia notificação quando cliente atinge limite"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Política de Agendamento"
        verbose_name_plural = "Políticas de Agendamento"
    
    def __str__(self) -> str:
        return f"Política - {self.tenant.name}"
    
    @classmethod
    def get_or_create_for_tenant(cls, tenant):
        """Retorna a política do tenant, criando uma com valores padrão se não existir"""
        policy, created = cls.objects.get_or_create(tenant=tenant)
        return policy


class Target(models.Model):
    """Metas e targets financeiros do negócio"""
    
    PERIOD_CHOICES = [
        ('daily', 'Diário'),
        ('weekly', 'Semanal'),
        ('monthly', 'Mensal'),
        ('yearly', 'Anual'),
    ]
    
    TARGET_TYPE_CHOICES = [
        ('revenue', 'Receita'),
        ('bookings', 'Agendamentos'),
        ('average_ticket', 'Ticket Médio'),
        ('confirmed_rate', 'Taxa de Confirmação'),
    ]
    
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="targets")
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES, default='monthly')
    target_type = models.CharField(max_length=20, choices=TARGET_TYPE_CHOICES)
    target_value = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Meta"
        verbose_name_plural = "Metas"
        unique_together = ('tenant', 'period', 'target_type')
        ordering = ('period', 'target_type')
    
    def __str__(self) -> str:
        return f"{self.get_target_type_display()} - {self.get_period_display()}: {self.target_value}"
    
    def get_period_label(self) -> str:
        """Retorna o rótulo do período"""
        return dict(self.PERIOD_CHOICES).get(self.period, '')
    
    def get_target_type_label(self) -> str:
        """Retorna o rótulo do tipo de target"""
        return dict(self.TARGET_TYPE_CHOICES).get(self.target_type, '')


# ============================================================================
# Evolution API - Gerenciamento de múltiplas instâncias WhatsApp
# ============================================================================

class EvolutionAPI(models.Model):
    """
    Representa uma instância do Evolution API
    Cada instância pode conter até 50 WhatsApps para MVP
    """
    
    instance_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="ID da Instância",
        help_text="Ex: evolution-1, evolution-2"
    )
    
    url = models.URLField(
        verbose_name="URL da API",
        help_text="Ex: https://seu-dominio.com"
    )
    
    api_key = models.CharField(
        max_length=500,
        verbose_name="API Key",
        help_text="Chave de autenticação da instância"
    )
    
    capacity = models.IntegerField(
        default=50,
        verbose_name="Capacidade (WhatsApps)",
        help_text="Máximo recomendado: 50 (conservador: 20, agressivo: 100)"
    )
    
    priority = models.IntegerField(
        default=10,
        verbose_name="Prioridade",
        help_text="Maior número = maior prioridade no load balancing (0-10)"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativa",
        help_text="Se desativada, não será usada para enviar mensagens"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Evolution API"
        verbose_name_plural = "Evolution APIs"
        ordering = ["-priority", "instance_id"]
    
    def __str__(self):
        status = "✅" if self.is_active else "❌"
        count = self.whatsapp_instances.count()
        return f"{status} {self.instance_id} ({count}/{self.capacity})"
    
    @property
    def current_usage(self):
        """Retorna quantas instâncias estão usando"""
        return self.whatsapp_instances.count()
    
    @property
    def has_capacity(self):
        """Verifica se ainda pode adicionar WhatsApps"""
        return self.current_usage < self.capacity
    
    @property
    def available_slots(self):
        """Retorna quantos WhatsApps ainda podem ser adicionados"""
        return max(0, self.capacity - self.current_usage)
    
    def get_usage_percentage(self):
        """Retorna o percentual de uso (0-100)"""
        if self.capacity == 0:
            return 0
        return int((self.current_usage / self.capacity) * 100)


class WhatsAppInstance(models.Model):
    """
    Representa um WhatsApp individual dentro de uma instância Evolution API
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('connecting', 'Conectando'),
        ('connected', 'Conectado'),
        ('disconnected', 'Desconectado'),
        ('error', 'Erro'),
    ]
    
    evolution_api = models.ForeignKey(
        EvolutionAPI,
        on_delete=models.CASCADE,
        related_name="whatsapp_instances",
        verbose_name="Evolution API"
    )
    
    phone_number = models.CharField(
        max_length=20,
        verbose_name="Número de WhatsApp",
        help_text="Formato: 5511987654321"
    )
    
    display_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Nome de Exibição",
        help_text="Como o WhatsApp aparece nos contatos"
    )
    
    connection_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Status de Conexão"
    )
    
    is_primary = models.BooleanField(
        default=False,
        verbose_name="Principal",
        help_text="WhatsApp principal para agendamentos"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name="Ativo"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "WhatsApp Instance"
        verbose_name_plural = "WhatsApp Instances"
        ordering = ["evolution_api", "-is_primary", "phone_number"]
        unique_together = ("evolution_api", "phone_number")
    
    def __str__(self):
        status_icon = {
            "connected": "✅",
            "connecting": "⏳",
            "pending": "📋",
            "disconnected": "❌",
            "error": "⚠️",
        }
        icon = status_icon.get(self.connection_status, '❓')
        return f"{icon} {self.phone_number} ({self.evolution_api.instance_id})"

