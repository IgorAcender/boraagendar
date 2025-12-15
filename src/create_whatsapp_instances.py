#!/usr/bin/env python3
"""
Script para criar 100 instâncias de WhatsApp automaticamente
Distribui 50 em cada Evolution API

Uso: python create_whatsapp_instances.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from scheduling.models import EvolutionAPI, WhatsAppInstance

def create_whatsapp_instances():
    """Cria 100 instâncias de WhatsApp (50 em cada Evolution API)"""
    
    print("=" * 80)
    print("🚀 CRIANDO 100 INSTÂNCIAS DE WHATSAPP")
    print("=" * 80)
    
    # Buscar Evolution APIs
    print("\n📋 Buscando Evolution APIs...")
    evolution_apis = EvolutionAPI.objects.filter(is_active=True).order_by("id")
    
    if evolution_apis.count() < 2:
        print("❌ ERRO: Você precisa ter pelo menos 2 Evolution APIs criadas!")
        print("\nCrie-as no admin:")
        print("  http://seu-dominio/admin/scheduling/evolutionapi/")
        return False
    
    print(f"✅ Encontradas {evolution_apis.count()} Evolution APIs")
    for evo in evolution_apis:
        print(f"   - {evo.name} ({evo.whatsapp_capacity} slots)")
    
    # Configuração dos WhatsApps
    print("\n⚙️  Configuração:")
    print("   - Total: 100 WhatsApps")
    print("   - Por Evolution: 50")
    print("   - Padrão: Desconectados (status: 'disconnected')")
    print("   - Um principal por Evolution (para receber agendamentos)")
    
    # Criar os WhatsApps
    print("\n🔨 Criando instâncias...")
    
    created_count = 0
    errors = []
    
    for evo_index, evolution_api in enumerate(evolution_apis[:2], 1):
        print(f"\n   Evolution API {evo_index}: {evolution_api.name}")
        
        for wa_number in range(50):
            # Gerar número fictício para teste
            # Formato: 55 + índice_evolution + índice_whatsapp padronizado
            phone = f"55119876{evo_index}{wa_number:04d}"
            
            try:
                whatsapp = WhatsAppInstance.objects.create(
                    evolution_api=evolution_api,
                    phone_number=phone,
                    display_name=f"WhatsApp {wa_number + 1} (Evo {evo_index})",
                    status="disconnected",
                    is_primary=(wa_number == 0)  # Primeira de cada é principal
                )
                created_count += 1
                
                if wa_number % 10 == 0:
                    print(f"      ✅ {wa_number + 1}/50 criados...")
                    
            except Exception as e:
                error_msg = f"Erro ao criar {phone}: {str(e)}"
                errors.append(error_msg)
                print(f"      ❌ {error_msg}")
        
        print(f"      ✅ 50/50 concluídos!")
    
    # Resumo
    print("\n" + "=" * 80)
    print("📊 RESUMO")
    print("=" * 80)
    print(f"✅ Instâncias criadas: {created_count}")
    
    if errors:
        print(f"❌ Erros: {len(errors)}")
        for error in errors[:5]:
            print(f"   - {error}")
        if len(errors) > 5:
            print(f"   ... e {len(errors) - 5} erros mais")
    
    # Estatísticas
    print("\n📈 Estatísticas:")
    for evolution_api in EvolutionAPI.objects.filter(is_active=True):
        wa_count = WhatsAppInstance.objects.filter(
            evolution_api=evolution_api
        ).count()
        primary = WhatsAppInstance.objects.filter(
            evolution_api=evolution_api,
            is_primary=True
        ).count()
        connected = WhatsAppInstance.objects.filter(
            evolution_api=evolution_api,
            status="connected"
        ).count()
        
        print(f"\n   {evolution_api.name}:")
        print(f"   - Total: {wa_count}")
        print(f"   - Primários: {primary}")
        print(f"   - Conectados: {connected}")
        print(f"   - Capacidade: {evolution_api.whatsapp_capacity}")
    
    print("\n" + "=" * 80)
    print("✅ Processo concluído!")
    print("=" * 80)
    print("\n📝 Próximos passos:")
    print("   1. Conectar os WhatsApps no Evolution API")
    print("   2. Verificar status na evolução de agendamentos")
    print("   3. Testar envio de confirmação via WhatsApp")
    
    print("\n🔗 Links úteis:")
    print(f"   Admin: http://seu-dominio/admin/scheduling/whatsappinstance/")
    print(f"   Evolution API: https://seu-dominio/evolution-api/")
    
    return True


if __name__ == "__main__":
    try:
        success = create_whatsapp_instances()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
