"""
URLs para gerenciamento de WhatsApp
"""

from django.urls import path
from scheduling.views.whatsapp_manager import (
    whatsapp_dashboard,
    whatsapp_detail,
    whatsapp_create,
    whatsapp_generate_qrcode,
    whatsapp_disconnect,
    whatsapp_set_primary,
    whatsapp_status_api,
    whatsapp_list_api,
    whatsapp_webhook_update,
)

app_name = 'whatsapp'

urlpatterns = [
    # Dashboard
    path('', whatsapp_dashboard, name='dashboard'),
    
    # Criar novo WhatsApp
    path('criar/', whatsapp_create, name='create'),
    
    # Detalhes
    path('<int:whatsapp_id>/', whatsapp_detail, name='detail'),
    
    # Ações
    path('<int:whatsapp_id>/gerar-qrcode/', whatsapp_generate_qrcode, name='generate_qrcode'),
    path('<int:whatsapp_id>/desconectar/', whatsapp_disconnect, name='disconnect'),
    path('<int:whatsapp_id>/set-primary/', whatsapp_set_primary, name='set_primary'),
    
    # APIs (para frontend)
    path('<int:whatsapp_id>/status/', whatsapp_status_api, name='status_api'),
    path('list/api/', whatsapp_list_api, name='list_api'),
    
    # Webhook (para Evolution API)
    path('webhook/update/', whatsapp_webhook_update, name='webhook_update'),
]
