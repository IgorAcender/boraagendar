#!/usr/bin/env python3
"""
🧪 TESTE SIMPLIFICADO - PADRÃO RIFAS
Testa conexão com Evolution API usando variáveis de ambiente
"""
import os
import requests

# Carregar .env manualmente
def load_env():
    env_file = '.env'
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value

load_env()

EVOLUTION_API_URL = os.getenv('EVOLUTION_API_URL', '')
EVOLUTION_API_KEY = os.getenv('EVOLUTION_API_KEY', '')

print("\n" + "="*70)
print("  🧪 TESTE: Evolution API (Padrão RIFAS)")
print("="*70 + "\n")

# Verificar variáveis
print("1️⃣  Verificando variáveis de ambiente...")
print("─" * 70)
print(f"   EVOLUTION_API_URL: {EVOLUTION_API_URL or '❌ NÃO CONFIGURADA'}")
print(f"   EVOLUTION_API_KEY: {('✅ ' + '*' * 20 + EVOLUTION_API_KEY[-4:]) if EVOLUTION_API_KEY else '❌ NÃO CONFIGURADA'}")

if not EVOLUTION_API_URL or not EVOLUTION_API_KEY:
    print("\n❌ ERRO: Configure as variáveis no arquivo .env:\n")
    print("   EVOLUTION_API_URL=http://seu-evolution-api.com/manager")
    print("   EVOLUTION_API_KEY=sua-chave-aqui")
    print()
    exit(1)

print()

# Testar conexão
print("2️⃣  Testando conexão com Evolution API...")
print("─" * 70)

# Usar instance_name de teste
instance_name = "teste_conexao"
url = f"{EVOLUTION_API_URL}/instance/connect/{instance_name}"
headers = {'apikey': EVOLUTION_API_KEY}

print(f"   URL: {url}")
print(f"   Method: GET")
print(f"   Headers: {{'apikey': '***{EVOLUTION_API_KEY[-4:]}'}}")
print()

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('Content-Type', 'unknown')}")
    print(f"   Response (first 200 chars): {response.text[:200]}")
    print()
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"   ✅ PASSOU: Evolution API respondeu!\n")
            print(f"   Response keys: {list(data.keys())}")
            
            if 'base64' in data:
                qr_code = data.get('base64', '')
                print(f"   ✨ QR Code recebido: {len(qr_code)} caracteres")
                print(f"   ✨ Começa com: {qr_code[:50]}...")
                print()
                print("   🎉 SUCESSO! O QR code funcionará no dashboard!")
            else:
                print(f"   ⚠️  Resposta não contém 'base64'")
                print(f"   Resposta: {data}")
        except ValueError:
            print(f"   ⚠️  Resposta não é JSON válido")
            print(f"   ✅ MAS a Evolution API ESTÁ RESPONDENDO!")
            print(f"   Pode ser HTML de configuração ou outra página")
    elif response.status_code == 404:
        print(f"   ⚠️  Instance não encontrada (normal para teste)")
        print(f"   ✅ MAS a Evolution API ESTÁ RESPONDENDO!")
        print(f"   ✅ O dashboard criará a instance automaticamente")
    else:
        print(f"   ❌ Status inesperado: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
except requests.exceptions.ConnectionError as e:
    print(f"   ❌ NÃO CONSEGUIU CONECTAR")
    print(f"   Erro: {e}")
    print()
    print("   Verifique:")
    print(f"   • Evolution API está rodando?")
    print(f"   • URL está correta: {EVOLUTION_API_URL}")
    print(f"   • Não há firewall bloqueando?")
    
except requests.exceptions.Timeout:
    print(f"   ❌ TIMEOUT: Evolution API não respondeu")
    
except Exception as e:
    print(f"   ❌ ERRO: {e}")

print()
print("="*70)
print("\n📝 RESUMO\n")
print("✅ Se passou: Abra http://localhost:8000/dashboard/whatsapp/")
print("   e clique em '➕ Conectar WhatsApp'")
print()
print("❌ Se falhou: Verifique Evolution API está rodando e acessível")
print()
print("="*70 + "\n")
