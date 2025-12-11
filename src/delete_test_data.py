"""
Script para deletar dados de teste
Remove todos os agendamentos criados para testes
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from scheduling.models import Booking, Tenant

def delete_test_data():
    """Deletar todos os agendamentos de teste"""
    
    try:
        tenant = Tenant.objects.get(slug='test-clinic')
        print(f"✓ Usando tenant: {tenant.name}")
    except Tenant.DoesNotExist:
        print("❌ Tenant 'test-clinic' não encontrado")
        return
    
    # Contar agendamentos antes
    before_count = Booking.objects.filter(tenant=tenant).count()
    before_revenue = sum(b.price for b in Booking.objects.filter(tenant=tenant))
    
    print(f"\n📊 Antes da exclusão:")
    print(f"  - Total de agendamentos: {before_count}")
    print(f"  - Total de receita: R$ {before_revenue:.2f}")
    
    # Deletar todos os agendamentos do tenant
    deleted_count, _ = Booking.objects.filter(tenant=tenant).delete()
    
    print(f"\n✅ Dados de teste deletados!")
    print(f"  - Agendamentos removidos: {deleted_count}")
    
    # Verificar que ficou vazio
    after_count = Booking.objects.filter(tenant=tenant).count()
    print(f"\n📊 Depois da exclusão:")
    print(f"  - Total de agendamentos: {after_count}")

if __name__ == '__main__':
    delete_test_data()
