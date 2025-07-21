from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(CategoriaHerramienta)
admin.site.register(Herramienta)
admin.site.register(AsignacionHerramienta)
admin.site.register(Servicios)
admin.site.register(Reportes_Unidades)
admin.site.register(Unidades_Detalles)
admin.site.register(Conductor)
admin.site.register(LicenciaConductor)
admin.site.register(CertificadoMedico)