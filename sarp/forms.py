from django import forms
from django.db.models import Q
from django.db.models import Case, When, Value, IntegerField
from django.forms import inlineformset_factory
from django.forms import BaseInlineFormSet
from django.utils.safestring import mark_safe
from .models import *
from .views import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


# ================================================================================ Formularios Para el Area del Sarc ===================================================================


def Asignar_ops_Operadores(): 
    # jerarquias = [ 
    #     "General", "Coronel", "Teniente Coronel", "Mayor", "Capitán", "Primer Teniente", 
    #     "Teniente", "Sargento Mayor", "Sargento Primero", "Sargento Segundo", "Cabo Primero", 
    #     "Cabo Segundo", "Distinguido", "Bombero"
    # ] 
    
    # Obtener personal con los filtros adecuados
    personal = Personal.objects.filter(
        id__in=[0,44,5,53,73]
    ).exclude(id=4)

    # # Ordenar según jerarquía
    # personal_ordenado = personal.order_by(
    #     Case(
    #         *[When(jerarquia=nombre, then=Value(pos)) for pos, nombre in enumerate(jerarquias)],
    #         output_field=IntegerField()
    #     )
    # )

    # Construir opciones para el desplegable
    op = [("", "Seleccione Una Opción")]  
    for persona in personal:
        op.append((str(persona.id), f"{persona.jerarquia} {persona.nombres} {persona.apellidos}"))  
    
    return op

def Asignar_ops_Drones():
    # Obtener personal con los filtros adecuados
    personal = Drones.objects.all()

    # Construir opciones para el desplegable
    op = [("", "Seleccione Una Opción")]  
    for persona in personal:
        op.append((str(persona.id_dron), f"{persona.nombre_dron} {persona.modelo_dron}"))  
    
    return op


# ---------------------- FORMULARIO PARA DRONES ----------------------
class DronesForm(forms.Form):
    nombre_dron = forms.CharField(max_length=100, label="Nombre del Dron")
    id_dron = forms.CharField(max_length=50, label="ID del Dron")
    modelo_dron = forms.CharField(max_length=100, label="Modelo del Dron")

    # 🎉 Añade el constructor __init__ y el helper para Crispy Forms
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            # Puedes usar Row y Column para organizar los campos en filas de Bootstrap
            Row(
                Column('nombre_dron', css_class='form-group col-md-4 mb-0'),
                Column('id_dron', css_class='form-group col-md-4 mb-0'),
                Column('modelo_dron', css_class='form-group col-md-4 mb-0'),
                css_class='form-row' # Clase para la fila de Bootstrap
            ),
            # Si quieres un botón de enviar, puedes añadirlo aquí
            # Submit('submit', 'Guardar Dron', css_class='btn btn-primary mt-3')
        )

# ---------------------- FORMULARIO PARA REGISTRO DE VUELOS ----------------------
class RegistroVuelosForm(forms.Form):
    opc = [("", "Seleccion Una Opcion"),
           ("Planimetria", "Planimetria"),
            ("Vuelo de Reconocimiento", "Vuelo de Reconocimiento"),
            ("Vigilancia", "Vigilancia"),
            ("Apoyo Audiovisual", "Apoyo Audiovisual"),
            ("Control Forestal", "Control Forestal"),
            ("Control de Incendios", "Control de Incendios"),
            ("Gestion de Riesgo", "Gestion de Riesgo"),
            ("Busqueda y Rescate", "Busqueda y Rescate"),
            ("Otros", "Otros")
           ]

    id_operador = forms.ChoiceField(choices=Asignar_ops_Operadores(), label="Operador del Vuelo", widget=forms.Select(attrs={"class": "disable-first-option"}))
    id_observador = forms.ChoiceField(choices=Asignar_ops_Operadores(), label="Observador del Vuelo", widget=forms.Select(attrs={"class": "disable-first-option"}))
    observador_externo = forms.CharField(label="Observador Externo", required=False)
    fecha = forms.DateField(label="Fecha del Vuelo", widget=forms.DateInput(attrs={'type': 'date'}))
    sitio = forms.CharField(max_length=100, label="Sitio del Vuelo")
    hora_despegue = forms.TimeField(label="Hora de Despegue", widget=forms.TimeInput(attrs={'type': 'time'}))
    hora_aterrizaje = forms.TimeField(label="Hora de Aterrizaje", widget=forms.TimeInput(attrs={'type': 'time'}))
    id_dron = forms.ChoiceField(choices=Asignar_ops_Drones(), label="Dron Utilizado", widget=forms.Select(attrs={"class": "disable-first-option"}))

    tipo_mision = forms.ChoiceField(choices=opc, label="Tipo de Misión")
    observaciones_vuelo = forms.CharField(label="Observaciones", widget=forms.Textarea)
    apoyo_realizado_a = forms.CharField(label="Apoyo Realizado A")

