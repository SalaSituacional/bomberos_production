from django import forms
from django.forms import ModelForm, DateInput, TimeInput, ModelChoiceField
from django.utils import timezone
from django.db.models import Case, When, Value, IntegerField
from .models import *
from web.models import Personal

class PersonalModelChoiceField(ModelChoiceField):
    """Campo personalizado para mostrar Personal en formato 'jerarquía - apellidos nombres'"""
    def label_from_instance(self, obj):
        return f"{obj.jerarquia} - {obj.apellidos} {obj.nombres}"

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
        
        # Ordenar tipo_servicio alfabéticamente
        self.fields['tipo_servicio'].queryset = TipoServicio.objects.all().order_by('nombre')
        
        # Definir el orden de las jerarquías (de mayor a menor rango)
        HIERARCHY_ORDER = [
            'General',
            'Coronel',
            'Teniente Coronel',
            'Mayor',
            'Capitán',
            'Primer Teniente',
            'Teniente',
            'Sargento Mayor',
            'Sargento Primero',
            'Sargento Segundo',
            'Cabo Primero',
            'Cabo Segundo',
            'Distinguido',
            'Bombero'
        ]
        
        # Crear condiciones para el ordenamiento
        hierarchy_order = Case(
            *[When(jerarquia=rank, then=Value(i)) for i, rank in enumerate(HIERARCHY_ORDER)],
            default=Value(len(HIERARCHY_ORDER)),
            output_field=IntegerField()
        )
        
        # Ordenar personal por jerarquía y luego por apellidos y nombres
        personal_queryset = (
            Personal.objects
            .exclude(id__in=[0, 4])
            .only('jerarquia', 'apellidos', 'nombres')
            .annotate(hierarchy_order=hierarchy_order)
            .order_by('hierarchy_order')
        )
        
        self.fields['operador_de_guardia'].queryset = personal_queryset

        # Establecer fecha y hora actuales si es un nuevo registro
        if not self.instance.pk:
            now = timezone.localtime(timezone.now())
            self.initial['fecha'] = now.date()
            self.initial['hora'] = now.time()

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data