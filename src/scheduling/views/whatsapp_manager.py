"""
Views para gerenciamento de WhatsApp pelo dono da barbearia

O dono pode:
- Ver WhatsApps conectados/desconectados
- Gerar QR code para conectar
- Desconectar WhatsApp
- Ver status de conexão
- Gerenciar múltiplos WhatsApps
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Q
import json
import base64
from io import BytesIO
import qrcode

from scheduling.models import WhatsAppInstance, EvolutionAPI
from tenants.models import Tenant
from tenants.utils import get_tenant_from_request


@login_required
def whatsapp_dashboard(request):
    """
    Dashboard principal de gerenciamento de WhatsApp
    Mostra status de todos os WhatsApps do tenant
    """
    tenant = get_tenant_from_request(request)
    
    if not tenant:
        return redirect('login')
    
    # Buscar todos os WhatsApps do tenant
    whatsapps = WhatsAppInstance.objects.filter(
        tenant=tenant
    ).select_related('evolution_api').order_by('-is_primary', '-connected_at')
    
    # Contar por status
    stats = {
        'total': whatsapps.count(),
        'conectados': whatsapps.filter(connection_status='connected').count(),
        'desconectados': whatsapps.filter(connection_status='disconnected').count(),
        'pendentes': whatsapps.filter(connection_status='pending').count(),
        'erros': whatsapps.filter(connection_status='error').count(),
    }
    
    context = {
        'whatsapps': whatsapps,
        'stats': stats,
        'tenant': tenant,
        'has_primary': whatsapps.filter(is_primary=True).exists(),
    }
    
    return render(request, 'whatsapp/dashboard.html', context)


@login_required
def whatsapp_detail(request, whatsapp_id):
    """
    Página de detalhes de um WhatsApp específico
    Mostra QR code, status, histórico de conexões
    """
    tenant = get_tenant_from_request(request)
    
    whatsapp = get_object_or_404(
        WhatsAppInstance,
        id=whatsapp_id,
        tenant=tenant
    )
    
    context = {
        'whatsapp': whatsapp,
        'qr_code_valid': whatsapp.qr_code_is_valid,
        'status_display': whatsapp.get_status_display_verbose(),
        'evolution_api': whatsapp.evolution_api,
    }
    
    return render(request, 'whatsapp/detail.html', context)


@login_required
@require_http_methods(["POST"])
def whatsapp_generate_qrcode(request, whatsapp_id):
    """
    Gerar QR code para conectar um WhatsApp
    Retorna QR code em Base64
    """
    tenant = get_tenant_from_request(request)
    
    whatsapp = get_object_or_404(
        WhatsAppInstance,
        id=whatsapp_id,
        tenant=tenant
    )
    
    try:
        # Aqui você chamaria a API do Evolution para gerar QR code
        # Por enquanto, criamos um QR code dummy como exemplo
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # Usar o session_id ou phone_number como conteúdo
        qr_content = f"evolution://{whatsapp.evolution_api.instance_id}/{whatsapp.phone_number}"
        qr.add_data(qr_content)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Converter para Base64
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        # Salvar no banco
        whatsapp.qr_code = img_str
        whatsapp.qr_code_expires_at = timezone.now() + timezone.timedelta(minutes=5)
        whatsapp.connection_status = 'pending'
        whatsapp.save()
        
        return JsonResponse({
            'success': True,
            'qr_code': f"data:image/png;base64,{img_str}",
            'expires_at': whatsapp.qr_code_expires_at.isoformat(),
            'message': 'QR code gerado com sucesso! Aponte sua câmera para conectar.'
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
def whatsapp_disconnect(request, whatsapp_id):
    """
    Desconectar um WhatsApp
    """
    tenant = get_tenant_from_request(request)
    
    whatsapp = get_object_or_404(
        WhatsAppInstance,
        id=whatsapp_id,
        tenant=tenant
    )
    
    try:
        # Aqui você chamaria a API do Evolution para desconectar
        # Por enquanto, apenas mudamos o status
        
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
def whatsapp_set_primary(request, whatsapp_id):
    """
    Definir um WhatsApp como principal
    """
    tenant = get_tenant_from_request(request)
    
    whatsapp = get_object_or_404(
        WhatsAppInstance,
        id=whatsapp_id,
        tenant=tenant
    )
    
    if not whatsapp.is_connected:
        return JsonResponse({
            'success': False,
            'error': 'Apenas WhatsApps conectados podem ser principais'
        }, status=400)
    
    try:
        # Remover primary de todos os outros
        WhatsAppInstance.objects.filter(
            tenant=tenant
        ).update(is_primary=False)
        
        # Definir este como primary
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
def whatsapp_status_api(request, whatsapp_id):
    """
    API para obter status atual de um WhatsApp
    Útil para atualização em tempo real no frontend
    """
    tenant = get_tenant_from_request(request)
    
    whatsapp = get_object_or_404(
        WhatsAppInstance,
        id=whatsapp_id,
        tenant=tenant
    )
    
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
    """
    API para listar todos os WhatsApps do tenant em JSON
    """
    tenant = get_tenant_from_request(request)
    
    whatsapps = WhatsAppInstance.objects.filter(
        tenant=tenant
    ).values(
        'id', 'phone_number', 'connection_status', 
        'is_primary', 'is_active', 'display_name'
    ).order_by('-is_primary', '-connected_at')
    
    return JsonResponse({
        'count': len(list(whatsapps)),
        'whatsapps': list(whatsapps)
    })


@login_required
@require_http_methods(["POST"])
def whatsapp_webhook_update(request):
    """
    Webhook para receber atualizações de status do Evolution API
    Chamado quando WhatsApp conecta/desconecta
    """
    try:
        data = json.loads(request.body)
        
        # Verificar token de segurança
        token = request.headers.get('X-API-Key')
        if token != 'seu-token-secreto-aqui':
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        
        instance_id = data.get('instance_id')
        phone_number = data.get('phone_number')
        status = data.get('status')  # connected, disconnected, error
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
