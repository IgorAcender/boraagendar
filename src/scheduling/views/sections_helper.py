"""
Helper para gerenciar a configuração e ordem das seções da landing page
"""

from typing import Dict, List, Tuple


def get_sections_config(branding_settings) -> Dict[str, Dict]:
    """
    Retorna a configuração de seções do branding settings.
    
    Se não houver configuração, retorna ordem padrão com todas visíveis.
    
    Formato:
    {
        "about": {"visible": true, "order": 0},
        "team": {"visible": true, "order": 1},
        ...
    }
    """
    if not branding_settings or not branding_settings.sections_config:
        # Ordem padrão
        return {
            "about": {"visible": True, "order": 0},
            "team": {"visible": True, "order": 1},
            "hours": {"visible": True, "order": 2},
            "contact": {"visible": True, "order": 3},
            "location": {"visible": True, "order": 4},
            "amenities": {"visible": True, "order": 5},
            "payment_methods": {"visible": True, "order": 6},
            "social": {"visible": True, "order": 7},
        }
    
    return branding_settings.sections_config


def get_sections_order(branding_settings) -> List[str]:
    """
    Retorna lista de IDs de seções em ordem, incluindo apenas as visíveis.
    """
    config = get_sections_config(branding_settings)
    
    # Filtra apenas visíveis e ordena
    visible_sections = [
        (section_id, data['order'])
        for section_id, data in config.items()
        if data.get('visible', True)
    ]
    
    # Ordena por número de ordem
    visible_sections.sort(key=lambda x: x[1])
    
    return [section_id for section_id, _ in visible_sections]


def is_section_visible(branding_settings, section_id: str) -> bool:
    """
    Verifica se uma seção deve ser exibida.
    """
    config = get_sections_config(branding_settings)
    return config.get(section_id, {}).get('visible', True)


def get_section_order(branding_settings, section_id: str) -> int:
    """
    Retorna a posição de uma seção na ordem.
    """
    config = get_sections_config(branding_settings)
    return config.get(section_id, {}).get('order', 999)
