from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """
    Template filter to get an item from a dictionary by key.
    Usage: {{ my_dict|get_item:key }}
    """
    if dictionary is None:
        return {}
    return dictionary.get(key, {} if isinstance(dictionary, dict) else [])


@register.filter
def darker_color(hex_color, percent=0.8):
    """
    Template filter para escurecer uma cor.
    Por padrão, escurece 20% (multiplica por 0.8).
    Usage: {{ branding.button_color_primary|darker_color }}
    """
    try:
        hex_color = str(hex_color).lstrip("#")
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Escurecer multiplicando pelo percentual
        r = max(0, int(r * float(percent)))
        g = max(0, int(g * float(percent)))
        b = max(0, int(b * float(percent)))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    except:
        return hex_color

