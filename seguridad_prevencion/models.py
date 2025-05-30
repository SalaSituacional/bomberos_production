from django.db import models
from web.models import Municipios, Parroquias

# Create your models here.
class Comercio(models.Model):
    id_comercio = models.CharField(max_length=10, unique=True, editable=False, default='')
    nombre_comercio = models.CharField(max_length=100)
    rif_empresarial = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if not self.id_comercio:
            last_comercio = Comercio.objects.order_by('-id').first()  # Obtiene el último objeto
            next_value = 1 if not last_comercio else int(last_comercio.id_comercio.split('-')[1]) + 1
            self.id_comercio = f'SEG-{next_value:06d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.id_comercio} - {self.nombre_comercio}"

class Solicitudes(models.Model):
    id_solicitud = models.ForeignKey(Comercio, on_delete=models.CASCADE)
    fecha_solicitud = models.DateField()
    hora_solicitud = models.TimeField()
    tipo_servicio = models.CharField()
    solicitante_nombre_apellido = models.CharField()
    solicitante_cedula = models.CharField(blank=True, null=True)
    tipo_representante = models.CharField()
    rif_representante_legal = models.CharField(blank=True, null=True)
    direccion = models.CharField()
    estado = models.CharField()
    municipio = models.ForeignKey(Municipios, on_delete=models.CASCADE)
    parroquia = models.ForeignKey(Parroquias, on_delete=models.CASCADE, default="0")
    numero_telefono = models.CharField()
    correo_electronico = models.CharField()
    pago_tasa = models.CharField()
    metodo_pago = models.CharField()
    referencia = models.CharField(default="NO HAY REFERENCIA")

    def __str__(self):
            return f"Solicitud {self.id_solicitud} - {self.tipo_servicio} - {self.solicitante_nombre_apellido}"

class Requisitos(models.Model):
  id_solicitud = models.ForeignKey(Solicitudes, on_delete=models.CASCADE)
  cedula_identidad = models.BooleanField(default=False)
  cedula_vencimiento = models.DateField(blank=True, null=True)
  
  rif_representante = models.BooleanField(default=False)
  rif_representante_vencimiento = models.DateField(blank=True, null=True)
  
  rif_comercio = models.BooleanField(default=False)
  rif_comercio_vencimiento = models.DateField(blank=True, null=True)
  
  permiso_anterior = models.BooleanField(default=False)
  registro_comercio = models.BooleanField(default=False)
  
  documento_propiedad = models.BooleanField(default=False)
  documento_propiedad_vencimiento = models.DateField(blank=True, null=True)
  
  cedula_catastral = models.BooleanField(default=False)
  cedula_catastral_vencimiento = models.DateField(blank=True, null=True)
  
  carta_autorizacion = models.BooleanField(default=False)
  plano_bomberil = models.BooleanField(blank=True, default=False)
  
  def __str__(self):
      return f"Requisitos para Solicitud {self.id_solicitud}"
