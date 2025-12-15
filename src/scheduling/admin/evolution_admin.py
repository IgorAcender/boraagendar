"""
Admin para gerenciar múltiplas instâncias de Evolution API
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from scheduling.models import EvolutionAPI, WhatsAppInstance


@admin.register(EvolutionAPI)
class EvolutionAPIAdmin(admin.ModelAdmin):
    """Admin para gerenciar instâncias da Evolution API"""
    
    list_display = (
        "name_with_status",
        "whatsapp_usage_bar",
        "priority",
        "is_active",
        "created_at"
    )
    
    list_filter = ("is_active", "priority", "created_at")
    search_fields = ("name", "url")
    
    fieldsets = (
        (_("Informações Básicas"), {
            "fields": ("name", "is_active", "priority")
        }),
        (_("Configuração da API"), {
            "fields": ("url", "api_key")
        }),
        (_("Capacidade"), {
            "fields": ("whatsapp_capacity", "whatsapp_connected"),
            "description": _("Máximo de WhatsApps e quantos estão conectados")
        }),
        (_("Observações"), {
            "fields": ("notes",),
            "classes": ("collapse",)
        }),
    )
    
    readonly_fields = ("created_at", "updated_at")
    
    def name_with_status(self, obj):
        """Mostra nome com ícone de status"""
        status_icon = "✅" if obj.is_active else "❌"
        return f"{status_icon} {obj.name}"
    name_with_status.short_description = _("Instância")
    
    def whatsapp_usage_bar(self, obj):
        """Mostra barra de progresso de uso"""
        usage = obj.get_usage_percentage()
        
        # Cores baseadas no uso
        if usage < 50:
            color = "#28a745"  # Verde
        elif usage < 80:
            color = "#ffc107"  # Amarelo
        else:
            color = "#dc3545"  # Vermelho
        
        bar_html = (
            f'<div style="'
            f'width: 200px; '
            f'height: 20px; '
            f'background-color: #e9ecef; '
            f'border-radius: 5px; '
            f'overflow: hidden; '
            f'display: inline-block;">'
            f'<div style="'
            f'width: {usage}%; '
            f'height: 100%; '
            f'background-color: {color}; '
            f'transition: width 0.3s;">'
            f'</div></div>'
            f'<span style="margin-left: 10px;">{usage}%</span> '
            f'({obj.whatsapp_connected}/{obj.whatsapp_capacity})'
        )
        
        return format_html(bar_html)
    whatsapp_usage_bar.short_description = _("Uso de Capacidade")


@admin.register(WhatsAppInstance)
class WhatsAppInstanceAdmin(admin.ModelAdmin):
    """Admin para gerenciar WhatsApps individuais"""
    
    list_display = (
        "phone_with_status",
        "evolution_api",
        "display_name",
        "is_primary_badge",
        "status_badge"
    )
    
    list_filter = ("status", "is_primary", "evolution_api", "created_at")
    search_fields = ("phone_number", "display_name", "evolution_api__name")
    
    fieldsets = (
        (_("Informações Básicas"), {
            "fields": ("evolution_api", "phone_number", "display_name")
        }),
        (_("Status"), {
            "fields": ("status", "is_primary")
        }),
    )
    
    readonly_fields = ("created_at", "updated_at")
    
    def phone_with_status(self, obj):
        """Mostra número com ícone de status"""
        status_icons = {
            "connected": "✅",
            "connecting": "⏳",
            "disconnected": "❌",
            "error": "⚠️",
        }
        icon = status_icons.get(obj.status, "❓")
        return f"{icon} {obj.phone_number}"
    phone_with_status.short_description = _("WhatsApp")
    
    def is_primary_badge(self, obj):
        """Mostra se é principal"""
        if obj.is_primary:
            return format_html('<span style="color: #28a745; font-weight: bold;">⭐ Principal</span>')
        return "Secundário"
    is_primary_badge.short_description = _("Tipo")
    
    def status_badge(self, obj):
        """Mostra status com cores"""
        colors = {
            "connected": "#28a745",
            "connecting": "#ffc107",
            "disconnected": "#6c757d",
            "error": "#dc3545",
        }
        color = colors.get(obj.status, "#6c757d")
        labels = {
            "connected": _("Conectado"),
            "connecting": _("Conectando"),
            "disconnected": _("Desconectado"),
            "error": _("Erro"),
        }
        label = labels.get(obj.status, obj.status)
        
        return format_html(
            '<span style="color: white; background-color: {}; padding: 5px 10px; border-radius: 3px;">{}</span>',
            color,
            label
        )
    status_badge.short_description = _("Status")
