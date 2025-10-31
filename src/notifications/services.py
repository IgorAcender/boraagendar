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


class EvolutionApiClient:
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None) -> None:
        self.base_url = base_url or getattr(settings, "EVOLUTION_API_URL", "")
        self.api_key = api_key or getattr(settings, "EVOLUTION_API_KEY", "")

    def send_message(self, payload: WhatsappMessage) -> bool:
        if not self.base_url or not self.api_key:
            logger.warning("Evolution API credentials missing. Skipping message send.")
            return False

        data = {
            "tenant": payload.tenant_slug,
            "to": payload.to_number,
            "message": payload.message,
        }
        headers = {"Authorization": f"Bearer {self.api_key}"}

        try:
            response = requests.post(self.base_url, json=data, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.RequestException as exc:  # pragma: no cover - network call
            logger.exception("Failed to send WhatsApp message: %s", exc)
            return False
        return True
