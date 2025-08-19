from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Inventario)
admin.site.register(TipoInsumo)
admin.site.register(Insumo)
admin.site.register(Lote)
admin.site.register(Movimiento)
