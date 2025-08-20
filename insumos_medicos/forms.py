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