from django.db import models
from web.models import Personal
# Create your models here.

# ========================================== MODELOS PARA EL AREA DE BIENES E INMUEBLES ===============================================================================================

class Dependencia(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class EstadoBien(models.TextChoices):
    BUENO = 'Bueno', 'Bueno'
    REGULAR = 'Regular', 'Regular'
    DEFECTUOSO = 'Defectuoso', 'Defectuoso'
    DANIADO = 'Dañado', 'Dañado'


class BienMunicipal(models.Model):
    identificador = models.CharField(max_length=20, unique=True)
    descripcion = models.TextField(default="none")
    cantidad = models.IntegerField(default=0)
    dependencia = models.ForeignKey(Dependencia, on_delete=models.CASCADE)  # Ej: Cuartel Central
    departamento = models.CharField(max_length=100)  # Ej: Sala Situación
    responsable = models.ForeignKey(Personal, on_delete=models.CASCADE)  # Ej: 1er Tte Daniel Alarcón
    fecha_registro = models.DateField()
    estado_actual = models.CharField(max_length=20, choices=EstadoBien.choices)

    def __str__(self):
        return f"{self.identificador} - {self.descripcion}"

class MovimientoBien(models.Model):
    bien = models.ForeignKey(BienMunicipal, on_delete=models.CASCADE)
    nueva_dependencia = models.ForeignKey(Dependencia, on_delete=models.CASCADE)
    nuevo_departamento = models.CharField(max_length=20,default="none")
    ordenado_por = models.ForeignKey(Personal, on_delete=models.CASCADE)
    fecha_orden = models.DateField()

    def __str__(self):
        return f"Movimiento de {self.bien.identificador} en {self.fecha_orden}"
    
class CambiarEstadoBien(models.Model):
    bien = models.ForeignKey(BienMunicipal, on_delete=models.CASCADE)
    nuevo_estado = models.CharField(max_length=20, choices=EstadoBien.choices)
    fecha_orden = models.DateField()

    def __str__(self):
        return f"Cambio de Estado de {self.bien.identificador} a {self.nuevo_estado} en {self.fecha_orden}"


