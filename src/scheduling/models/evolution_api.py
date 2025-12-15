"""
Modelo para gerenciar múltiplas instâncias de Evolution API
Cada instância pode ter até 20 WhatsApps conectados
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class EvolutionAPI(models.Model):
    """
    Representa uma instância do Evolution API
    Cada instância pode conter até 20 WhatsApps
    """
    
    name = models.CharField(
        max_length=100,
        verbose_name=_("Nome da Instância"),
        help_text="Ex: Evolution API 1, Evolution API 2, etc"
    )
    
    url = models.URLField(
        verbose_name=_("URL da API"),
        help_text="Ex: https://evo1.seu-dominio.com/message/sendText"
    )
    
    api_key = models.CharField(
        max_length=500,
        verbose_name=_("API Key"),
        help_text="Chave de autenticação da instância"
    )
    
    whatsapp_capacity = models.IntegerField(
        default=20,
        verbose_name=_("Capacidade de WhatsApps"),
        help_text="Máximo de WhatsApps que pode conectar (recomendado: 20)"
    )
    
    whatsapp_connected = models.IntegerField(
        default=0,
        verbose_name=_("WhatsApps Conectados"),
        help_text="Número de WhatsApps atualmente conectados"
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Ativa"),
        help_text="Se desativada, não será usada para enviar mensagens"
    )
    
    priority = models.IntegerField(
        default=0,
        verbose_name=_("Prioridade"),
        help_text="Maior número = maior prioridade (0-10)"
    )
    
    notes = models.TextField(
        blank=True,
        verbose_name=_("Observações"),
        help_text="Notas internas sobre esta instância"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("Evolution API")
        verbose_name_plural = _("Evolution APIs")
        ordering = ["-priority", "name"]
    
    def __str__(self):
        status = "✅" if self.is_active else "❌"
        return f"{status} {self.name} ({self.whatsapp_connected}/{self.whatsapp_capacity})"
    
    @property
    def has_capacity(self):
        """Verifica se ainda pode adicionar WhatsApps"""
        return self.whatsapp_connected < self.whatsapp_capacity
    
    @property
    def available_slots(self):
        """Retorna quantos WhatsApps ainda podem ser adicionados"""
        return self.whatsapp_capacity - self.whatsapp_connected
    
    def get_usage_percentage(self):
        """Retorna o percentual de uso"""
        if self.whatsapp_capacity == 0:
            return 0
        return int((self.whatsapp_connected / self.whatsapp_capacity) * 100)


class WhatsAppInstance(models.Model):
    """
    Representa um WhatsApp individual dentro de uma instância Evolution API
    """
    
    STATUS_CHOICES = (
        ("disconnected", _("Desconectado")),
        ("connecting", _("Conectando")),
        ("connected", _("Conectado")),
        ("error", _("Erro")),
    )
    
    evolution_api = models.ForeignKey(
        EvolutionAPI,
        on_delete=models.CASCADE,
        related_name="whatsapp_instances",
        verbose_name=_("Instância Evolution API")
    )
    
    phone_number = models.CharField(
        max_length=20,
        verbose_name=_("Número de WhatsApp"),
        help_text="Formato: 5511987654321"
    )
    
    display_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Nome de Exibição"),
        help_text="Como o WhatsApp aparece nos contatos"
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="disconnected",
        verbose_name=_("Status")
    )
    
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_("Principal"),
        help_text="WhatsApp principal para agendamentos"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _("WhatsApp Instance")
        verbose_name_plural = _("WhatsApp Instances")
        ordering = ["evolution_api", "-is_primary", "phone_number"]
        unique_together = ("evolution_api", "phone_number")
    
    def __str__(self):
        status_icon = {
            "connected": "✅",
            "connecting": "⏳",
            "disconnected": "❌",
            "error": "⚠️",
        }
        return f"{status_icon.get(self.status, '❓')} {self.phone_number} ({self.evolution_api.name})"
