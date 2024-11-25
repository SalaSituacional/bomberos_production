from django.shortcuts import render, redirect
from django.http import HttpResponse
from ..forms import *
from ..models import *
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
import json
from datetime import datetime
from django.utils import timezone
from django.db.models import Count
import json
from datetime import datetime
from dateutil.relativedelta import relativedelta
from datetime import timedelta
 
# Api para crear seccion de lista de procedimientos por cada division, por tipo y parroquia en la seccion de Estadistica
def generar_resultados(request):
    try:
        month = request.GET.get("month")
    
        # Filtrar procedimientos del año actual si no se especifica mes
        if month:
            year, month = map(int, month.split("-"))
            procedimientos = Procedimientos.objects.filter(fecha__year=year, fecha__month=month)
        else:
            current_year = datetime.now().year
            procedimientos = Procedimientos.objects.filter(fecha__year=current_year)

        # Diccionario para almacenar los resultados por división
        resultados_divisiones = {}

        # Definir los nombres de las divisiones
        nombres_divisiones = {
            1: 'Rescate',
            2: 'Operaciones',
            3: 'Prevención',
            4: 'Grumae',
            5: 'Prehospitalaria',
            6: 'Enfermería',
            7: 'ServiciosMédicos',
            8: 'Psicología',
            9: 'Capacitación'
        }

        for division_id, division_nombre in nombres_divisiones.items():
            # Filtrar procedimientos por división
            division_procedimientos = procedimientos.filter(id_division=division_id)

            # Agrupar y contar procedimientos por tipo y parroquia
            tipos_procedimientos_parroquias = (
                division_procedimientos
                .values('id_tipo_procedimiento__tipo_procedimiento', 'id_parroquia__parroquia')
                .annotate(cantidad=Count('id'))
                .order_by('id_tipo_procedimiento__tipo_procedimiento', 'id_parroquia__parroquia')
            )

            # Estructura de resultados por división, tipo de procedimiento y parroquia
            resultados_divisiones[division_nombre] = {
                'total_por_tipo': {},  # Añadir un diccionario para los totales por tipo
                'detalles': {}  # Añadir un diccionario para los detalles
            }

            for item in tipos_procedimientos_parroquias:
                tipo_procedimiento = item['id_tipo_procedimiento__tipo_procedimiento']
                parroquia = item['id_parroquia__parroquia']
                cantidad = item['cantidad']

                # Añadir al diccionario de detalles
                if tipo_procedimiento not in resultados_divisiones[division_nombre]['detalles']:
                    resultados_divisiones[division_nombre]['detalles'][tipo_procedimiento] = {}

                resultados_divisiones[division_nombre]['detalles'][tipo_procedimiento][parroquia] = cantidad

                # Sumar al total por tipo
                if tipo_procedimiento not in resultados_divisiones[division_nombre]['total_por_tipo']:
                    resultados_divisiones[division_nombre]['total_por_tipo'][tipo_procedimiento] = 0

                resultados_divisiones[division_nombre]['total_por_tipo'][tipo_procedimiento] += cantidad

        # Convertir a JSON y devolver como respuesta
        return JsonResponse(resultados_divisiones, json_dumps_params={'ensure_ascii': False, 'indent': 4})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# Api para crear seccion de grafica anual de meses en el dashboard
def filtrado_mes(mes):
    año_actual = datetime.now().year

    # Filtrado de datos por mes para la grafica anual
    procedimientos_mes = Procedimientos.objects.filter(
    fecha__month=mes,  # Septiembre
    fecha__year=año_actual  # Año 2023
    )
    return procedimientos_mes.count()

def obtener_meses(request):
    enero = filtrado_mes(1)
    febrero = filtrado_mes(2)
    marzo = filtrado_mes(3)
    abril = filtrado_mes(4)
    mayo = filtrado_mes(5)
    junio = filtrado_mes(6)
    julio = filtrado_mes(7)
    agosto = filtrado_mes(8)
    septiembre = filtrado_mes(9)
    octubre = filtrado_mes(10)
    noviembre = filtrado_mes(11)
    diciembre = filtrado_mes(12)

    data = {
        "enero": enero,
        "febrero": febrero,
        "marzo": marzo,
        "abril": abril,
        "mayo": mayo,
        "junio": junio,
        "julio": julio,
        "agosto": agosto,
        "septiembre": septiembre,
        "octubre": octubre,
        "noviembre": noviembre,
        "diciembre": diciembre,
    }
    return JsonResponse(data)

# Api para obtener porcentajes para las cards de la seccion del dashboard
def obtener_porcentajes(request, periodo="general"):
    if periodo == "mes":
        now = timezone.now()
        start_of_month = now.replace(day=1)
        procedimientos_queryset = Procedimientos.objects.filter(fecha__gte=start_of_month)
    else:
        procedimientos_queryset = Procedimientos.objects.all()

    # Contar procedimientos por división
    divisiones = {
        'rescate': procedimientos_queryset.filter(id_division=1).count(),
        'operaciones': procedimientos_queryset.filter(id_division=2).count(),
        'prevencion': procedimientos_queryset.filter(id_division=3).count(),
        'grumae': procedimientos_queryset.filter(id_division=4).count(),
        'prehospitalaria': procedimientos_queryset.filter(id_division=5).count(),
        'enfermeria': procedimientos_queryset.filter(id_division=6).count(),
        'servicios_medicos': procedimientos_queryset.filter(id_division=7).count(),
        'psicologia': procedimientos_queryset.filter(id_division=8).count(),
        'capacitacion': procedimientos_queryset.filter(id_division=9).count(),
    }

    # Total de procedimientos
    procedimientos_totales = sum(divisiones.values())


    # Inicializar porcentajes
    porcentajes = {key: 0.0 for key in divisiones.keys()}

    # Calcular y ajustar los porcentajes
    if procedimientos_totales > 0:
        total_ajustado = 0.0

        for key, count in divisiones.items():
            porcentaje = (count / procedimientos_totales) * 100
            porcentaje_redondeado = round(porcentaje, 1)
            porcentajes[key] = porcentaje_redondeado
            total_ajustado += porcentaje_redondeado

        # Calcular el ajuste necesario
        ajuste = 100 - total_ajustado


        if ajuste != 0:
            # Ajustar el último porcentaje
            last_key = list(porcentajes.keys())[-1]
            porcentajes[last_key] += ajuste

            # Asegurarse de que el último porcentaje no exceda 100
            if porcentajes[last_key] > 100:
                porcentajes[last_key] = 100

    return JsonResponse(porcentajes)

