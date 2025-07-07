from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

# from sequences import get_next_value

# Modelos Para Agregar Datos Aparte
class InstagramPost(models.Model):
    url = models.URLField()  # Para almacenar la URL de la publicación
    fecha = models.DateTimeField(default="2000-01-01T00:00:00")  # Para almacenar la fecha de la publicación

    def __str__(self):
        return f"{self.url} - {self.fecha}"

class Doctores(models.Model):
  doctor = models.TextField()

  def __str__(self):
    return self.doctor

class Enfermeros(models.Model):
  enfermeros = models.TextField()

  def __str__(self):
    return self.enfermeros

class Psicologa(models.Model):
  psicologa = models.TextField()

  def __str__(self):
    return self.psicologa

# Tabla personal cuerpo de bomberos
class Personal(models.Model):
  nombres = models.TextField()
  apellidos = models.TextField()
  jerarquia = models.TextField()
  cargo = models.TextField()
  cedula = models.CharField(max_length=50)
  sexo = models.CharField(max_length=50)
  rol = models.TextField()
  status = models.CharField(max_length=70)

  def __str__(self):
    return self.nombres + " -- " + self.apellidos + " -- " + self.jerarquia + " -- " + self.cargo + " -- " + self.cedula + " -- " + self.sexo + " -- " + self.rol + " -- " + self.status
  
class Detalles_Personal(models.Model):
  personal = models.ForeignKey(Personal, on_delete=models.CASCADE)
  fecha_nacimiento = models.DateField()
  talla_camisa = models.TextField()
  talla_pantalon = models.TextField()
  talla_zapato = models.TextField()
  grupo_sanguineo = models.TextField()
  fecha_ingreso = models.DateField()
  direccion = models.TextField()
  email = models.TextField()
  telefono = models.TextField()
  horario = models.TextField()
  estado_civil = models.TextField()

  banco = models.TextField()
  nro_cuenta = models.TextField()
  seguro_social = models.TextField()
  nro_rif = models.TextField()

  def __str__(self):
    return self.personal.nombres + " -- " + str(self.fecha_nacimiento) + " -- " + self.talla_camisa + " -- " + self.talla_pantalon + " -- " + self.talla_zapato + " -- " + self.grupo_sanguineo + " -- " + str(self.fecha_ingreso)

class Ascensos(models.Model):
   personal = models.ForeignKey(Personal, on_delete=models.CASCADE)
   gaceta = models.TextField()
   actual = models.TextField()
   fecha = models.DateField(default=timezone.now)
   nuevo = models.TextField()

   def __str__(self):
      return self.personal.nombres + " -- " + self.personal.apellidos + " -- " + str(self.fecha) + " -- " + self.actual + " -- " + self.nuevo

class Familiares(models.Model):
   personal = models.ForeignKey(Personal, on_delete=models.CASCADE)
   nombres = models.TextField()
   apellidos = models.TextField()
   parentesco = models.TextField()
   fecha_nacimiento = models.DateField()
   cedula = models.TextField(null=True, blank=True)
   partida_nacimiento = models.TextField(null=True, blank=True)

   def __str__(self):
      return self.nombres + " -- " + self.apellidos + " -- " + self.parentesco + " -- " + str(self.fecha_nacimiento)
   
class Sanciones(models.Model):
  personal = models.ForeignKey(Personal, on_delete=models.CASCADE)
  fecha = models.DateField(default=timezone.now)
  sancion = models.TextField()
  observaciones = models.TextField()

  def __str__(self):
    return f"{self.personal.nombres} {self.personal.apellidos} -- {self.fecha} -- {self.sancion} -- {self.observaciones}"
  
class Titulos_Academicos(models.Model):
    personal = models.ForeignKey(Personal, on_delete=models.CASCADE)
    titulo = models.TextField()
    institucion = models.TextField()
    fecha_obtencion = models.DateField(default=timezone.now)
    numero_constancia = models.TextField()
    hrs_academicas = models.TextField()

    def __str__(self):
        return f"{self.personal.nombres} {self.personal.apellidos} -- {self.titulo} -- {self.institucion} -- {self.fecha_obtencion} -- {self.numero_constancia} -- {self.hrs_academicas}"

# Tabla de usuarios que pueden entrar a la pagina
class Usuarios(models.Model):
    user = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    encargado = models.ForeignKey(Personal, on_delete=models.CASCADE)
    
    def __str__(self):
      return self.user + " -- " + self.password + " -- " + self.encargado.nombres + " " + self.encargado.apellidos


class RegistroPeticiones(models.Model):
    usuario = models.ForeignKey(Usuarios, on_delete=models.SET_NULL, null=True, blank=True)  # Usuario logeado
    url = models.CharField(max_length=255)  # URL donde se realizó la petición
    datos_post = models.JSONField()  # Datos enviados en la petición POST
    fecha_hora = models.DateTimeField(auto_now_add=True)  # Fecha y hora del registro

    def __str__(self):
        return f"Petición de {self.usuario} en {self.fecha_hora} a {self.url}"

# Tabla de divisiones del cuerpo de bomberos
class Divisiones(models.Model):
    division = models.CharField(max_length=20)
    
    def __str__(self):
      return self.division

# tabla de municipios
class Municipios(models.Model):
    municipio = models.CharField(max_length=70)
    
    def __str__(self):
      return self.municipio

# tabla de parroquias
class Parroquias(models.Model):
    parroquia = models.CharField(max_length=40)
    
    def __str__(self):
      return self.parroquia

