from django import forms
from.models import *
from django.db.models import Q
from django.db.models import Case, When, Value, IntegerField
from django.forms import inlineformset_factory
from django.forms import BaseInlineFormSet
from django.utils.safestring import mark_safe
from web.models import Divisiones


def Asignar_Servicios():
   procedimientos = Servicios.objects.all()
   op = [("", "Seleccione Una Opcion")]
   for procedimiento in procedimientos:
       op.append((str(procedimiento.id), f"{procedimiento.nombre_servicio}"))
   return op

# ============================================

class LicenciaConductorForm(forms.ModelForm):
    class Meta:
        model = LicenciaConductor
        fields = ['tipo_licencia', 'numero_licencia', 'fecha_emision', 
                 'fecha_vencimiento', 'organismo_emisor', 'restricciones', 
                 'observaciones']
        widgets = {
            'tipo_licencia': forms.Select(attrs={
                'class': 'form-select'
            }),
            'numero_licencia': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'fecha_emision': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'organismo_emisor': forms.TextInput(attrs={'class': 'form-control'}),
            'restricciones': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }


class CertificadoMedicoForm(forms.ModelForm):
    class Meta:
        model = CertificadoMedico
        fields = ['fecha_emision', 'fecha_vencimiento', 'centro_medico', 
                'medico', 'observaciones']
        widgets = {
            'centro_medico': forms.TextInput(attrs={'class': 'form-control'}),
            'medico': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_emision': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observaciones': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

class ConductorForm(forms.ModelForm):
    class Meta:
        model = Conductor
        fields = ['personal', 'fecha_vencimiento', 'observaciones_generales']
        widgets = {
            'personal': forms.Select(attrs={
                'class': 'form-select'
            }),
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'observaciones_generales': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        jerarquias = [ "General", "Coronel", "Teniente Coronel", "Mayor", "Capitán", "Primer Teniente", "Teniente", "Sargento Mayor", "Sargento Primero", "Sargento segundo", "Cabo Primero", "Cabo Segundo", "Distinguido", "Bombero" ] 
        
        # Filtramos el personal y personalizamos cómo se muestra
        self.fields['personal'].queryset = Personal.objects.exclude(id__in=[0, 4]).filter(status="Activo").filter(rol="Bombero").order_by( Case(*[When(jerarquia=nombre, then=pos) for pos, nombre in enumerate(jerarquias)]) )
        
        # Personalizar cómo se muestran las opciones en el select
        self.fields['personal'].label_from_instance = lambda obj: f"{obj.nombres} {obj.apellidos} {obj.cedula} ({obj.jerarquia})"

class LicenciaConductorFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        for form in self.forms:
            if not form.has_changed() and form.instance.pk:
                continue  # Saltar validación para no modificados
            
            if form.cleaned_data.get('DELETE'):
                continue  # No validar los que se eliminarán
            
            # Solo validar para nuevas licencias o modificadas
            if not form.instance.pk or form.has_changed():
                numero_licencia = form.cleaned_data.get('numero_licencia')
                tipo_licencia = form.cleaned_data.get('tipo_licencia')
                
                if numero_licencia and tipo_licencia:
                    qs = LicenciaConductor.objects.filter(
                        numero_licencia=numero_licencia,
                        tipo_licencia=tipo_licencia
                    )
                    if form.instance.pk:
                        qs = qs.exclude(pk=form.instance.pk)
                    if qs.exists():
                        form.add_error(None, 'Esta combinación de número y tipo de licencia ya existe')

# Actualiza tu LicenciaFormSet
LicenciaFormSet = inlineformset_factory(
    Conductor,
    LicenciaConductor,
    form=LicenciaConductorForm,
    formset=LicenciaConductorFormSet,
    extra=1,
    can_delete=True
)

CertificadoMedicoFormSet = inlineformset_factory(
    Conductor, 
    CertificadoMedico,
    form=CertificadoMedicoForm,
    extra=1,  # Solo un formulario extra vacío
    max_num=1,  # Máximo un certificado
    can_delete=True,
    validate_max=True  # Validar que no se exceda el máximo
)


# =======================================================================================

class Unidades_Informacion(forms.Form):
    op = [
        ("", "Seleccione una Opción"),
        ("1", "Rescate"),
        ("2", "Operaciones"),
        ("3", "Prevención"),
        ("4", "GRUMAE"),
        ("5", "Prehospitalaria"),
        ("6", "Enfermería"),
        ("7", "Servicios Médicos"),
        ("8", "Psicología"),
        ("9", "Capacitación"),
    ]
    
    nombre_unidad = forms.CharField()
    division = forms.ChoiceField(label="Seleccionar División", choices=op, required=True, widget=forms.Select(attrs={"class": "disable-first-option"}))
    tipo_vehiculo = forms.ChoiceField(label="Tipo de Vehiculo", choices=[("", "Seleccione una Opción"), ("Moto", "Moto"), ("Camion", "Camion"), ("Carro", "Carro")], required=True, widget=forms.Select(attrs={"class": "disable-first-option"}))
    serial_carroceria = forms.CharField()
    serial_chasis = forms.CharField()
    marca = forms.CharField()
    año = forms.CharField()
    modelo = forms.CharField()
    placas = forms.CharField()
    tipo_filtro_aceite = forms.CharField()
    tipo_filtro_combustible = forms.CharField()
    bateria = forms.CharField()
    numero_tag = forms.CharField()
    tipo_bujia = forms.CharField()
    uso = forms.CharField()
    capacidad_carga = forms.CharField()
    numero_ejes = forms.CharField()
    numero_puestos = forms.CharField()
    tipo_combustible = forms.ChoiceField(label="Tipo de Combustible", choices=[
        ("", "Seleccione una Opción"),
        ("Gasoil", "Gasoil"),
        ("Gasolina", "Gasolina"),
    ], required=True, widget=forms.Select(attrs={"class": "disable-first-option"}))
    tipo_aceite = forms.CharField()
    medida_neumaticos = forms.CharField()
    tipo_correa = forms.CharField()
    estado = forms.ChoiceField(label="Estado", choices=[
        ("", "Seleccione una Opción"),
        ("🔴 Fuera de Servicio", "Fuera de Servicio"),
        ("🟢 Activo", "Activo"),
        ("🟡 Mantenimiento", "Mantenimiento"),
    ], required=True, widget=forms.Select(attrs={"class": "disable-first-option"}))

class Reportes(forms.Form):
    
    
    id_unidad = forms.CharField(label="Unidad")
    servicio = forms.ChoiceField(label="Seleccionar Tipo de Servicio", choices=Asignar_Servicios(), required=True, widget=forms.Select(attrs={"class": "disable-first-option"}))
    fecha =  forms.DateField(
        label="Fecha",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    hora = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'))  # Especificar explícitamente el tipo de input

    responsable = forms.CharField()
    descripcion = forms.CharField()

class Cambiar_Estado(forms.Form):
    op = [
        ("", "Seleccione una Opción"),
        ("🔴 Fuera de Servicio", "Fuera de Servicio"),
        ("🟢 Activo", "Activo"),
        ("🟡 Mantenimiento", "Mantenimiento"),
    ]
    id_unidad_status = forms.CharField(
        max_length=100,
        label='Unidad',
    )
    actual = forms.CharField(
        max_length=100,
        label='Actual',
    )
    nuevo = forms.ChoiceField(label="Seleccionar Estado del Vehiculo", choices=op, required=True, widget=forms.Select(attrs={"class": "disable-first-option"}))

class Cambiar_Division(forms.Form):
    op = [
        ("", "Seleccione una Opción"),
        ("1", "Rescate"),
        ("2", "Operaciones"),
        ("3", "Prevención"),
        ("4", "GRUMAE"),
        ("5", "Prehospitalaria"),
        ("6", "Enfermería"),
        ("7", "Servicios Médicos"),
        ("8", "Psicología"),
        ("9", "Capacitación"),
    ]
    
    id_unidad_division = forms.CharField(
        max_length=100,
        label='Unidad',
    )
    actual_division = forms.CharField(
        max_length=100,
        label='Actual',
    )
    nuevo = forms.ModelMultipleChoiceField(
        queryset=Divisiones.objects.all(), 
        widget=forms.CheckboxSelectMultiple  # O SelectMultiple para un dropdown
    )

# =============================================================================== Formularios Para el Area de Inventarios Unidades ===============================================

class HerramientaForm(forms.ModelForm):
     class Meta:
        model = Herramienta
        fields = '__all__'
        widgets = {
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'fecha_adquisicion': forms.DateInput(attrs={'type': 'date'}),
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'activo': 'Activo?',  # Cambia el texto del label
        }

class AsignacionForm(forms.ModelForm):
    class Meta:
        model = AsignacionHerramienta
        fields = '__all__'
        widgets = {
            'fecha_asignacion': forms.DateInput(attrs={'type': 'date'}),
            'fecha_devolucion': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        herramienta = cleaned_data.get('herramienta')
        fecha_devolucion = cleaned_data.get('fecha_devolucion')
        
        if not fecha_devolucion:
            if herramienta and herramienta.cantidad_disponible <= 0:
                raise ValidationError(f"No hay unidades disponibles de {herramienta}. Cantidad total: {herramienta.cantidad_total}, Asignadas: {herramienta.cantidad_total - herramienta.cantidad_disponible}")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar herramientas disponibles
        if 'herramienta' in self.fields:
            self.fields['herramienta'].queryset = self.fields['herramienta'].queryset.filter(
                activo=True,
                cantidad_total__gt=0
            )
            
        if 'responsable' in self.fields:
            jerarquias = [ "General", "Coronel", "Teniente Coronel", "Mayor", "Capitán", "Primer Teniente", "Teniente", "Sargento Mayor", "Sargento Primero", "Sargento segundo", "Cabo Primero", "Cabo Segundo", "Distinguido", "Bombero" ] 

            # Excluir ciertos IDs primero
            self.fields['responsable'].queryset = self.fields['responsable'].queryset.exclude(id__in=[0, 4]).filter(status="Activo").filter(rol="Bombero").order_by( Case(*[When(jerarquia=nombre, then=pos) for pos, nombre in enumerate(jerarquias)]) )
            # Luego personalizar la visualización
            self.fields['responsable'].label_from_instance = lambda obj: f"{obj.jerarquia} {obj.nombres} {obj.apellidos}"

        if 'unidad' in self.fields:
            # Excluir ciertos IDs primero
            self.fields['unidad'].queryset = self.fields['unidad'].queryset.exclude(id__in=[26, 30, 27]).order_by("id")

class DevolucionHerramientaForm(forms.ModelForm):
    class Meta:
        model = AsignacionHerramienta
        fields = ['fecha_devolucion', 'observaciones']
        widgets = {
            'fecha_devolucion': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }

class InventarioForm(forms.ModelForm):
    class Meta:
        model = InventarioUnidad
        fields = '__all__'
        widgets = {
            'fecha_revision': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'realizado_por' in self.fields:
            jerarquias = [ "General", "Coronel", "Teniente Coronel", "Mayor", "Capitán", "Primer Teniente", "Teniente", "Sargento Mayor", "Sargento Primero", "Sargento segundo", "Cabo Primero", "Cabo Segundo", "Distinguido", "Bombero" ] 

            # Excluir ciertos IDs primero
            self.fields['realizado_por'].queryset = self.fields['realizado_por'].queryset.exclude(id__in=[0, 4]).filter(status="Activo").filter(rol="Bombero").order_by( Case(*[When(jerarquia=nombre, then=pos) for pos, nombre in enumerate(jerarquias)]) )
            # Luego personalizar la visualización
            self.fields['realizado_por'].label_from_instance = lambda obj: f"{obj.jerarquia} {obj.nombres} {obj.apellidos}"

        if 'unidad' in self.fields:
            # Excluir ciertos IDs primero
            self.fields['unidad'].queryset = self.fields['unidad'].queryset.exclude(id__in=[26, 30, 27]).order_by("id")

class DetalleInventarioForm(forms.ModelForm):
    class Meta:
        model = DetalleInventario
        fields = '__all__'
        widgets = {
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar herramientas disponibles
        if 'herramienta' in self.fields:
            self.fields['herramienta'].queryset = self.fields['herramienta'].queryset.filter(
                activo=True,
                cantidad_total__gt=0
            )
            
        if 'responsable' in self.fields:
            jerarquias = [ "General", "Coronel", "Teniente Coronel", "Mayor", "Capitán", "Primer Teniente", "Teniente", "Sargento Mayor", "Sargento Primero", "Sargento segundo", "Cabo Primero", "Cabo Segundo", "Distinguido", "Bombero" ] 

            # Excluir ciertos IDs primero
            self.fields['responsable'].queryset = self.fields['responsable'].queryset.exclude(id__in=[0, 4]).filter(status="Activo").filter(rol="Bombero").order_by( Case(*[When(jerarquia=nombre, then=pos) for pos, nombre in enumerate(jerarquias)]) )
            # Luego personalizar la visualización
            self.fields['responsable'].label_from_instance = lambda obj: f"{obj.jerarquia} {obj.nombres} {obj.apellidos}"

        if 'unidad' in self.fields:
            # Excluir ciertos IDs primero
            self.fields['unidad'].queryset = self.fields['unidad'].queryset.exclude(id__in=[26, 30, 27]).order_by("id")

            