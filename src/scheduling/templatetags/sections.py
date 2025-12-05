"""
Template tags para gerenciar seções da landing page
"""

from django import template

from scheduling.views.sections_helper import (
    get_sections_config,
    get_sections_order,
    is_section_visible,
    get_section_order,
)

register = template.Library()


@register.filter
def section_visible(branding_settings, section_id):
    """
    Uso: {% if branding.branding_settings|section_visible:"about" %}
    """
    return is_section_visible(branding_settings, section_id)


@register.filter
def sections_order(branding_settings):
    """
    Retorna lista de seções visíveis em ordem
    Uso: {% for section_id in branding.branding_settings|sections_order %}
    """
    return get_sections_order(branding_settings)


@register.simple_tag
def get_section_config(branding_settings, section_id):
    """
    Retorna a configuração completa de uma seção
    Uso: {% get_section_config branding.branding_settings "about" as section_config %}
    """
    config = get_sections_config(branding_settings)
    return config.get(section_id, {})