# tabla de posibles motivos para guardias de prevencion
class Motivo_Prevencion(models.Model):
    motivo = models.CharField(max_length=60)
    
    def __str__(self):
      return self.motivo

# tabla de lugares de suministros de agua
class Tipo_Institucion(models.Model):
  nombre_institucion = models.CharField(max_length=70)
  
  def __str__(self):
     return self.nombre_institucion
  
# tabla de cilindros de gas
class Tipo_Cilindro(models.Model):
  nombre_cilindro = models.CharField(max_length=70)
  
  def __str__(self):
     return self.nombre_cilindro

# tabla de posibles apoyos a otras unidades
class Tipo_apoyo(models.Model):
  tipo_apoyo = models.CharField(max_length=70)
  
  def __str__(self):
    return self.tipo_apoyo

# tabla de tipos de procedimientos
class Tipos_Procedimientos(models.Model):
    tipo_procedimiento = models.CharField(max_length=70)
    id_division = models.ManyToManyField(Divisiones)
    
    def __str__(self):
      return self.tipo_procedimiento

# tabla de posibles motivos para Despliegues de seguridad
class Motivo_Despliegue(models.Model):
  motivo = models.CharField(max_length=70)
  
  def __str__(self):
    return self.motivo

# tabla de posibles tipos de rescate
class Tipo_Rescate(models.Model):
  tipo_rescate = models.CharField(max_length=70)
  
  def __str__(self):
    return self.tipo_rescate

# tabla de posibles tipos de servicios especiales
class Tipo_servicios(models.Model):
  serv_especiales = models.CharField(max_length=70)
  
  def __str__(self):
    return self.serv_especiales
  
# tabla de posibles motivos de falsa alarma
class Motivo_Alarma(models.Model):
  motivo = models.CharField(max_length=70)
  
  def __str__(self):
    return self.motivo

# tabla de posibles motivos de evaluacion de riesgo
class Motivo_Riesgo(models.Model):
  tipo_riesgo = models.CharField(max_length=100)
  
  def __str__(self):
    return self.tipo_riesgo

# tabla de posibles mitigacion de riesgo
class Mitigacion_riesgo(models.Model):
  tipo_servicio = models.CharField(max_length=100)
  
  def __str__(self):
    return self.tipo_servicio

# Tabla de motivos para el procedimiento de Puesto de Avanzada
class Motivo_Avanzada(models.Model):
  tipo_servicio = models.CharField(max_length=70)
  
  def __str__(self):
    return self.tipo_servicio

# tabla de listado de unidades del cuerpo de bomberos
class Unidades(models.Model):
  nombre_unidad = models.CharField(max_length=70)
  id_division = models.ManyToManyField(Divisiones)  
  
  def __str__(self):
    return self.nombre_unidad

# ===================================================

class Tipo_Incendio(models.Model):
  tipo_incendio = models.CharField(max_length=70)

  def __str__(self):
    return self.tipo_incendio

# Tipos de procedimiento por artificio pirotecnico
class Tipos_Artificios(models.Model):
  tipo = models.CharField(max_length=80)

  def __str__(self):
    return self.tipo

class Tipos_Investigacion(models.Model):
  tipo_investigacion = models.CharField(max_length=100)

  def __str__(self):
    return self.tipo_investigacion

class Tipos_Comision(models.Model):
  tipo_comision = models.CharField(max_length=80)

  def __str__(self):
    return self.tipo_comision

# Modelo Proncipal para todos los Procedimientos
class Procedimientos(models.Model):
    id_division = models.ForeignKey(Divisiones, on_delete=models.CASCADE, default=0, blank=True)
    tipo_servicio = models.CharField(max_length=70, blank=True)
    id_solicitante = models.ForeignKey(Personal, on_delete=models.CASCADE, related_name="personal1", null=True, blank=True)
    solicitante_externo = models.TextField(default="Interno", blank=True)
    unidad = models.ForeignKey(Unidades, on_delete=models.CASCADE, default=27)
    id_jefe_comision = models.ForeignKey(Personal, on_delete=models.CASCADE, related_name="personal2", null=True, blank=True)
    dependencia = models.CharField(max_length=80, blank=True)
    efectivos_enviados = models.CharField(max_length=40, blank=True)
    id_municipio = models.ForeignKey(Municipios, on_delete=models.CASCADE)
    id_parroquia = models.ForeignKey(Parroquias, on_delete=models.CASCADE, default="0")
    fecha = models.DateField(default="1999-01-01")
    hora = models.TimeField(default="00:00")
    direccion = models.TextField()
    id_tipo_procedimiento = models.ForeignKey(Tipos_Procedimientos, on_delete=models.CASCADE)

    def __str__(self):
      return self.id_division.division + " -- " + self.id_municipio.municipio + " -- " + self.id_parroquia.parroquia + " -- " + str(self.fecha) + " " + str(self.hora) + " -- " + self.direccion + " -- " + self.id_tipo_procedimiento.tipo_procedimiento

# Modelo Para las comisiones presentes
class Comisiones(models.Model):
  procedimiento = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  comision = models.ForeignKey(Tipos_Comision, on_delete=models.CASCADE)
  nombre_oficial = models.TextField()
  apellido_oficial = models.TextField()
  cedula_oficial = models.CharField(max_length=80)
  nro_unidad = models.TextField()
  nro_cuadrante = models.TextField()

  def __str__(self):
    return self.procedimiento.id_tipo_procedimiento.tipo_procedimiento + " -- " + self.comision.tipo_comision + " -- " + self.nombre_oficial + " -- " + self.apellido_oficial + " -- " + self.cedula_oficial + " -- " + self.nro_unidad + " -- " + self.nro_cuadrante

