from django.http import HttpRequest
from .models import BrandingSettings


def branding(request: HttpRequest) -> dict:
    """
    Context processor que adiciona configurações de branding do tenant aos templates.
    """
    context = {
        "branding": None,
    }
    
    # Verifica se há um tenant no request (via middleware de multi-tenancy)
    if hasattr(request, "tenant") and request.tenant:
        try:
            branding_settings = request.tenant.branding_settings
            context["branding"] = {
                "background_color": branding_settings.background_color,
                "text_color": branding_settings.text_color,
                "button_color_primary": branding_settings.button_color_primary,
                "button_color_secondary": branding_settings.button_color_secondary,
                "button_text_color": branding_settings.button_text_color,
                "use_gradient_buttons": branding_settings.use_gradient_buttons,
                "button_hover_color": branding_settings.get_hover_color(branding_settings.button_color_primary),
            }
        except BrandingSettings.DoesNotExist:
            # Se não houver BrandingSettings, usa cores padrão
            context["branding"] = {
                "background_color": "#0F172A",
                "text_color": "#E2E8F0",
                "button_color_primary": "#667EEA",
                "button_color_secondary": "#764BA2",
                "button_text_color": "#FFFFFF",
                "use_gradient_buttons": True,
                "button_hover_color": "#8090F6",
            }
    
    return context
