from django import forms
from.models import *
from web.forms import Asignar_op_Municipios

def Asignar_Comercios():
   procedimientos = Comercio.objects.all()
   op = [("", "Seleccione Una Opcion")]
   for procedimiento in procedimientos:
       op.append((str(procedimiento.id_comercio), f"{procedimiento.id_comercio}: {procedimiento.nombre_comercio}"))
   return op

class Comercios(forms.Form):
    nombre_comercio = forms.CharField(required=False)
    rif_empresarial = forms.CharField(required=False)

class Formulario_Solicitud(forms.Form):
    opc = [("", "Seleccione una Opcion"),
        ("1", "La Concordia"),
        ("2", "Pedro Maria Morantes"),
        ("3", "San Juan Bautista"),
        ("4", "San Sebastian"),
        ("6", "Francisco Romero Lobo"),
    ]

    comercio = forms.ChoiceField(choices=Asignar_Comercios,required=False,widget=forms.Select(attrs={'class': 'disable-first-option'}))

    fecha_solicitud = forms.DateField(
        label="Fecha Solicitud",
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    hora_solicitud = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}, format='%H:%M'),
        required=False)  #

    tipo_servicio = forms.ChoiceField(choices=(("", "Selecione Una Opcion"), ("Inspeccion", "Inspeccion"), ("Reinspeccion", "Reinspeccion")), required=False, widget=forms.Select(attrs={'class': 'disable-first-option'}))

    solicitante_nombre_apellido = forms.CharField(label="Nombres Y Apellidos del Solicitante",required=False)

    tipo_representante = forms.ChoiceField(choices=(("", "Selecione Una Opcion"), ("Presidente", "Presidente"), ("Propietario", "Propietario"), ("Representante Legal", "Representante Legal"), ("Encargado", "Encargado")), required=False, widget=forms.Select(attrs={'class': 'disable-first-option'}))

    direccion = forms.CharField(required=False)

    estado = forms.CharField(required=False)

    municipio = forms.ChoiceField(choices=Asignar_op_Municipios, required=False,
        widget=forms.Select(attrs={'class': 'disable-first-option'}))

    parroquia = forms.ChoiceField(choices=opc, required=False,
        widget=forms.Select(attrs={'class': 'disable-first-option'}))
    
    numero_telefono = forms.CharField(required=False)
    correo_electronico = forms.EmailField(required=False)
    pago_tasa = forms.CharField(required=False)
    metodo_pago = forms.ChoiceField(choices=(("", "Seleccione Una Opcion"), ("Efectivo", "Efectivo"), ("Transferencia", "Transferencia"), ("Deposito", "Deposito"), ("Otra Moneda", "Otra Moneda")),required=False)
    referencia = forms.CharField(required=False)

class Formularia_Requisitos(forms.Form):
    cedula_identidad = forms.BooleanField(required=False,label="Cedula de Identidad")
    solicitante_cedula = forms.CharField(label="Cedula Solicitante",required=False)
    cedula_vecimiento = forms.DateField(
        label="Fecha Vencimiento",
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    rif_representante = forms.BooleanField(required=False,label="RIF Representante")
    rif_representante_legal = forms.CharField(required=False)
    rif_representante_vencimiento = forms.DateField(
        label="Fecha Vencimiento",
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    rif_comercio = forms.BooleanField(required=False,label="RIF Comercio")
    rif_comercio_vencimiento = forms.DateField(
        label="Fecha Vencimiento",
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    cedula_catastral = forms.BooleanField(required=False,label="Cedula Catastral")
    cedula_catastral_vencimiento = forms.DateField(
        label="Fecha Vencimiento",
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )

    documento_propiedad = forms.BooleanField(required=False,label="Documento de Propiedad/Carta de Arrendamiento")
    documento_propiedad_vencimiento = forms.DateField(
        label="Fecha Vencimiento",
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=False
    )
    
    permiso_anterior = forms.BooleanField(required=False,label="Permiso Anterior (En Caso de Renovacion)")
    carta_autorizacion = forms.BooleanField(required=False,label="Carta Autorizacion")
    plano_bomberil = forms.BooleanField(required=False,label="Plano de Uso Bomberil")
    registro_comercio = forms.BooleanField(required=False,label="Registro Comercio")
