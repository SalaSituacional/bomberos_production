from django import template

register = template.Library()

@register.filter
def get_unidad_nombre(unidades, unidad_id):
    try:
        unidad_id = int(unidad_id)
        for unidad in unidades:
            if unidad.id == unidad_id:
                return unidad.nombre_unidad
        return "Unidad no encontrada"
    except (ValueError, TypeError):
        return "Todas las unidades"