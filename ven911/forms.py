from django import forms
from django.forms import ModelForm, DateInput, TimeInput, ModelChoiceField
from django.utils import timezone
from .models import *
from web.models import Personal

class PersonalModelChoiceField(ModelChoiceField):
    """Campo personalizado para mostrar Personal en formato 'nombres apellidos - jerarquia'"""
    def label_from_instance(self, obj):
        return f"{obj.nombres} {obj.apellidos} - {obj.jerarquia}"

class ServicioForm(ModelForm):
    operador_de_guardia = PersonalModelChoiceField(
        queryset=Personal.objects.none(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Servicio
        fields = '__all__'
        widgets = {
            'tipo_servicio': forms.Select(attrs={'class': 'form-control'}),
            'cantidad_tipo_servicio': forms.NumberInput(attrs={'class': 'form-control'}),
            'fecha': DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
            }, format='%Y-%m-%d'),
            'hora': TimeInput(attrs={
                'type': 'time',
                'class': 'form-control',
            }, format='%H:%M'),
        }
        labels = {
            'tipo_servicio': 'Tipo de Servicio',
            'cantidad_tipo_servicio': 'Cantidad de Servicio',
            'operador_de_guardia': 'Operador de Guardia',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tipo_servicio'].queryset = TipoServicio.objects.all()
        personal_queryset = Personal.objects.exclude(id__in=[0, 4]).only('nombres', 'apellidos', 'jerarquia')
        self.fields['operador_de_guardia'].queryset = personal_queryset

        # Establecer fecha y hora actuales si es un nuevo registro (no instancia existente)
        if not self.instance.pk:
            now = timezone.localtime(timezone.now())  # Usa la zona horaria configurada
            self.initial['fecha'] = now.date()
            self.initial['hora'] = now.time()

    def clean(self):
        cleaned_data = super().clean()
        # Validaciones adicionales si son necesarias
        return cleaned_data