# Api para obtener los valores de las cards por parroquias de la seccion del Dashboard
def obtener_procedimientos_parroquias(request):

    username = request.headers.get("X-User-Name")
    
    # Obtener la fecha de hoy y el primer día del mes
    hoy = datetime.now().date()
    primer_dia_mes = hoy.replace(day=1)

    if username == "Sala_Situacional" or username == "Comandancia" or username == "2dacomandancia" or username == "SeRvEr":

        procedimientos = {
            "otros_municipios": {
                "total": Procedimientos.objects.filter(id_parroquia=0).count(),
                "del_mes": Procedimientos.objects.filter(id_parroquia=0, fecha__gte=primer_dia_mes).count(),
                "hoy": Procedimientos.objects.filter(id_parroquia=0, fecha=hoy).count(),
            },
            "concordia": {
                "total": Procedimientos.objects.filter(id_parroquia=1).count(),
                "del_mes": Procedimientos.objects.filter(id_parroquia=1, fecha__gte=primer_dia_mes).count(),
                "hoy": Procedimientos.objects.filter(id_parroquia=1, fecha=hoy).count(),
            },
            "pedro_m": {
                "total": Procedimientos.objects.filter(id_parroquia=2).count(),
                "del_mes": Procedimientos.objects.filter(id_parroquia=2, fecha__gte=primer_dia_mes).count(),
                "hoy": Procedimientos.objects.filter(id_parroquia=2, fecha=hoy).count(),
            },
            "san_juan": {
                "total": Procedimientos.objects.filter(id_parroquia=3).count(),
                "del_mes": Procedimientos.objects.filter(id_parroquia=3, fecha__gte=primer_dia_mes).count(),
                "hoy": Procedimientos.objects.filter(id_parroquia=3, fecha=hoy).count(),
            },
            "san_sebastian": {
                "total": Procedimientos.objects.filter(id_parroquia=4).count(),
                "del_mes": Procedimientos.objects.filter(id_parroquia=4, fecha__gte=primer_dia_mes).count(),
                "hoy": Procedimientos.objects.filter(id_parroquia=4, fecha=hoy).count(),
            },
            "francisco_romero_lobo": {
                "total": Procedimientos.objects.filter(id_parroquia=6).count(),
                "del_mes": Procedimientos.objects.filter(id_parroquia=6, fecha__gte=primer_dia_mes).count(),
                "hoy": Procedimientos.objects.filter(id_parroquia=6, fecha=hoy).count(),
            },
        }
    
    if username == "Operaciones01":
        procedimientos = {
            "otros_municipios": {
                "hoy": Procedimientos.objects.filter(id_parroquia=0, fecha=hoy, id_division=2).count(),
            },
            "concordia": {
                "hoy": Procedimientos.objects.filter(id_parroquia=1, fecha=hoy, id_division=2).count(),
            },
            "pedro_m": {
                "hoy": Procedimientos.objects.filter(id_parroquia=2, fecha=hoy, id_division=2).count(),
            },
            "san_juan": {
                "hoy": Procedimientos.objects.filter(id_parroquia=3, fecha=hoy, id_division=2).count(),
            },
            "san_sebastian": {
                "hoy": Procedimientos.objects.filter(id_parroquia=4, fecha=hoy, id_division=2).count(),
            },
            "francisco_romero_lobo": {
                "hoy": Procedimientos.objects.filter(id_parroquia=6, fecha=hoy, id_division=2).count(),
            },
        }
    
    if username == "Grumae02":
        procedimientos = {
            "otros_municipios": {
                "hoy": Procedimientos.objects.filter(id_parroquia=0, fecha=hoy, id_division=4).count(),
            },
            "concordia": {
                "hoy": Procedimientos.objects.filter(id_parroquia=1, fecha=hoy, id_division=4).count(),
            },
            "pedro_m": {
                "hoy": Procedimientos.objects.filter(id_parroquia=2, fecha=hoy, id_division=4).count(),
            },
            "san_juan": {
                "hoy": Procedimientos.objects.filter(id_parroquia=3, fecha=hoy, id_division=4).count(),
            },
            "san_sebastian": {
                "hoy": Procedimientos.objects.filter(id_parroquia=4, fecha=hoy, id_division=4).count(),
            },
            "francisco_romero_lobo": {
                "hoy": Procedimientos.objects.filter(id_parroquia=6, fecha=hoy, id_division=4).count(),
            },
        }

    if username == "Rescate03":
        procedimientos = {
            "otros_municipios": {
                "hoy": Procedimientos.objects.filter(id_parroquia=0, fecha=hoy, id_division=1).count(),
            },
            "concordia": {
                "hoy": Procedimientos.objects.filter(id_parroquia=1, fecha=hoy, id_division=1).count(),
            },
            "pedro_m": {
                "hoy": Procedimientos.objects.filter(id_parroquia=2, fecha=hoy, id_division=1).count(),
            },
            "san_juan": {
                "hoy": Procedimientos.objects.filter(id_parroquia=3, fecha=hoy, id_division=1).count(),
            },
            "san_sebastian": {
                "hoy": Procedimientos.objects.filter(id_parroquia=4, fecha=hoy, id_division=1).count(),
            },
            "francisco_romero_lobo": {
                "hoy": Procedimientos.objects.filter(id_parroquia=6, fecha=hoy, id_division=1).count(),
            },
        }

    if username == "Prehospitalaria04":
        procedimientos = {
            "otros_municipios": {
                "hoy": Procedimientos.objects.filter(id_parroquia=0, fecha=hoy, id_division=5).count(),
            },
            "concordia": {
                "hoy": Procedimientos.objects.filter(id_parroquia=1, fecha=hoy, id_division=5).count(),
            },
            "pedro_m": {
                "hoy": Procedimientos.objects.filter(id_parroquia=2, fecha=hoy, id_division=5).count(),
            },
            "san_juan": {
                "hoy": Procedimientos.objects.filter(id_parroquia=3, fecha=hoy, id_division=5).count(),
            },
            "san_sebastian": {
                "hoy": Procedimientos.objects.filter(id_parroquia=4, fecha=hoy, id_division=5).count(),
            },
            "francisco_romero_lobo": {
                "hoy": Procedimientos.objects.filter(id_parroquia=6, fecha=hoy, id_division=5).count(),
            },
        }

    if username == "Prevencion05":
        procedimientos = {
            "otros_municipios": {
                "hoy": Procedimientos.objects.filter(id_parroquia=0, fecha=hoy, id_division=3).count(),
            },
            "concordia": {
                "hoy": Procedimientos.objects.filter(id_parroquia=1, fecha=hoy, id_division=3).count(),
            },
            "pedro_m": {
                "hoy": Procedimientos.objects.filter(id_parroquia=2, fecha=hoy, id_division=3).count(),
            },
            "san_juan": {
                "hoy": Procedimientos.objects.filter(id_parroquia=3, fecha=hoy, id_division=3).count(),
            },
            "san_sebastian": {
                "hoy": Procedimientos.objects.filter(id_parroquia=4, fecha=hoy, id_division=3).count(),
            },
            "francisco_romero_lobo": {
                "hoy": Procedimientos.objects.filter(id_parroquia=6, fecha=hoy, id_division=3).count(),
            },
        }

    if username == "Serviciosmedicos06":
        procedimientos = {
            "otros_municipios": {
                "hoy": Procedimientos.objects.filter(id_parroquia=0, fecha=hoy, id_division=7).count(),
            },
            "concordia": {
                "hoy": Procedimientos.objects.filter(id_parroquia=1, fecha=hoy, id_division=7).count(),
            },
            "pedro_m": {
                "hoy": Procedimientos.objects.filter(id_parroquia=2, fecha=hoy, id_division=7).count(),
            },
            "san_juan": {
                "hoy": Procedimientos.objects.filter(id_parroquia=3, fecha=hoy, id_division=7).count(),
            },
            "san_sebastian": {
                "hoy": Procedimientos.objects.filter(id_parroquia=4, fecha=hoy, id_division=7).count(),
            },
            "francisco_romero_lobo": {
                "hoy": Procedimientos.objects.filter(id_parroquia=6, fecha=hoy, id_division=7).count(),
            },
        }

    if username == "Capacitacion07":
        procedimientos = {
            "otros_municipios": {
                "hoy": Procedimientos.objects.filter(id_parroquia=0, fecha=hoy, id_division=9).count(),
            },
            "concordia": {
                "hoy": Procedimientos.objects.filter(id_parroquia=1, fecha=hoy, id_division=9).count(),
            },
            "pedro_m": {
                "hoy": Procedimientos.objects.filter(id_parroquia=2, fecha=hoy, id_division=9).count(),
            },
            "san_juan": {
                "hoy": Procedimientos.objects.filter(id_parroquia=3, fecha=hoy, id_division=9).count(),
            },
            "san_sebastian": {
                "hoy": Procedimientos.objects.filter(id_parroquia=4, fecha=hoy, id_division=9).count(),
            },
            "francisco_romero_lobo": {
                "hoy": Procedimientos.objects.filter(id_parroquia=6, fecha=hoy, id_division=9).count(),
            },
        }

    if username == "Enfermeria08":
        procedimientos = {
            "otros_municipios": {
                "hoy": Procedimientos.objects.filter(id_parroquia=0, fecha=hoy, id_division=6).count(),
            },
            "concordia": {
                "hoy": Procedimientos.objects.filter(id_parroquia=1, fecha=hoy, id_division=6).count(),
            },
            "pedro_m": {
                "hoy": Procedimientos.objects.filter(id_parroquia=2, fecha=hoy, id_division=6).count(),
            },
            "san_juan": {
                "hoy": Procedimientos.objects.filter(id_parroquia=3, fecha=hoy, id_division=6).count(),
            },
            "san_sebastian": {
                "hoy": Procedimientos.objects.filter(id_parroquia=4, fecha=hoy, id_division=6).count(),
            },
            "francisco_romero_lobo": {
                "hoy": Procedimientos.objects.filter(id_parroquia=6, fecha=hoy, id_division=6).count(),
            },
        }

    if username == "Psicologia09":
        procedimientos = {
            "otros_municipios": {
                "hoy": Procedimientos.objects.filter(id_parroquia=0, fecha=hoy, id_division=8).count(),
            },
            "concordia": {
                "hoy": Procedimientos.objects.filter(id_parroquia=1, fecha=hoy, id_division=8).count(),
            },
            "pedro_m": {
                "hoy": Procedimientos.objects.filter(id_parroquia=2, fecha=hoy, id_division=8).count(),
            },
            "san_juan": {
                "hoy": Procedimientos.objects.filter(id_parroquia=3, fecha=hoy, id_division=8).count(),
            },
            "san_sebastian": {
                "hoy": Procedimientos.objects.filter(id_parroquia=4, fecha=hoy, id_division=8).count(),
            },
            "francisco_romero_lobo": {
                "hoy": Procedimientos.objects.filter(id_parroquia=6, fecha=hoy, id_division=8).count(),
            },
        }

    # print(procedimientos)
    return JsonResponse(procedimientos)

# Api para generar valores para las graficas de pie de la seccion de estadistica
def api_procedimientos_division(request):
    division_id = request.GET.get('param_id')
    mes = request.GET.get('mes')

    # Filtrar por división
    procedimientos = Procedimientos.objects.filter(id_division=division_id)

    # Filtrar por mes si se proporciona
    if mes:
        # Convertir 'mes' a un rango de fechas
        fecha_inicio = datetime.strptime(mes, '%Y-%m').date()
        fecha_fin = fecha_inicio.replace(day=1) + relativedelta(months=1)  # Primer día del siguiente mes
        procedimientos = procedimientos.filter(fecha__gte=fecha_inicio, fecha__lt=fecha_fin)

    # Agrupar por tipo de procedimiento
    conteo_procedimientos = procedimientos.values('id_tipo_procedimiento__tipo_procedimiento').annotate(count=Count('id')).order_by('id_tipo_procedimiento__tipo_procedimiento')

    return JsonResponse(list(conteo_procedimientos), safe=False)

# Api para generar valores para las graficas de donut de la seccion de estadistica
def api_procedimientos_division_parroquias(request):
    division_id = request.GET.get('param_id')
    mes = request.GET.get('mes')

    # Filtrar por división
    procedimientos = Procedimientos.objects.filter(id_division=division_id)

    # Filtrar por mes si se proporciona
    if mes:
        # Convertir 'mes' a un rango de fechas
        fecha_inicio = datetime.strptime(mes, '%Y-%m').date()
        fecha_fin = fecha_inicio.replace(day=1) + relativedelta(months=1)  # Primer día del siguiente mes
        procedimientos = procedimientos.filter(fecha__gte=fecha_inicio, fecha__lt=fecha_fin)

    # Agrupar por parroquia y contar
    conteo_procedimientos = procedimientos.values(
        'id_parroquia__parroquia'  # Agrupar por el campo de la parroquia
    ).annotate(count=Count('id')).order_by('id_parroquia__parroquia')

    # Convertir a lista y retornar
    return JsonResponse(list(conteo_procedimientos), safe=False)

