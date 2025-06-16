from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(CategoriaHerramienta)
admin.site.register(Herramienta)
admin.site.register(AsignacionHerramienta)
admin.site.register(InventarioUnidad)
admin.site.register(DetalleInventario)
admin.site.register(Servicios)