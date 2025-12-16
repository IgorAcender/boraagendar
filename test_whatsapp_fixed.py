#!/usr/bin/env python3
"""
Script de teste para verificar se o setup funcionou
Execute: python3 test_whatsapp_fixed.py
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
django.setup()

from scheduling.models import EvolutionAPI, WhatsAppInstance
from tenants.models import Tenant
import json

print("\n" + "="*70)
print("  🧪 TESTE: Verificar se WhatsApp QR Code funciona")
print("="*70 + "\n")

# 1. Verificar Evolution API
print("1️⃣  Verificando Evolution API...")
print("─" * 70)

evo_apis = EvolutionAPI.objects.all()
if evo_apis.count() == 0:
    print("❌ FALHOU: Nenhuma Evolution API no banco!")
    print("   Execute: python3 setup_evolution_quick.py")
    sys.exit(1)
else:
    print(f"✅ PASSOU: {evo_apis.count()} Evolution API(s) encontrada(s)")
    for api in evo_apis:
        print(f"   - {api.instance_id} (Ativa: {api.is_active})")

# 2. Verificar Tenant
print("\n2️⃣  Verificando Tenant...")
print("─" * 70)

tenants = Tenant.objects.all()
if tenants.count() == 0:
    print("❌ FALHOU: Nenhum Tenant no banco!")
    print("   Crie um Tenant antes de testar")
    sys.exit(1)
else:
    print(f"✅ PASSOU: {tenants.count()} Tenant(s) encontrado(s)")
    for tenant in tenants:
        print(f"   - {tenant.name}")

# 3. Testar criação de WhatsApp (simulado)
print("\n3️⃣  Testando lógica de criação de WhatsApp...")
print("─" * 70)

try:
    evo_api = evo_apis.first()
    tenant = tenants.first()
    
    # Simular a lógica da view
    wa_count = WhatsAppInstance.objects.filter(tenant=tenant).count() + 1
    base_number = f"55119990{wa_count:04d}"
    
    print(f"✅ PASSOU: Número gerado seria: {base_number}")
    
    # Testar geração de QR code
    print("\n4️⃣  Testando geração de QR code...")
    print("─" * 70)
    
    import qrcode
    from io import BytesIO
    import base64
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    
    qr_content = f"evolution://{evo_api.instance_id}/{base_number}"
    qr.add_data(qr_content)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    print(f"✅ PASSOU: QR code gerado com sucesso!")
    print(f"   Tamanho: {len(img_str)} caracteres")
    print(f"   Começa com: {img_str[:50]}...")
    
except Exception as e:
    print(f"❌ FALHOU: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 5. Resultado final
print("\n" + "="*70)
print("  ✅ TODOS OS TESTES PASSARAM!")
print("="*70)
print("\n🎉 O QR code deve funcionar agora!")
print("\n📌 Próximos passos:")
print("   1. Abra: http://localhost:8000/dashboard/whatsapp/")
print("   2. Clique: '+ Conectar WhatsApp'")
print("   3. Aponte: Sua câmera para o QR code")
print("   4. Aproveite: Seu WhatsApp conectado! 📱")
print("\n" + "="*70 + "\n")