# Api para generar valores para la grafica de procedimientos por tipo
def api_procedimientos_tipo(request):
    tipo_procedimiento_id = request.GET.get('param_id')
    mes = request.GET.get('mes')

    # Filtrar por tipo de procedimiento
    procedimientos = Procedimientos.objects.all()
    if tipo_procedimiento_id:
        procedimientos = procedimientos.filter(id_tipo_procedimiento=tipo_procedimiento_id)

    # Filtrar por mes si se proporciona
    if mes:
        fecha_inicio = datetime.strptime(mes, '%Y-%m').date()
        fecha_fin = fecha_inicio.replace(day=1) + relativedelta(months=1)
        procedimientos = procedimientos.filter(fecha__gte=fecha_inicio, fecha__lt=fecha_fin)

    # Agrupar por división y contar procedimientos
    conteo_procedimientos = procedimientos.values(
        'id_division__division'  # Agrupar por nombre de la división
    ).annotate(count=Count('id')).order_by('id_division__division')

    return JsonResponse(list(conteo_procedimientos), safe=False)

# Api para generar valores para la grafica de procedimientos por tipo
def api_procedimientos_tipo_parroquias(request):
    tipo_procedimiento_id = request.GET.get('param_id')
    mes = request.GET.get('mes')

    # Filtrar por tipo de procedimiento
    procedimientos = Procedimientos.objects.all()
    if tipo_procedimiento_id:
        procedimientos = procedimientos.filter(id_tipo_procedimiento=tipo_procedimiento_id)

    # Filtrar por mes si se proporciona
    if mes:
        fecha_inicio = datetime.strptime(mes, '%Y-%m').date()
        fecha_fin = fecha_inicio.replace(day=1) + relativedelta(months=1)
        procedimientos = procedimientos.filter(fecha__gte=fecha_inicio, fecha__lt=fecha_fin)

    # Agrupar por parroquia y contar procedimientos
    conteo_procedimientos = procedimientos.values(
        'id_parroquia__parroquia'  # Cambia esto si el campo se llama de otra manera
    ).annotate(count=Count('id')).order_by('id_parroquia__parroquia')  # Ordenar por nombre de la parroquia

    return JsonResponse(list(conteo_procedimientos), safe=False)

# Api procedimiento por tipo de servicio - Tipo de detalles
# API para generar valores para la gráfica de procedimientos por tipo y detalles específicos
def api_procedimientos_tipo_detalles(request):
    tipo_procedimiento_id = request.GET.get('param_id')
    mes = request.GET.get('mes')

    # Filtrar procedimientos por tipo de procedimiento y mes
    procedimientos = Procedimientos.objects.all()
    if tipo_procedimiento_id:
        procedimientos = procedimientos.filter(id_tipo_procedimiento=tipo_procedimiento_id)

    if mes:
        fecha_inicio = datetime.strptime(mes, '%Y-%m').date()
        fecha_fin = fecha_inicio.replace(day=1) + relativedelta(months=1)
        procedimientos = procedimientos.filter(fecha__gte=fecha_inicio, fecha__lt=fecha_fin)

    # Variable para almacenar los resultados
    resultados = []

    # Filtrar y agrupar según el tipo de procedimiento
    if tipo_procedimiento_id == "1":  # Ejemplo: ID para "Abastecimiento de Agua"
        abastecimiento_data = Abastecimiento_agua.objects.filter(id_procedimiento__in=procedimientos).values(
            'id_tipo_servicio__nombre_institucion'  # Asume que `nombre` es el campo en Tipo_Institucion
        ).annotate(count=Count('id')).order_by('id_tipo_servicio__nombre_institucion')

        resultados = [
            {"tipo_servicio": item['id_tipo_servicio__nombre_institucion'], "count": item['count']}
            for item in abastecimiento_data
        ]
    # Filtrar y agrupar según el tipo de procedimiento
    if tipo_procedimiento_id == "2":  # Ejemplo: ID para "Abastecimiento de Agua"
        abastecimiento_data = Apoyo_Unidades.objects.filter(id_procedimiento__in=procedimientos).values(
            'id_tipo_apoyo__tipo_apoyo'  # Asume que `nombre` es el campo en Tipo_Institucion
        ).annotate(count=Count('id')).order_by('id_tipo_apoyo__tipo_apoyo')

        resultados = [
            {"tipo_servicio": item['id_tipo_apoyo__tipo_apoyo'], "count": item['count']}
            for item in abastecimiento_data
        ]
    # Filtrar y agrupar según el tipo de procedimiento
    if tipo_procedimiento_id == "3":  # Ejemplo: ID para "Abastecimiento de Agua"
        abastecimiento_data = Guardia_prevencion.objects.filter(id_procedimiento__in=procedimientos).values(
            'id_motivo_prevencion__motivo'  # Asume que `nombre` es el campo en Tipo_Institucion
        ).annotate(count=Count('id')).order_by('id_motivo_prevencion__motivo')

        resultados = [
            {"tipo_servicio": item['id_motivo_prevencion__motivo'], "count": item['count']}
            for item in abastecimiento_data
        ]

    # Filtrar y agrupar según el tipo de procedimiento
    if tipo_procedimiento_id == "5":  # Ejemplo: ID para "Abastecimiento de Agua"
        abastecimiento_data = Despliegue_Seguridad.objects.filter(id_procedimiento__in=procedimientos).values(
            'motivo_despliegue__motivo'  # Asume que `nombre` es el campo en Tipo_Institucion
        ).annotate(count=Count('id')).order_by('motivo_despliegue__motivo')

        resultados = [
            {"tipo_servicio": item['motivo_despliegue__motivo'], "count": item['count']}
            for item in abastecimiento_data
        ]
    
    # Filtrar y agrupar según el tipo de procedimiento
    if tipo_procedimiento_id == "12":  # Ejemplo: ID para "Abastecimiento de Agua"
        abastecimiento_data = Fallecidos.objects.filter(id_procedimiento__in=procedimientos).values(
            'motivo_fallecimiento'  # Asume que `nombre` es el campo en Tipo_Institucion
        ).annotate(count=Count('id')).order_by('motivo_fallecimiento')

        resultados = [
            {"tipo_servicio": item['motivo_fallecimiento'], "count": item['count']}
            for item in abastecimiento_data
        ]
    
    # Filtrar y agrupar según el tipo de procedimiento
    if tipo_procedimiento_id == "6":  # Ejemplo: ID para "Abastecimiento de Agua"
        abastecimiento_data = Falsa_Alarma.objects.filter(id_procedimiento__in=procedimientos).values(
            'motivo_alarma__motivo'  # Asume que `nombre` es el campo en Tipo_Institucion
        ).annotate(count=Count('id')).order_by('motivo_alarma__motivo')

        resultados = [
            {"tipo_servicio": item['motivo_alarma__motivo'], "count": item['count']}
            for item in abastecimiento_data
        ]
    
    # Filtrar y agrupar según el tipo de procedimiento
    if tipo_procedimiento_id == "9":  # Ejemplo: ID para "Abastecimiento de Agua"
        abastecimiento_data = Servicios_Especiales.objects.filter(id_procedimientos__in=procedimientos).values(
            'tipo_servicio__serv_especiales'  # Asume que `nombre` es el campo en Tipo_Institucion
        ).annotate(count=Count('id')).order_by('tipo_servicio__serv_especiales')

        resultados = [
            {"tipo_servicio": item['tipo_servicio__serv_especiales'], "count": item['count']}
            for item in abastecimiento_data
        ]

    # Filtrar y agrupar según el tipo de procedimiento
    if tipo_procedimiento_id == "10":  # Ejemplo: ID para "Abastecimiento de Agua"
        abastecimiento_data = Rescate.objects.filter(id_procedimientos__in=procedimientos).values(
            'tipo_rescate__tipo_rescate'  # Asume que `nombre` es el campo en Tipo_Institucion
        ).annotate(count=Count('id')).order_by('tipo_rescate__tipo_rescate')

        resultados = [
            {"tipo_servicio": item['tipo_rescate__tipo_rescate'], "count": item['count']}
            for item in abastecimiento_data
        ]

    # Filtrar y agrupar según el tipo de procedimiento
    if tipo_procedimiento_id == "11":  # Ejemplo: ID para "Abastecimiento de Agua"
        abastecimiento_data = Incendios.objects.filter(id_procedimientos__in=procedimientos).values(
            'id_tipo_incendio__tipo_incendio'  # Asume que `nombre` es el campo en Tipo_Institucion
        ).annotate(count=Count('id')).order_by('id_tipo_incendio__tipo_incendio')

        resultados = [
            {"tipo_servicio": item['id_tipo_incendio__tipo_incendio'], "count": item['count']}
            for item in abastecimiento_data
        ]

    # Filtrar y agrupar según el tipo de procedimiento
    if tipo_procedimiento_id == "7":  # Ejemplo: ID para "Abastecimiento de Agua"
        abastecimiento_data = Atenciones_Paramedicas.objects.filter(id_procedimientos__in=procedimientos).values(
            'tipo_atencion'  # Asume que `nombre` es el campo en Tipo_Institucion
        ).annotate(count=Count('id')).order_by('tipo_atencion')

        resultados = [
            {"tipo_servicio": item['tipo_atencion'], "count": item['count']}
            for item in abastecimiento_data
        ]

    # Filtrar y agrupar según el tipo de procedimiento
    if tipo_procedimiento_id == "16":  # Ejemplo: ID para "Abastecimiento de Agua"
        abastecimiento_data = Traslado_Prehospitalaria.objects.filter(id_procedimiento__in=procedimientos).values(
            'id_tipo_traslado__tipo_traslado'  # Asume que `nombre` es el campo en Tipo_Institucion
        ).annotate(count=Count('id')).order_by('id_tipo_traslado__tipo_traslado')

        resultados = [
            {"tipo_servicio": item['id_tipo_traslado__tipo_traslado'], "count": item['count']}
            for item in abastecimiento_data
        ]

    # Filtrar y agrupar según el tipo de procedimiento
    if tipo_procedimiento_id == "14":  # Ejemplo: ID para "Abastecimiento de Agua"
        abastecimiento_data = Evaluacion_Riesgo.objects.filter(id_procedimientos__in=procedimientos).values(
            'id_tipo_riesgo__tipo_riesgo'  # Asume que `nombre` es el campo en Tipo_Institucion
        ).annotate(count=Count('id')).order_by('id_tipo_riesgo__tipo_riesgo')

        resultados = [
            {"tipo_servicio": item['id_tipo_riesgo__tipo_riesgo'], "count": item['count']}
            for item in abastecimiento_data
        ]

    # Filtrar y agrupar según el tipo de procedimiento
    if tipo_procedimiento_id == "13":  # Ejemplo: ID para "Abastecimiento de Agua"
        abastecimiento_data = Mitigacion_Riesgos.objects.filter(id_procedimientos__in=procedimientos).values(
            'id_tipo_servicio__tipo_servicio'  # Asume que `nombre` es el campo en Tipo_Institucion
        ).annotate(count=Count('id')).order_by('id_tipo_servicio__tipo_servicio')

        resultados = [
            {"tipo_servicio": item['id_tipo_servicio__tipo_servicio'], "count": item['count']}
            for item in abastecimiento_data
        ]

    # Filtrar y agrupar según el tipo de procedimiento
    if tipo_procedimiento_id == "15":  # Ejemplo: ID para "Abastecimiento de Agua"
        abastecimiento_data = Puesto_Avanzada.objects.filter(id_procedimientos__in=procedimientos).values(
            'id_tipo_servicio__tipo_servicio'  # Asume que `nombre` es el campo en Tipo_Institucion
        ).annotate(count=Count('id')).order_by('id_tipo_servicio__tipo_servicio')

        resultados = [
            {"tipo_servicio": item['id_tipo_servicio__tipo_servicio'], "count": item['count']}
            for item in abastecimiento_data
        ]

    # Filtrar y agrupar según el tipo de procedimiento
    if tipo_procedimiento_id == "21":  # Ejemplo: ID para "Abastecimiento de Agua"
        abastecimiento_data = Retencion_Preventiva.objects.filter(id_procedimiento__in=procedimientos).values(
            'tipo_cilindro'  # Asume que `nombre` es el campo en Tipo_Institucion
        ).annotate(count=Count('id')).order_by('tipo_cilindro')

        resultados = [
            {"tipo_servicio": item['tipo_cilindro'], "count": item['count']}
            for item in abastecimiento_data
        ]

    # Filtrar y agrupar según el tipo de procedimiento
    if tipo_procedimiento_id == "22":  # Ejemplo: ID para "Abastecimiento de Agua"
        abastecimiento_data = Artificios_Pirotecnicos.objects.filter(id_procedimiento__in=procedimientos).values(
            'tipo_procedimiento__tipo'  # Asume que `nombre` es el campo en Tipo_Institucion
        ).annotate(count=Count('id')).order_by('tipo_procedimiento__tipo')

        resultados = [
            {"tipo_servicio": item['tipo_procedimiento__tipo'], "count": item['count']}
            for item in abastecimiento_data
        ]

    # Filtrar y agrupar según el tipo de procedimiento
    if tipo_procedimiento_id == "45":  # Ejemplo: ID para "Abastecimiento de Agua"
        abastecimiento_data = Procedimientos_Capacitacion.objects.filter(id_procedimientos__in=procedimientos).values(
            'tipo_capacitacion'  # Asume que `nombre` es el campo en Tipo_Institucion
        ).annotate(count=Count('id')).order_by('tipo_capacitacion')

        resultados = [
            {"tipo_servicio": item['tipo_capacitacion'], "count": item['count']}
            for item in abastecimiento_data
        ]

    # Filtrar y agrupar según el tipo de procedimiento
    if tipo_procedimiento_id == "18":  # Ejemplo: ID para "Abastecimiento de Agua"
        abastecimiento_data = Inspeccion_Prevencion_Asesorias_Tecnicas.objects.filter(id_procedimientos__in=procedimientos).values(
            'tipo_inspeccion'  # Asume que `nombre` es el campo en Tipo_Institucion
        ).annotate(count=Count('id')).order_by('tipo_inspeccion')

        resultados = [
            {"tipo_servicio": item['tipo_inspeccion'], "count": item['count']}
            for item in abastecimiento_data
        ]
        
        abastecimiento_data = Inspeccion_Habitabilidad.objects.filter(id_procedimientos__in=procedimientos).values(
            'tipo_inspeccion'  # Asume que `nombre` es el campo en Tipo_Institucion
        ).annotate(count=Count('id')).order_by('tipo_inspeccion')

        resultados += [
            {"tipo_servicio": item['tipo_inspeccion'], "count": item['count']}
            for item in abastecimiento_data
        ]

        abastecimiento_data = Inspeccion_Otros.objects.filter(id_procedimientos__in=procedimientos).values(
            'tipo_inspeccion'  # Asume que `nombre` es el campo en Tipo_Institucion
        ).annotate(count=Count('id')).order_by('tipo_inspeccion')

        resultados += [
            {"tipo_servicio": item['tipo_inspeccion'], "count": item['count']}
            for item in abastecimiento_data
        ]
        
        abastecimiento_data = Inspeccion_Arbol.objects.filter(id_procedimientos__in=procedimientos).values(
            'tipo_inspeccion'  # Asume que `nombre` es el campo en Tipo_Institucion
        ).annotate(count=Count('id')).order_by('tipo_inspeccion')

        resultados += [
            {"tipo_servicio": item['tipo_inspeccion'], "count": item['count']}
            for item in abastecimiento_data
        ]

    
    # Filtrar y agrupar según el tipo de procedimiento
    if tipo_procedimiento_id == "19":  # Ejemplo: ID para "Abastecimiento de Agua"
        abastecimiento_data = Investigacion.objects.filter(id_procedimientos__in=procedimientos).values(
            'tipo_siniestro'  # Asume que `nombre` es el campo en Tipo_Institucion
        ).annotate(count=Count('id')).order_by('tipo_siniestro')

        resultados = [
            {"tipo_servicio": item['tipo_siniestro'], "count": item['count']}
            for item in abastecimiento_data
        ]

    # Retornar el JSON con los resultados formateados
    return JsonResponse(resultados, safe=False)

