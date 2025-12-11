"""
Modelos de Subscription e Planos
"""
from django.db import models
from django.utils import timezone
from datetime import timedelta


class Plan(models.Model):
    """Planos disponíveis no sistema."""
    
    PLAN_TYPES = [
        ('free', 'Gratuito'),
        ('starter', 'Iniciante'),
        ('professional', 'Profissional'),
        ('premium', 'Premium'),
        ('enterprise', 'Enterprise'),
    ]
    
    slug = models.SlugField("Identificador", unique=True)
    name = models.CharField("Nome do Plano", max_length=100)
    description = models.TextField("Descrição", blank=True)
    plan_type = models.CharField("Tipo", max_length=20, choices=PLAN_TYPES, default='free')
    price_monthly = models.DecimalField("Preço Mensal (R$)", max_digits=10, decimal_places=2, default=0)
    price_annual = models.DecimalField("Preço Anual (R$)", max_digits=10, decimal_places=2, default=0)
    
    # Features disponíveis
    max_professionals = models.IntegerField("Máx. Profissionais", default=1, help_text="-1 para ilimitado")
    max_services = models.IntegerField("Máx. Serviços", default=5, help_text="-1 para ilimitado")
    max_monthly_bookings = models.IntegerField("Máx. Agendamentos/mês", default=100, help_text="-1 para ilimitado")
    
    # Módulos disponíveis
    has_dashboard = models.BooleanField("Acesso ao Dashboard", default=True)
    has_financial_module = models.BooleanField("Módulo Financeiro", default=False)
    has_advanced_analytics = models.BooleanField("Análises Avançadas", default=False)
    has_sms_notifications = models.BooleanField("Notificações SMS", default=False)
    has_email_campaigns = models.BooleanField("Campanhas por Email", default=False)
    has_customer_reviews = models.BooleanField("Avaliações de Clientes", default=False)
    has_custom_domain = models.BooleanField("Domínio Customizado", default=False)
    has_api_access = models.BooleanField("Acesso à API", default=False)
    has_white_label = models.BooleanField("White Label", default=False)
    
    is_active = models.BooleanField("Ativo", default=True)
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)
    
    class Meta:
        verbose_name = "Plano"
        verbose_name_plural = "Planos"
        ordering = ['price_monthly']
    
    def __str__(self):
        return f"{self.name} - {self.get_plan_type_display()}"


class Subscription(models.Model):
    """Subscrição de um Tenant a um Plano."""
    
    STATUS_CHOICES = [
        ('active', 'Ativo'),
        ('trial', 'Período de Teste'),
        ('paused', 'Pausado'),
        ('cancelled', 'Cancelado'),
        ('past_due', 'Vencido'),
    ]
    
    BILLING_CYCLE = [
        ('monthly', 'Mensal'),
        ('annual', 'Anual'),
    ]
    
    tenant = models.OneToOneField('Tenant', on_delete=models.CASCADE, related_name='subscription')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    status = models.CharField("Status", max_length=20, choices=STATUS_CHOICES, default='trial')
    billing_cycle = models.CharField("Ciclo de Cobrança", max_length=20, choices=BILLING_CYCLE, default='monthly')
    
    # Datas
    trial_started_at = models.DateTimeField("Teste iniciado em", null=True, blank=True)
    trial_ends_at = models.DateTimeField("Teste termina em", null=True, blank=True)
    started_at = models.DateTimeField("Subscrição iniciada em", auto_now_add=True)
    next_billing_date = models.DateField("Próxima cobrança", null=True, blank=True)
    cancelled_at = models.DateTimeField("Cancelado em", null=True, blank=True)
    
    # Informações de pagamento
    payment_method = models.CharField("Forma de Pagamento", max_length=50, blank=True)
    stripe_customer_id = models.CharField("Stripe Customer ID", max_length=100, blank=True)
    stripe_subscription_id = models.CharField("Stripe Subscription ID", max_length=100, blank=True)
    
    # Configurações
    auto_renew = models.BooleanField("Renovação Automática", default=True)
    
    created_at = models.DateTimeField("Criado em", auto_now_add=True)
    updated_at = models.DateTimeField("Atualizado em", auto_now=True)
    
    class Meta:
        verbose_name = "Subscrição"
        verbose_name_plural = "Subscrições"
    
    def __str__(self):
        return f"{self.tenant.name} - {self.plan.name} ({self.status})"
    
    @property
    def is_active_subscription(self):
        """Verifica se a subscrição está ativa."""
        return self.status in ['active', 'trial']
    
    @property
    def is_trial(self):
        """Verifica se está em período de teste."""
        return self.status == 'trial' and self.trial_ends_at > timezone.now()
    
    @property
    def trial_days_remaining(self):
        """Dias restantes do período de teste."""
        if self.is_trial:
            return (self.trial_ends_at - timezone.now()).days
        return 0
    
    @property
    def is_expired(self):
        """Verifica se expirou."""
        if self.trial_ends_at and self.status == 'trial':
            return timezone.now() > self.trial_ends_at
        return False


class FeatureUsage(models.Model):
    """Rastreamento de uso de features do plano."""
    
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='feature_usage')
    feature_name = models.CharField("Feature", max_length=100)
    monthly_usage = models.IntegerField("Uso Este Mês", default=0)
    monthly_limit = models.IntegerField("Limite Este Mês", default=0)
    reset_date = models.DateField("Data do Reset", auto_now_add=True)
    
    class Meta:
        verbose_name = "Uso de Feature"
        verbose_name_plural = "Uso de Features"
        unique_together = ('subscription', 'feature_name')
    
    def __str__(self):
        return f"{self.subscription.tenant.name} - {self.feature_name}"
    
    @property
    def is_limit_exceeded(self):
        """Verifica se excedeu o limite."""
        if self.monthly_limit == -1:  # Ilimitado
            return False
        return self.monthly_usage >= self.monthly_limit
    
    @property
    def percentage_used(self):
        """Percentual de uso."""
        if self.monthly_limit == -1:
            return 0
        return (self.monthly_usage / self.monthly_limit * 100) if self.monthly_limit > 0 else 0
