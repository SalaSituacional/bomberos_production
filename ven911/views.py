from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db.models import Case, When
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Max
from django.db.models import Count
from django.utils.timezone import localdate
from django.forms.models import model_to_dict
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Q
from .urls import *
from .forms import *
import json


# Create your views here.

# Vista del dashboard Ven911
@login_required
def ven911(request):
    user = request.session.get('user')
    if not user:
        return redirect('/')
    # Renderizar la página con los datos
    return render(request, "Dashboard_ven911.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
    })
# Vista del formulario con su metodo de guardado
@login_required
def form_services(request):
    user = request.session.get('user')
    if not user:
        return redirect('/')

    if request.method == 'POST':
        form_services = ServicioForm(request.POST)
        if form_services.is_valid():
            try:
                servicio = form_services.save(commit=False)
                
                # Ejemplo: Asignar automáticamente el operador si es necesario
                # if not servicio.operador_de_guardia:
                #     servicio.operador_de_guardia = Personal.objects.get(user_id=user['id'])
                
                servicio.save()
                messages.success(request, 'Servicio registrado correctamente!')
                return redirect('home_911')
            except Exception as e:
                messages.error(request, f'Error al guardar: {str(e)}')
        else:
            messages.error(request, 'Error en el formulario. Revise los datos.')
    else:
        form_services = ServicioForm()

    return render(request, "formulario_servicios.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "formulario_servicios": form_services,
    })


# Vista de informacion de los servicios
@login_required
def view_table_911(request):
    registros = Servicio.objects.all().count()
    user = request.session.get('user')
    if not user:
        return redirect('/')
    # Renderizar la página con los datos
    return render(request, "table_911.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "registros_totales" : registros,
    })

# Api Json para enviar los datos a la tabla del 911

def obtener_servicios_json(request):
    # Calculamos la fecha de hace 7 días atrás desde ahora
    fecha_limite = timezone.now() - timedelta(days=7)
    
    # Filtramos los servicios de los últimos 7 días
    servicios = Servicio.objects.filter(
        fecha__gte=fecha_limite
    ).select_related(
        'tipo_servicio',
        'operador_de_guardia',
        'municipio',
        'parroquia',
        'unidad',
        'jefe_de_comision'
    ).order_by('-fecha', '-hora')  # Ordenamos por fecha y hora descendente
    
    datos_servicios = []
    for servicio in servicios:
        datos_servicios.append({
            'id': servicio.id,
            'tipo_servicio': {
                'id': servicio.tipo_servicio.id if servicio.tipo_servicio else None,
                'nombre': servicio.tipo_servicio.nombre if servicio.tipo_servicio else None
            },
            'operador_de_guardia': {
                'id': servicio.operador_de_guardia.id if servicio.operador_de_guardia else None,
                'nombre_completo': f"{servicio.operador_de_guardia.nombres} {servicio.operador_de_guardia.apellidos} - {servicio.operador_de_guardia.jerarquia}" if servicio.operador_de_guardia else None
            },
            'fecha': servicio.fecha.strftime('%Y-%m-%d') if servicio.fecha else None,
            'hora': servicio.hora.strftime('%H:%M') if servicio.hora else None,
            'lugar': servicio.lugar,
            'municipio': {
                'id': servicio.municipio.id if servicio.municipio else None,
                'nombre': str(servicio.municipio) if servicio.municipio else None
            },
            'parroquia': {
                'id': servicio.parroquia.id if servicio.parroquia else None,
                'nombre': str(servicio.parroquia) if servicio.parroquia else None
            },
            'unidad': {
                'id': servicio.unidad.id if servicio.unidad else None,
                'nombre': str(servicio.unidad) if servicio.unidad else None
            },
            'jefe_de_comision': {
                'id': servicio.jefe_de_comision.id if servicio.jefe_de_comision else None,
                'nombre_completo': f"{servicio.jefe_de_comision.nombres} {servicio.jefe_de_comision.apellidos} - {servicio.jefe_de_comision.jerarquia}" if servicio.jefe_de_comision else None
            },
            'descripcion': servicio.descripcion
        })
    
    return JsonResponse({'servicios': datos_servicios}, safe=False)