# Api para generar los valores para la grafica de barras de la seccion de estadistica
def obtener_divisiones_estadistica(request):
    # Obtener el parámetro 'mes' (en formato 'YYYY-MM')
    mes = request.GET.get('mes', None)
    
    # Obtener el mes o el año actual si 'mes' no se proporciona
    hoy = datetime.now()
    if mes:
        try:
            # Si se proporciona el mes, obtenemos el primer día del mes
            primer_dia_mes = datetime.strptime(mes, '%Y-%m').date()
        except ValueError:
            return JsonResponse({"error": "Formato de mes inválido. Debe ser 'YYYY-MM'."}, status=400)
        ultimo_dia_mes = primer_dia_mes.replace(day=1).replace(month=primer_dia_mes.month % 12 + 1) - timedelta(days=1)
    else:
        # Si no se selecciona ningún mes, usar el año actual
        primer_dia_mes = hoy.replace(month=1, day=1).date()
        ultimo_dia_mes = hoy.replace(month=12, day=31).date()

    # Filtrar procedimientos por división en el rango de fechas determinado
    divisiones = {
        "rescate": {
            "total": Procedimientos.objects.filter(id_division=1, fecha__range=(primer_dia_mes, ultimo_dia_mes)).count(),
        },
        "operaciones": {
            "total": Procedimientos.objects.filter(id_division=2, fecha__range=(primer_dia_mes, ultimo_dia_mes)).count(),
        },
        "prevencion": {
            "total": Procedimientos.objects.filter(id_division=3, fecha__range=(primer_dia_mes, ultimo_dia_mes)).count(),
        },
        "grumae": {
            "total": Procedimientos.objects.filter(id_division=4, fecha__range=(primer_dia_mes, ultimo_dia_mes)).count(),
        },
        "prehospitalaria": {
            "total": Procedimientos.objects.filter(id_division=5, fecha__range=(primer_dia_mes, ultimo_dia_mes)).count(),
        },
        "enfermeria": {
            "total": Procedimientos.objects.filter(id_division=6, fecha__range=(primer_dia_mes, ultimo_dia_mes)).count(),
        },
        "servicios_medicos": {
            "total": Procedimientos.objects.filter(id_division=7, fecha__range=(primer_dia_mes, ultimo_dia_mes)).count(),
        },
        "psicologia": {
            "total": Procedimientos.objects.filter(id_division=8, fecha__range=(primer_dia_mes, ultimo_dia_mes)).count(),
        },
        "capacitacion": {
            "total": Procedimientos.objects.filter(id_division=9, fecha__range=(primer_dia_mes, ultimo_dia_mes)).count(),
        },
    }

    return JsonResponse(divisiones)

