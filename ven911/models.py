from django.contrib.auth import get_user_model
from django.db import models
from django.db import models
from web.models import Personal,Unidades
# Create your models here.

class TipoServicio(models.Model):
    """Modelo para los tipos de servicios"""
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre

class Servicio(models.Model):
    # agregar canoi de cabtudad de tipo de servicio
    """Modelo principal para los servicios"""
    tipo_servicio = models.ForeignKey(TipoServicio, on_delete=models.SET_NULL, null=True, blank=False)
    cantidad_tipo_servicio = models.IntegerField(default=1, blank=False, null=False)
    operador_de_guardia = models.ForeignKey(Personal, on_delete=models.SET_NULL, null=True, blank=False,related_name='servicios_como_operador')
    fecha = models.DateField(default="1999-02-02", blank=False, null=False)
    hora = models.TimeField(default="00:00", blank=False, null=False)
    
    def __str__(self):
        return f"Servicio {self.id} - {self.fecha} - {self.operador_de_guardia} - {self.tipo_servicio.nombre} - Cantidad: {self.cantidad_tipo_servicio}"