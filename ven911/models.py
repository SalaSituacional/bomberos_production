from django.contrib.auth import get_user_model
from django.db import models
from django.db import models
from web.models import Personal,Municipios,Parroquias,Unidades
# Create your models here.

class OperadorDeGuardia(models.Model):
    """Modelo para los operadores de guardia"""
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.nombre}"

class TipoServicio(models.Model):
    """Modelo para los tipos de servicios"""
    nombre = models.CharField(max_length=100)
    
    def __str__(self):
        return self.nombre

class Servicio(models.Model):
    """Modelo principal para los servicios"""
    operador_de_guardia = models.ForeignKey(OperadorDeGuardia, on_delete=models.SET_NULL, null=True, blank=True)
    fecha = models.DateField()
    hora = models.TimeField()
    lugar = models.CharField(max_length=100, blank=True)
    municipio = models.ForeignKey(Municipios, on_delete=models.SET_NULL, null=True, blank=True)  # Podría derivarse del lugar
    parroquia = models.ForeignKey(Parroquias, on_delete=models.SET_NULL, null=True, blank=True)  # Podría derivarse del lugar
    tipo_servicio = models.ForeignKey(TipoServicio, on_delete=models.SET_NULL, null=True, blank=True)
    unidad = models.ForeignKey(Unidades, on_delete=models.SET_NULL, null=True, blank=True)
    jefe_de_comision = models.ForeignKey(Personal, on_delete=models.SET_NULL, null=True, blank=True)
    descripcion = models.TextField()
    
    def __str__(self):
        return f"Servicio {self.id} - {self.fecha}"
    
    def save(self, *args, **kwargs):
        # Si se selecciona un lugar, actualizar municipio y parroquia automáticamente
        if self.lugar:
            self.municipio = self.lugar.municipio
            self.parroquia = self.lugar.parroquia
        super().save(*args, **kwargs)