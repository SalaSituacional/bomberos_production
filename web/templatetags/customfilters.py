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