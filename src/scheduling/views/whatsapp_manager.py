"""
Views para gerenciamento de WhatsApp pelo dono da barbearia
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db import models
from django.db.models import Q
from django.conf import settings
import json
import base64
import requests
from io import BytesIO
import qrcode
from datetime import timedelta

from scheduling.models import WhatsAppInstance, EvolutionAPI
from tenants.models import Tenant
from tenants.services import ensure_membership_for_request, TenantSelectionRequired
from django.urls import reverse
from scheduling.services.evolution_manager import EvolutionAPIManager


def _get_tenant_or_redirect(request):
    """Helper para obter tenant do request"""
    try:
        membership = ensure_membership_for_request(request, allowed_roles=["owner", "manager"])
    except TenantSelectionRequired:
        select_url = f"{reverse('accounts:select_tenant')}?next={request.get_full_path()}"
        return None, redirect(select_url)
    return membership.tenant, None


@login_required
def whatsapp_dashboard(request):
    """Dashboard principal de gerenciamento de WhatsApp"""
    tenant, redirect_response = _get_tenant_or_redirect(request)
    if redirect_response:
        return redirect_response
    
    whatsapps = WhatsAppInstance.objects.filter(
        tenant=tenant
    ).select_related('evolution_api').order_by('-is_primary', '-connected_at')
    
    stats = {
        'total': whatsapps.count(),
        'conectados': whatsapps.filter(connection_status='connected').count(),
        'desconectados': whatsapps.filter(connection_status='disconnected').count(),
        'pendentes': whatsapps.filter(connection_status='pending').count(),
    }
    
    context = {
        'whatsapps': whatsapps,
        'stats': stats,
        'tenant': tenant,
        'has_primary': whatsapps.filter(is_primary=True).exists(),
        'EVOLUTION_API_URL': settings.EVOLUTION_API_URL,
    }
    
    return render(request, 'whatsapp/dashboard.html', context)


@login_required
def whatsapp_detail(request, id):
    """Página de detalhes de um WhatsApp"""
    tenant, redirect_response = _get_tenant_or_redirect(request)
    if redirect_response:
        return redirect_response
    
    whatsapp = get_object_or_404(WhatsAppInstance, id=id, tenant=tenant)
    
    context = {
        'tenant': tenant,
        'whatsapp': whatsapp,
        'qr_code_valid': whatsapp.qr_code_is_valid,
        'status_display': whatsapp.get_status_display_verbose(),
        'evolution_api': whatsapp.evolution_api,
    }
    
    return render(request, 'whatsapp/detail.html', context)


@login_required
@require_http_methods(["POST"])
def whatsapp_generate_qrcode(request, id):
    """Gerar QR code para conectar"""
    tenant, redirect_response = _get_tenant_or_redirect(request)
    if redirect_response:
        return redirect_response
    
    whatsapp = get_object_or_404(WhatsAppInstance, id=id, tenant=tenant)
    
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        qr_content = f"evolution://{whatsapp.evolution_api.instance_id}/{whatsapp.phone_number}"
        qr.add_data(qr_content)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        whatsapp.qr_code = img_str
        whatsapp.qr_code_expires_at = timezone.now() + timedelta(minutes=5)
        whatsapp.connection_status = 'pending'
        whatsapp.save()
        
        return JsonResponse({
            'success': True,
            'qr_code': f"data:image/png;base64,{img_str}",
            'expires_at': whatsapp.qr_code_expires_at.isoformat(),
            'message': 'QR code gerado com sucesso!'
        })
    
    except Exception as e:
        whatsapp.connection_status = 'error'
        whatsapp.error_message = str(e)
        whatsapp.save()
        
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def whatsapp_disconnect(request, id):
    """Desconectar um WhatsApp"""
    tenant, redirect_response = _get_tenant_or_redirect(request)
    if redirect_response:
        return redirect_response
    
    whatsapp = get_object_or_404(WhatsAppInstance, id=id, tenant=tenant)
    
    try:
        whatsapp.connection_status = 'disconnected'
        whatsapp.disconnected_at = timezone.now()
        whatsapp.session_id = ''
        whatsapp.save()
        
        return JsonResponse({
            'success': True,
            'message': 'WhatsApp desconectado com sucesso!'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def whatsapp_set_primary(request, id):
    """Definir como principal"""
    tenant, redirect_response = _get_tenant_or_redirect(request)
    if redirect_response:
        return redirect_response
    
    whatsapp = get_object_or_404(WhatsAppInstance, id=id, tenant=tenant)
    
    if not whatsapp.is_connected:
        return JsonResponse({
            'success': False,
            'error': 'Apenas WhatsApps conectados podem ser principais'
        }, status=400)
    
    try:
        WhatsAppInstance.objects.filter(tenant=tenant).update(is_primary=False)
        whatsapp.is_primary = True
        whatsapp.save()
        
        return JsonResponse({
            'success': True,
            'message': 'WhatsApp definido como principal!'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
def whatsapp_status_api(request, id):
    """API para obter status"""
    tenant, redirect_response = _get_tenant_or_redirect(request)
    if redirect_response:
        return redirect_response
    
    whatsapp = get_object_or_404(WhatsAppInstance, id=id, tenant=tenant)
    
    return JsonResponse({
        'id': whatsapp.id,
        'phone_number': whatsapp.phone_number,
        'status': whatsapp.connection_status,
        'status_display': whatsapp.get_status_display_verbose(),
        'is_connected': whatsapp.is_connected,
        'is_primary': whatsapp.is_primary,
        'connected_at': whatsapp.connected_at.isoformat() if whatsapp.connected_at else None,
        'error_message': whatsapp.error_message,
        'qr_code_valid': whatsapp.qr_code_is_valid,
    })


@login_required
@require_http_methods(["POST"])
def whatsapp_send_test(request):
    """Enviar mensagem de teste a partir do dashboard"""
    tenant, redirect_response = _get_tenant_or_redirect(request)
    if redirect_response:
        return redirect_response

    try:
        data = json.loads(request.body or "{}")
        to_number = data.get('to')
        message = data.get('message')
        if not to_number or not message:
            return JsonResponse({'success': False, 'error': 'Campos to e message são obrigatórios'}, status=400)

        # Tenta enviar via EvolutionAPIManager
        success = EvolutionAPIManager.send_message_auto(
            tenant_slug=tenant.slug,
            to_number=to_number,
            message=message,
        )

        if success:
            return JsonResponse({'success': True, 'message': 'Mensagem enviada com sucesso'})
        else:
            return JsonResponse({'success': False, 'error': 'Falha ao enviar mensagem'}, status=500)

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def whatsapp_list_api(request):
    """API para listar todos"""
    tenant, redirect_response = _get_tenant_or_redirect(request)
    if redirect_response:
        return redirect_response
    
    whatsapps = WhatsAppInstance.objects.filter(
        tenant=tenant
    ).values(
        'id', 'phone_number', 'status', 
        'is_primary', 'is_active', 'display_name'
    ).order_by('-is_primary', '-connected_at')
    
    return JsonResponse({
        'count': len(list(whatsapps)),
        'whatsapps': list(whatsapps)
    })


@login_required
@require_http_methods(["POST"])
def whatsapp_create(request):
    """
    Conectar WhatsApp do salão (SaaS Multi-tenant)
    - Primeira vez: Cria instância na Evolution API com nome do salão
    - Próximas vezes: Apenas reconecta (gera novo QR) na mesma instância
    """
    tenant, redirect_response = _get_tenant_or_redirect(request)
    if redirect_response:
        return redirect_response
    
    try:
        # Verificar se as variáveis de ambiente estão configuradas
        if not settings.EVOLUTION_API_URL or not settings.EVOLUTION_API_KEY:
            return JsonResponse({
                'success': False,
                'error': 'Evolution API não configurada. Contate o suporte.'
            }, status=500)
        
        data = json.loads(request.body) if request.body else {}
        headers = {'apikey': settings.EVOLUTION_API_KEY, 'Content-Type': 'application/json'}
        
        # Verificar se já existe instância para este tenant
        existing_whatsapp = WhatsAppInstance.objects.filter(tenant=tenant).first()
        
        if existing_whatsapp:
            # JÁ EXISTE INSTÂNCIA - Apenas reconectar (gerar novo QR)
            instance_name = existing_whatsapp.instance_name
            print(f"♻️  Reconectando instância existente: {instance_name}")
            
            # Obter novo QR code da instância existente
            connect_url = f"{settings.EVOLUTION_API_URL}/instance/connect/{instance_name}"
            print(f"🔗 GET {connect_url}")
            
            try:
                connect_response = requests.get(connect_url, headers=headers, timeout=10)
                connect_response.raise_for_status()
                
                api_response = connect_response.json()
                print(f"📡 API Response: {api_response}")
                
                # Tentar extrair QR code de diferentes formatos de resposta
                qr_code_base64 = None
                if isinstance(api_response, dict):
                    # Tentar vários campos possíveis
                    qr_code_base64 = (
                        api_response.get('base64') or 
                        api_response.get('qrcode') or 
                        api_response.get('qr_code') or
                        api_response.get('qr') or
                        (api_response.get('instance', {}).get('qrcode')) or
                        (api_response.get('instance', {}).get('base64'))
                    )
                
                # Limpar prefixo se já vier com data:image
                if isinstance(qr_code_base64, str) and qr_code_base64.startswith('data:image'):
                    qr_code_base64 = qr_code_base64.split(',', 1)[-1]
                
                if not qr_code_base64:
                    print(f"⚠️  Tentando gerar QR code via endpoint /qrcode/")
                    # Se não conseguiu extrair, tentar outro endpoint
                    qr_url = f"{settings.EVOLUTION_API_URL}/instance/qrcode/{instance_name}"
                    qr_response = requests.get(qr_url, headers=headers, timeout=10)
                    if qr_response.status_code == 200:
                        qr_data = qr_response.json()
                        print(f"📡 QR Endpoint Response: {qr_data}")
                        qr_code_base64 = (
                            qr_data.get('base64') or 
                            qr_data.get('qrcode') or 
                            qr_data.get('qr_code') or
                            qr_data.get('qr')
                        )
                    
                    if not qr_code_base64:
                        return JsonResponse({
                            'success': False,
                            'error': f'Evolution API não retornou QR code. Response: {api_response}'
                        }, status=400)
                
                # Atualizar QR code no banco
                existing_whatsapp.qr_code = qr_code_base64
                existing_whatsapp.qr_code_expires_at = timezone.now() + timedelta(minutes=5)
                existing_whatsapp.connection_status = 'connecting'
                existing_whatsapp.save()
                
                print(f"✅ QR code atualizado para instância {instance_name}")
                
                return JsonResponse({
                    'success': True,
                    'whatsapp_id': existing_whatsapp.id,
                    'qr_code': f"data:image/png;base64,{qr_code_base64}",
                    'expires_at': existing_whatsapp.qr_code_expires_at.isoformat(),
                    'message': 'Reconecte seu WhatsApp escaneando o QR code!',
                    'instance_name': instance_name,
                    'is_reconnect': True
                })
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Erro ao obter QR code: {e}")
                return JsonResponse({
                    'success': False,
                    'error': f'Erro ao conectar com Evolution API: {str(e)}'
                }, status=400)
        
        else:
            # PRIMEIRA VEZ - Criar nova instância com nome do salão
            instance_name = f"{tenant.slug}_whatsapp"  # Nome único baseado no slug do tenant
            print(f"🆕 Criando PRIMEIRA instância para {tenant.name}: {instance_name}")
            
            # Passo 1: Criar instância na Evolution API
            create_url = f"{settings.EVOLUTION_API_URL}/instance/create"
            create_data = {
                "instanceName": instance_name,
                "qrcode": True,
                "integration": "WHATSAPP-BAILEYS"
            }
            
            print(f"🔗 [1/2] POST {create_url}")
            print(f"📦 Data: {create_data}")
            
            try:
                create_response = requests.post(create_url, json=create_data, headers=headers, timeout=10)
                print(f"📊 Status criação: {create_response.status_code}")
                
                # Se já existe (409), tudo bem - vamos apenas conectar
                if create_response.status_code not in [200, 201, 409]:
                    return JsonResponse({
                        'success': False,
                        'error': f'Erro ao criar instância: {create_response.text[:200]}'
                    }, status=400)
                
                print(f"✅ Instância criada/encontrada: {instance_name}")
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Erro ao criar instância: {e}")
                return JsonResponse({
                    'success': False,
                    'error': f'Erro ao criar instância: {str(e)}'
                }, status=400)
            
            # Passo 2: Obter QR code
            connect_url = f"{settings.EVOLUTION_API_URL}/instance/connect/{instance_name}"
            print(f"🔗 [2/2] GET {connect_url}")
            
            try:
                connect_response = requests.get(connect_url, headers=headers, timeout=10)
                connect_response.raise_for_status()
                
                api_response = connect_response.json()
                print(f"📡 API Response: {api_response}")
                
                # Tentar extrair QR code de diferentes formatos de resposta
                qr_code_base64 = None
                if isinstance(api_response, dict):
                    # Tentar vários campos possíveis
                    qr_code_base64 = (
                        api_response.get('base64') or 
                        api_response.get('qrcode') or 
                        api_response.get('qr_code') or
                        api_response.get('qr') or
                        (api_response.get('instance', {}).get('qrcode')) or
                        (api_response.get('instance', {}).get('base64'))
                    )
                
                # Limpar prefixo se já vier com data:image
                if isinstance(qr_code_base64, str) and qr_code_base64.startswith('data:image'):
                    qr_code_base64 = qr_code_base64.split(',', 1)[-1]
                
                if not qr_code_base64:
                    print(f"⚠️  Tentando gerar QR code via endpoint /qrcode/")
                    # Se não conseguiu extrair, tentar outro endpoint
                    qr_url = f"{settings.EVOLUTION_API_URL}/instance/qrcode/{instance_name}"
                    qr_response = requests.get(qr_url, headers=headers, timeout=10)
                    if qr_response.status_code == 200:
                        qr_data = qr_response.json()
                        print(f"📡 QR Endpoint Response: {qr_data}")
                        qr_code_base64 = (
                            qr_data.get('base64') or 
                            qr_data.get('qrcode') or 
                            qr_data.get('qr_code') or
                            qr_data.get('qr')
                        )
                    
                    if not qr_code_base64:
                        return JsonResponse({
                            'success': False,
                            'error': f'Evolution API não retornou QR code. Response: {api_response}'
                        }, status=400)
                
                # Criar registro no banco (PRIMEIRA VEZ)
                whatsapp = WhatsAppInstance.objects.create(
                    instance_name=instance_name,
                    phone_number="pending",
                    display_name=f"WhatsApp {tenant.name}",
                    tenant=tenant,
                    connection_status='connecting',
                    is_primary=True,
                    qr_code=qr_code_base64,
                    qr_code_expires_at=timezone.now() + timedelta(minutes=5)
                )
                
                print(f"✅ Registro criado no banco para {tenant.name}")
                
                return JsonResponse({
                    'success': True,
                    'whatsapp_id': whatsapp.id,
                    'qr_code': f"data:image/png;base64,{qr_code_base64}",
                    'expires_at': whatsapp.qr_code_expires_at.isoformat(),
                    'message': 'Escaneie o QR code para conectar seu WhatsApp!',
                    'instance_name': instance_name,
                    'is_reconnect': False
                })
                
            except requests.exceptions.RequestException as e:
                print(f"❌ Erro ao obter QR code: {e}")
                return JsonResponse({
                    'success': False,
                    'error': f'Erro ao conectar com Evolution API: {str(e)}'
                }, status=400)
    
    except Exception as e:
        print(f"❌ Erro geral em whatsapp_create: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def whatsapp_webhook_update(request):
    """Webhook para atualizações de status"""
    try:
        data = json.loads(request.body)
        
        token = request.headers.get('X-API-Key')
        if token != getattr(settings, 'WHATSAPP_WEBHOOK_API_KEY', 'secret'):
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        
        instance_id = data.get('instance_id')
        phone_number = data.get('phone_number')
        status = data.get('status')
        session_id = data.get('session_id')
        error_message = data.get('error_message', '')
        
        whatsapp = WhatsAppInstance.objects.filter(
            evolution_api__instance_id=instance_id,
            phone_number=phone_number
        ).first()
        
        if whatsapp:
            whatsapp.connection_status = status
            whatsapp.session_id = session_id
            
            if status == 'connected':
                whatsapp.connected_at = timezone.now()
                whatsapp.error_message = ''
            elif status == 'disconnected':
                whatsapp.disconnected_at = timezone.now()
            elif status == 'error':
                whatsapp.error_message = error_message
            
            whatsapp.save()
            
            return JsonResponse({'success': True})
        
        return JsonResponse({'error': 'WhatsApp not found'}, status=404)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
