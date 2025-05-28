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
from django.db.models import Count, Q, Sum
from .urls import *
from .forms import *
import json
from django.db.models import Prefetch



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
@never_cache  # Evita que la vista se cachee
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
    registros_totales = Servicio.objects.all().count()
    registros_hoy = Servicio.objects.filter(fecha=localdate()).count()
    # Verificar si el usuario está en la sesión
    user = request.session.get('user')
    if not user:
        return redirect('/')
    # Renderizar la página con los datos
    return render(request, "table_911.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "registros_totales" : registros_totales,
        "registros_hoy" : registros_hoy,
    })


def obtener_servicios_json(request):
    try:
        # Consulta optimizada
        servicios = Servicio.objects.filter(
            fecha__gte=timezone.now() - timedelta(days=1)
        ).select_related('tipo_servicio', 'operador_de_guardia'
        ).order_by('-fecha', '-hora')
        
        # Construcción de datos
        datos_servicios = []
        for s in servicios:
            operador = None
            if s.operador_de_guardia:
                operador = {
                    'id': s.operador_de_guardia.id,
                    'nombre_completo': f"{s.operador_de_guardia.nombres} {s.operador_de_guardia.apellidos}"
                }
                if hasattr(s.operador_de_guardia, 'jerarquia'):
                    operador['nombre_completo'] += f" - {s.operador_de_guardia.jerarquia}"
            
            datos_servicios.append({
                'id': s.id,
                'tipo_servicio': {
                    'id': s.tipo_servicio.id,
                    'nombre': s.tipo_servicio.nombre
                } if s.tipo_servicio else None,
                'cantidad_tipo_servicio': s.cantidad_tipo_servicio or 1,
                'operador_de_guardia': operador,
                'fecha': s.fecha.strftime('%Y-%m-%d') if s.fecha else None,
                'hora': str(s.hora) if s.hora else None,
            })
        
        return JsonResponse({'servicios': datos_servicios}, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


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

def api_conteo_servicios(request):
    tipos_servicio = TipoServicio.objects.all().order_by('nombre')
    filtro_servicios = Q()
    
    # Filtro por rango de fechas
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if fecha_inicio and fecha_fin:
        try:
            start_date = timezone.datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            end_date = timezone.datetime.strptime(fecha_fin, "%Y-%m-%d").date()
            
            # Validar que la fecha inicio <= fecha fin
            if start_date <= end_date:
                filtro_servicios &= Q(servicio__fecha__range=(start_date, end_date))
        except ValueError:
            pass  # Si hay error en el formato, ignoramos el filtro
    
    datos = tipos_servicio.annotate(
        total=Sum('servicio__cantidad_tipo_servicio', filter=filtro_servicios)
    ).values('nombre', 'total')
    
    conteo = {item['nombre']: item['total'] or 0 for item in datos}
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
        total=Sum('servicio__cantidad_tipo_servicio', filter=Q(servicio__fecha__isnull=False)
        )
    ).values_list('nombre', 'total').order_by('nombre')

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