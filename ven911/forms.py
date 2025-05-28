from django import forms
from django.forms import ModelForm, DateInput, TimeInput, ModelChoiceField
from .models import *
from web.models import Personal

class PersonalModelChoiceField(ModelChoiceField):
    """Campo personalizado para mostrar Personal en formato 'nombres apellidos - jerarquia'"""
    def label_from_instance(self, obj):
        return f"{obj.nombres} {obj.apellidos} - {obj.jerarquia}"

class ServicioForm(ModelForm):
    # Sobreescribimos los campos que usan Personal con nuestro campo personalizado
    operador_de_guardia = PersonalModelChoiceField(
        queryset=Personal.objects.none(),  # Se actualizará en __init__
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    class Meta:
        model = Servicio
        fields = '__all__'
        widgets = {
            'tipo_servicio': forms.Select(attrs={'class': 'form-control'}),
            'cantidad_tipo_servicio' : forms.NumberInput(attrs={'class': 'form-control'}),
            'operador_de_guardia': forms.Select(attrs={'class': 'form-control'}),
            'fecha': DateInput(attrs={'type': 'date', 'class': 'form-control'}, format='%Y-%m-%d'),
            'hora': TimeInput(attrs={'type': 'time', 'class': 'form-control'}, format='%H:%M'),

        }
        labels = {
            'tipo_servicio': 'Tipo de Servicio',
            'cantidad_tipo_servicio': 'Cantidad de Servicio',
            'operador_de_guardia': 'Operador de Guardia',
            'fecha': 'Fecha del Servicio',
            'hora': 'Hora del Servicio',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Optimizamos las consultas para solo traer los campos necesarios
        self.fields['tipo_servicio'].queryset = TipoServicio.objects.all()
        
        # Personalizamos los querysets para Personal, excluyendo IDs 0 y 4
        personal_queryset = Personal.objects.exclude(id__in=[0, 4]).only('nombres', 'apellidos', 'jerarquia')
        self.fields['operador_de_guardia'].queryset = personal_queryset
    def clean(self):
        cleaned_data = super().clean()
        # Aquí puedes agregar validaciones personalizadas si las necesitas
        return cleaned_data