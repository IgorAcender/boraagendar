from django.test import TestCase
from django.contrib.auth.models import User
from tenants.models import Tenant
from .models import Account, Transaction, Commission


class AccountTestCase(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='Test Tenant', slug='test-tenant')
        self.account = Account.objects.create(
            tenant=self.tenant,
            name='Cash',
            account_type='cash'
        )

    def test_account_creation(self):
        self.assertEqual(self.account.name, 'Cash')
        self.assertEqual(self.account.balance, 0)


class TransactionTestCase(TestCase):
    def setUp(self):
        self.tenant = Tenant.objects.create(name='Test Tenant', slug='test-tenant')
        self.account = Account.objects.create(
            tenant=self.tenant,
            name='Cash',
            account_type='cash'
        )

    def test_transaction_creation(self):
        transaction = Transaction.objects.create(
            tenant=self.tenant,
            account=self.account,
            transaction_type='income',
            payment_method='cash',
            description='Test Income',
            amount=100
        )
        self.assertEqual(transaction.amount, 100)
        self.assertEqual(transaction.transaction_type, 'income')
