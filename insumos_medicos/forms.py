from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from .models import *

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