# Api para obtener valores para las cards de divisones de la seccion del dashboard
def obtener_divisiones(request):
    hoy = datetime.now().date()
    primer_dia_mes = hoy.replace(day=1)

    # Filtrado de procedimientos por división
    divisiones = {
        "rescate": {
            "total": Procedimientos.objects.filter(id_division=1).count(),
            "del_mes": Procedimientos.objects.filter(id_division=1, fecha__gte=primer_dia_mes).count(),
            "hoy": Procedimientos.objects.filter(id_division=1, fecha=hoy).count(),
        },
        "operaciones": {
            "total": Procedimientos.objects.filter(id_division=2).count(),
            "del_mes": Procedimientos.objects.filter(id_division=2, fecha__gte=primer_dia_mes).count(),
            "hoy": Procedimientos.objects.filter(id_division=2, fecha=hoy).count(),
        },
        "prevencion": {
            "total": Procedimientos.objects.filter(id_division=3).count(),
            "del_mes": Procedimientos.objects.filter(id_division=3, fecha__gte=primer_dia_mes).count(),
            "hoy": Procedimientos.objects.filter(id_division=3, fecha=hoy).count(),
        },
        "grumae": {
            "total": Procedimientos.objects.filter(id_division=4).count(),
            "del_mes": Procedimientos.objects.filter(id_division=4, fecha__gte=primer_dia_mes).count(),
            "hoy": Procedimientos.objects.filter(id_division=4, fecha=hoy).count(),
        },
        "prehospitalaria": {
            "total": Procedimientos.objects.filter(id_division=5).count(),
            "del_mes": Procedimientos.objects.filter(id_division=5, fecha__gte=primer_dia_mes).count(),
            "hoy": Procedimientos.objects.filter(id_division=5, fecha=hoy).count(),
        },
        "enfermeria": {
            "total": Procedimientos.objects.filter(id_division=6).count(),
            "del_mes": Procedimientos.objects.filter(id_division=6, fecha__gte=primer_dia_mes).count(),
            "hoy": Procedimientos.objects.filter(id_division=6, fecha=hoy).count(),
        },
        "servicios_medicos": {
            "total": Procedimientos.objects.filter(id_division=7).count(),
            "del_mes": Procedimientos.objects.filter(id_division=7, fecha__gte=primer_dia_mes).count(),
            "hoy": Procedimientos.objects.filter(id_division=7, fecha=hoy).count(),
        },
        "psicologia": {
            "total": Procedimientos.objects.filter(id_division=8).count(),
            "del_mes": Procedimientos.objects.filter(id_division=8, fecha__gte=primer_dia_mes).count(),
            "hoy": Procedimientos.objects.filter(id_division=8, fecha=hoy).count(),
        },
        "capacitacion": {
            "total": Procedimientos.objects.filter(id_division=9).count(),
            "del_mes": Procedimientos.objects.filter(id_division=9, fecha__gte=primer_dia_mes).count(),
            "hoy": Procedimientos.objects.filter(id_division=9, fecha=hoy).count(),
        },
    }

    return JsonResponse(divisiones)

# Api para Editar la informacion seleccionada del Personal
def edit_personal(request):
    if request.method == 'POST':
        # Obtener el ID de la persona
        persona_id = request.POST.get('personal_id')
        
        # Verificar si el ID está presente
        if persona_id:
            # Obtener el objeto Personal por su ID
            personal = get_object_or_404(Personal, id=persona_id)
            
            cedula = request.POST.get('formulario-cedula')
            nac = request.POST.get('formulario-nacionalidad')

            # Actualizar los campos del modelo
            personal.nombres = request.POST.get('formulario-nombres')
            personal.apellidos = request.POST.get('formulario-apellidos')
            personal.jerarquia = request.POST.get('formulario-jerarquia')
            personal.cargo = request.POST.get('formulario-cargo')
            personal.cedula = f"{nac}- {cedula}"
            personal.sexo = request.POST.get('formulario-sexo')
            personal.rol = request.POST.get('formulario-rol')
            personal.status = request.POST.get('formulario-status')
            
            # Guardar los cambios
            personal.save()
            
            # Redirigir o mostrar un mensaje de éxito
            return redirect('/personal/')  # Reemplaza con tu vista deseada
        else:
            # Si no se pasó el ID
            return redirect('/personal/')  # Redirigir a una página de error o donde desees
    
    # Si es GET, mostrar el formulario vacío o con los datos del objeto
    return render(request, 'editar_personal.html')

# Api para obtener el valor de el personal seleccionado
def get_persona(request, persona_id):
    try:
        persona = Personal.objects.get(id=persona_id)
        data = {
            'nombre': persona.nombres,
            'apellido': persona.apellidos,
            'cedula': persona.cedula,
            'jerarquia': persona.jerarquia,
            'cargo': persona.cargo,
            'rol': persona.rol,
            'sexo': persona.sexo,
            'status': persona.status,
        }
        return JsonResponse(data)
    except Personal.DoesNotExist:
        return JsonResponse({'error': 'Persona no encontrada'}, status=404)

