"""
Serviço para selecionar a melhor instância Evolution API
Usa load balancing entre múltiplas instâncias
"""

import logging
from typing import Optional

from django.conf import settings
from django.db.models import F

from scheduling.models import EvolutionAPI, WhatsAppInstance
from notifications.services import EvolutionApiClient, WhatsappMessage

logger = logging.getLogger(__name__)


class EvolutionAPIManager:
    """Gerencia seleção e envio via múltiplas Evolution APIs"""
    
    @staticmethod
    def get_best_instance() -> Optional[EvolutionAPI]:
        """
        Seleciona a melhor instância Evolution API disponível
        
        Critérios:
        1. Ativa
        2. Com espaço disponível
        3. Maior prioridade
        4. Menor uso (load balancing)
        """
        instance = EvolutionAPI.objects.filter(
            is_active=True,
            whatsapp_connected__lt=F("whatsapp_capacity")  # Tem espaço
        ).order_by(
            "-priority",  # Maior prioridade primeiro
            "whatsapp_connected",  # Depois a menos usada
        ).first()
        
        if not instance:
            logger.warning("Nenhuma instância Evolution API disponível")
            return None
        
        logger.info(f"Selecionada Evolution API: {instance.name} ({instance.whatsapp_connected}/{instance.whatsapp_capacity})")
        return instance
    
    @staticmethod
    def get_instance_by_name(name: str) -> Optional[EvolutionAPI]:
        """Busca instância por nome"""
        return EvolutionAPI.objects.filter(
            name__iexact=name,
            is_active=True
        ).first()
    
    @staticmethod
    def get_all_active_instances():
        """Retorna todas as instâncias ativas"""
        return EvolutionAPI.objects.filter(is_active=True).order_by("-priority")
    
    @staticmethod
    def send_message_auto(
        tenant_slug: str,
        to_number: str,
        message: str,
        evolution_api: Optional[EvolutionAPI] = None
    ) -> bool:
        """
        Envia mensagem automaticamente para a melhor instância disponível
        
        Args:
            tenant_slug: Slug do tenant
            to_number: Número do WhatsApp
            message: Mensagem a enviar
            evolution_api: Instância específica (se None, auto-seleciona)
        
        Returns:
            bool: True se enviado com sucesso
        """
        # Se não especificou instância, seleciona automaticamente
        if evolution_api is None:
            evolution_api = EvolutionAPIManager.get_best_instance()
        if not evolution_api:
            logger.error("Nenhuma Evolution API disponível para enviar mensagem")
            return False

        # Seleciona o WhatsApp principal/ativo do tenant
        whatsapp_instance = (
            WhatsAppInstance.objects.filter(
                tenant__slug=tenant_slug,
                is_active=True,
                connection_status="connected",
            )
            .order_by("-is_primary", "-connected_at")
            .first()
            or WhatsAppInstance.objects.filter(
                tenant__slug=tenant_slug,
                is_active=True,
            )
            .order_by("-is_primary", "-connected_at")
            .first()
        )

        # Descobre credenciais e instance_name a partir do WhatsApp ou dos defaults
        api_url = None
        api_key = None
        instance_name = None

        if whatsapp_instance:
            instance_name = whatsapp_instance.instance_name or instance_name
            if whatsapp_instance.evolution_api and evolution_api is None:
                evolution_api = whatsapp_instance.evolution_api

        if evolution_api:
            api_url = evolution_api.url or api_url
            api_key = evolution_api.api_key or api_key
            instance_name = instance_name or evolution_api.instance_id

        api_url = (api_url or getattr(settings, "EVOLUTION_API_URL", "")).rstrip("/")
        api_key = api_key or getattr(settings, "EVOLUTION_API_KEY", "")
        instance_name = instance_name or getattr(settings, "EVOLUTION_INSTANCE_NAME", "")

        if not api_url or not api_key or not instance_name:
            logger.error("Configuração da Evolution API incompleta (url/api_key/instance_name).")
            return False

        # Criar cliente e enviar
        client = EvolutionApiClient(
            base_url=api_url,
            api_key=api_key,
            instance_name=instance_name,
        )
        
        payload = WhatsappMessage(
            tenant_slug=tenant_slug,
            to_number=to_number,
            message=message,
            instance_name=instance_name,
        )
        
        success = client.send_message(payload)
        
        if success:
            logger.info(f"Mensagem enviada via {evolution_api.name}")
        else:
            logger.error(f"Falha ao enviar via {evolution_api.name}")
        
        return success
    
    @staticmethod
    def get_connected_whatsapps(evolution_api: Optional[EvolutionAPI] = None):
        """
        Retorna lista de WhatsApps conectados
        
        Args:
            evolution_api: Se especificada, retorna apenas os da instância
        """
        query = WhatsAppInstance.objects.filter(status="connected")
        
        if evolution_api:
            query = query.filter(evolution_api=evolution_api)
        
        return query.order_by("evolution_api__name", "-is_primary")
    
    @staticmethod
    def get_usage_stats():
        """Retorna estatísticas de uso de todas as instâncias"""
        instances = EvolutionAPI.objects.filter(is_active=True)
        
        stats = {
            "total_instances": instances.count(),
            "total_capacity": sum(i.whatsapp_capacity for i in instances),
            "total_connected": sum(i.whatsapp_connected for i in instances),
            "instances": []
        }
        
        for instance in instances:
            stats["instances"].append({
                "name": instance.name,
                "url": instance.url,
                "connected": instance.whatsapp_connected,
                "capacity": instance.whatsapp_capacity,
                "available": instance.available_slots,
                "usage_percentage": instance.get_usage_percentage(),
                "status": "✅ Online" if instance.is_active else "❌ Offline"
            })
        
        return stats