# Modelos de los detalles por procedimiento

class Abastecimiento_agua(models.Model):
  id_procedimiento = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  id_tipo_servicio = models.ForeignKey(Tipo_Institucion, on_delete=models.CASCADE)
  nombres = models.TextField(default="Nombre_1 Nombre_2")
  apellidos = models.TextField(default="Apellido_1 Apellido_2")
  cedula = models.CharField(max_length=20, default="V-00000000")
  ltrs_agua = models.CharField(max_length=10, default="0L")
  personas_atendidas = models.CharField(max_length=10, default="0")
  descripcion = models.TextField(default="Aqui va la Descripcion")
  material_utilizado = models.TextField(default="Materiales Usados")
  status = models.CharField(max_length=20, default="...")
  
  def __str__(self):
    return self.id_procedimiento.id_division.division + " -- " + self.id_tipo_servicio.nombre_institucion + " -- " + self.nombres + " -- " + self.apellidos + " -- " + self.cedula + " -- " + self.ltrs_agua + " -- " + self.personas_atendidas + " -- " + self.descripcion + " -- " + self.material_utilizado + " -- " + self.status
  
class Apoyo_Unidades(models.Model):
  id_procedimiento = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  id_tipo_apoyo = models.ForeignKey(Tipo_apoyo, on_delete=models.CASCADE)
  unidad_apoyada = models.TextField()
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=50)
  
  def __str__(self):
    return self.id_procedimiento.id_division.division + " -- " + self.id_tipo_apoyo.tipo_apoyo + " -- " + self.unidad_apoyada + " -- " + self.descripcion + " -- " + self.material_utilizado + " -- " + self.status
  
class Guardia_prevencion(models.Model):
  id_procedimiento = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  id_motivo_prevencion = models.ForeignKey(Motivo_Prevencion, on_delete=models.CASCADE)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=50)
  
  def __str__(self):
    return self.id_procedimiento.id_division.division + "--" + self.id_motivo_prevencion.motivo + " -- " + self.descripcion + " -- " + self.material_utilizado + " -- " + self.status

class Atendido_no_Efectuado(models.Model):
  id_procedimiento = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=50)
  
  def __str__(self):
    return self.id_procedimiento.id_division.division + " -- " + self.descripcion + " -- " + self.material_utilizado + " -- " + self.status

class Despliegue_Seguridad(models.Model):
  id_procedimiento = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  motivo_despliegue = models.ForeignKey(Motivo_Despliegue, on_delete=models.CASCADE)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=50)
  
  def __str__(self):
    return self.id_procedimiento.id_division.division + " -- " + self.motivo_despliegue.motivo + " -- " + self.descripcion + " -- " + self.material_utilizado + " -- " + self.status
  
class Fallecidos(models.Model):
  id_procedimiento = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  motivo_fallecimiento = models.TextField()
  nombres = models.CharField(max_length=70)
  apellidos = models.CharField(max_length=70)
  cedula = models.CharField(max_length=20)
  edad = models.CharField(max_length=4)
  sexo = models.CharField(max_length=10)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=20)
  
  def __str__(self):
   return self.id_procedimiento.id_division.division + " -- " + self.motivo_fallecimiento + " -- " + self.nombres + " -- " + self.apellidos + " -- " + self.cedula + " -- " + self.edad + " -- " + self.sexo + " -- " + self.descripcion + " -- " + self.material_utilizado + " -- " + self.status

class Falsa_Alarma(models.Model):
  id_procedimiento = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  motivo_alarma = models.ForeignKey(Motivo_Alarma, on_delete=models.CASCADE)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=20)
  
  def __str__(self):
   return self.id_procedimiento.id_division.division + " -- " + self.motivo_alarma.motivo + " -- " + self.descripcion + " -- " + self.material_utilizado + " -- " + self.status

class Servicios_Especiales(models.Model):
  id_procedimientos = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  tipo_servicio = models.ForeignKey(Tipo_servicios, on_delete=models.CASCADE)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=20)
  
  def __str__(self):
   return self.id_procedimientos.id_division.division + " -- " + self.tipo_servicio.serv_especiales + " -- " + self.descripcion + " -- " + self.material_utilizado + " -- " + self.status

class Rescate(models.Model):
  id_procedimientos = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  material_utilizado = models.TextField()
  status = models.CharField(max_length=50)
  tipo_rescate = models.ForeignKey(Tipo_Rescate, on_delete=models.CASCADE)
  
  def __str__(self):
    return self.id_procedimientos.id_division.division + " -- " + self.material_utilizado + " -- " + self.status + " -- " + self.tipo_rescate.tipo_rescate
  
class Rescate_Persona(models.Model):
  id_rescate = models.ForeignKey(Rescate, on_delete=models.CASCADE)
  nombre = models.CharField(max_length=70)
  apellidos = models.CharField(max_length=70)
  cedula = models.CharField(max_length=20)
  edad = models.CharField(max_length=3)
  sexo = models.CharField(max_length=30)
  descripcion = models.TextField()
  
  def __str__(self):
    return self.id_rescate.tipo_rescate.tipo_rescate  + " -- " + self.nombre  + " -- " + self.apellidos  + " -- " + self.cedula  + " -- " + self.edad  + " -- " + self.sexo  + " -- " + self.descripcion  
  
class Rescate_Animal(models.Model):
  id_rescate = models.ForeignKey(Rescate, on_delete=models.CASCADE)
  especie = models.TextField()
  descripcion = models.TextField()
  
  def __str__(self):
    return self.id_rescate.tipo_rescate.tipo_rescate  + " -- " + self.especie + " -- " + self.descripcion

