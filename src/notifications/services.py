import logging
from dataclasses import dataclass
from typing import Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class WhatsappMessage:
    tenant_slug: str
    to_number: str
    message: str
    instance_name: Optional[str] = None


class EvolutionApiClient:
    """
    Cliente de integração com Evolution API (mesmo padrão usado no app de rifas)
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        instance_name: Optional[str] = None,
    ) -> None:
        self.base_url = (base_url or getattr(settings, "EVOLUTION_API_URL", "")).rstrip("/")
        self.api_key = api_key or getattr(settings, "EVOLUTION_API_KEY", "")
        self.instance_name = instance_name or getattr(settings, "EVOLUTION_INSTANCE_NAME", "")

    def _get_headers(self) -> dict:
        return {"apikey": self.api_key, "Content-Type": "application/json"}

    def _is_group(self, phone: str) -> bool:
        return "@g.us" in str(phone).lower()

    def _normalize_phone(self, phone: str) -> str:
        phone = str(phone).strip()

        if self._is_group(phone):
            return phone

        if "@" in phone:
            phone = phone.split("@")[0]

        for char in [" ", "-", "(", ")", "+"]:
            phone = phone.replace(char, "")

        phone = "".join(filter(str.isdigit, phone))

        if phone and not phone.startswith("55"):
            phone = "55" + phone

        return phone

    def _build_send_text_url(self, instance_name: str) -> str:
        base = self.base_url.rstrip("/")
        send_path = "/message/sendText"
        if base.endswith(send_path):
            return f"{base}/{instance_name}"
        return f"{base}{send_path}/{instance_name}"

    def _build_send_media_url(self, instance_name: str) -> str:
        base = self.base_url.rstrip("/")
        media_path = "/message/sendMedia"
        if base.endswith(media_path):
            return f"{base}/{instance_name}"
        return f"{base}{media_path}/{instance_name}"

    def _build_status_url(self, instance_name: str) -> str:
        base = self.base_url.rstrip("/")
        status_path = "/instance/connectionState"
        if base.endswith(status_path):
            return f"{base}/{instance_name}"
        return f"{base}{status_path}/{instance_name}"

    def send_text_message(self, phone: str, message: str, instance_name: Optional[str] = None) -> bool:
        if not self.base_url or not self.api_key:
            logger.warning("Evolution API URL ou API key não configurados.")
            return False

        target_instance = instance_name or self.instance_name
        if not target_instance:
            logger.warning("instance_name não informado para enviar WhatsApp.")
            return False

        url = self._build_send_text_url(target_instance)
        phone_normalized = self._normalize_phone(phone)
        payload = {"number": phone_normalized, "text": message}

        logger.info("📤 Enviando WhatsApp via Evolution API", extra={"url": url, "number": phone_normalized})

        try:
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            logger.info("✅ WhatsApp enviado com sucesso", extra={"response": response.text[:200]})
            return True
        except requests.exceptions.Timeout:
            logger.error("⏱️  Timeout ao enviar WhatsApp para %s", phone_normalized)
            return False
        except requests.RequestException as exc:  # pragma: no cover - chamada externa
            logger.exception("❌ Erro ao enviar WhatsApp para %s: %s", phone_normalized, exc)
            return False

    def send_media_message(
        self,
        phone: str,
        media_url: str,
        caption: str = "",
        instance_name: Optional[str] = None,
    ) -> bool:
        if not self.base_url or not self.api_key:
            logger.warning("Evolution API URL ou API key não configurados.")
            return False

        target_instance = instance_name or self.instance_name
        if not target_instance:
            logger.warning("instance_name não informado para enviar mídia pelo WhatsApp.")
            return False

        url = self._build_send_media_url(target_instance)
        phone_normalized = self._normalize_phone(phone)
        payload = {
            "number": phone_normalized,
            "mediatype": "image",
            "media": media_url,
            "caption": caption,
        }

        logger.info("📤 Enviando mídia via Evolution API", extra={"url": url, "number": phone_normalized})

        try:
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            logger.info("✅ Mídia enviada com sucesso", extra={"response": response.text[:200]})
            return True
        except requests.RequestException as exc:  # pragma: no cover - chamada externa
            logger.exception("❌ Erro ao enviar mídia para %s: %s", phone_normalized, exc)
            return False

    def check_instance_status(self, instance_name: Optional[str] = None):
        """Verifica se a instância está conectada."""
        target_instance = instance_name or self.instance_name
        if not self.base_url or not self.api_key or not target_instance:
            logger.warning("Configuração da Evolution API incompleta para checar status.")
            return None

        url = self._build_status_url(target_instance)

        try:
            response = requests.get(url, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:  # pragma: no cover - chamada externa
            logger.exception("Erro ao consultar status da Evolution API: %s", exc)
            return None

    def send_message(self, payload: WhatsappMessage) -> bool:
        if not self.base_url or not self.api_key:
            logger.warning("Evolution API credentials missing. Skipping message send.")
            return False

        return self.send_text_message(
            phone=payload.to_number,
            message=payload.message,
            instance_name=payload.instance_name or self.instance_name,
        )
