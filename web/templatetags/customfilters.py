# En tu app/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def sum_attr(listado, attr_path):
    total = 0
    for item in listado:
        value = item
        for part in attr_path.split('.'):
            try:
                value = getattr(value, part)
            except AttributeError:
                try:
                    value = value.get(part)
                except (AttributeError, KeyError, TypeError):
                    value = 0
                    break
        try:
            total += int(value)
        except (ValueError, TypeError):
            pass
    return total

@register.filter
def sub(value, arg):
    """Resta el arg del value"""
    return value - arg

@register.filter
def get_item(dictionary, key):
    """
    Allows dictionary lookup with a variable key in Django templates.
    Usage: {{ my_dict|get_item:my_key }}
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None # Return None if not a dictionary or key not found