class Incendios(models.Model): 
  id_procedimientos = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  id_tipo_incendio = models.ForeignKey(Tipo_Incendio, on_delete=models.CASCADE)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=40)
  
  def __str__(self):
    return self.id_procedimientos.id_tipo_procedimiento.tipo_procedimiento + " -- " + self.id_tipo_incendio.tipo_incendio + " -- " + self.descripcion + " -- " + self.material_utilizado + " -- " + self.status
  
# Tabla de Retencion Preventiva (GLP)
class Retencion_Preventiva_Incendios(models.Model):
  id_procedimiento = models.ForeignKey(Incendios, on_delete=models.CASCADE)
  tipo_cilindro = models.CharField(max_length=60)
  capacidad = models.CharField(max_length=60)
  serial = models.CharField(max_length=60)
  nro_constancia_retencion = models.CharField(max_length=60)
  nombre = models.CharField(max_length=60)
  apellidos = models.CharField(max_length=60)
  cedula = models.CharField(max_length=20)
  
  def __str__(self):
    return self.id_procedimiento.id_tipo_incendio.tipo_incendio + " -- " + self.tipo_cilindro + " -- " + self.capacidad + " -- " + self.serial + " -- " + self.nro_constancia_retencion


class Persona_Presente(models.Model):
  id_incendio = models.ForeignKey(Incendios, on_delete=models.CASCADE)
  nombre = models.CharField(max_length=80)
  apellidos = models.CharField(max_length=80)
  cedula = models.CharField(max_length=20)
  edad = models.CharField(max_length=3)
  
  def __str__(self):
    return self.id_incendio.id_tipo_incendio.tipo_incendio + " -- " + self.nombre + " -- " + self.apellidos + " -- " + self.cedula + " -- " + self.edad
  
class Detalles_Vehiculos(models.Model):
  id_vehiculo = models.ForeignKey(Incendios, on_delete=models.CASCADE)
  modelo = models.CharField(max_length=40)
  marca = models.CharField(max_length=40)
  color = models.CharField(max_length=40)
  año = models.CharField(max_length=40)
  placas = models.CharField(max_length=40)
  
  def __str__(self):
    return self.id_vehiculo.id_tipo_incendio.tipo_incendio + " -- " + self.modelo + " -- " + self.marca + " -- " + self.color + " -- " + self.año + " -- " + self.placas
 
class Atenciones_Paramedicas(models.Model):
  id_procedimientos = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  tipo_atencion = models.CharField(max_length=30)
  
  def __str__(self):
    return self.id_procedimientos.id_tipo_procedimiento.tipo_procedimiento + " -- "  + self.tipo_atencion

# tabla de Emergencias Medicas para procedmiento atenciones paramedicas
class Emergencias_Medicas(models.Model):
  id_atencion = models.ForeignKey(Atenciones_Paramedicas, on_delete=models.CASCADE)
  nombres = models.CharField(max_length=70)
  apellidos = models.CharField(max_length=70)
  cedula = models.CharField(max_length=20)
  edad = models.CharField(max_length=3)
  sexo = models.CharField(max_length=12)
  idx = models.CharField(max_length=70)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=20)
  
  def __str__(self):
    return self.id_atencion.tipo_atencion + " -- " + self.nombres + " -- " + self.apellidos + " -- " + self.cedula + " -- " + self.edad + " -- " + self.sexo + " -- " + self.idx + " -- " + self.descripcion + " -- " +  self.material_utilizado + " -- " + self.status
  
class Traslado(models.Model):
  id_lesionado = models.ForeignKey(Emergencias_Medicas, on_delete=models.CASCADE)
  hospital_trasladado = models.TextField()
  medico_receptor = models.TextField()
  mpps_cmt = models.CharField(max_length=20)
  
  def __str__(self):
    return self.hospital_trasladado + " -- " + self.medico_receptor + " -- " + self.mpps_cmt

class Tipos_Traslado(models.Model):
  tipo_traslado = models.CharField(max_length=100)
  
  def __str__(self):
    return self.tipo_traslado

# Tabla de Traslados(Prehospitalaria)
class Traslado_Prehospitalaria(models.Model):
  id_procedimiento = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  id_tipo_traslado = models.ForeignKey(Tipos_Traslado, on_delete=models.CASCADE)
  nombre = models.CharField(max_length=70)
  apellido = models.CharField(max_length=70)
  cedula = models.CharField(max_length=20)
  edad = models.CharField(max_length=3)
  sexo = models.CharField(max_length=12)
  idx = models.TextField()
  hospital_trasladado = models.TextField()
  medico_receptor = models.CharField(max_length=80)
  mpps_cmt = models.CharField(max_length=40)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=100)

  def __str__(self):
    return self.id_procedimiento.id_tipo_procedimiento.tipo_procedimiento + " -- " + self.id_tipo_traslado.tipo_traslado + " -- " + self.nombre + " -- " + self.apellido + " -- " + self.cedula + " -- " + self.edad + " -- " + self.sexo + " -- " + self.idx + " -- " + self.hospital_trasladado + " -- " + self.medico_receptor + " -- " + self.mpps_cmt + " -- " + self.descripcion + " -- " + self.material_utilizado + " -- " + self.material_utilizado + " -- " + self.status

# tabla de accidentes de transito para procedimiento atenciones paramedicas
class Tipo_Accidente(models.Model):
  tipo_accidente = models.CharField(max_length=70)
  
  def __str__(self):
    return self.tipo_accidente