# api para elmininar servicio
@csrf_exempt  # Solo si no usas CSRF en APIs (o configura CSRF correctamente)
def eliminar_servicio(request, id):
    if request.method == 'DELETE':
        try:
            servicio = Servicio.objects.get(id=id)
            servicio.delete()
            return JsonResponse({"status": "success"}, status=200)
        except Servicio.DoesNotExist:
            return JsonResponse({"error": "Servicio no encontrado"}, status=404)
    return JsonResponse({"error": "Método no permitido"}, status=405)


# api para el conteo de servicios

# def api_conteo_servicios(request):
#     # Obtener parámetro de semana si existe
#     week_param = request.GET.get('week')
    
#     # Inicializar el filtro como Q() que no filtra nada
#     filtro_servicios = Q()
    
#     # Aplicar filtro de semana solo si se proporciona
#     if week_param:
#         try:
#             # Parsear el valor de entrada type="week" (formato YYYY-WWW)
#             year, week = map(int, week_param.split('-W'))
#             start_date = timezone.datetime.strptime(f'{year}-{week}-1', "%Y-%W-%w").date()
#             end_date = start_date + timezone.timedelta(days=6)
            
#             # Crear filtro para el rango de fechas
#             filtro_servicios = Q(servicio__fecha__gte=start_date) & Q(servicio__fecha__lte=end_date)
#         except (ValueError, AttributeError):
#             # Si hay error en el formato, ignorar el filtro (mostrar todo)
#             pass
    
#     # Consulta que funciona tanto con filtro como sin filtro
#     datos = TipoServicio.objects \
#         .filter(filtro_servicios) \
#         .order_by('nombre') \
#         .annotate(total=Count('servicio')) \
#         .values('nombre', 'total')
    
#     conteo = {item['nombre']: item['total'] for item in datos}
#     return JsonResponse(conteo)


def api_conteo_servicios(request):
    # Consulta base para tipos de servicio
    tipos_servicio = TipoServicio.objects.all().order_by('nombre')
    
    # Inicializamos sin filtro (mostrará todos los servicios)
    filtro_servicios = Q()
    
    # Verificamos si hay filtro por semana (solo aplicamos filtro si existe y es válido)
    if 'week' in request.GET and request.GET['week']:
        try:
            year, week = map(int, request.GET['week'].split('-W'))
            start_date = timezone.datetime.strptime(f'{year}-{week}-1', "%Y-%W-%w").date()
            end_date = start_date + timezone.timedelta(days=6)
            
            # Creamos el filtro para el rango de fechas seleccionado
            filtro_servicios = Q(servicio__fecha__range=(start_date, end_date))
        except:
            # Si hay error en el formato, mantenemos sin filtro (muestra todo)
            pass
    
    # Aplicamos el conteo condicional
    datos = tipos_servicio.annotate(
        total=Count('servicio', filter=filtro_servicios)
    ).values('nombre', 'total')
    
    # Convertimos a diccionario
    conteo = {item['nombre']: item['total'] for item in datos}
    
    return JsonResponse(conteo)

# api servicios de grafica
def api_servicios_grafico(request):
    # Obtener parámetro de mes
    month_filter = request.GET.get('month')
    
    # Filtrar servicios basados en el mes si se proporciona
    servicios_query = Servicio.objects.all()
    
    if month_filter:
        try:
            # Convertir string 'YYYY-MM' a objeto date
            filter_date = datetime.strptime(month_filter, '%Y-%m').date()
            year, month = filter_date.year, filter_date.month
            
            # Filtrar servicios por año y mes
            servicios_query = servicios_query.filter(
                fecha__year=year,
                fecha__month=month
            )
        except (ValueError, TypeError):
            # Manejar error si el formato de fecha es incorrecto
            pass
    
    # Anotar y contar los tipos de servicio
    datos = TipoServicio.objects.filter(
        servicio__in=servicios_query
    ).annotate(
        total=Count('servicio')
    ).filter(total__gte=1).order_by('-total').values_list('nombre', 'total')

    # Preparar datos para la respuesta
    labels = []
    valores = []
    for nombre, total in datos:
        labels.append(nombre)
        valores.append(total)

    return JsonResponse({
        'labels': labels,
        'data': valores,
        'count': len(labels)
    })