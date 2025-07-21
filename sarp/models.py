from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from web.models import Personal
# ========================================= MODELOS PARA EL AREA DE CONTROL DE VUELOS =============================================================================================

class Drones(models.Model): 
    nombre_dron = models.CharField(max_length=100)
    id_dron = models.CharField(max_length=50, unique=True)
    modelo_dron = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.nombre_dron} ({self.modelo_dron}) - ID: {self.id_dron}"


class Registro_Vuelos(models.Model):
    id_vuelo = models.CharField(unique=True, editable=False, default='')
    id_operador = models.ForeignKey(Personal, on_delete=models.CASCADE, related_name="operador", null=True, blank=True)
    id_observador = models.ForeignKey(Personal, on_delete=models.CASCADE, related_name="observador", null=True, blank=True)
    observador_externo = models.TextField(default="Interno", blank=True)
    fecha = models.DateField(default="1999-01-01")
    sitio = models.CharField()
    hora_despegue = models.TimeField(default="00:00")
    hora_aterrizaje = models.TimeField(default="00:00")
    id_dron = models.ForeignKey(Drones, on_delete=models.CASCADE)
    tipo_mision = models.CharField(max_length=100)
    observaciones_vuelo = models.CharField()
    apoyo_realizado_a = models.CharField()

    def save(self, *args, **kwargs):
        if not self.id_vuelo:
            last_vuelo = Registro_Vuelos.objects.order_by('-id').first()
            next_value = 1 if not last_vuelo else int(last_vuelo.id_vuelo.split('-')[1]) + 1
            self.id_vuelo = f'UDBSC-{next_value:06d}'
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Vuelo {self.id_vuelo} - {self.fecha} - {self.sitio} - Dron: {self.id_dron}"

class EstadoDron(models.Model):
    id_vuelo = models.ForeignKey(Registro_Vuelos, on_delete=models.CASCADE)
    id_dron = models.ForeignKey(Drones, on_delete=models.CASCADE)
    cuerpo = models.CharField(max_length=5)
    observacion_cuerpo = models.CharField(default="Ninguna")
    camara = models.CharField(max_length=5)
    observacion_camara = models.CharField(default="Ninguna")
    helices = models.CharField(max_length=5)
    observacion_helices = models.CharField(default="Ninguna")
    sensores = models.CharField(max_length=5)
    observacion_sensores = models.CharField(default="Ninguna")
    motores = models.CharField(max_length=5)
    observacion_motores = models.CharField(default="Ninguna")

    def __str__(self):
        return f"Estado Dron ({self.id_dron}) - Vuelo {self.id_vuelo}"

class EstadoBaterias(models.Model):
    id_vuelo = models.ForeignKey(Registro_Vuelos, on_delete=models.CASCADE)
    id_dron = models.ForeignKey(Drones, on_delete=models.CASCADE)
    bateria1 = models.CharField(max_length=5)
    bateria2 = models.CharField(max_length=5)
    bateria3 = models.CharField(max_length=5)
    bateria4 = models.CharField(max_length=5)

    def __str__(self):
        return f"Baterías Dron ({self.id_dron}) - Vuelo {self.id_vuelo}"

class EstadoControl(models.Model):
    id_vuelo = models.ForeignKey(Registro_Vuelos, on_delete=models.CASCADE)
    id_dron = models.ForeignKey(Drones, on_delete=models.CASCADE)
    cuerpo = models.CharField(max_length=5)
    joysticks = models.CharField(max_length=5)
    pantalla = models.CharField(max_length=5)
    antenas = models.CharField(max_length=5)
    bateria = models.CharField(max_length=5)

    def __str__(self):
        return f"Estado Control ({self.id_dron}) - Vuelo {self.id_vuelo}"

class DetallesVuelo(models.Model):
    id_vuelo = models.ForeignKey(Registro_Vuelos, on_delete=models.CASCADE)
    viento = models.CharField()
    nubosidad = models.CharField()
    riesgo_vuelo = models.CharField()
    zona_vuelo = models.CharField()
    numero_satelites = models.CharField()
    distancia_recorrida = models.CharField()
    altitud = models.CharField()
    duracion_vuelo = models.CharField()
    observaciones = models.CharField()

    def __str__(self):
        return f"Detalles Vuelo {self.id_vuelo} - {self.viento}, {self.nubosidad}, {self.riesgo_vuelo}"
