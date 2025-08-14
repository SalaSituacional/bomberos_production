from django.contrib import admin
from .models import Dependencia, BienMunicipal, MovimientoBien, CambiarEstadoBien
# Register your models here.
admin.site.register(Dependencia)
admin.site.register(BienMunicipal)
admin.site.register(MovimientoBien)
admin.site.register(CambiarEstadoBien)