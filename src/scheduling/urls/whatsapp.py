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
    whatsapp_send_test,
)
from scheduling.views.whatsapp_debug import whatsapp_create_debug

app_name = 'whatsapp'

urlpatterns = [
    # Dashboard
    path('', whatsapp_dashboard, name='dashboard'),
    
    # Debug
    path('debug/criar/', whatsapp_create_debug, name='create_debug'),
    
    # Criar novo WhatsApp
    path('criar/', whatsapp_create, name='create'),
    
    # Detalhes
    path('<int:id>/', whatsapp_detail, name='detail'),
    
    # Ações
    path('<int:id>/gerar-qrcode/', whatsapp_generate_qrcode, name='generate_qrcode'),
    path('<int:id>/desconectar/', whatsapp_disconnect, name='disconnect'),
    path('<int:id>/set-primary/', whatsapp_set_primary, name='set_primary'),
    
    # APIs (para frontend)
    path('<int:id>/status/', whatsapp_status_api, name='status_api'),
    path('list/api/', whatsapp_list_api, name='list_api'),
    path('send-test/', whatsapp_send_test, name='send_test'),
    
    # Webhook (para Evolution API)
    path('webhook/update/', whatsapp_webhook_update, name='webhook_update'),
]
