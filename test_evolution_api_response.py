#!/usr/bin/env python3
"""
Teste para verificar se a Evolution API está respondendo corretamente
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
django.setup()

from scheduling.models import EvolutionAPI
import requests

print("\n" + "="*70)
print("  🧪 TESTE: Verificar Evolution API")
print("="*70 + "\n")

# 1. Verificar Evolution API no banco
print("1️⃣  Verificando Evolution API no banco...")
print("─" * 70)

evo_apis = EvolutionAPI.objects.all()
if evo_apis.count() == 0:
    print("❌ FALHOU: Nenhuma Evolution API no banco!")
    print("   Execute: python3 setup_evolution_quick.py")
    sys.exit(1)
else:
    print(f"✅ PASSOU: {evo_apis.count()} Evolution API(s) encontrada(s)\n")

# 2. Testar cada Evolution API
for api in evo_apis:
    print(f"2️⃣  Testando {api.instance_id}...")
    print("─" * 70)
    print(f"   URL: {api.api_url}")
    print(f"   Instance ID: {api.instance_id}")
    print(f"   Ativa: {api.is_active}")
    
    if not api.is_active:
        print("   ⚠️  Evolution API marcada como inativa!")
        continue
    
    # 3. Testar conexão com Evolution API
    print(f"\n3️⃣  Tentando conectar na Evolution API...")
    
    try:
        url = f"{api.api_url}/instance/connect/{api.instance_id}"
        headers = {'apikey': api.api_key}
        
        print(f"   GET {url}")
        print(f"   Headers: {headers}")
        
        response = requests.get(url, headers=headers, timeout=5)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ PASSOU: Evolution API respondeu!")
            print(f"   Response keys: {list(data.keys())}")
            
            if 'base64' in data:
                qr_code = data.get('base64', '')
                print(f"   QR Code tamanho: {len(qr_code)} caracteres")
                print(f"   QR Code começa com: {qr_code[:50]}...")
                print(f"\n   ✨ QR CODE SERÁ FUNCIONARÁ NO DASHBOARD!")
            else:
                print(f"   ⚠️  Resposta não contém 'base64'")
                print(f"   Resposta completa: {data}")
        else:
            print(f"   ❌ FALHOU: Status {response.status_code}")
            print(f"   Response: {response.text[:200]}")
            
    except requests.exceptions.ConnectionError:
        print(f"   ❌ NÃO CONSEGUIU CONECTAR na Evolution API")
        print(f"   Verifique se:")
        print(f"     - Evolution API está rodando")
        print(f"     - URL está correta: {api.api_url}")
        print(f"     - Não há firewall bloqueando")
        
    except requests.exceptions.Timeout:
        print(f"   ❌ TIMEOUT: Evolution API não respondeu em tempo")
        
    except Exception as e:
        print(f"   ❌ ERRO: {e}")
    
    print()

print("="*70)
print("\n📝 RESUMO\n")
print("Se o teste passou:")
print("  ✅ Abra http://localhost:8000/dashboard/whatsapp/")
print("  ✅ Clique em '➕ Conectar WhatsApp'")
print("  ✅ O QR code deve aparecer!")
print()
print("Se o teste falhou:")
print("  ❌ Verifique se Evolution API está rodando")
print("  ❌ Verifique a URL e chave de API")
print("  ❌ Verifique logs do Evolution API")
print()
print("="*70 + "\n")
