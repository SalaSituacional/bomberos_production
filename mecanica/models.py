from django.db import models
from web.models import Unidades, Personal
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum, F
from django.db.models.functions import Coalesce

# Create your models here.
# ========================================= MODELOS PARA EL AREA DE CONTROL DE UNIDADES =============================================================================================

class Unidades_Detalles(models.Model):
  id_unidad = models.ForeignKey(Unidades, on_delete=models.CASCADE, related_name='detalles_de_unidad')
  tipo_vehiculo = models.CharField()
  serial_carroceria = models.CharField()
  serial_chasis = models.CharField()
  marca = models.CharField()
  año = models.CharField()
  modelo = models.CharField()
  placas = models.CharField()
  tipo_filtro_aceite = models.CharField()
  tipo_filtro_combustible = models.CharField()
  bateria = models.CharField()
  numero_tag = models.CharField()
  tipo_bujia = models.CharField()
  uso = models.CharField()
  capacidad_carga = models.CharField()
  numero_ejes = models.CharField()
  numero_puestos = models.CharField()
  tipo_combustible = models.CharField()
  tipo_aceite = models.CharField()
  medida_neumaticos = models.CharField()
  tipo_correa = models.CharField()
  estado = models.CharField()

  def __str__(self):
        return f"{self.id_unidad.nombre_unidad} {self.tipo_vehiculo} {self.marca} {self.modelo} ({self.año})"

class Servicios(models.Model):
  nombre_servicio = models.CharField()

  def __str__(self):
    return f"{self.nombre_servicio}"

class Reportes_Unidades(models.Model):
  id_unidad = models.ForeignKey(Unidades, on_delete=models.CASCADE)
  servicio = models.ForeignKey(Servicios, on_delete=models.CASCADE)
  fecha = models.DateField(default="1999-01-01")
  hora = models.TimeField(default="00:00")
  descripcion = models.CharField()
  persona_responsable = models.CharField()

  def __str__(self):
        return f"{self.servicio} - {self.fecha} {self.hora} - {self.persona_responsable}"


# ============================================ MODELOS PARA EL AREA DE CONTROL DE HERRAMIENTAS =============================================================================================

class CategoriaHerramienta(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    
    def __str__(self):
        return self.nombre

class Herramienta(models.Model):
    ESTADOS = [
        ('B', 'Bueno'),
        ('R', 'Regular'),
        ('M', 'Malo'),
        ('P', 'En reparación'),
    ]
    
    categoria = models.ForeignKey(CategoriaHerramienta, on_delete=models.PROTECT)
    nombre = models.CharField(max_length=100)
    cantidad_total = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    modelo = models.CharField(max_length=50, blank=True)
    marca = models.CharField(max_length=50, blank=True)
    numero_serie = models.CharField(max_length=50, blank=True, unique=True, null=True)
    fecha_adquisicion = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=1, choices=ESTADOS, default='B')
    activo = models.BooleanField(default=True)
    
    @property
    def cantidad_disponible(self):
        asignadas = self.asignaciones.filter(fecha_devolucion__isnull=True).aggregate(
            total=Coalesce(Sum('cantidad'), 0)
        )['total'] or 0
        return self.cantidad_total - asignadas
    
    def __str__(self):
        return f"{self.nombre} (Total: {self.cantidad_total}, Disp: {self.cantidad_disponible})"

class AsignacionHerramienta(models.Model):
    herramienta = models.ForeignKey(
        Herramienta, 
        on_delete=models.CASCADE,
        related_name='asignaciones'
    )
    unidad = models.ForeignKey(
        Unidades, 
        on_delete=models.CASCADE,
        related_name='asignaciones_herramientas'
    )
    cantidad = models.PositiveIntegerField(default=1)  # Nuevo campo
    fecha_asignacion = models.DateField(auto_now_add=True)
    fecha_devolucion = models.DateField(null=True, blank=True)
    observaciones = models.TextField(blank=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['herramienta', 'unidad'],
                condition=Q(fecha_devolucion__isnull=True),
                name='unique_active_assignment'
            )
        ]
        verbose_name_plural = "Asignaciones de herramientas"
        ordering = ['-fecha_asignacion']
    
    def clean(self):
        if not self.pk and not self.fecha_devolucion:
            disponibles = self.herramienta.cantidad_disponible
            if self.cantidad > disponibles:
                raise ValidationError(
                    f"No hay suficientes unidades disponibles de {self.herramienta}. "
                    f"Disponibles: {disponibles}, Solicitadas: {self.cantidad}"
                )


# ========================================= MODELOS PARA EL AREA DE CONTROL DE CONDUCTORES =============================================================================================
class LicenciaConductor(models.Model):
    TIPO_LICENCIA_CHOICES = [
        ('2', '2° Segundo Grado'),
        ('3', '3° Tercer Grado'),
        ('4', '4° Cuarto Grado'),
        ('5', '5° Quinto Grado'),
    ]
    
    conductor = models.ForeignKey('Conductor', on_delete=models.CASCADE, related_name='licencias')
    tipo_licencia = models.CharField(max_length=1, choices=TIPO_LICENCIA_CHOICES)
    numero_licencia = models.CharField(max_length=50)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField()
    organismo_emisor = models.CharField(max_length=100)
    restricciones = models.TextField(blank=True, null=True)
    observaciones = models.TextField(blank=True, null=True)
    activa = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.get_tipo_licencia_display()} - {self.numero_licencia} (Vence: {self.fecha_vencimiento})"

    class Meta:
        verbose_name = "Licencia de Conductor"
        verbose_name_plural = "Licencias de Conductores"

        constraints = [
            models.UniqueConstraint(
                fields=['numero_licencia', 'tipo_licencia'],
                name='unique_licencia_numero_tipo'
            )
        ]

class CertificadoMedico(models.Model):
    conductor = models.ForeignKey('Conductor', on_delete=models.CASCADE, related_name='certificados_medicos')
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField()
    centro_medico = models.CharField(max_length=200)
    medico = models.CharField(max_length=200)
    observaciones = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Certificado médico - {self.centro_medico} (Vence: {self.fecha_vencimiento})"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['conductor'],
                name='unique_certificado_por_conductor'
            )
        ]

class Conductor(models.Model):
    personal = models.OneToOneField(Personal, on_delete=models.CASCADE, related_name='conductor')
    fecha_vencimiento = models.DateField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    observaciones_generales = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.personal.nombres} {self.personal.apellidos} - C.I.: {self.personal.cedula or 'N/D'}"
    
    @property
    def licencia_activa(self):
        return self.licencias.filter(activa=True).first()
    
    @property
    def certificado_medico_activo(self):
        return self.certificados_medicos.filter(activo=True).first()
    
    class Meta:
        verbose_name = "Conductor"
        verbose_name_plural = "Conductores"