def obtener_procedimiento(request, id):
    
    procedimiento = get_object_or_404(Procedimientos, pk=id)

    division = procedimiento.id_division.division

    if division == "Rescate" or division == "Operaciones" or division == "Prevencion" or division == "GRUMAE" or division == "PreHospitalaria":        
        data = {
            'id': procedimiento.id,
            'division': procedimiento.id_division.division,
            'solicitante': f"{procedimiento.id_solicitante.jerarquia} {procedimiento.id_solicitante.nombres} {procedimiento.id_solicitante.apellidos}",
            'solicitante_externo': procedimiento.solicitante_externo,
            'jefe_comision': f"{procedimiento.id_jefe_comision.jerarquia} {procedimiento.id_jefe_comision.nombres} {procedimiento.id_jefe_comision.apellidos}",
            'unidad': procedimiento.unidad.nombre_unidad,
            'efectivos': procedimiento.efectivos_enviados,
            'parroquia': procedimiento.id_parroquia.parroquia,
            'municipio': procedimiento.id_municipio.municipio,
            'direccion': procedimiento.direccion,
            'fecha': procedimiento.fecha,
            'hora': procedimiento.hora,
            'tipo_procedimiento': procedimiento.id_tipo_procedimiento.tipo_procedimiento,
        }

        # Obteniendo las comisiones relacionadas con el procedimiento
        comisiones = Comisiones.objects.filter(procedimiento=procedimiento)

        # Formateando las comisiones en una lista
        comisiones_lista = [
            {
                'comision': comision.comision.tipo_comision,
                'nombre_oficial': comision.nombre_oficial,
                'apellido_oficial': comision.apellido_oficial,
                'cedula_oficial': comision.cedula_oficial,
                'nro_unidad': comision.nro_unidad,
                'nro_cuadrante': comision.nro_cuadrante,
            }
            for comision in comisiones
        ]

        # Agregando la lista de comisiones al diccionario
        data['comisiones'] = comisiones_lista
    
    if division == "Enfermeria":
        data = {
            'id': procedimiento.id,
            'division': procedimiento.id_division.division,
            'dependencia': procedimiento.dependencia,
            'solicitante_externo': procedimiento.solicitante_externo,
            'parroquia': procedimiento.id_parroquia.parroquia,
            'municipio': procedimiento.id_municipio.municipio,
            'direccion': procedimiento.direccion,
            'fecha': procedimiento.fecha,
            'hora': procedimiento.hora,
            'tipo_procedimiento': procedimiento.id_tipo_procedimiento.tipo_procedimiento,
        }

    if division == "Servicios Medicos":
        data = {
            'id': procedimiento.id,
            'division': procedimiento.id_division.division,
            'tipo_servicio': procedimiento.tipo_servicio,
            'solicitante_externo': procedimiento.solicitante_externo,
            'efectivos': procedimiento.efectivos_enviados,
            'parroquia': procedimiento.id_parroquia.parroquia,
            'municipio': procedimiento.id_municipio.municipio,
            'direccion': procedimiento.direccion,
            'fecha': procedimiento.fecha,
            'hora': procedimiento.hora,
            'tipo_procedimiento': procedimiento.id_tipo_procedimiento.tipo_procedimiento,
        }

    if division == "Psicologia":
            data = {
                'id': procedimiento.id,
                'division': procedimiento.id_division.division,
                'solicitante_externo': procedimiento.solicitante_externo,
                'parroquia': procedimiento.id_parroquia.parroquia,
                'municipio': procedimiento.id_municipio.municipio,
                'direccion': procedimiento.direccion,
                'fecha': procedimiento.fecha,
                'hora': procedimiento.hora,
                'tipo_procedimiento': procedimiento.id_tipo_procedimiento.tipo_procedimiento,
            }
    
    if division == "Capacitacion":
        data = {
            'id': procedimiento.id,
            'division': procedimiento.id_division.division,
            'solicitante': f"{procedimiento.id_solicitante.jerarquia} {procedimiento.id_solicitante.nombres} {procedimiento.id_solicitante.apellidos}",
            'solicitante_externo': procedimiento.solicitante_externo,
            'jefe_comision': f"{procedimiento.id_jefe_comision.jerarquia} {procedimiento.id_jefe_comision.nombres} {procedimiento.id_jefe_comision.apellidos}",
            'dependencia': procedimiento.dependencia,
            'parroquia': procedimiento.id_parroquia.parroquia,
            'municipio': procedimiento.id_municipio.municipio,
            'direccion': procedimiento.direccion,
            'fecha': procedimiento.fecha,
            'hora': procedimiento.hora,
            'tipo_procedimiento': procedimiento.id_tipo_procedimiento.tipo_procedimiento,
        }
    
    if str(procedimiento.id_tipo_procedimiento.id) == "1":
        detalle_procedimiento = get_object_or_404(Abastecimiento_agua, id_procedimiento=id)

        data = dict(data,
                    ente_suministrado = detalle_procedimiento.id_tipo_servicio.nombre_institucion,
                    nombres = detalle_procedimiento.nombres,
                    apellidos = detalle_procedimiento.apellidos,
                    cedula = detalle_procedimiento.cedula,
                    ltrs_agua = detalle_procedimiento.ltrs_agua,
                    personas_atendidas = detalle_procedimiento.personas_atendidas,
                    descripcion = detalle_procedimiento.descripcion,
                    material_utilizado = detalle_procedimiento.material_utilizado,
                    status = detalle_procedimiento.status)

    if str(procedimiento.id_tipo_procedimiento.id) == "2":
        detalle_procedimiento = get_object_or_404(Apoyo_Unidades, id_procedimiento=id)
        data = dict(data,
                    tipo_apoyo = detalle_procedimiento.id_tipo_apoyo.tipo_apoyo,
                    unidad_apoyada = detalle_procedimiento.unidad_apoyada,
                    descripcion = detalle_procedimiento.descripcion,
                    material_utilizado = detalle_procedimiento.material_utilizado,
                    status = detalle_procedimiento.status,
                    )

    if str(procedimiento.id_tipo_procedimiento.id) == "3":
        detalle_procedimiento = get_object_or_404(Guardia_prevencion, id_procedimiento=id)
        data = dict(data,
                    motivo_prevencion = detalle_procedimiento.id_motivo_prevencion.motivo,
                    descripcion = detalle_procedimiento.descripcion,
                    material_utilizado = detalle_procedimiento.material_utilizado,
                    status = detalle_procedimiento.status,
                    )

    if str(procedimiento.id_tipo_procedimiento.id) == "4":
        detalle_procedimiento = get_object_or_404(Atendido_no_Efectuado, id_procedimiento=id)
        data = dict(data,
                    descripcion = detalle_procedimiento.descripcion,
                    material_utilizado = detalle_procedimiento.material_utilizado,
                    status = detalle_procedimiento.status,
                    )

    if str(procedimiento.id_tipo_procedimiento.id) == "5":
        detalle_procedimiento = get_object_or_404(Despliegue_Seguridad, id_procedimiento=id)
        data = dict(data,
                    motivo_despliegue = detalle_procedimiento. motivo_despliegue.motivo,
                    descripcion = detalle_procedimiento.descripcion,
                    material_utilizado = detalle_procedimiento.material_utilizado,
                    status = detalle_procedimiento.status,
                    )

    if str(procedimiento.id_tipo_procedimiento.id) == "6":
        detalle_procedimiento = get_object_or_404(Falsa_Alarma, id_procedimiento=id)
        data = dict(data,
                    motivo_alarma = detalle_procedimiento.motivo_alarma.motivo,
                    descripcion = detalle_procedimiento.descripcion,
                    material_utilizado = detalle_procedimiento.material_utilizado,
                    status = detalle_procedimiento.status,
                    )

    if str(procedimiento.id_tipo_procedimiento.id) == "7":
        # Obtener el detalle del procedimiento
        detalle_procedimiento = get_object_or_404(Atenciones_Paramedicas, id_procedimientos=id)

        # Agregar detalles del procedimiento a los datos
        data = dict(data,
                    tipo_atencion=detalle_procedimiento.tipo_atencion,
                    )

        if detalle_procedimiento.tipo_atencion == "Emergencias Medicas":
            emergencia = Emergencias_Medicas.objects.get(id_atencion=detalle_procedimiento.id)
            data = dict(data,
                emergencia = True,
                nombres = emergencia.nombres,
                apellidos = emergencia.apellidos,
                cedula = emergencia.cedula,
                edad = emergencia.edad,
                sexo = emergencia.sexo,
                idx = emergencia.idx,
                descripcion = emergencia.descripcion,
                material_utilizado = emergencia.material_utilizado,
                status = emergencia.status,
            )

            if Traslado.objects.filter(id_lesionado=emergencia.id).exists():
                traslado = Traslado.objects.get(id_lesionado = emergencia.id)

                data = dict(data,
                            traslado = True,
                            hospital = traslado.hospital_trasladado,
                            medico = traslado.medico_receptor,
                            mpps_cmt = traslado.mpps_cmt,
                        )

        if detalle_procedimiento.tipo_atencion == "Accidentes de Transito":
            accidente = Accidentes_Transito.objects.get(id_atencion=detalle_procedimiento.id)
            data = dict(data,
                accidente = True,
                tipo_accidente=accidente.tipo_de_accidente.tipo_accidente,
                cantidad_lesionados=accidente.cantidad_lesionados,
                material_utilizado=accidente.material_utilizado,
                status=accidente.status,
            )

            # Filtrar todos los vehículos relacionados con el accidente
            vehiculos = Detalles_Vehiculos_Accidente.objects.filter(id_vehiculo=accidente.id)

            # Si hay vehículos, recopilarlos en una lista
            if vehiculos:
                data = dict(data,
                    vehiculo = True
                )
                vehiculos_list = []
                for vehiculo in vehiculos:
                    vehiculos_list.append({
                        'marca': vehiculo.marca,
                        'modelo': vehiculo.modelo,
                        'color': vehiculo.color,
                        'año': vehiculo.año,
                        'placas': vehiculo.placas,
                        # Añade aquí otros campos que necesites
                    })
                data['vehiculos'] = vehiculos_list  # Agrega la lista de vehículos a 'data'
            else:
                data['vehiculos'] = []  # O puedes omitir esta línea si prefieres no agregar la clave

            # Filtrar los lesionados asociados al accidente
            lesionados = Lesionados.objects.filter(id_accidente=accidente.id)

            # Si hay lesionados, recopilarlos en una lista
            if lesionados:
                data = dict(data,
                    lesionado = True
                )
                lesionados_list = []
                for lesionado in lesionados:
                    lesionado_data = {
                        'nombre': lesionado.nombres,
                        'apellidos': lesionado.apellidos,
                        'cedula': lesionado.cedula,
                        'edad': lesionado.edad,
                        'sexo': lesionado.sexo,
                        'idx': lesionado.idx,
                        'descripcion': lesionado.descripcion,
                        # Añade aquí otros campos que necesites
                    }

                    # Filtrar traslados asociados a cada lesionado
                    traslados = Traslado_Accidente.objects.filter(id_lesionado=lesionado.id)

                    # Si hay traslados, añadirlos a los datos del lesionado
                    if traslados:
                        traslados_list = []
                        for traslado in traslados:
                            traslados_list.append({
                                'hospital': traslado.hospital_trasladado,
                                'medico': traslado.medico_receptor,
                                'mpps_cmt': traslado.mpps_cmt,
                            })
                        lesionado_data['traslados'] = traslados_list
                    else:
                        lesionado_data['traslados'] = []

                    # Añadir cada lesionado a la lista
                    lesionados_list.append(lesionado_data)

                data['lesionados'] = lesionados_list  # Agregar la lista de lesionados a 'data'
            else:
                data['lesionados'] = []  # Si no hay lesionados, agregar una lista vacía

    if str(procedimiento.id_tipo_procedimiento.id) == "9":
        detalle_procedimiento = get_object_or_404(Servicios_Especiales, id_procedimientos=id)
        data = dict(data,
                    tipo_servicio = detalle_procedimiento.tipo_servicio.serv_especiales,
                    descripcion = detalle_procedimiento.descripcion,
                    material_utilizado = detalle_procedimiento.material_utilizado,
                    status = detalle_procedimiento.status,
                    )

    if str(procedimiento.id_tipo_procedimiento.id) == "10":
        detalle_procedimiento = get_object_or_404(Rescate, id_procedimientos=id)
        data = dict(data,
                    material_utilizado = detalle_procedimiento.material_utilizado,
                    status = detalle_procedimiento.status,
                    tipo_rescate = detalle_procedimiento.tipo_rescate.tipo_rescate,
                    )

        if detalle_procedimiento.tipo_rescate.tipo_rescate == "Rescate de Animal":
            detalle_tipo_rescate = get_object_or_404(Rescate_Animal, id_rescate=detalle_procedimiento.id)
            data = dict(data,
                        especie = detalle_tipo_rescate.especie,
                        descripcion = detalle_tipo_rescate.descripcion,
                        )

        else:
            detalle_tipo_rescate = get_object_or_404(Rescate_Persona, id_rescate=detalle_procedimiento.id)
            data = dict(data,
                        nombres = detalle_tipo_rescate.nombre,
                        apellidos = detalle_tipo_rescate.apellidos,
                        cedula = detalle_tipo_rescate.cedula,
                        edad = detalle_tipo_rescate.edad,
                        sexo = detalle_tipo_rescate.sexo,
                        descripcion = detalle_tipo_rescate.descripcion,
                        )

    if str(procedimiento.id_tipo_procedimiento.id) == "11":
      # Obtener el detalle del procedimiento
      detalle_procedimiento = get_object_or_404(Incendios, id_procedimientos=id)

      # Agregar detalles del procedimiento a los datos
      data = dict(data,
                  tipo_incendio=detalle_procedimiento.id_tipo_incendio.tipo_incendio,
                  descripcion=detalle_procedimiento.descripcion,
                  status=detalle_procedimiento.status,
                  material_utilizado=detalle_procedimiento.material_utilizado,
                )

      if Persona_Presente.objects.filter(id_incendio=detalle_procedimiento.id).exists():
          persona_presente_detalles = Persona_Presente.objects.get(id_incendio=detalle_procedimiento.id)
          data.update({
              "persona": True,
              "nombre": persona_presente_detalles.nombre,
              "apellidos": persona_presente_detalles.apellidos,
              "cedula": persona_presente_detalles.cedula,
              "edad": persona_presente_detalles.edad,
          })
      else:
          pass

      if Detalles_Vehiculos.objects.filter(id_vehiculo=detalle_procedimiento.id).exists():
          vehiculo_detalles = Detalles_Vehiculos.objects.get(id_vehiculo=detalle_procedimiento.id)
          data.update({
              "vehiculo": True,
              "modelo": vehiculo_detalles.modelo,
              "marca": vehiculo_detalles.marca,
              "color": vehiculo_detalles.color,
              "año": vehiculo_detalles.año,
              "placas": vehiculo_detalles.placas,
          })
      else:
          pass

    if str(procedimiento.id_tipo_procedimiento.id) == "12":
        detalle_procedimiento = get_object_or_404(Fallecidos, id_procedimiento=id)
        data = dict(data,
                    motivo_fallecimiento = detalle_procedimiento.motivo_fallecimiento,
                    nombres = detalle_procedimiento.nombres,
                    apellidos = detalle_procedimiento.apellidos,
                    cedula = detalle_procedimiento.cedula,
                    edad = detalle_procedimiento.edad,
                    sexo = detalle_procedimiento.sexo,
                    descripcion = detalle_procedimiento.descripcion,
                    material_utilizado = detalle_procedimiento.material_utilizado,
                    status = detalle_procedimiento.status,
                    )

    if str(procedimiento.id_tipo_procedimiento.id) == "13":
        detalle_procedimiento = get_object_or_404(Mitigacion_Riesgos, id_procedimientos=id)
        data = dict(data,
                    tipo_servicio = detalle_procedimiento.id_tipo_servicio.tipo_servicio,
                    descripcion = detalle_procedimiento.descripcion,
                    material_utilizado = detalle_procedimiento.material_utilizado,
                    status = detalle_procedimiento.status,
                    )

    if str(procedimiento.id_tipo_procedimiento.id) == "14":
        detalle_procedimiento = get_object_or_404(Evaluacion_Riesgo, id_procedimientos=id)
        data = dict(data,
                    tipo_de_evaluacion = detalle_procedimiento.id_tipo_riesgo.tipo_riesgo,
                    descripcion = detalle_procedimiento.descripcion,
                    material_utilizado = detalle_procedimiento.material_utilizado,
                    status = detalle_procedimiento.status,
                    )

        if str(detalle_procedimiento.id_procedimientos.id_division) == "Prevencion":
            detalle_persona = get_object_or_404(Persona_Presente_Eval, id_persona=detalle_procedimiento.id)
            data = dict(data,
                        nombre = detalle_persona.nombre,
                        apellido = detalle_persona.apellidos,
                        cedula = detalle_persona.cedula,
                        telefono = detalle_persona.telefono,
                        )
        if detalle_procedimiento.tipo_estructura:
            data = dict(data,
                        tipo_estructura = detalle_procedimiento.tipo_estructura)

        else:
            data = dict(data,
                        tipo_estructura = "")

    if str(procedimiento.id_tipo_procedimiento.id) == "15":
        detalle_procedimiento = get_object_or_404(Puesto_Avanzada, id_procedimientos=id)
        data = dict(data,
                    tipo_de_servicio = detalle_procedimiento.id_tipo_servicio.tipo_servicio,
                    descripcion = detalle_procedimiento.descripcion,
                    material_utilizado = detalle_procedimiento.material_utilizado,
                    status = detalle_procedimiento.status,
                    )

    if str(procedimiento.id_tipo_procedimiento.id) == "16":
        detalle_procedimiento = get_object_or_404(Traslado_Prehospitalaria, id_procedimiento=id)
        data = dict(data,
                    traslado = detalle_procedimiento.id_tipo_traslado.tipo_traslado,
                    descripcion = detalle_procedimiento.descripcion,
                    material_utilizado = detalle_procedimiento.material_utilizado,
                    status = detalle_procedimiento.status,
                    nombre = detalle_procedimiento.nombre,
                    apellido = detalle_procedimiento.apellido,
                    cedula = detalle_procedimiento.cedula,
                    edad = detalle_procedimiento.edad,
                    sexo = detalle_procedimiento.sexo,
                    idx = detalle_procedimiento.idx,
                    hospital = detalle_procedimiento.hospital_trasladado,
                    medico = detalle_procedimiento.medico_receptor,
                    mpps = detalle_procedimiento.mpps_cmt
                    )

    if str(procedimiento.id_tipo_procedimiento.id) == "17":
        detalle_procedimiento = get_object_or_404(Asesoramiento, id_procedimiento=id)
        data = dict(data,
                    nombre_comercio = detalle_procedimiento.nombre_comercio,
                    rif_comercio = detalle_procedimiento.rif_comercio,
                    nombre = detalle_procedimiento.nombres,
                    apellido = detalle_procedimiento.apellidos,
                    cedula = detalle_procedimiento.cedula,
                    sexo = detalle_procedimiento.sexo,
                    telefono = detalle_procedimiento.telefono,
                    descripcion = detalle_procedimiento.descripcion,
                    material_utilizado = detalle_procedimiento.material_utilizado,
                    status = detalle_procedimiento.status,
                    )

    if str(procedimiento.id_tipo_procedimiento.id) == "18":  # Supongamos que 18 es el ID de Procedimiento
        # Diccionario para mapear tipos de inspección a sus modelos
        inspection_models = {
            "Prevención": Inspeccion_Prevencion_Asesorias_Tecnicas,
            "Habitabilidad": Inspeccion_Habitabilidad,
            "Otros": Inspeccion_Otros,
            "Arbol": Inspeccion_Arbol
        }

        # Intentar obtener la instancia de inspección
        for tipo_inspeccion, model_class in inspection_models.items():
            try:
                detalle_procedimiento = model_class.objects.get(id_procedimientos=id)

                # Actualizar datos en función del tipo de inspección
                data.update({
                    "tipo_inspeccion": detalle_procedimiento.tipo_inspeccion,
                    "persona_sitio_nombre": detalle_procedimiento.persona_sitio_nombre,
                    "persona_sitio_apellido": detalle_procedimiento.persona_sitio_apellido,
                    "persona_sitio_cedula": detalle_procedimiento.persona_sitio_cedula,
                    "persona_sitio_telefono": detalle_procedimiento.persona_sitio_telefono,
                    "material_utilizado": detalle_procedimiento.material_utilizado,
                    "status": detalle_procedimiento.status,
                })

                # Actualizar campos específicos según el tipo de inspección
                if tipo_inspeccion == "Prevención":
                    data.update({
                        "nombre_comercio": detalle_procedimiento.nombre_comercio,
                        "propietario": detalle_procedimiento.propietario,
                        "cedula_propietario": detalle_procedimiento.cedula_propietario,
                        "descripcion": detalle_procedimiento.descripcion,
                    })
                elif tipo_inspeccion == "Habitabilidad":
                    data.update({
                        "descripcion": detalle_procedimiento.descripcion,
                    })
                elif tipo_inspeccion == "Otros":
                    data.update({
                        "especifique": detalle_procedimiento.especifique,
                        "descripcion": detalle_procedimiento.descripcion,
                    })
                elif tipo_inspeccion == "Arbol":
                    data.update({
                        "especie": detalle_procedimiento.especie,
                        "altura_aprox": detalle_procedimiento.altura_aprox,
                        "ubicacion_arbol": detalle_procedimiento.ubicacion_arbol,
                        "descripcion": detalle_procedimiento.descripcion,
                    })

                # Salir del ciclo una vez que se haya encontrado y procesado la inspección
                break

            except model_class.DoesNotExist:
                # Si no se encuentra la inspección, continuar con el siguiente tipo
                continue

    if str(procedimiento.id_tipo_procedimiento.id) == "19":
        investigacion = get_object_or_404(Investigacion, id_procedimientos=id)
        data.update({
            "tipo_investigacion": investigacion.id_tipo_investigacion.tipo_investigacion,
            "tipo_siniestro": investigacion.tipo_siniestro,
        })
        
        if investigacion.tipo_siniestro == "Vehiculo":
            vehiculo = Investigacion_Vehiculo.objects.filter(id_investigacion=investigacion).first()
            if vehiculo:
                data.update({
                    "marca": vehiculo.marca,
                    "modelo": vehiculo.modelo,
                    "color": vehiculo.color,
                    "placas": vehiculo.placas,
                    "año": vehiculo.año,
                    "nombre_propietario": vehiculo.nombre_propietario,
                    "apellido_propietario": vehiculo.apellido_propietario,
                    "cedula_propietario": vehiculo.cedula_propietario,
                    "descripcion": vehiculo.descripcion,
                    "material_utilizado": vehiculo.material_utilizado,
                    "status": vehiculo.status,
                })

        elif investigacion.tipo_siniestro == "Comercio":
            comercio = Investigacion_Comercio.objects.filter(id_investigacion=investigacion).first()
            if comercio:
                data.update({
                    "nombre_comercio_investigacion": comercio.nombre_comercio,
                    "rif_comercio_investigacion": comercio.rif_comercio,
                    "nombre_propietario_comercio": comercio.nombre_propietario,
                    "apellido_propietario_comercio": comercio.apellido_propietario,
                    "cedula_propietario_comercio": comercio.cedula_propietario,
                    "descripcion_comercio": comercio.descripcion,
                    "material_utilizado_comercio": comercio.material_utilizado,
                    "status_comercio": comercio.status,
                })

        elif investigacion.tipo_siniestro == "Estructura" or investigacion.tipo_siniestro == "Vivienda":
            estructura = Investigacion_Estructura_Vivienda.objects.filter(id_investigacion=investigacion).first()
            if estructura:
                data.update({
                    "tipo_estructura": estructura.tipo_estructura,
                    "nombre_propietario_estructura": estructura.nombre,
                    "apellido_propietario_estructura": estructura.apellido,
                    "cedula_propietario_estructura": estructura.cedula,
                    "descripcion_estructura": estructura.descripcion,
                    "material_utilizado_estructura": estructura.material_utilizado,
                    "status_estructura": estructura.status,
                })

    if str(procedimiento.id_tipo_procedimiento.id) == "20":
        detalle_procedimiento = get_object_or_404(Reinspeccion_Prevencion, id_procedimiento=id)
        data = dict(data,
                    nombre_comercio = detalle_procedimiento.nombre_comercio,
                    rif_comercio = detalle_procedimiento.rif_comercio,
                    nombre = detalle_procedimiento.nombre,
                    apellido = detalle_procedimiento.apellidos,
                    cedula = detalle_procedimiento.cedula,
                    sexo = detalle_procedimiento.sexo,
                    telefono = detalle_procedimiento.telefono,
                    descripcion = detalle_procedimiento.descripcion,
                    material_utilizado = detalle_procedimiento.material_utilizado,
                    status = detalle_procedimiento.status,
                    )

    if str(procedimiento.id_tipo_procedimiento.id) == "21":
        detalle_procedimiento = get_object_or_404(Retencion_Preventiva, id_procedimiento=id)
        data = dict(data,
                
                    tipo_cilindro = detalle_procedimiento.tipo_cilindro,
                    capacidad = detalle_procedimiento.capacidad,
                    serial = detalle_procedimiento.serial,
                    nro_constancia = detalle_procedimiento.nro_constancia_retencion,
                    nombre = detalle_procedimiento.nombre,
                    apellidos = detalle_procedimiento.apellidos,
                    cedula = detalle_procedimiento.cedula,
                    descripcion = detalle_procedimiento.descripcion,
                    material_utilizado = detalle_procedimiento.material_utilizado,
                    status = detalle_procedimiento.status,
                    )

    if str(procedimiento.id_tipo_procedimiento.id) == "22":
        detalle_procedimiento = get_object_or_404(Artificios_Pirotecnicos, id_procedimiento=id)

        data = dict(data,
                   nombre_comercio = detalle_procedimiento.nombre_comercio,
                    rif_comercio = detalle_procedimiento.rif_comerciante,
                    tipo_procedimiento_art = detalle_procedimiento.tipo_procedimiento.tipo,
                )

        if detalle_procedimiento.tipo_procedimiento.id == 1:
            incendio = get_object_or_404(Incendios_Art, id_procedimientos=detalle_procedimiento.id)
            data.update({
                'tipo_incendio': incendio.id_tipo_incendio.tipo_incendio,
                'descripcion': incendio.descripcion,
                'material_utilizado': incendio.material_utilizado,
                'status': incendio.status,
            })

            try:
                if get_object_or_404(Persona_Presente_Art, id_incendio=incendio.id):
                    persona = get_object_or_404(Persona_Presente_Art, id_incendio=incendio.id)
                    data = dict(data,
                                person = True,
                                nombre = persona.nombre,
                                apellidos = persona.apellidos,
                                cedula = persona.cedula,
                                edad = persona.edad,
                                )
            except: 
                pass

            if incendio.id_tipo_incendio.tipo_incendio == "Incendio de Vehiculo":
                vehiculo = get_object_or_404(Detalles_Vehiculos_Art, id_vehiculo=incendio.id)
                data = dict(data,
                            carro = True,
                            modelo = vehiculo.modelo,
                            marca = vehiculo.marca,
                            color = vehiculo.color,
                            año = vehiculo.año,
                            placas = vehiculo.placas,
                            )

        if detalle_procedimiento.tipo_procedimiento.id == 2:
            lesionado = get_object_or_404(Lesionados_Art, id_accidente=detalle_procedimiento.id)
            data.update({
                'nombres': lesionado.nombres,
                'apellidos': lesionado.apellidos,
                'cedula': lesionado.cedula,
                'edad': lesionado.edad,
                'sexo': lesionado.sexo,
                'idx': lesionado.idx,
                'descripcion': lesionado.descripcion,
                'status': lesionado.status,
            })

        if detalle_procedimiento.tipo_procedimiento.id == 3:
            fallecido = get_object_or_404(Fallecidos_Art, id_procedimiento=detalle_procedimiento.id)
            data.update({
                'motivo_fallecimiento': fallecido.motivo_fallecimiento,
                'nombres': fallecido.nombres,
                'apellidos': fallecido.apellidos,
                'cedula': fallecido.cedula,
                'edad': fallecido.edad,
                'sexo': fallecido.sexo,
                'descripcion': fallecido.descripcion,
                'material_utilizado': fallecido.material_utilizado,
                'status': fallecido.status,
            })

    if str(procedimiento.id_tipo_procedimiento.id) == "23":
        detalle_procedimiento = get_object_or_404(Inspeccion_Establecimiento_Art, id_proc_artificio=id)
        data = dict(data,
                    nombre_comercio = detalle_procedimiento.nombre_comercio,
                    rif_comercio = detalle_procedimiento.rif_comercio,
                    encargado_nombre = detalle_procedimiento.encargado_nombre,
                    encargado_apellidos = detalle_procedimiento.encargado_apellidos,
                    encargado_cedula = detalle_procedimiento.encargado_cedula,
                    encargado_sexo = detalle_procedimiento.encargado_sexo,
                    descripcion = detalle_procedimiento.descripcion,
                    material_utilizado = detalle_procedimiento.material_utilizado,
                    status = detalle_procedimiento.status,
                    )

    if str(procedimiento.id_tipo_procedimiento.id) == "24":
        detalles = get_object_or_404(Valoracion_Medica, id_procedimientos = id)

        data = dict(data,
                    nombres = detalles.nombre,
                    apellidos = detalles.apellido,
                    cedula = detalles.cedula,
                    edad = detalles.edad,
                    sexo = detalles.sexo,
                    telefono = detalles.telefono,
                    descripcion = detalles.descripcion,
                    material_utilizado = detalles.material_utilizado,
                    status = detalles.status,
                    )
        
    if str(procedimiento.id_tipo_procedimiento.id) == "25":
        detalles = get_object_or_404(Jornada_Medica, id_procedimientos = id)

        data = dict(data,
                    nombre_jornada = detalles.nombre_jornada,
                    cant_personas = detalles.cant_personas_aten,
                    descripcion = detalles.descripcion,
                    material_utilizado = detalles.material_utilizado,
                    status = detalles.status,
                    )

    if str(procedimiento.id_tipo_procedimiento.id) == "26" or str(procedimiento.id_tipo_procedimiento.id) == "27" or str(procedimiento.id_tipo_procedimiento.id) == "28" or str(procedimiento.id_tipo_procedimiento.id) == "29" or str(procedimiento.id_tipo_procedimiento.id) == "30" or str(procedimiento.id_tipo_procedimiento.id) == "31" or str(procedimiento.id_tipo_procedimiento.id) == "32" or str(procedimiento.id_tipo_procedimiento.id) == "33" or str(procedimiento.id_tipo_procedimiento.id) == "34":
        detalles = get_object_or_404(Detalles_Enfermeria, id_procedimientos = id)

        data = dict(data,
                    nombres = detalles.nombre,
                    apellidos = detalles.apellido,
                    cedula = detalles.cedula,
                    edad = detalles.edad,
                    sexo = detalles.sexo,
                    telefono = detalles.telefono,
                    descripcion = detalles.descripcion,
                    material_utilizado = detalles.material_utilizado,
                    status = detalles.status,
                    )
        
    if str(procedimiento.id_tipo_procedimiento.id) == "35" or str(procedimiento.id_tipo_procedimiento.id) == "36" or str(procedimiento.id_tipo_procedimiento.id) == "37" or str(procedimiento.id_tipo_procedimiento.id) == "38" or str(procedimiento.id_tipo_procedimiento.id) == "39" or str(procedimiento.id_tipo_procedimiento.id) == "40" or str(procedimiento.id_tipo_procedimiento.id) == "41":
        detalles = get_object_or_404(Procedimientos_Psicologia, id_procedimientos = id)

        data = dict(data,
                    nombres = detalles.nombre,
                    apellidos = detalles.apellido,
                    cedula = detalles.cedula,
                    edad = detalles.edad,
                    sexo = detalles.sexo,
                    descripcion = detalles.descripcion,
                    material_utilizado = detalles.material_utilizado,
                    status = detalles.status,
                    )
        
    if str(procedimiento.id_tipo_procedimiento.id) == "45":
        if procedimiento.dependencia == "Capacitacion":
            detalles = get_object_or_404(Procedimientos_Capacitacion, id_procedimientos = id)

            data = dict(data,
                    tipo_capacitacion = detalles.tipo_capacitacion,
                    tipo_clasificacion = detalles.tipo_clasificacion,
                    personas_beneficiadas = detalles.personas_beneficiadas,
                    descripcion = detalles.descripcion,
                    material_utilizado = detalles.material_utilizado,
                    status = detalles.status
                    )
        
        if procedimiento.dependencia == "Frente Preventivo":
            detalles = get_object_or_404(Procedimientos_Frente_Preventivo, id_procedimientos = id)

            data = dict(data,
                    nombre_actividad = detalles.nombre_actividad,
                    estrategia = detalles.estrategia,
                    personas_beneficiadas = detalles.personas_beneficiadas,
                    descripcion = detalles.descripcion,
                    material_utilizado = detalles.material_utilizado,
                    status = detalles.status
                    )
        
    return JsonResponse(data)