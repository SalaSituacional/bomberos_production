from django import forms
from.models import *
# from web.forms import Asignar_op_Municipios

class ComercioForm(forms.ModelForm):
    class Meta:
        model = Comercio
        fields = ['nombre_comercio', 'rif_empresarial', 'departamento']

class SolicitudForm(forms.ModelForm):
    parroquia = forms.ModelChoiceField(
        queryset=Parroquias.objects.all(),
        required=True
    )
    
    TIPO_SERVICIO_CHOICES = [
        ("", "Selecione Una Opcion"), 
        ("Inspeccion", "Inspeccion"), 
        ("Reinspeccion", "Reinspeccion")
    ]
    
    TIPO_REPRESENTANTE_CHOICES = [
        ("", "Selecione Una Opcion"), 
        ("Presidente", "Presidente"), 
        ("Propietario", "Propietario"), 
        ("Representante Legal", "Representante Legal"), 
        ("Encargado", "Encargado")
    ]
    
    METODO_PAGO_CHOICES = [
        ("", "Seleccione Una Opcion"), 
        ("Efectivo", "Efectivo"), 
        ("Transferencia", "Transferencia"), 
        ("Deposito", "Deposito"), 
        ("Otra Moneda", "Otra Moneda")
    ]

    municipio = forms.ModelChoiceField(
        queryset=Municipios.objects.all(),
        required=True
    )
    id_solicitud = forms.ModelChoiceField(
        queryset=Comercio.objects.all().order_by("id_comercio"),
        required=True,
        label="Comercio",
        error_messages={
            'invalid_choice': 'Por favor seleccione un comercio válido de la lista'
        }
    )

    tipo_servicio = forms.ChoiceField(choices=TIPO_SERVICIO_CHOICES, required=False)
    tipo_representante = forms.ChoiceField(choices=TIPO_REPRESENTANTE_CHOICES, required=False)
    metodo_pago = forms.ChoiceField(choices=METODO_PAGO_CHOICES, required=False)
    
    class Meta:
        model = Solicitudes
        fields = '__all__'
        widgets = {
            'fecha_solicitud': forms.DateInput(attrs={'type': 'date'}),
            'hora_solicitud': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            'id_solicitud': forms.Select(attrs={'class': 'form-select'}),  # Widget para el campo ForeignKey
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Añadir clases CSS a los campos
        for field_name, field in self.fields.items():
            if isinstance(field, forms.ChoiceField):
                if field.choices and field.choices[0][0] == "":
                    field.widget.attrs.update({'class': 'disable-first-option'})
                elif isinstance(field, forms.ModelChoiceField):
                    field.widget.attrs.update({'class': 'form-select'})
            elif isinstance(field, forms.CharField):
                field.widget.attrs.update({'class': 'form-control'})

        self.editing = kwargs.pop('editing', False)
        super().__init__(*args, **kwargs)
        
        if self.editing:
            # Personalizaciones específicas para edición
            self.fields['id_solicitud'].disabled = True
            self.fields['fecha_solicitud'].disabled = True

    def clean(self):
        cleaned_data = super().clean()
        metodo_pago = cleaned_data.get('metodo_pago')
        referencia = cleaned_data.get('referencia')
        
        if metodo_pago in ['Transferencia', 'Deposito'] and not referencia:
            self.add_error('referencia', 'Este campo es requerido para Transferencia/Deposito')
        elif metodo_pago not in ['Transferencia', 'Deposito']:
            cleaned_data['referencia'] = 'No Hay Referencia'
            
        return cleaned_data

class RequisitosForm(forms.ModelForm):
    class Meta:
        model = Requisitos
        fields = '__all__'
        exclude = ['id_solicitud']
        widgets = {
            'cedula_vencimiento': forms.DateInput(attrs={'type': 'date'}),
            'rif_representante_vencimiento': forms.DateInput(attrs={'type': 'date'}),
            'rif_comercio_vencimiento': forms.DateInput(attrs={'type': 'date'}),
            'documento_propiedad_vencimiento': forms.DateInput(attrs={'type': 'date'}),
            'cedula_catastral_vencimiento': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Configurar los campos booleanos
        for field_name, field in self.fields.items():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs.update({'class': 'form-check-input'})
