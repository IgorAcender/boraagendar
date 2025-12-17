from django.db import models
from django.utils import timezone
from tenants.models import Tenant
from scheduling.models import Professional, Booking


class Account(models.Model):
    """Conta de caixa por tenant"""
    ACCOUNT_TYPE_CHOICES = [
        ('cash', 'Dinheiro'),
        ('bank', 'Banco'),
        ('card', 'Cartão'),
        ('pix', 'PIX'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='financial_accounts')
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'financial_account'
        ordering = ['-created_at']
        verbose_name = 'Conta Financeira'
        verbose_name_plural = 'Contas Financeiras'

    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"


class Transaction(models.Model):
    """Transação financeira"""
    TRANSACTION_TYPE_CHOICES = [
        ('income', 'Receita'),
        ('expense', 'Despesa'),
        ('transfer', 'Transferência'),
    ]

    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Dinheiro'),
        ('card_credit', 'Cartão Crédito'),
        ('card_debit', 'Cartão Débito'),
        ('pix', 'PIX'),
        ('bank_transfer', 'Transferência Bancária'),
        ('check', 'Cheque'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='financial_transactions')
    account = models.ForeignKey(Account, on_delete=models.PROTECT, related_name='transactions')
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name='financial_transactions')
    
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    transaction_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'financial_transaction'
        ordering = ['-transaction_date', '-created_at']
        verbose_name = 'Transação'
        verbose_name_plural = 'Transações'
        indexes = [
            models.Index(fields=['tenant', '-transaction_date']),
            models.Index(fields=['account', '-transaction_date']),
        ]

    def __str__(self):
        return f"{self.description} - R$ {self.amount}"


class Commission(models.Model):
    """Comissão de profissional"""
    STATUS_CHOICES = [
        ('pending', 'Pendente'),
        ('paid', 'Pago'),
        ('cancelled', 'Cancelado'),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='financial_commissions')
    professional = models.ForeignKey(Professional, on_delete=models.CASCADE, related_name='commissions')
    booking = models.OneToOneField(Booking, on_delete=models.PROTECT, related_name='commission')
    
    commission_type = models.CharField(max_length=50, default='percentage', help_text='Tipo: percentage ou fixed_amount')
    commission_value = models.DecimalField(max_digits=12, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    paid_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'financial_commission'
        ordering = ['-created_at']
        verbose_name = 'Comissão'
        verbose_name_plural = 'Comissões'
        indexes = [
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['professional', '-created_at']),
        ]

    def __str__(self):
        return f"Comissão {self.professional.name} - R$ {self.amount} ({self.get_status_display()})"

    def mark_as_paid(self):
        self.status = 'paid'
        self.paid_at = timezone.now()
        self.save()
