from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json

@login_required
def whatsapp_create_debug(request):
    """Debug version para testar se o endpoint responde"""
    try:
        data = json.loads(request.body) if request.body else {}
        
        return JsonResponse({
            'success': True,
            'debug': 'Este é um endpoint de debug',
            'request_method': request.method,
            'user': str(request.user),
            'has_body': bool(request.body),
            'message': 'Endpoint respondendo corretamente!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