class Accidentes_Transito(models.Model):
  id_atencion = models.ForeignKey(Atenciones_Paramedicas, on_delete=models.CASCADE)
  tipo_de_accidente = models.ForeignKey(Tipo_Accidente, on_delete=models.CASCADE)
  cantidad_lesionados = models.CharField(max_length=20)
  material_utilizado = models.TextField()
  status = models.CharField(max_length=30)
  
  def __str__(self):
    return self.id_atencion.tipo_atencion + " -- " + self.tipo_de_accidente.tipo_accidente + " -- " + self.cantidad_lesionados

class Detalles_Vehiculos_Accidente(models.Model):
  id_vehiculo = models.ForeignKey(Accidentes_Transito, on_delete=models.CASCADE)
  modelo = models.CharField(max_length=40)
  marca = models.CharField(max_length=40)
  color = models.CharField(max_length=40)
  año = models.CharField(max_length=40)
  placas = models.CharField(max_length=40)
  
  def __str__(self):
    return self.id_vehiculo.tipo_de_accidente.tipo_accidente + " -- " + self.modelo + " -- " + self.marca + " -- " + self.color + " -- " + self.año + " -- " + self.placas
  
class Lesionados(models.Model):
    id_accidente = models.ForeignKey(Accidentes_Transito, on_delete=models.CASCADE)
    nombres = models.CharField(max_length=50)
    apellidos = models.CharField(max_length=50)
    cedula = models.CharField(max_length=20)
    edad = models.CharField(max_length=3)
    sexo = models.CharField(max_length=12)
    idx = models.TextField()
    descripcion = models.TextField()
    
    def __str__(self):
      return self.id_accidente.tipo_de_accidente.tipo_accidente + " -- " + self.nombres + " -- " + self.apellidos + " -- " + self.cedula + " -- " + self.edad + " -- " + self.sexo + " -- " + self.idx + " -- " + self.descripcion
    
class Traslado_Accidente(models.Model):
  id_lesionado = models.ForeignKey(Lesionados, on_delete=models.CASCADE)
  hospital_trasladado = models.TextField()
  medico_receptor = models.TextField()
  mpps_cmt = models.TextField()
  
  def __str__(self):
    return self.hospital_trasladado + " -- " + self.medico_receptor + " -- " + self.mpps_cmt

# Tabla Eevaluacion de Riesgo
class Evaluacion_Riesgo(models.Model):
  id_procedimientos = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  id_tipo_riesgo = models.ForeignKey(Motivo_Riesgo, on_delete=models.CASCADE)
  tipo_estructura = models.TextField()
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=100)
  
  def __str__(self):
    return self.id_procedimientos.id_tipo_procedimiento.tipo_procedimiento + " -- " + self.id_tipo_riesgo.tipo_riesgo + " -- " + self.tipo_estructura + " -- " + self.descripcion + " -- " + self.material_utilizado + " -- " + self.status

# Tabla Mitigacion de Riesgos
class Mitigacion_Riesgos(models.Model):
  id_procedimientos = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  id_tipo_servicio = models.ForeignKey(Mitigacion_riesgo, on_delete=models.CASCADE)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=100)
  
  def __str__(self):
    return self.id_procedimientos.id_tipo_procedimiento.tipo_procedimiento + " -- " + self.id_tipo_servicio.tipo_servicio + " -- " + self.descripcion + " -- " + self.material_utilizado + " -- " + self.status
  
class Detalles_Vehiculo_Derrame(models.Model):
    id_vehiculo = models.ForeignKey(Mitigacion_Riesgos, on_delete=models.CASCADE)
    modelo = models.CharField()
    marca = models.CharField()
    color = models.CharField(max_length=40)
    año = models.CharField(max_length=40)
    placas = models.CharField(max_length=40)

# Tabla Puesto de Avanzada
class Puesto_Avanzada(models.Model):
  id_procedimientos = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  id_tipo_servicio = models.ForeignKey(Motivo_Avanzada, on_delete=models.CASCADE)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=100)
  
  def __str__(self):
    return self.id_procedimientos.id_tipo_procedimiento.tipo_procedimiento + " -- " + self.id_tipo_servicio.tipo_servicio + " -- " + self.descripcion + " -- " + self.material_utilizado + " -- " + self.status
  
# tabla de Emergencias Medicas para procedmiento atenciones paramedicas
class Asesoramiento(models.Model):
  id_procedimiento = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  nombre_comercio = models.CharField(max_length=70)
  rif_comercio = models.CharField(max_length=70)
  nombres = models.CharField(max_length=70)
  apellidos = models.CharField(max_length=70)
  cedula = models.CharField(max_length=20)
  sexo = models.CharField(max_length=12)
  telefono = models.CharField(max_length=30)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=20)
  
  def __str__(self):
    return self.id_procedimiento.id_tipo_procedimiento.tipo_procedimiento + " -- " + self.nombre_comercio + " -- " + self.rif_comercio + " -- " + self.nombres + " -- " + self.apellidos + " -- " + self.cedula + " -- " + self.sexo + " -- " + self.telefono + " -- " + self.descripcion + " -- " +  self.material_utilizado + " -- " + self.status
  
class Persona_Presente_Eval(models.Model):
  id_persona = models.ForeignKey(Evaluacion_Riesgo, on_delete=models.CASCADE)
  nombre = models.CharField(max_length=70)
  apellidos = models.CharField(max_length=70)
  cedula = models.CharField(max_length=20)
  telefono = models.CharField(max_length=30)
  
  def __str__(self):
    return self.id_persona.id_tipo_riesgo.tipo_riesgo + " -- " + self.nombre + " -- " + self.apellidos + " -- " + self.cedula + " -- " + self.telefono
  
