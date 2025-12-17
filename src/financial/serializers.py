from rest_framework import serializers
from .models import Account, Transaction, Commission


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'name', 'account_type', 'balance', 'description', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class TransactionSerializer(serializers.ModelSerializer):
    account_name = serializers.CharField(source='account.name', read_only=True)
    booking_id = serializers.IntegerField(source='booking.id', read_only=True, required=False)

    class Meta:
        model = Transaction
        fields = [
            'id', 'account', 'account_name', 'booking_id', 'transaction_type',
            'payment_method', 'description', 'amount', 'transaction_date', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class CommissionSerializer(serializers.ModelSerializer):
    professional_name = serializers.CharField(source='professional.name', read_only=True)
    booking_id = serializers.IntegerField(source='booking.id', read_only=True)

    class Meta:
        model = Commission
        fields = [
            'id', 'professional', 'professional_name', 'booking_id',
            'commission_type', 'commission_value', 'amount', 'status',
            'paid_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'paid_at']
