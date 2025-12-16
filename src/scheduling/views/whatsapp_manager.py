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
    """Criar um novo WhatsApp para o tenant - VERSÃO SIMPLIFICADA COMO RIFAS"""
    tenant, redirect_response = _get_tenant_or_redirect(request)
    if redirect_response:
        return redirect_response
    
    try:
        # Verificar se as variáveis de ambiente estão configuradas
        if not settings.EVOLUTION_API_URL or not settings.EVOLUTION_API_KEY:
            return JsonResponse({
                'success': False,
                'error': 'Evolution API não configurada. Verifique as variáveis EVOLUTION_API_URL e EVOLUTION_API_KEY'
            }, status=500)
        
        data = json.loads(request.body) if request.body else {}
        
        # Gerar instance_name único para este tenant
        wa_count = WhatsAppInstance.objects.filter(tenant=tenant).count() + 1
        instance_name = f"{tenant.slug}_wa_{wa_count}"
        
        # Requisitar QR code DA EVOLUTION API (IGUAL AO RIFAS!)
        try:
            url = f"{settings.EVOLUTION_API_URL}/instance/connect/{instance_name}"
            headers = {'apikey': settings.EVOLUTION_API_KEY}
            
            print(f"🔗 [RIFAS PATTERN] Requisitando QR code de: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            api_response = response.json()
            qr_code_base64 = api_response.get('base64', '')
            
            if not qr_code_base64:
                return JsonResponse({
                    'success': False,
                    'error': 'Evolution API não retornou QR code'
                }, status=400)
            
            # Criar instância WhatsApp no banco (SEM evolution_api FK)
            whatsapp = WhatsAppInstance.objects.create(
                phone_number=f"pending_{wa_count}",
                display_name=data.get('display_name', f'WhatsApp #{wa_count}'),
                tenant=tenant,
                connection_status='pending',
                is_primary=wa_count == 1,
                qr_code=qr_code_base64,
                qr_code_expires_at=timezone.now() + timedelta(minutes=5),
                instance_name=instance_name  # Salvar o instance_name
            )
            
            return JsonResponse({
                'success': True,
                'whatsapp_id': whatsapp.id,
                'qr_code': f"data:image/png;base64,{qr_code_base64}",
                'expires_at': whatsapp.qr_code_expires_at.isoformat(),
                'message': 'Aponte sua câmera para o QR code para conectar seu WhatsApp!',
                'instance_name': instance_name
            })
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao conectar com Evolution API: {e}")
            return JsonResponse({
                'success': False,
                'error': f'Erro ao conectar com Evolution API: {str(e)}'
            }, status=400)
        except Exception as qr_error:
            print(f"❌ Erro ao processar resposta da Evolution API: {qr_error}")
            return JsonResponse({
                'success': False,
                'error': f'Erro ao processar QR code: {str(qr_error)}'
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
