from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Field
from .models import *
from web.forms import Asignar_ops_Personal


class BienMunicipalForm(forms.Form):
    identificador = forms.CharField(max_length=20)
    descripcion = forms.CharField(widget=forms.Textarea)
    cantidad = forms.IntegerField(min_value=0)
    dependencia = forms.ModelChoiceField(queryset=Dependencia.objects.all())
    departamento = forms.CharField(max_length=100)
    responsable = forms.ChoiceField(choices=Asignar_ops_Personal(), label="Responsable", widget=forms.Select(attrs={"class": "disable-first-option"}))
    fecha_registro = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    estado_actual = forms.ChoiceField(choices=EstadoBien.choices)

class CambiarEstadoBienForm(forms.Form):
    bien_cambiar_estado = forms.CharField()
    estado_actual = forms.CharField(max_length=100)
    nuevo_estado = forms.ChoiceField(choices=EstadoBien.choices)
    fecha_orden = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))


class MovimientoBienForm(forms.Form):
    bien = forms.CharField(label="Identificador del Bien",
                           widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'})) # Añadido readonly y clase para Bootstrap
    nueva_dependencia = forms.ModelChoiceField(queryset=Dependencia.objects.all(),
                                               empty_label="Seleccione una Dependencia", # Opción por defecto
                                               widget=forms.Select(attrs={'class': 'form-select'})) # Clase Bootstrap
    nuevo_departamento = forms.CharField(max_length=100,
                                         widget=forms.TextInput(attrs={'class': 'form-control'})) # Clase Bootstrap
    ordenado_por = forms.ChoiceField(choices=Asignar_ops_Personal(),
                                     label="Ordenado Por",
                                     widget=forms.Select(attrs={"class": "form-select disable-first-option"})) # Clase Bootstrap
    fecha_orden = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})) # Clase Bootstrap

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post' # O 'get' si tu vista es GET
        # Si tienes un botón de submit en el template, no necesitas esta línea
        # self.helper.add_input(Submit('submit', 'Guardar Movimiento', css_class='btn btn-primary mt-3'))

        self.helper.layout = Layout(
            Row(
                Column('bien', css_class='form-group col-md-6 mb-0'),
                Column('nueva_dependencia', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('nuevo_departamento', css_class='form-group col-md-6 mb-0'),
                Column('ordenado_por', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'fecha_orden', # Este campo irá en una línea completa
            # Si necesitas un botón de submit dentro del layout del formulario
            # Submit('submit', 'Guardar Movimiento', css_class='btn btn-primary mt-3')
        )