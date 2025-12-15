#!/usr/bin/env python
"""
🚀 CREATE WHATSAPP INSTANCES - SIMPLES (50 WhatsApps)

Este script cria 50 instâncias de WhatsApp conectadas ao Evolution API
Começa com 1 Evolution, pronto para escalar a 2+ depois

Uso:
    python create_whatsapp_instances.py
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from scheduling.models import EvolutionAPI, WhatsAppInstance
from django.utils import timezone

def create_instances():
    """Cria 50 WhatsApps distribuídos no Evolution API disponível"""
    
    print("\n" + "="*70)
    print("📱 CRIANDO 50 INSTÂNCIAS DE WHATSAPP")
    print("="*70 + "\n")
    
    # Buscar Evolution APIs ativos
    evolution_apis = EvolutionAPI.objects.filter(is_active=True).order_by('priority')
    
    if not evolution_apis.exists():
        print("❌ Nenhum Evolution API encontrado!")
        print("   Execute primeiro: bash setup_evolution_simple.sh")
        return False
    
    print(f"📊 Evolution APIs encontrados: {evolution_apis.count()}\n")
    for api in evolution_apis:
        print(f"   • {api.instance_id}: {api.capacity} slots")
    print()
    
    # Contar WhatsApps existentes
    existing_count = WhatsAppInstance.objects.count()
    print(f"📈 WhatsApps existentes: {existing_count}\n")
    
    # Se já temos 50, avisar
    if existing_count >= 50:
        print("⚠️  Já existem 50 WhatsApps criados!")
        print("   Instâncias atuais:")
        for instance in WhatsAppInstance.objects.all()[:10]:
            print(f"      • {instance.phone_number} ({instance.evolution_api.instance_id})")
        if existing_count > 10:
            print(f"      • ... e mais {existing_count - 10}")
        return True
    
    # Criar 50 instâncias
    to_create = 50 - existing_count
    print(f"🔄 Criando {to_create} novas instâncias...\n")
    
    created = 0
    
    # Distribuir entre os Evolution APIs
    api_index = 0
    apis_list = list(evolution_apis)
    
    # Números de telefone começando em 55 11 99900000
    base_phone = 5511999
    
    for i in range(existing_count, 50):
        # Selecionar Evolution API (round-robin)
        evolution_api = apis_list[api_index % len(apis_list)]
        api_index += 1
        
        # Gerar número único
        phone_number = f"{base_phone}{i:05d}"
        
        try:
            instance = WhatsAppInstance.objects.create(
                evolution_api=evolution_api,
                phone_number=phone_number,
                display_name=f"WhatsApp #{i+1}",
                is_active=True,
                is_primary=(i == existing_count),  # Primeira como primária
                connection_status='pending'
            )
            created += 1
            
            if (i + 1 - existing_count) % 10 == 0:
                print(f"   ✓ {i + 1 - existing_count} instâncias criadas...")
        
        except Exception as e:
            print(f"   ⚠️  Erro ao criar instância {i+1}: {str(e)}")
            continue
    
    print()
    print("✅ CONCLUSÃO")
    print("="*70)
    print(f"   • Instâncias criadas: {created}")
    print(f"   • Total agora: {WhatsAppInstance.objects.count()}")
    print(f"   • Distribuído em: {evolution_apis.count()} Evolution API(s)")
    print()
    
    # Mostrar distribuição
    for api in evolution_apis:
        count = WhatsAppInstance.objects.filter(evolution_api=api).count()
        percent = (count / api.capacity) * 100
        print(f"   📊 {api.instance_id}: {count}/{api.capacity} ({percent:.0f}%)")
    
    print()
    print("🎉 Pronto! Seus WhatsApps estão registrados no banco de dados")
    print()
    print("   Próximos passos:")
    print("   1. Conectar as instâncias no Evolution API")
    print("   2. Testar envio de mensagens")
    print("   3. Quando pronto, adicione 2º Evolution: bash setup_evolution_add.sh")
    print()
    
    return True

if __name__ == '__main__':
    try:
        success = create_instances()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