# Tabla de Reinspeccion de prevencion
class Reinspeccion_Prevencion(models.Model):
  id_procedimiento = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  nombre_comercio = models.CharField(max_length=70)
  rif_comercio = models.CharField(max_length=70)
  nombre = models.CharField(max_length=60)
  apellidos = models.CharField(max_length=60)
  sexo = models.CharField(max_length=12)
  cedula = models.CharField(max_length=20)
  telefono = models.CharField(max_length=30)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=20)
  
  def __str__(self):
    return self.id_procedimiento.id_tipo_procedimiento.tipo_procedimiento + " -- " + self.nombre_comercio + " -- " + self.rif_comercio + " -- " + self.nombre + " -- " + self.apellidos + " -- " + self.cedula + " -- " + self.sexo + " -- " + self.telefono + " -- " + self.descripcion + " -- " + self.material_utilizado + " -- " + self.status

# Tabla de Retencion Preventiva (GLP)
class Retencion_Preventiva(models.Model):
  id_procedimiento = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  tipo_cilindro = models.CharField(max_length=60)
  capacidad = models.CharField(max_length=60)
  serial = models.CharField(max_length=60)
  nro_constancia_retencion = models.CharField(max_length=60)
  nombre = models.CharField(max_length=60)
  apellidos = models.CharField(max_length=60)
  cedula = models.CharField(max_length=20)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=50)
  
  def __str__(self):
    return self.id_procedimiento.id_tipo_procedimiento.tipo_procedimiento + " -- " + self.tipo_cilindro + " -- " + self.capacidad + " -- " + self.serial + " -- " + self.nro_constancia_retencion + " -- " + self.descripcion + " -- " + self.material_utilizado + " -- " + self.status

# Tabla de Artificios Pirotecnicos
class Artificios_Pirotecnicos(models.Model):
   id_procedimiento = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
   nombre_comercio = models.CharField(max_length=70)
   rif_comerciante = models.CharField(max_length=70)
   tipo_procedimiento = models.ForeignKey(Tipos_Artificios, on_delete=models.CASCADE)

   def __str__(self):
     return self.id_procedimiento.id_tipo_procedimiento.tipo_procedimiento + " -- " + self.nombre_comercio + " -- " + self.rif_comerciante + " -- " + self.tipo_procedimiento.tipo
   
class Incendios_Art(models.Model): 
  id_procedimientos = models.ForeignKey(Artificios_Pirotecnicos, on_delete=models.CASCADE)
  id_tipo_incendio = models.ForeignKey(Tipo_Incendio, on_delete=models.CASCADE)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=40)
  
  def __str__(self):
    return self.id_procedimientos.tipo_procedimiento.tipo + " -- " + self.id_tipo_incendio.tipo_incendio + " -- " + self.descripcion + " -- " + self.material_utilizado + " -- " + self.status
  
class Persona_Presente_Art(models.Model):
  id_incendio = models.ForeignKey(Incendios_Art, on_delete=models.CASCADE)
  nombre = models.CharField(max_length=70)
  apellidos = models.CharField(max_length=70)
  cedula = models.CharField(max_length=20)
  edad = models.CharField(max_length=3)
  
  def __str__(self):
    return self.id_incendio.id_procedimientos.tipo_procedimiento.tipo + " -- " + self.nombre + " -- " + self.apellidos + " -- " + self.cedula + " -- " + self.edad
  
class Detalles_Vehiculos_Art(models.Model):
  id_vehiculo = models.ForeignKey(Incendios_Art, on_delete=models.CASCADE)
  modelo = models.CharField(max_length=60)
  marca = models.CharField(max_length=60)
  color = models.CharField(max_length=40)
  año = models.CharField(max_length=40)
  placas = models.CharField(max_length=40)
  
  def __str__(self):
    return self.id_vehiculo.id_procedimientos.tipo_procedimiento.tipo + " -- " + self.modelo + " -- " + self.marca + " -- " + self.color + " -- " + self.año + " -- " + self.placas

class Lesionados_Art(models.Model):
    id_accidente = models.ForeignKey(Artificios_Pirotecnicos, on_delete=models.CASCADE)
    nombres = models.CharField(max_length=60)
    apellidos = models.CharField(max_length=60)
    cedula = models.CharField(max_length=20)
    edad = models.CharField(max_length=3)
    sexo = models.CharField(max_length=12)
    idx = models.TextField()
    descripcion = models.TextField()
    status = models.CharField(max_length=40)
    
    def __str__(self):
      return self.id_accidente.tipo_procedimiento.tipo + " -- " + self.nombres + " -- " + self.apellidos + " -- " + self.cedula + " -- " + self.edad + " -- " + self.sexo + " -- " + self.idx + " -- " + self.descripcion
 
class Fallecidos_Art(models.Model):
  id_procedimiento = models.ForeignKey(Artificios_Pirotecnicos, on_delete=models.CASCADE)
  motivo_fallecimiento = models.TextField()
  nombres = models.CharField(max_length=60)
  apellidos = models.CharField(max_length=60)
  cedula = models.CharField(max_length=20)
  edad = models.CharField(max_length=3)
  sexo = models.CharField(max_length=20)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=20)
  
  def __str__(self):
   return self.id_procedimiento.tipo_procedimiento.tipo + " -- " + self.motivo_fallecimiento + " -- " + self.nombres + " -- " + self.apellidos + " -- " + self.cedula + " -- " + self.edad + " -- " + self.sexo + " -- " + self.descripcion + " -- " + self.material_utilizado + " -- " + self.status

