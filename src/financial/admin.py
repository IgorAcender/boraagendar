from django.contrib import admin
from .models import Account, Transaction, Commission


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'account_type', 'balance', 'is_active', 'created_at']
    list_filter = ['account_type', 'is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['description', 'transaction_type', 'payment_method', 'amount', 'transaction_date']
    list_filter = ['transaction_type', 'payment_method', 'transaction_date']
    search_fields = ['description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ['professional', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['professional__name']
    readonly_fields = ['created_at', 'updated_at']