# ---------------------- FORMULARIO PARA ESTADO DEL DRON ----------------------
class EstadoDronForm(forms.Form):
    cuerpo = forms.ChoiceField(choices=[("", "Seleccione Una Opcion"), ("EE", "EE"), ("RE", "RE"), ("ME", "ME")], label="Estado del Cuerpo")
    observacion_cuerpo = forms.CharField(label="Observacion")
    camara = forms.ChoiceField(choices=[("", "Seleccione Una Opcion"), ("EE", "EE"), ("RE", "RE"), ("ME", "ME")], label="Estado de la Cámara")
    observacion_camara = forms.CharField(label="Observacion")
    helices = forms.ChoiceField(choices=[("", "Seleccione Una Opcion"), ("EE", "EE"), ("RE", "RE"), ("ME", "ME")], label="Estado de las Hélices")
    observacion_helices = forms.CharField(label="Observacion")
    sensores = forms.ChoiceField(choices=[("", "Seleccione Una Opcion"), ("EE", "EE"), ("RE", "RE"), ("ME", "ME")], label="Estado de los Sensores")
    observacion_sensores = forms.CharField(label="Observacion")
    motores = forms.ChoiceField(choices=[("", "Seleccione Una Opcion"), ("EE", "EE"), ("RE", "RE"), ("ME", "ME")], label="Estado de los Motores")
    observacion_motores = forms.CharField(label="Observacion")

# ---------------------- FORMULARIO PARA ESTADO DE LAS BATERÍAS ----------------------
class EstadoBateriasForm(forms.Form):
    bateria1 = forms.ChoiceField(choices=[("", "Seleccione Una Opcion"), ("100", "100"), ("75", "75"), ("50", "50"), ("25", "25"), ("0", "0")], label="Estado de Batería 1")
    bateria2 = forms.ChoiceField(choices=[("", "Seleccione Una Opcion"), ("100", "100"), ("75", "75"), ("50", "50"), ("25", "25"), ("0", "0")], label="Estado de Batería 2")
    bateria3 = forms.ChoiceField(choices=[("", "Seleccione Una Opcion"), ("100", "100"), ("75", "75"), ("50", "50"), ("25", "25"), ("0", "0")], label="Estado de Batería 3")
    bateria4 = forms.ChoiceField(choices=[("", "Seleccione Una Opcion"), ("100", "100"), ("75", "75"), ("50", "50"), ("25", "25"), ("0", "0")], label="Estado de Batería 4")

# ---------------------- FORMULARIO PARA ESTADO DEL CONTROL ----------------------
class EstadoControlForm(forms.Form):
    cuerpo_control = forms.ChoiceField(choices=[("", "Seleccione Una Opcion"), ("EE", "EE"), ("RE", "RE"), ("ME", "ME")], label="Estado del Cuerpo")
    joysticks = forms.ChoiceField(choices=[("", "Seleccione Una Opcion"), ("EE", "EE"), ("RE", "RE"), ("ME", "ME")], label="Estado de los Joysticks")
    pantalla = forms.ChoiceField(choices=[("", "Seleccione Una Opcion"), ("EE", "EE"), ("RE", "RE"), ("ME", "ME")], label="Estado de la Pantalla")
    antenas = forms.ChoiceField(choices=[("", "Seleccione Una Opcion"), ("EE", "EE"), ("RE", "RE"), ("ME", "ME")], label="Estado de las Antenas")
    bateria = forms.ChoiceField(choices=[("", "Seleccione Una Opcion"), ("100", "100"), ("75", "75"), ("50", "50"), ("25", "25"), ("0", "0")], label="Estado de la Batería del Control")

# ---------------------- FORMULARIO PARA DETALLES DEL VUELO ----------------------
class DetallesVueloForm(forms.Form):
    viento = forms.ChoiceField(choices=[("", "Seleccione Una Opcion"), ("Normal", "Normal"), ("Fuerte", "Fuerte"), ("No Apto", "No Apto")], label="Viento")
    nubosidad = forms.ChoiceField(choices=[("", "Seleccione Una Opcion"), ("Despejado", "Despejado"), ("Nublado", "Nublado"), ("Muy Nublado", "Muy Nublado")], label="Nubosidad")
    riesgo_vuelo = forms.ChoiceField(choices=[("", "Seleccione Una Opcion"), ("Alto", "Alto"), ("Medio", "Medio"), ("Bajo", "Bajo")], label="Riesgo del Vuelo")
    zona_vuelo = forms.ChoiceField(choices=[("", "Seleccione Una Opcion"), ("Zona de Seguridad", "Zona de Seguridad"), ("Zona sin Seguridad", "Zona sin Seguridad")], label="Zona de Vuelo")
    numero_satelites = forms.CharField(label="Número de Satélites")
    distancia_recorrida = forms.CharField(max_length=10, label="Distancia Recorrida")
    magnitud_distancia = forms.ChoiceField(choices=[("Km", "Km"), ("Mtrs", "Mtrs")], label="")
    altitud = forms.CharField(max_length=10, label="Altitud")
    duracion_vuelo = forms.CharField(max_length=10, label="Duración del Vuelo")
    observaciones = forms.CharField(label="Observaciones", widget=forms.Textarea)
