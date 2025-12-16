#!/usr/bin/env python3
"""
🧪 TESTE: Criar instância + Obter QR code na Evolution API
"""
import os
import requests
import json

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
print("  🧪 TESTE: Criar Instância + Obter QR Code")
print("="*70 + "\n")

if not EVOLUTION_API_URL or not EVOLUTION_API_KEY:
    print("❌ ERRO: Configure EVOLUTION_API_URL e EVOLUTION_API_KEY no .env")
    exit(1)

print(f"📍 URL: {EVOLUTION_API_URL}")
print(f"🔑 Key: {'*' * 20}{EVOLUTION_API_KEY[-4:]}")
print()

# Nome da instância de teste
instance_name = "teste_qrcode_001"
headers = {
    'apikey': EVOLUTION_API_KEY,
    'Content-Type': 'application/json'
}

# Passo 1: Criar instância
print("1️⃣  Criando instância na Evolution API...")
print("─" * 70)

create_url = f"{EVOLUTION_API_URL}/instance/create"
create_data = {
    "instanceName": instance_name,
    "qrcode": True,
    "integration": "WHATSAPP-BAILEYS"
}

print(f"   POST {create_url}")
print(f"   Data: {json.dumps(create_data, indent=2)}")
print()

try:
    response = requests.post(create_url, json=create_data, headers=headers, timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('Content-Type', 'unknown')}")
    
    if response.status_code in [200, 201]:
        print(f"   ✅ Instância criada com sucesso!")
        try:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)[:500]}")
        except:
            print(f"   Response (text): {response.text[:500]}")
    else:
        print(f"   ⚠️  Status: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")

print()

# Passo 2: Obter QR Code
print("2️⃣  Obtendo QR code...")
print("─" * 70)

connect_url = f"{EVOLUTION_API_URL}/instance/connect/{instance_name}"
print(f"   GET {connect_url}")
print()

try:
    response = requests.get(connect_url, headers=headers, timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Content-Type: {response.headers.get('Content-Type', 'unknown')}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"   ✅ Resposta JSON recebida!")
            print(f"   Keys: {list(data.keys())}")
            
            if 'base64' in data:
                qr = data['base64']
                print(f"   ✨ QR Code: {len(qr)} caracteres")
                print(f"   ✨ Começa com: {qr[:50]}...")
                print()
                print("   🎉 SUCESSO! QR code funcionará no dashboard!")
            else:
                print(f"   ⚠️  Sem campo 'base64'")
                print(f"   Response: {json.dumps(data, indent=2)[:500]}")
                
        except ValueError:
            print(f"   ⚠️  Resposta não é JSON")
            print(f"   Response: {response.text[:500]}")
    else:
        print(f"   ⚠️  Status: {response.status_code}")
        print(f"   Response: {response.text[:500]}")
        
except Exception as e:
    print(f"   ❌ Erro: {e}")

print()
print("="*70)
print()
print("💡 Dica: Se deu erro 409 (Conflict), a instância já existe.")
print("   Tente com outro instance_name ou delete a instância existente.")
print()
print("="*70 + "\n")
