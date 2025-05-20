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