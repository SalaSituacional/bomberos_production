from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from .models import *

# Formulario para crear un nuevo lote de insumos en el inventario principal
class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = ['insumo', 'cantidad', 'fecha_vencimiento']
        widgets = {
            'fecha_vencimiento': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicializa FormHelper para controlar la apariencia del formulario
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'insumo',
            'cantidad',
            'fecha_vencimiento',
            Submit('submit', 'Guardar Lote')
        )
        
# Asignacion de inventarios o isumos principal --> subinventarios

class AsignarInsumoForm(forms.Form):
    # Usaremos un queryset vacío que se filtrará en la vista
    lote = forms.ModelChoiceField(
        queryset=Lote.objects.all(),
        label="Seleccionar Lote a Asignar",
        help_text="Seleccione un lote del inventario principal."
    )
    cantidad = forms.IntegerField(
        min_value=1,
        label="Cantidad a Asignar"
    )
    # Excluimos el inventario principal para evitar asignaciones a sí mismo
    inventario_destino = forms.ModelChoiceField(
        queryset=Inventario.objects.exclude(is_principal=True),
        label="Inventario de Destino"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra el queryset de 'lote' para mostrar solo los lotes del inventario principal
        try:
            inventario_principal = Inventario.objects.get(is_principal=True)
            self.fields['lote'].queryset = Lote.objects.filter(inventario=inventario_principal).order_by('fecha_vencimiento')
        except Inventario.DoesNotExist:
            pass
            
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            'lote',
            'cantidad',
            'inventario_destino',
            Submit('submit', 'Asignar Insumos', css_class='btn btn-primary mt-3')
        )


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
