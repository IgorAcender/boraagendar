from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter
from django.db import models

from scheduling.api.viewsets import TenantScopedMixin
from .models import Account, Transaction, Commission
from .serializers import AccountSerializer, TransactionSerializer, CommissionSerializer


class AccountViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    """API para contas financeiras"""
    serializer_class = AccountSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['name', 'balance', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Account.objects.filter(tenant=self.request.tenant)

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Resumo das contas"""
        accounts = self.get_queryset()
        total_balance = sum(acc.balance for acc in accounts)
        return Response({
            'total_accounts': accounts.count(),
            'total_balance': total_balance,
            'accounts': AccountSerializer(accounts, many=True).data
        })


class TransactionViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    """API para transações financeiras"""
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['transaction_date', 'amount', 'created_at']
    ordering = ['-transaction_date']

    def get_queryset(self):
        return Transaction.objects.filter(tenant=self.request.tenant).select_related('account', 'booking')

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Resumo por tipo de transação"""
        transactions = self.get_queryset()
        income_total = transactions.filter(transaction_type='income').aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        expense_total = transactions.filter(transaction_type='expense').aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        return Response({
            'total_transactions': transactions.count(),
            'income': income_total,
            'expense': expense_total,
            'net': income_total - expense_total
        })


class CommissionViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    """API para comissões de profissionais"""
    serializer_class = CommissionSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at', 'amount', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        return Commission.objects.filter(tenant=self.request.tenant).select_related('professional', 'booking')

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.tenant)

    @action(detail=True, methods=['post'])
    def mark_as_paid(self, request, pk=None):
        """Marcar comissão como paga"""
        commission = self.get_object()
        commission.mark_as_paid()
        return Response(
            CommissionSerializer(commission).data,
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Resumo de comissões pendentes"""
        commissions = self.get_queryset()
        pending_total = commissions.filter(status='pending').aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        paid_total = commissions.filter(status='paid').aggregate(
            total=models.Sum('amount')
        )['total'] or 0
        
        return Response({
            'pending_commissions': commissions.filter(status='pending').count(),
            'pending_total': pending_total,
            'paid_total': paid_total,
            'total_paid_commissions': commissions.filter(status='paid').count()
        })
