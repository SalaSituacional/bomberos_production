from django import forms
from .models import *
from web.forms import Asignar_ops_Personal

class BienMunicipalForm(forms.Form):
    identificador = forms.CharField(max_length=20)
    descripcion = forms.CharField(widget=forms.Textarea)
    cantidad = forms.IntegerField(min_value=0)
    dependencia = forms.ModelChoiceField(queryset=Dependencia.objects.all())
    departamento = forms.CharField(max_length=100)
    responsable = forms.ChoiceField(choices=Asignar_ops_Personal(), label="Responsable", widget=forms.Select(attrs={"class": "disable-first-option"}))
    fecha_registro = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    estado_actual = forms.ChoiceField(choices=EstadoBien.choices)


class MovimientoBienForm(forms.Form):
    bien = forms.CharField()
    nueva_dependencia = forms.ModelChoiceField(queryset=Dependencia.objects.all())
    nuevo_departamento = forms.CharField(max_length=100)
    ordenado_por = forms.ChoiceField(choices=Asignar_ops_Personal(), label="Ordenado Por", widget=forms.Select(attrs={"class": "disable-first-option"}))
    fecha_orden = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

class CambiarEstadoBienForm(forms.Form):
    bien_cambiar_estado = forms.CharField()
    estado_actual = forms.CharField(max_length=100)
    nuevo_estado = forms.ChoiceField(choices=EstadoBien.choices)
    fecha_orden = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
