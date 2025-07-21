from django import forms
from.models import *
import logging
logger = logging.getLogger(__name__)
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
        queryset=Comercio.objects.none(),  # Se sobrescribirá en __init__
        required=True,
        label="Comercio",
        error_messages={
            'invalid_choice': 'Por favor seleccione un comercio válido de la lista'
        }
    )

    referencia = forms.CharField(required=False) # Deja required=False aquí.

    # Estos campos son declarados como ChoiceField en lugar de usar los del modelo
    # Asegúrate de que tus modelos no los definan como CharField con choices.
    # Si lo hacen, puedes quitarlos de aquí y Django los manejará.
    # Si tus modelos usan IntegerChoices o TextChoices, estos campos deberían ser simples CharFields
    # en el formulario y sus choices se obtendrían de los modelos.
    tipo_servicio = forms.ChoiceField(choices=TIPO_SERVICIO_CHOICES, required=True) # Generalmente son requeridos
    tipo_representante = forms.ChoiceField(choices=TIPO_REPRESENTANTE_CHOICES, required=True) # Generalmente son requeridos
    metodo_pago = forms.ChoiceField(choices=METODO_PAGO_CHOICES, required=True) # Generalmente son requeridos

    class Meta:
        model = Solicitudes
        fields = '__all__'
        widgets = {
            'fecha_solicitud': forms.DateInput(attrs={'type': 'date'}),
            'hora_solicitud': forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
            'id_solicitud': forms.Select(attrs={'class': 'form-select'}),
            # Elimina 'required': False aquí si ya lo definiste en el campo de arriba
            # y si quieres que se aplique la lógica del clean method.
            # 'referencia': forms.TextInput(attrs={"required": False}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        editing = kwargs.pop('editing', False)

        super().__init__(*args, **kwargs)

        # Añadir clases CSS a los campos
        for field_name, field in self.fields.items():
            if isinstance(field, forms.ChoiceField) or isinstance(field, forms.ModelChoiceField):
                # Aplicar form-select a todos los ChoiceField y ModelChoiceField
                field.widget.attrs.update({'class': 'form-select'})
                # Si el primer valor es vacío, añadir 'disable-first-option'
                if field.choices and field.choices[0][0] == "":
                    field.widget.attrs.update({'class': field.widget.attrs.get('class', '') + ' disable-first-option'})
            elif isinstance(field, (forms.CharField, forms.DateField, forms.TimeField, forms.DecimalField, forms.IntegerField)):
                field.widget.attrs.update({'class': 'form-control'})
            elif isinstance(field, forms.BooleanField):
                field.widget.attrs.update({'class': 'form-check-input'})


        # Si estamos editando, y el campo id_solicitud existe, lo hacemos no requerido
        # y opcionalmente deshabilitamos el widget si quisieras (aunque el HTML ya lo hace readonly)
        if editing and 'id_solicitud' in self.fields:
            self.fields['id_solicitud'].required = False
            # self.fields['id_solicitud'].widget.attrs['disabled'] = 'disabled' # CUIDADO: esto hace que no se envíe el valor en POST

        # Filtrar el campo id_solicitud (Comercio) basado en el usuario
        if self.user and 'id_solicitud' in self.fields:
            user_jerarquia_departments = {
                'ComandanciaJunin': 'Junin',
                'Prevencion05': 'San Cristobal',
            }
            department = user_jerarquia_departments.get(self.user.get('user'))

            if department:
                self.fields['id_solicitud'].queryset = Comercio.objects.filter(
                    departamento=department
                ).order_by("id_comercio")
                logger.debug(f"Filtrado comercios por departamento: {department}")
            else:
                self.fields['id_solicitud'].queryset = Comercio.objects.all().order_by("id_comercio")
                logger.debug("Mostrando todos los comercios (usuario sin departamento asignado)")

        # Si el formulario está inicializado con una instancia (modo edición),
        # y tiene un valor para id_solicitud, asegúrate de que esa opción esté disponible
        if editing and self.instance.pk and self.instance.id_solicitud and 'id_solicitud' in self.fields:
            current_comercio = self.instance.id_solicitud
            # Si el comercio actual no está en el queryset filtrado, añádelo temporalmente
            if current_comercio not in self.fields['id_solicitud'].queryset:
                self.fields['id_solicitud'].queryset |= Comercio.objects.filter(pk=current_comercio.pk)


    def clean(self):
        cleaned_data = super().clean()
        metodo_pago = cleaned_data.get('metodo_pago')
        referencia = cleaned_data.get('referencia')

        # Lógica para hacer 'referencia' requerido condicionalmente
        if metodo_pago in ['Transferencia', 'Deposito'] and not referencia:
            self.add_error('referencia', 'Este campo es requerido para Transferencia/Deposito.')
        elif metodo_pago not in ['Transferencia', 'Deposito']:
            # Si no requiere referencia, asegúrate de que se guarde un valor por defecto
            # Esto es importante para el modelo si el campo es NOT NULL
            cleaned_data['referencia'] = 'No Hay Referencia' # O None, si el campo permite nulos

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
        for field_name, field in self.fields.items():
            if isinstance(field, forms.BooleanField):
                field.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(field, (forms.CharField, forms.DateField, forms.TimeField, forms.DecimalField, forms.IntegerField)):
                 field.widget.attrs.update({'class': 'form-control'})
