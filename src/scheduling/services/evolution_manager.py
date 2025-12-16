"""
Serviço para selecionar a melhor instância Evolution API
Usa load balancing entre múltiplas instâncias
"""

import logging
from typing import Optional

from django.conf import settings
from django.db.models import F, Count

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
        2. Com espaço disponível (compatível com esquemas antigos)
        3. Maior prioridade
        4. Menor uso (load balancing)
        """
        # Descobre nomes de campos conforme o schema em uso
        capacity_field = "whatsapp_capacity" if "whatsapp_capacity" in [f.name for f in EvolutionAPI._meta.fields] else "capacity"
        connected_field = "whatsapp_connected" if "whatsapp_connected" in [f.name for f in EvolutionAPI._meta.fields] else None

        queryset = EvolutionAPI.objects.filter(is_active=True)

        if connected_field:
            # Usa campo dedicado, se existir
            queryset = queryset.filter(**{f"{connected_field}__lt": F(capacity_field)}).order_by(
                "-priority",
                connected_field,
            )
        else:
            # Fallback: conta quantos WhatsApps estão relacionados
            queryset = (
                queryset.annotate(connected_count=Count("whatsapp_instances"))
                .filter(connected_count__lt=F(capacity_field))
                .order_by("-priority", "connected_count")
            )

        instance = queryset.first()
        
        if not instance:
            logger.warning("Nenhuma instância Evolution API disponível")
            return None
        
        # Log seguro para diferentes esquemas
        name = getattr(instance, "name", None) or getattr(instance, "instance_id", "sem-nome")
        capacity_val = getattr(instance, capacity_field, None)
        connected_val = getattr(instance, connected_field or "connected_count", None)
        logger.info(f"Selecionada Evolution API: {name} ({connected_val}/{capacity_val})")
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
        wa_fields = [f.name for f in WhatsAppInstance._meta.fields]
        status_field = "connection_status" if "connection_status" in wa_fields else "status"
        is_active_field = "is_active" if "is_active" in wa_fields else None

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
                **({is_active_field: True} if is_active_field else {}),
                **{status_field: "connected"},
            )
            .order_by("-is_primary", "-connected_at")
            .first()
            or WhatsAppInstance.objects.filter(
                tenant__slug=tenant_slug,
                **({is_active_field: True} if is_active_field else {}),
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
        
        evo_name = getattr(evolution_api, "name", None) or getattr(evolution_api, "instance_id", "EvolutionAPI")
        if success:
            logger.info(f"Mensagem enviada via {evo_name}")
        else:
            logger.error(f"Falha ao enviar via {evo_name}")
        
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
        
        evo_name_field = "evolution_api__name"
        if "name" not in [f.name for f in EvolutionAPI._meta.fields] and "instance_id" in [f.name for f in EvolutionAPI._meta.fields]:
            evo_name_field = "evolution_api__instance_id"
        return query.order_by(evo_name_field, "-is_primary")
    
    @staticmethod
    def get_usage_stats():
        """Retorna estatísticas de uso de todas as instâncias"""
        capacity_field = "whatsapp_capacity" if "whatsapp_capacity" in [f.name for f in EvolutionAPI._meta.fields] else "capacity"
        connected_field = "whatsapp_connected" if "whatsapp_connected" in [f.name for f in EvolutionAPI._meta.fields] else None

        instances = EvolutionAPI.objects.filter(is_active=True)
        if not connected_field:
            instances = instances.annotate(connected_count=Count("whatsapp_instances"))

        stats = {
            "total_instances": instances.count(),
            "total_capacity": sum(getattr(i, capacity_field, 0) or 0 for i in instances),
            "total_connected": sum(
                getattr(i, connected_field or "connected_count", 0) or 0 for i in instances
            ),
            "instances": []
        }
        
        for instance in instances:
            connected_val = getattr(instance, connected_field or "connected_count", 0) or 0
            capacity_val = getattr(instance, capacity_field, 0) or 0
            available = max(capacity_val - connected_val, 0) if capacity_val else 0
            usage_percentage = int((connected_val / capacity_val) * 100) if capacity_val else 0
            name = getattr(instance, "name", None) or getattr(instance, "instance_id", "sem-nome")
            stats["instances"].append({
                "name": name,
                "url": instance.url,
                "connected": connected_val,
                "capacity": capacity_val,
                "available": available,
                "usage_percentage": usage_percentage,
                "status": "✅ Online" if instance.is_active else "❌ Offline"
            })
        
        return stats
