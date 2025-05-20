from django.contrib.auth import get_user_model
from django.db import models
from django.db import models
from web.models import Personal,Municipios,Parroquias,Unidades
# Create your models here.

class TipoServicio(models.Model):
    """Modelo para los tipos de servicios"""
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre

class Servicio(models.Model):
    """Modelo principal para los servicios"""
    tipo_servicio = models.ForeignKey(TipoServicio, on_delete=models.SET_NULL, null=True, blank=False)
    operador_de_guardia = models.ForeignKey(Personal, on_delete=models.SET_NULL, null=True, blank=False,related_name='servicios_como_operador')
    fecha = models.DateField()
    hora = models.TimeField()
    lugar = models.CharField(max_length=100, blank=False)
    municipio = models.ForeignKey(Municipios, on_delete=models.SET_NULL, null=True, blank=False)
    parroquia = models.ForeignKey(Parroquias, on_delete=models.SET_NULL, null=True, blank=False)
    unidad = models.ForeignKey(Unidades, on_delete=models.SET_NULL, null=True, blank=False)
    jefe_de_comision = models.ForeignKey(Personal, on_delete=models.SET_NULL, null=True, blank=False,related_name='servicios_como_jefe')
    descripcion = models.TextField()
    
    def __str__(self):
        return f"Servicio {self.id} - {self.fecha} - {self.operador_de_guardia} - {self.lugar} - {self.municipio} - {self.parroquia} - {self.tipo_servicio} - {self.unidad} - {self.jefe_de_comision}"