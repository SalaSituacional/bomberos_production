from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from .models import *

# Asignacion de inventarios o isumos principal --> subinventarios
class RegistroConsumoForm(forms.Form):
    # Campo oculto para el inventario_origen
    inventario_origen = forms.CharField(widget=forms.HiddenInput(), required=False)
    
    insumo = forms.ModelChoiceField(
        queryset=Insumo.objects.none(),
        label="Selecciona el Insumo",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    lote = forms.ModelChoiceField(
        queryset=Lote.objects.none(),
        label="Selecciona el Lote",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cantidad = forms.IntegerField(
        min_value=1,
        label="Cantidad a consumir",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Cantidad'})
    )
    descripcion = forms.CharField(
        required=False,
        label="Motivo del consumo",
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    def __init__(self, *args, **kwargs):
        # Extrae inventario_id de los kwargs si se envía desde la vista
        inventario_id_from_view = kwargs.pop('inventario_id', None)
        super().__init__(*args, **kwargs)

        # Si se recibe un inventario_id desde la vista, lo usa para inicializar
        # el campo insumo y el campo oculto. Este es el queryset inicial para GET.
        if inventario_id_from_view:
            self.fields['insumo'].queryset = Insumo.objects.filter(
                lotes__inventario__id=inventario_id_from_view
            ).distinct()
            self.fields['inventario_origen'].initial = inventario_id_from_view

        # Si el formulario está ligado a datos (petición POST)
        if self.is_bound and 'insumo' in self.data:
            try:
                # Obtiene el ID del insumo de los datos del POST
                insumo_id = int(self.data.get('insumo'))
                
                # Reconstruye el queryset del lote usando el insumo_id del POST
                # y el inventario_id que la vista le ha pasado a la instancia del formulario
                self.fields['lote'].queryset = Lote.objects.filter(
                    insumo_id=insumo_id, 
                    inventario__id=self.fields['inventario_origen'].initial
                ).order_by('fecha_vencimiento')
            except (ValueError, TypeError):
                self.fields['lote'].queryset = Lote.objects.none()

# registro de insumo (Medicamentos)
class InsumoForm(forms.ModelForm):
    """
    Formulario para registrar un nuevo insumo médico.
    """
    class Meta:
        model = Insumo
        fields = ['nombre', 'tipo', 'presentacion', 'descripcion']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-control'}),
            'presentacion': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    # Puedes agregar validaciones personalizadas si lo necesitas
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Opcional: Filtra el queryset del campo 'tipo' si es necesario
        self.fields['tipo'].queryset = TipoInsumo.objects.all().order_by('nombre')
