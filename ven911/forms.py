from django import forms
from django.forms import ModelForm, DateInput, TimeInput
from .models import Servicio, OperadorDeGuardia, TipoServicio
from web.models import Municipios, Parroquias, Unidades, Personal

class ServicioForm(ModelForm):
    class Meta:
        model = Servicio
        fields = '__all__'
        widgets = {
            'fecha': DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                },
                format='%Y-%m-%d'
            ),
            'hora': TimeInput(
                attrs={
                    'type': 'time',
                    'class': 'form-control',
                },
                format='%H:%M'
            ),
            'operador_de_guardia': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),
            'municipio': forms.Select(
                attrs={
                    'class': 'form-control',
                    'id': 'id_municipio',  # ID para el JavaScript
                }
            ),
            'parroquia': forms.Select(
                attrs={
                    'class': 'form-control',
                    'id': 'id_parroquia',
                }
            ),
            'tipo_servicio': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),
            'unidad': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),
            'jefe_de_comision': forms.Select(
                attrs={
                    'class': 'form-control',
                }
            ),
            'descripcion': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 3,
                }
            ),
            'lugar': forms.TextInput(
                attrs={
                    'class': 'form-control',
                }
            )
        }
        labels = {
            'operador_de_guardia': 'Operador de Guardia',
            'fecha': 'Fecha del Servicio',
            'hora': 'Hora del Servicio',
            'lugar': 'Lugar Específico',
            'municipio': 'Municipio',
            'parroquia': 'Parroquia',
            'tipo_servicio': 'Tipo de Servicio',
            'unidad': 'Unidad Responsable',
            'jefe_de_comision': 'Jefe de Comisión',
            'descripcion': 'Descripción Detallada'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ordenar los querysets por nombre
        self.fields['municipio'].queryset = Municipios.objects.all().order_by('municipio')
        self.fields['parroquia'].queryset = Parroquias.objects.all().order_by('parroquia')  # Inicialmente vacío
        self.fields['unidad'].queryset = Unidades.objects.all()
        self.fields['jefe_de_comision'].queryset = Personal.objects.all()
        self.fields['tipo_servicio'].queryset = TipoServicio.objects.all()
        self.fields['operador_de_guardia'].queryset = OperadorDeGuardia.objects.all()
