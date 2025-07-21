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

def get_personal_choices_for_model_form():
    # This queryset will be used by the ModelChoiceField
    return Personal.objects.filter(
        id__in=[44, 5, 53, 73]
    ).exclude(id=4).order_by('nombres')

def get_personal_choices_for_observadores_model_form():
    return Personal.objects.filter(
        id__in=[0, 44, 5, 53, 73]
    ).exclude(id=4).order_by('nombres')

def get_drones_choices_for_model_form():
    # Assuming 'nombre_dron' is the field to display
    return Drones.objects.all().order_by('nombre_dron')

# ---------------------- FORMULARIO PARA REGISTRO DE VUELOS ----------------------
class RegistroVuelosForm(forms.ModelForm):
    # Fixed choices for 'tipo_mision' as it's not directly from a model relationship
    tipo_mision_choices = [
        ("", "Seleccion Una Opcion"),
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

    # Explicitly define fields to control their type, widgets, and labels,
    # especially for ForeignKey fields to use custom display logic.
    id_operador = forms.ModelChoiceField(
        queryset=Personal.objects.none(), # Initial empty queryset, will be set in __init__
        label="Operador del Vuelo",
        widget=forms.Select(attrs={"class": "form-select disable-first-option"}),
        empty_label="Seleccione Una Opcion" # Ensures the 'Seleccione Una Opcion' for ModelChoiceField
    )
    id_observador = forms.ModelChoiceField(
        queryset=Personal.objects.none(), # Initial empty queryset, will be set in __init__
        label="Observador del Vuelo",
        widget=forms.Select(attrs={"class": "form-select disable-first-option"}),
        empty_label="Seleccione Una Opcion"
    )
    id_dron = forms.ModelChoiceField(
        queryset=Drones.objects.none(), # Initial empty queryset, will be set in __init__
        label="Dron Utilizado",
        widget=forms.Select(attrs={"class": "form-select disable-first-option"}),
        empty_label="Seleccione Una Opcion"
    )

    # Fields that were already custom in the ModelForm and match your form.Form definition
    fecha = forms.DateField(label="Fecha del Vuelo", widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))
    hora_despegue = forms.TimeField(label="Hora de Despegue", widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}))
    hora_aterrizaje = forms.TimeField(label="Hora de Aterrizaje", widget=forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}))

    # Fields that need specific widgets/required status
    observador_externo = forms.CharField(label="Observador Externo", required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    sitio = forms.CharField(max_length=100, label="Sitio del Vuelo", widget=forms.TextInput(attrs={'class': 'form-control'}))
    
    # Use ChoiceField for tipo_mision with custom choices
    tipo_mision = forms.ChoiceField(choices=tipo_mision_choices, label="Tipo de Misión", widget=forms.Select(attrs={'class': 'form-select'}))
    observaciones_vuelo = forms.CharField(label="Observaciones", widget=forms.TextInput(attrs={'class': 'form-control', 'rows': 3}))
    apoyo_realizado_a = forms.CharField(label="Apoyo Realizado A", widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Registro_Vuelos
        # Define fields explicitly or use '__all__' / 'exclude'
        # Ensure all fields defined above are included here or implicitly by '__all__'
        fields = [
            'id_operador', 'id_observador', 'observador_externo', 'fecha', 'sitio',
            'hora_despegue', 'hora_aterrizaje', 'id_dron', 'tipo_mision',
            'observaciones_vuelo', 'apoyo_realizado_a'
        ]
        # 'id_vuelo' is excluded as it's auto-generated and not part of the form submission.
        # No need for `widgets` or `labels` dicts if fields are explicitly defined above.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Apply the filtered queryset to id_operador and id_observador
        self.fields['id_operador'].queryset = get_personal_choices_for_model_form()
        self.fields['id_observador'].queryset = get_personal_choices_for_observadores_model_form()
        self.fields['id_dron'].queryset = get_drones_choices_for_model_form()

        def get_personal_display_label(person_instance):
            jerarquia_abreviatura = person_instance.jerarquia
            return f"{jerarquia_abreviatura} {person_instance.nombres} {person_instance.apellidos}".strip()

        self.fields['id_operador'].label_from_instance = get_personal_display_label
        self.fields['id_observador'].label_from_instance = get_personal_display_label
        
        # Custom label_from_instance for Drones (assuming 'nombre_dron' is the display field)
        def get_dron_display_label(dron_instance):
            return dron_instance.nombre_dron
        
        self.fields['id_dron'].label_from_instance = get_dron_display_label

### `EstadoDronForm` (ModelForm)
class EstadoDronForm(forms.ModelForm):
    # Defined choices for consistent dropdown options
    estado_choices = [("", "Seleccione Una Opcion"), ("EE", "EE"), ("RE", "RE"), ("ME", "ME")]

    # Explicitly define fields that use ChoiceField with specific options
    cuerpo = forms.ChoiceField(choices=estado_choices, label="Estado del Cuerpo")
    observacion_cuerpo = forms.CharField(label="Observacion", required=False)
    camara = forms.ChoiceField(choices=estado_choices, label="Estado de la Cámara")
    observacion_camara = forms.CharField(label="Observacion", required=False)
    helices = forms.ChoiceField(choices=estado_choices, label="Estado de las Hélices")
    observacion_helices = forms.CharField(label="Observacion", required=False)
    sensores = forms.ChoiceField(choices=estado_choices, label="Estado de los Sensores")
    observacion_sensores = forms.CharField(label="Observacion", required=False)
    motores = forms.ChoiceField(choices=estado_choices, label="Estado de los Motores")
    observacion_motores = forms.CharField(label="Observacion", required=False)

    class Meta:
        model = EstadoDron
        exclude = ['id_dron', 'id_vuelo'] # Exclude 'id_vuelo' as it's typically set outside the form
        widgets = {
            'cuerpo': forms.Select(attrs={'class': 'form-select'}),
            'observacion_cuerpo': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'camara': forms.Select(attrs={'class': 'form-select'}),
            'observacion_camara': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'helices': forms.Select(attrs={'class': 'form-select'}),
            'observacion_helices': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'sensores': forms.Select(attrs={'class': 'form-select'}),
            'observacion_sensores': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'motores': forms.Select(attrs={'class': 'form-select'}),
            'observacion_motores': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class EstadoBateriasForm(forms.ModelForm):
    bateria_level_choices = [("", "Seleccione Una Opcion"), ("100", "100"), ("75", "75"), ("50", "50"), ("25", "25"), ("0", "0")]

    bateria1 = forms.ChoiceField(choices=bateria_level_choices, label="Estado de Batería 1")
    bateria2 = forms.ChoiceField(choices=bateria_level_choices, label="Estado de Batería 2")
    bateria3 = forms.ChoiceField(choices=bateria_level_choices, label="Estado de Batería 3")
    bateria4 = forms.ChoiceField(choices=bateria_level_choices, label="Estado de Batería 4")

    class Meta:
        model = EstadoBaterias
        exclude = ['id_dron', 'id_vuelo']
        widgets = {
            'bateria1': forms.Select(attrs={'class': 'form-select'}),
            'bateria2': forms.Select(attrs={'class': 'form-select'}),
            'bateria3': forms.Select(attrs={'class': 'form-select'}),
            'bateria4': forms.Select(attrs={'class': 'form-select'}),
        }
        # Labels are already set in the field definitions above, so no need for `labels` dict here.


class EstadoControlForm(forms.ModelForm):
    estado_choices = [("", "Seleccione Una Opcion"), ("EE", "EE"), ("RE", "RE"), ("ME", "ME")]
    bateria_level_choices = [("", "Seleccione Una Opcion"), ("100", "100"), ("75", "75"), ("50", "50"), ("25", "25"), ("0", "0")]

    # Renamed field to 'cuerpo' to match the model (assuming it's 'cuerpo' not 'cuerpo_control' on the model)
    cuerpo = forms.ChoiceField(choices=estado_choices, label="Estado del Cuerpo")
    joysticks = forms.ChoiceField(choices=estado_choices, label="Estado de los Joysticks")
    pantalla = forms.ChoiceField(choices=estado_choices, label="Estado de la Pantalla")
    antenas = forms.ChoiceField(choices=estado_choices, label="Estado de las Antenas")
    bateria = forms.ChoiceField(choices=bateria_level_choices, label="Estado de la Batería del Control")

    class Meta:
        model = EstadoControl
        exclude = ['id_dron', 'id_vuelo']
        widgets = {
            'cuerpo': forms.Select(attrs={'class': 'form-select'}),
            'joysticks': forms.Select(attrs={'class': 'form-select'}),
            'pantalla': forms.Select(attrs={'class': 'form-select'}),
            'antenas': forms.Select(attrs={'class': 'form-select'}),
            'bateria': forms.Select(attrs={'class': 'form-select'}), # Changed to Select as per your choices
        }


class DetallesVueloForm(forms.ModelForm):
    viento_choices = [("", "Seleccione Una Opcion"), ("Normal", "Normal"), ("Fuerte", "Fuerte"), ("No Apto", "No Apto")]
    nubosidad_choices = [("", "Seleccione Una Opcion"), ("Despejado", "Despejado"), ("Nublado", "Nublado"), ("Muy Nublado", "Muy Nublado")]
    riesgo_vuelo_choices = [("", "Seleccione Una Opcion"), ("Alto", "Alto"), ("Medio", "Medio"), ("Bajo", "Bajo")]
    zona_vuelo_choices = [("", "Seleccione Una Opcion"), ("Zona de Seguridad", "Zona de Seguridad"), ("Zona sin Seguridad", "Zona sin Seguridad")]
    magnitud_distancia_choices = [("Km", "Km"), ("Mtrs", "Mtrs")] # No "Seleccione Una Opcion" here, assuming a default will be selected

    viento = forms.ChoiceField(choices=viento_choices, label="Viento")
    nubosidad = forms.ChoiceField(choices=nubosidad_choices, label="Nubosidad")
    riesgo_vuelo = forms.ChoiceField(choices=riesgo_vuelo_choices, label="Riesgo del Vuelo")
    zona_vuelo = forms.ChoiceField(choices=zona_vuelo_choices, label="Zona de Vuelo")
    
    # CharField for text input, as in your original form.Form
    numero_satelites = forms.CharField(label="Número de Satélites", 
                                       widget=forms.TextInput(attrs={'class': 'form-control'}))
    distancia_recorrida = forms.CharField(max_length=10, label="Distancia Recorrida", 
                                          widget=forms.TextInput(attrs={'class': 'form-control'}))
    magnitud_distancia = forms.ChoiceField(choices=magnitud_distancia_choices, label="Unidad de Distancia", 
                                           widget=forms.Select(attrs={'class': 'form-select'}))
    altitud = forms.CharField(max_length=10, label="Altitud", 
                              widget=forms.TextInput(attrs={'class': 'form-control'}))
    duracion_vuelo = forms.CharField(max_length=10, label="Duración del Vuelo", 
                                    widget=forms.TextInput(attrs={'class': 'form-control'}))
    observaciones = forms.CharField(label="Observaciones", 
                                   widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = DetallesVuelo
        exclude = ['id_vuelo']
        # Widgets are already defined directly in the field declarations above.
        # Labels are also defined directly.
        # Ensure all fields explicitly defined above exist on the DetallesVuelo model.