class Inspeccion_Establecimiento_Art(models.Model):
  id_proc_artificio = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  nombre_comercio = models.TextField()
  rif_comercio = models.CharField(max_length=60)
  encargado_nombre = models.CharField(max_length=60)
  encargado_apellidos = models.CharField(max_length=60)
  encargado_cedula = models.CharField(max_length=20)
  encargado_sexo = models.CharField(max_length=60)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=60)

  def __str__(self):
    return self.id_proc_artificio.id_tipo_procedimiento.tipo_procedimiento + " -- " + self.nombre_comercio + " -- " + self.rif_comercio + " -- " + self.encargado_nombre + " -- " + self.encargado_apellidos + " -- " + self.encargado_cedula + " -- " + self.encargado_sexo + " -- " + self.descripcion + " -- " + self.material_utilizado + " -- " + self.status

class Valoracion_Medica(models.Model):
  id_procedimientos = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  nombre = models.CharField(max_length=80)
  apellido = models.CharField(max_length=80)
  cedula = models.CharField(max_length=20)
  edad = models.CharField(max_length=3)
  sexo = models.CharField(max_length=20)
  telefono = models.CharField(max_length=40)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=15)

  def __str__(self):
    return self.id_procedimientos.id_tipo_procedimiento.tipo_procedimiento + " -- " + self.nombre + " -- " + self.apellido + " -- " + self.cedula + " -- " + self.edad + " -- " + self.sexo + " -- " + self.telefono + " -- " + self.descripcion + " -- " + self.material_utilizado + " -- " + self.status
  
class Detalles_Enfermeria(models.Model):
  id_procedimientos = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  nombre = models.CharField(max_length=80)
  apellido = models.CharField(max_length=80)
  cedula = models.CharField(max_length=20)
  edad = models.CharField(max_length=3)
  sexo = models.CharField(max_length=20)
  telefono = models.CharField(max_length=40)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=20)

  def __str__(self):
    return self.id_procedimientos.id_tipo_procedimiento.tipo_procedimiento + " -- " + self.nombre + " -- " + self.apellido + " -- " + self.cedula + " -- " + self.edad + " -- " + self.sexo + " -- " + self.telefono + " -- " + self.descripcion + " -- " + self.material_utilizado + " -- " + self.status
  
class Procedimientos_Psicologia(models.Model):
  id_procedimientos = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  nombre = models.CharField(max_length=80)
  apellido = models.CharField(max_length=80)
  cedula = models.CharField(max_length=20)
  edad = models.CharField(max_length=3)
  sexo = models.CharField(max_length=20)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=15)

  def __str__(self):
    return self.id_procedimientos.id_tipo_procedimiento.tipo_procedimiento + " -- " + self.nombre + " -- " + self.apellido + " -- " + self.cedula + " -- " + self.edad + " -- " + self.sexo + " -- "  + self.descripcion + " -- " + self.material_utilizado + " -- " + self.status
  
class Procedimientos_Capacitacion(models.Model):
  id_procedimientos = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  tipo_capacitacion = models.CharField(max_length=40)
  tipo_clasificacion = models.CharField(max_length=40)
  personas_beneficiadas = models.CharField(max_length=4)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=50)

  def __str__(self):
        return (
            self.id_procedimientos.id_tipo_procedimiento.tipo_procedimiento + " -- " +
            self.tipo_capacitacion + " -- " +
            self.tipo_clasificacion + " -- " +
            self.personas_beneficiadas + " -- " +
            self.descripcion + " -- " +
            self.material_utilizado + " -- " +
            self.status
        )

class Procedimientos_Brigada(models.Model):
  id_procedimientos = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  tipo_capacitacion = models.CharField(max_length=40)
  tipo_clasificacion = models.CharField(max_length=40)
  personas_beneficiadas = models.CharField(max_length=4)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=50)

  def __str__(self):
        return (
            self.id_procedimientos.id_tipo_procedimiento.tipo_procedimiento + " -- " +
            self.tipo_capacitacion + " -- " +
            self.tipo_clasificacion + " -- " +
            self.personas_beneficiadas + " -- " +
            self.descripcion + " -- " +
            self.material_utilizado + " -- " +
            self.status
        )

class Procedimientos_Frente_Preventivo(models.Model):
  id_procedimientos = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  nombre_actividad = models.TextField()
  estrategia = models.TextField()
  personas_beneficiadas = models.CharField(max_length=4)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=50)

  def __str__(self):
        return (
            self.id_procedimientos.id_tipo_procedimiento.tipo_procedimiento + " -- " +
            self.nombre_actividad + " -- " +
            self.estrategia + " -- " +
            self.personas_beneficiadas + " -- " +
            self.descripcion + " -- " +
            self.material_utilizado + " -- " +
            self.status
        )

class Jornada_Medica(models.Model):
  id_procedimientos = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  nombre_jornada = models.TextField()
  cant_personas_aten = models.CharField(max_length=4)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=20)

class Inspeccion_Prevencion_Asesorias_Tecnicas(models.Model):
  id_procedimientos = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  tipo_inspeccion = models.TextField()
  nombre_comercio = models.TextField()
  propietario = models.TextField()
  cedula_propietario = models.CharField(max_length=20)
  descripcion = models.TextField()
  persona_sitio_nombre = models.CharField(max_length=60)
  persona_sitio_apellido = models.CharField(max_length=60)
  persona_sitio_cedula = models.CharField(max_length=20)
  persona_sitio_telefono = models.CharField(max_length=30)
  material_utilizado = models.TextField()
  status = models.CharField(max_length=20)

  def __str__(self):
        return (
            self.id_procedimientos.id_tipo_procedimiento.tipo_procedimiento + " -- " +
            self.tipo_inspeccion + " -- " +
            self.nombre_comercio + " -- " +
            self.propietario + " -- " +
            self.cedula_propietario + " -- " +
            self.descripcion + " -- " +
            self.material_utilizado + " -- " +
            self.status
        )

class Inspeccion_Habitabilidad(models.Model):
  id_procedimientos = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  tipo_inspeccion = models.CharField(max_length=80)
  descripcion = models.TextField()
  persona_sitio_nombre = models.CharField(max_length=60)
  persona_sitio_apellido = models.CharField(max_length=60)
  persona_sitio_cedula = models.CharField(max_length=20)
  persona_sitio_telefono = models.CharField(max_length=30)
  material_utilizado = models.TextField()
  status = models.CharField(max_length=20)

  def __str__(self):
        return (
            self.id_procedimientos.id_tipo_procedimiento.tipo_procedimiento + " -- " +
            self.tipo_inspeccion + " -- " +
            self.descripcion + " -- " +
            self.persona_sitio_nombre + " -- " +
            self.persona_sitio_apellido + " -- " +
            self.persona_sitio_cedula + " -- " +
            self.persona_sitio_telefono + " -- " +
            self.material_utilizado + " -- " +
            self.status
        )

class Inspeccion_Otros(models.Model):
  id_procedimientos = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  tipo_inspeccion = models.CharField(max_length=80)
  especifique = models.TextField()
  descripcion = models.TextField()
  persona_sitio_nombre = models.CharField(max_length=60)
  persona_sitio_apellido = models.CharField(max_length=60)
  persona_sitio_cedula = models.CharField(max_length=20)
  persona_sitio_telefono = models.CharField(max_length=30)
  material_utilizado = models.TextField()
  status = models.CharField(max_length=20)

  def __str__(self):
        return (
            self.id_procedimientos.id_tipo_procedimiento.tipo_procedimiento + " -- " +
            self.tipo_inspeccion + " -- " +
            self.especifique + " -- " +
            self.descripcion + " -- " +
            self.persona_sitio_nombre + " -- " +
            self.persona_sitio_apellido + " -- " +
            self.persona_sitio_cedula + " -- " +
            self.persona_sitio_telefono + " -- " +
            self.material_utilizado + " -- " +
            self.status
        )

class Inspeccion_Arbol(models.Model):
  id_procedimientos = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  tipo_inspeccion = models.CharField(max_length=80)
  especie = models.TextField()
  altura_aprox = models.CharField(max_length=40)
  ubicacion_arbol = models.TextField()
  persona_sitio_nombre = models.CharField(max_length=60)
  persona_sitio_apellido = models.CharField(max_length=60)
  persona_sitio_cedula = models.CharField(max_length=20)
  persona_sitio_telefono = models.CharField(max_length=30)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=20)

  def __str__(self):
        return (
            self.id_procedimientos.id_tipo_procedimiento.tipo_procedimiento + " -- " +
            self.tipo_inspeccion + " -- " +
            self.especie + " -- " +
            self.altura_aprox + " -- " +
            self.ubicacion_arbol + " -- " +
            self.persona_sitio_nombre + " -- " +
            self.persona_sitio_apellido + " -- " +
            self.persona_sitio_cedula + " -- " +
            self.persona_sitio_telefono + " -- " +
            self.descripcion + " -- " +
            self.material_utilizado + " -- " +
            self.status
        )

# Modelos para el procedimiento "Investigacion"

class Investigacion(models.Model):
  id_procedimientos = models.ForeignKey(Procedimientos, on_delete=models.CASCADE)
  id_tipo_investigacion = models.ForeignKey(Tipos_Investigacion, on_delete=models.CASCADE)
  tipo_siniestro = models.CharField(max_length=100)

  def __str__(self):
    return self.id_procedimientos.id_tipo_procedimiento.tipo_procedimiento + " -- " + self.id_tipo_investigacion.tipo_investigacion + " -- " + self.tipo_siniestro
  
class Investigacion_Vehiculo(models.Model):
  id_investigacion = models.ForeignKey(Investigacion, on_delete=models.CASCADE)
  marca = models.CharField(max_length=40)
  modelo = models.CharField(max_length=25)
  color = models.CharField(max_length=20)
  placas = models.CharField(max_length=20)
  año = models.CharField(max_length=4)
  nombre_propietario = models.CharField(max_length=70)
  apellido_propietario = models.CharField(max_length=70)
  cedula_propietario = models.CharField(max_length=50)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=100)

class Investigacion_Comercio(models.Model):
  id_investigacion = models.ForeignKey(Investigacion, on_delete=models.CASCADE)
  nombre_comercio = models.CharField(max_length=100)
  rif_comercio = models.CharField(max_length=50)
  nombre_propietario = models.CharField(max_length=50)
  apellido_propietario = models.CharField(max_length=50)
  cedula_propietario = models.CharField(max_length=20)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=20)

class Investigacion_Estructura_Vivienda(models.Model):
  id_investigacion = models.ForeignKey(Investigacion, on_delete=models.CASCADE)
  tipo_estructura = models.CharField(max_length=80)
  nombre = models.CharField(max_length=50)
  apellido = models.CharField(max_length=50)
  cedula = models.CharField(max_length=20)
  descripcion = models.TextField()
  material_utilizado = models.TextField()
  status = models.CharField(max_length=20)

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
    descripcion = models.TextField()
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
    nuevo_departamento = models.CharField(max_length=20)
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


