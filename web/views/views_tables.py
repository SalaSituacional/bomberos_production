from django.shortcuts import render, redirect
from django.http import HttpResponse
from ..models import *
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from datetime import datetime
import json
from datetime import timedelta
from django.utils.timezone import make_aware
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


# Funciones Auxiliares
def contar_procedimientos_hoy():
    hoy_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    hoy_fin = hoy_inicio + timedelta(days=1)
    
    conteo_hoy = Procedimientos.objects.filter(
        id_division__id__in=range(1, 6),  # Divisiones 1-6
        fecha__gte=hoy_inicio,
        fecha__lt=hoy_fin
    ).count()
    
    return conteo_hoy



# Funciones Principales
def View_Operaciones(request):
    user = request.session.get('user')
    if not user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
        return redirect('/')

    conteo_total = Procedimientos.objects.filter(id_division=2)
    conteo_total = conteo_total.count()

    # Obtener la fecha enviada desde el frontend
    fecha_carga = request.GET.get('fecha', None)
    if fecha_carga:
        fecha_inicio = datetime.strptime(fecha_carga, "%Y-%m-%d")
        fecha_fin = fecha_inicio + timedelta(days=1)
    else:
        # Si no se pasa la fecha, por defecto cargar los procedimientos del día actual
        fecha_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_inicio + timedelta(days=1)

    # Filtrar procedimientos según la fecha
    datos_combined = Procedimientos.objects.filter(
        id_division=2,
        fecha__gte=fecha_inicio,
        fecha__lt=fecha_fin
    ).order_by('-fecha')

    # Conteo total
    total = datos_combined.count()

    # Manejo de eliminación por solicitud POST
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id = data.get('id')
            procedimiento = get_object_or_404(Procedimientos, id=id)
            procedimiento.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Verificar si es una solicitud AJAX
        # Serializa los datos en un formato compatible con JSON
        procedimientos = list(datos_combined.values(
            'id', 
            'id_division__division',  # Nombre de la division relacionada
            'tipo_servicio', 
            'id_solicitante__nombres',  # Nombre del solicitante relacionado
            'id_solicitante__apellidos',  # Nombre del solicitante relacionado
            'id_solicitante__jerarquia',  # Nombre del solicitante relacionado
            'solicitante_externo', 
            'unidad__nombre_unidad',  # Nombre de la unidad relacionada
            'id_jefe_comision__nombres',  # Nombre del jefe de comisión relacionado
            'id_jefe_comision__apellidos',  # Nombre del jefe de comisión relacionado
            'id_jefe_comision__jerarquia',  # Nombre del jefe de comisión relacionado
            'dependencia', 
            'efectivos_enviados', 
            'id_municipio__municipio',  # Nombre del municipio relacionado
            'id_parroquia__parroquia',  # Nombre de la parroquia relacionada
            'fecha', 
            'hora', 
            'direccion', 
            'id_tipo_procedimiento__tipo_procedimiento'  # Tipo de procedimiento relacionado
        ))

        # Responder con los datos en formato JSON y la fecha para la siguiente carga
        return JsonResponse({'procedimientos': procedimientos, 'total': total, 'fecha': fecha_inicio.strftime("%Y-%m-%d")})
    
    # Renderizar la página normal
    return render(request, "Divisiones/operaciones.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos_combined,
        "total": total,
        "contador_total": conteo_total,
        "fecha_actual": fecha_inicio.strftime("%Y-%m-%d"),  # El día actual
    })

def View_Rescate(request):
    user = request.session.get('user')
    if not user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
        return redirect('/')

    conteo_total = Procedimientos.objects.filter(id_division=1)
    conteo_total = conteo_total.count()

    # Obtener la fecha enviada desde el frontend
    fecha_carga = request.GET.get('fecha', None)
    if fecha_carga:
        fecha_inicio = datetime.strptime(fecha_carga, "%Y-%m-%d")
        fecha_fin = fecha_inicio + timedelta(days=1)
    else:
        # Si no se pasa la fecha, por defecto cargar los procedimientos del día actual
        fecha_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_inicio + timedelta(days=1)

    # Filtrar procedimientos según la fecha
    datos_combined = Procedimientos.objects.filter(
        id_division=1,
        fecha__gte=fecha_inicio,
        fecha__lt=fecha_fin
    ).order_by('-fecha')

    # Conteo total
    total = datos_combined.count()

    # Manejo de eliminación por solicitud POST
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id = data.get('id')
            procedimiento = get_object_or_404(Procedimientos, id=id)
            procedimiento.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Verificar si es una solicitud AJAX
        # Serializa los datos en un formato compatible con JSON
        procedimientos = list(datos_combined.values(
            'id', 
            'id_division__division',  # Nombre de la division relacionada
            'tipo_servicio', 
            'id_solicitante__nombres',  # Nombre del solicitante relacionado
            'id_solicitante__apellidos',  # Nombre del solicitante relacionado
            'id_solicitante__jerarquia',  # Nombre del solicitante relacionado
            'solicitante_externo', 
            'unidad__nombre_unidad',  # Nombre de la unidad relacionada
            'id_jefe_comision__nombres',  # Nombre del jefe de comisión relacionado
            'id_jefe_comision__apellidos',  # Nombre del jefe de comisión relacionado
            'id_jefe_comision__jerarquia',  # Nombre del jefe de comisión relacionado
            'dependencia', 
            'efectivos_enviados', 
            'id_municipio__municipio',  # Nombre del municipio relacionado
            'id_parroquia__parroquia',  # Nombre de la parroquia relacionada
            'fecha', 
            'hora', 
            'direccion', 
            'id_tipo_procedimiento__tipo_procedimiento'  # Tipo de procedimiento relacionado
        ))

        # Responder con los datos en formato JSON y la fecha para la siguiente carga
        return JsonResponse({'procedimientos': procedimientos, 'total': total, 'fecha': fecha_inicio.strftime("%Y-%m-%d")})
    
    # Renderizar la página normal
    return render(request, "Divisiones/rescate.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos_combined,
        "total": total,
        "contador_total": conteo_total,
        "fecha_actual": fecha_inicio.strftime("%Y-%m-%d"),  # El día actual
    })

def View_Prevencion(request):
    user = request.session.get('user')
    if not user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
        return redirect('/')

    conteo_total = Procedimientos.objects.filter(id_division=3)
    conteo_total = conteo_total.count()

    # Obtener la fecha enviada desde el frontend
    fecha_carga = request.GET.get('fecha', None)
    if fecha_carga:
        fecha_inicio = datetime.strptime(fecha_carga, "%Y-%m-%d")
        fecha_fin = fecha_inicio + timedelta(days=1)
    else:
        # Si no se pasa la fecha, por defecto cargar los procedimientos del día actual
        fecha_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_inicio + timedelta(days=1)

    # Filtrar procedimientos según la fecha
    datos_combined = Procedimientos.objects.filter(
        id_division=3,
        fecha__gte=fecha_inicio,
        fecha__lt=fecha_fin
    ).order_by('-fecha')

    # Conteo total
    total = datos_combined.count()

    # Manejo de eliminación por solicitud POST
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id = data.get('id')
            procedimiento = get_object_or_404(Procedimientos, id=id)
            procedimiento.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Verificar si es una solicitud AJAX
        # Serializa los datos en un formato compatible con JSON
        procedimientos = list(datos_combined.values(
            'id', 
            'id_division__division',  # Nombre de la division relacionada
            'tipo_servicio', 
            'id_solicitante__nombres',  # Nombre del solicitante relacionado
            'id_solicitante__apellidos',  # Nombre del solicitante relacionado
            'id_solicitante__jerarquia',  # Nombre del solicitante relacionado
            'solicitante_externo', 
            'unidad__nombre_unidad',  # Nombre de la unidad relacionada
            'id_jefe_comision__nombres',  # Nombre del jefe de comisión relacionado
            'id_jefe_comision__apellidos',  # Nombre del jefe de comisión relacionado
            'id_jefe_comision__jerarquia',  # Nombre del jefe de comisión relacionado
            'dependencia', 
            'efectivos_enviados', 
            'id_municipio__municipio',  # Nombre del municipio relacionado
            'id_parroquia__parroquia',  # Nombre de la parroquia relacionada
            'fecha', 
            'hora', 
            'direccion', 
            'id_tipo_procedimiento__tipo_procedimiento'  # Tipo de procedimiento relacionado
        ))

        # Responder con los datos en formato JSON y la fecha para la siguiente carga
        return JsonResponse({'procedimientos': procedimientos, 'total': total, 'fecha': fecha_inicio.strftime("%Y-%m-%d")})
    
    # Renderizar la página normal
    return render(request, "Divisiones/prevencion.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos_combined,
        "total": total,
        "contador_total": conteo_total,
        "fecha_actual": fecha_inicio.strftime("%Y-%m-%d"),  # El día actual
    })

def View_grumae(request):
    user = request.session.get('user')
    if not user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
        return redirect('/')

    conteo_total = Procedimientos.objects.filter(id_division=4)
    conteo_total = conteo_total.count()

    # Obtener la fecha enviada desde el frontend
    fecha_carga = request.GET.get('fecha', None)
    if fecha_carga:
        fecha_inicio = datetime.strptime(fecha_carga, "%Y-%m-%d")
        fecha_fin = fecha_inicio + timedelta(days=1)
    else:
        # Si no se pasa la fecha, por defecto cargar los procedimientos del día actual
        fecha_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_inicio + timedelta(days=1)


    # Filtrar procedimientos según la fecha
    datos_combined = Procedimientos.objects.filter(
        id_division=4,
        fecha__gte=fecha_inicio,
        fecha__lt=fecha_fin
    ).order_by('-fecha')

    # Conteo total
    total = datos_combined.count()

    # Manejo de eliminación por solicitud POST
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id = data.get('id')
            procedimiento = get_object_or_404(Procedimientos, id=id)
            procedimiento.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Verificar si es una solicitud AJAX
        # Serializa los datos en un formato compatible con JSON
        procedimientos = list(datos_combined.values(
            'id', 
            'id_division__division',  # Nombre de la division relacionada
            'tipo_servicio', 
            'id_solicitante__nombres',  # Nombre del solicitante relacionado
            'id_solicitante__apellidos',  # Nombre del solicitante relacionado
            'id_solicitante__jerarquia',  # Nombre del solicitante relacionado
            'solicitante_externo', 
            'unidad__nombre_unidad',  # Nombre de la unidad relacionada
            'id_jefe_comision__nombres',  # Nombre del jefe de comisión relacionado
            'id_jefe_comision__apellidos',  # Nombre del jefe de comisión relacionado
            'id_jefe_comision__jerarquia',  # Nombre del jefe de comisión relacionado
            'dependencia', 
            'efectivos_enviados', 
            'id_municipio__municipio',  # Nombre del municipio relacionado
            'id_parroquia__parroquia',  # Nombre de la parroquia relacionada
            'fecha', 
            'hora', 
            'direccion', 
            'id_tipo_procedimiento__tipo_procedimiento'  # Tipo de procedimiento relacionado
        ))

        # Responder con los datos en formato JSON y la fecha para la siguiente carga
        return JsonResponse({'procedimientos': procedimientos, 'total': total, 'fecha': fecha_inicio.strftime("%Y-%m-%d")})
    
    # Renderizar la página normal
    return render(request, "Divisiones/grumae.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos_combined,
        "total": total,
        "contador_total": conteo_total,
        "fecha_actual": fecha_inicio.strftime("%Y-%m-%d"),  # El día actual
    })

def View_prehospitalaria(request):
    user = request.session.get('user')
    if not user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
        return redirect('/')

    conteo_total = Procedimientos.objects.filter(id_division=5)
    conteo_total = conteo_total.count()

    # Obtener la fecha enviada desde el frontend
    fecha_carga = request.GET.get('fecha', None)
    if fecha_carga:
        fecha_inicio = datetime.strptime(fecha_carga, "%Y-%m-%d")
        fecha_fin = fecha_inicio + timedelta(days=1)
    else:
        # Si no se pasa la fecha, por defecto cargar los procedimientos del día actual
        fecha_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_inicio + timedelta(days=1)

    # Filtrar procedimientos según la fecha
    datos_combined = Procedimientos.objects.filter(
        id_division=5,
        fecha__gte=fecha_inicio,
        fecha__lt=fecha_fin
    ).order_by('-fecha')

    # Conteo total
    total = datos_combined.count()

    # Manejo de eliminación por solicitud POST
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id = data.get('id')
            procedimiento = get_object_or_404(Procedimientos, id=id)
            procedimiento.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Verificar si es una solicitud AJAX
        # Serializa los datos en un formato compatible con JSON
        procedimientos = list(datos_combined.values(
            'id', 
            'id_division__division',  # Nombre de la division relacionada
            'tipo_servicio', 
            'id_solicitante__nombres',  # Nombre del solicitante relacionado
            'id_solicitante__apellidos',  # Nombre del solicitante relacionado
            'id_solicitante__jerarquia',  # Nombre del solicitante relacionado
            'solicitante_externo', 
            'unidad__nombre_unidad',  # Nombre de la unidad relacionada
            'id_jefe_comision__nombres',  # Nombre del jefe de comisión relacionado
            'id_jefe_comision__apellidos',  # Nombre del jefe de comisión relacionado
            'id_jefe_comision__jerarquia',  # Nombre del jefe de comisión relacionado
            'dependencia', 
            'efectivos_enviados', 
            'id_municipio__municipio',  # Nombre del municipio relacionado
            'id_parroquia__parroquia',  # Nombre de la parroquia relacionada
            'fecha', 
            'hora', 
            'direccion', 
            'id_tipo_procedimiento__tipo_procedimiento'  # Tipo de procedimiento relacionado
        ))

        # Responder con los datos en formato JSON y la fecha para la siguiente carga
        return JsonResponse({'procedimientos': procedimientos, 'total': total, 'fecha': fecha_inicio.strftime("%Y-%m-%d")})
    
    # Renderizar la página normal
    return render(request, "Divisiones/prehospitalaria.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos_combined,
        "total": total,
        "contador_total": conteo_total,
        "fecha_actual": fecha_inicio.strftime("%Y-%m-%d"),  # El día actual
    })

def View_capacitacion(request):
    user = request.session.get('user')
    if not user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
        return redirect('/')

    conteo_total = Procedimientos.objects.filter(id_division=9)
    conteo_total = conteo_total.count()

    # Obtener la fecha enviada desde el frontend
    fecha_carga = request.GET.get('fecha', None)
    if fecha_carga:
        fecha_inicio = datetime.strptime(fecha_carga, "%Y-%m-%d")
        fecha_fin = fecha_inicio + timedelta(days=1)
    else:
        # Si no se pasa la fecha, por defecto cargar los procedimientos del día actual
        fecha_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_inicio + timedelta(days=1)

    # Filtrar procedimientos según la fecha
    datos_combined = Procedimientos.objects.filter(
        id_division=9,
        fecha__gte=fecha_inicio,
        fecha__lt=fecha_fin
    ).order_by('-fecha')

    # Conteo total
    total = datos_combined.count()

    # Manejo de eliminación por solicitud POST
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id = data.get('id')
            procedimiento = get_object_or_404(Procedimientos, id=id)
            procedimiento.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Verificar si es una solicitud AJAX
        # Serializa los datos en un formato compatible con JSON
        procedimientos = list(datos_combined.values(
            'id', 
            'id_division__division',  # Nombre de la division relacionada
            'tipo_servicio', 
            'id_solicitante__nombres',  # Nombre del solicitante relacionado
            'id_solicitante__apellidos',  # Nombre del solicitante relacionado
            'id_solicitante__jerarquia',  # Nombre del solicitante relacionado
            'solicitante_externo', 
            'unidad__nombre_unidad',  # Nombre de la unidad relacionada
            'id_jefe_comision__nombres',  # Nombre del jefe de comisión relacionado
            'id_jefe_comision__apellidos',  # Nombre del jefe de comisión relacionado
            'id_jefe_comision__jerarquia',  # Nombre del jefe de comisión relacionado
            'dependencia', 
            'efectivos_enviados', 
            'id_municipio__municipio',  # Nombre del municipio relacionado
            'id_parroquia__parroquia',  # Nombre de la parroquia relacionada
            'fecha', 
            'hora', 
            'direccion', 
            'id_tipo_procedimiento__tipo_procedimiento'  # Tipo de procedimiento relacionado
        ))

        # Responder con los datos en formato JSON y la fecha para la siguiente carga
        return JsonResponse({'procedimientos': procedimientos, 'total': total, 'fecha': fecha_inicio.strftime("%Y-%m-%d")})
    
    # Renderizar la página normal
    return render(request, "Divisiones/capacitacion.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos_combined,
        "total": total,
        "contador_total": conteo_total,
        "fecha_actual": fecha_inicio.strftime("%Y-%m-%d"),  # El día actual
    })

def View_enfermeria(request):
    user = request.session.get('user')
    if not user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
        return redirect('/')

    conteo_total = Procedimientos.objects.filter(id_division=6)
    conteo_total = conteo_total.count()

    # Obtener la fecha enviada desde el frontend
    fecha_carga = request.GET.get('fecha', None)
    if fecha_carga:
        fecha_inicio = datetime.strptime(fecha_carga, "%Y-%m-%d")
        fecha_fin = fecha_inicio + timedelta(days=1)
    else:
        # Si no se pasa la fecha, por defecto cargar los procedimientos del día actual
        fecha_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_inicio + timedelta(days=1)

    # Filtrar procedimientos según la fecha
    datos_combined = Procedimientos.objects.filter(
        id_division=6,
        fecha__gte=fecha_inicio,
        fecha__lt=fecha_fin
    ).order_by('-fecha')

    # Conteo total
    total = datos_combined.count()

    # Manejo de eliminación por solicitud POST
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id = data.get('id')
            procedimiento = get_object_or_404(Procedimientos, id=id)
            procedimiento.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Verificar si es una solicitud AJAX
        # Serializa los datos en un formato compatible con JSON
        procedimientos = list(datos_combined.values(
            'id', 
            'id_division__division',  # Nombre de la division relacionada
            'id_solicitante__nombres',  # Nombre del solicitante relacionado
            'id_solicitante__apellidos',  # Nombre del solicitante relacionado
            'id_solicitante__jerarquia',  # Nombre del solicitante relacionado
            'solicitante_externo', 
            'unidad__nombre_unidad',  # Nombre de la unidad relacionada
            'id_jefe_comision__nombres',  # Nombre del jefe de comisión relacionado
            'id_jefe_comision__apellidos',  # Nombre del jefe de comisión relacionado
            'id_jefe_comision__jerarquia',  # Nombre del jefe de comisión relacionado
            'dependencia', 
            'efectivos_enviados', 
            'id_municipio__municipio',  # Nombre del municipio relacionado
            'id_parroquia__parroquia',  # Nombre de la parroquia relacionada
            'fecha', 
            'hora', 
            'direccion', 
            'id_tipo_procedimiento__tipo_procedimiento'  # Tipo de procedimiento relacionado
        ))

        # Responder con los datos en formato JSON y la fecha para la siguiente carga
        return JsonResponse({'procedimientos': procedimientos, 'total': total, 'fecha': fecha_inicio.strftime("%Y-%m-%d")})
    
    # Renderizar la página normal
    return render(request, "Divisiones/enfermeria.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos_combined,
        "total": total,
        "contador_total": conteo_total,
        "fecha_actual": fecha_inicio.strftime("%Y-%m-%d"),  # El día actual
    })

def View_serviciosmedicos(request):
    user = request.session.get('user')
    if not user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
        return redirect('/')

    conteo_total = Procedimientos.objects.filter(id_division=7).count()

    # Obtener la fecha enviada desde el frontend
    fecha_carga = request.GET.get('fecha', None)
    if fecha_carga:
        fecha_inicio = datetime.strptime(fecha_carga, "%Y-%m-%d")
        fecha_fin = fecha_inicio + timedelta(days=1)
    else:
        # Si no se pasa la fecha, por defecto cargar los procedimientos del día actual
        fecha_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_inicio + timedelta(days=1)

    # Filtrar procedimientos según la fecha
    datos_combined = Procedimientos.objects.filter(
        id_division=7,
        fecha__gte=fecha_inicio,
        fecha__lt=fecha_fin
    ).order_by('-fecha')

    # Conteo total
    total = datos_combined.count()

    # Manejo de eliminación por solicitud POST
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id = data.get('id')
            procedimiento = get_object_or_404(Procedimientos, id=id)
            procedimiento.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Verificar si es una solicitud AJAX
        # Serializa los datos en un formato compatible con JSON
        procedimientos = list(datos_combined.values(
            'id', 
            'id_division__division',  # Nombre de la division relacionada
            'tipo_servicio', 
            'id_solicitante__nombres',  # Nombre del solicitante relacionado
            'id_solicitante__apellidos',  # Nombre del solicitante relacionado
            'id_solicitante__jerarquia',  # Nombre del solicitante relacionado
            'solicitante_externo', 
            'unidad__nombre_unidad',  # Nombre de la unidad relacionada
            'id_jefe_comision__nombres',  # Nombre del jefe de comisión relacionado
            'id_jefe_comision__apellidos',  # Nombre del jefe de comisión relacionado
            'id_jefe_comision__jerarquia',  # Nombre del jefe de comisión relacionado
            'dependencia', 
            'efectivos_enviados', 
            'id_municipio__municipio',  # Nombre del municipio relacionado
            'id_parroquia__parroquia',  # Nombre de la parroquia relacionada
            'fecha', 
            'hora', 
            'direccion', 
            'id_tipo_procedimiento__tipo_procedimiento'  # Tipo de procedimiento relacionado
        ))

        # Responder con los datos en formato JSON y la fecha para la siguiente carga
        return JsonResponse({'procedimientos': procedimientos, 'total': total, 'fecha': fecha_inicio.strftime("%Y-%m-%d")})
    
    # Renderizar la página normal
    return render(request, "Divisiones/serviciosmedicos.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos_combined,
        "total": total,
        "contador_total": conteo_total,
        "fecha_actual": fecha_inicio.strftime("%Y-%m-%d"),  # El día actual
    })

def View_psicologia(request):
    user = request.session.get('user')
    if not user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
        return redirect('/')

    conteo_total = Procedimientos.objects.filter(id_division=8)
    conteo_total = conteo_total.count()

    # Obtener la fecha enviada desde el frontend
    fecha_carga = request.GET.get('fecha', None)
    if fecha_carga:
        fecha_inicio = datetime.strptime(fecha_carga, "%Y-%m-%d")
        fecha_fin = fecha_inicio + timedelta(days=1)
    else:
        # Si no se pasa la fecha, por defecto cargar los procedimientos del día actual
        fecha_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_inicio + timedelta(days=1)

    # Filtrar procedimientos según la fecha
    datos_combined = Procedimientos.objects.filter(
        id_division=8,
        fecha__gte=fecha_inicio,
        fecha__lt=fecha_fin
    ).order_by('-fecha')

    # Conteo total
    total = datos_combined.count()

    # Manejo de eliminación por solicitud POST
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id = data.get('id')
            procedimiento = get_object_or_404(Procedimientos, id=id)
            procedimiento.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Verificar si es una solicitud AJAX
        # Serializa los datos en un formato compatible con JSON
        procedimientos = list(datos_combined.values(
            'id', 
            'id_division__division',  # Nombre de la division relacionada
            'tipo_servicio', 
            'id_solicitante__nombres',  # Nombre del solicitante relacionado
            'id_solicitante__apellidos',  # Nombre del solicitante relacionado
            'id_solicitante__jerarquia',  # Nombre del solicitante relacionado
            'solicitante_externo', 
            'id_municipio__municipio',  # Nombre del municipio relacionado
            'id_parroquia__parroquia',  # Nombre de la parroquia relacionada
            'fecha', 
            'hora', 
            'direccion', 
            'id_tipo_procedimiento__tipo_procedimiento'  # Tipo de procedimiento relacionado
        ))
        # Responder con los datos en formato JSON y la fecha para la siguiente carga
        return JsonResponse({'procedimientos': procedimientos, 'total': total, 'fecha': fecha_inicio.strftime("%Y-%m-%d")})


    # Renderizar la página normal
    return render(request, "Divisiones/psicologia.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos_combined,
        "total": total,
        "contador_total": conteo_total,
        "fecha_actual": fecha_inicio.strftime("%Y-%m-%d"),  # El día actual
    })

def tabla_general(request):
    user = request.session.get('user')
    if not user:
        return redirect('/')

    divisiones = range(1, 6)

    # Obtener parámetros de filtrado
    parroquia = request.GET.get('parroquia', '')
    procedimiento = request.GET.get('procedimiento', '')
    trimestre = request.GET.get('trimestre', '')

    # Consulta base
    datos_combined = Procedimientos.objects.filter(id_division__in=divisiones)

    # Aplicar filtros
    if parroquia:
        datos_combined = datos_combined.filter(
            Q(id_parroquia__id=parroquia)
        )

    if procedimiento:
        datos_combined = datos_combined.filter(
            Q(id_tipo_procedimiento__id=procedimiento)
        )

    if trimestre:
        trimestre = int(trimestre)
        # Definir meses por trimestre
        if trimestre == 1:  # Ene-Mar
            meses = [1, 2, 3]
        elif trimestre == 2:  # Abr-Jun
            meses = [4, 5, 6]
        elif trimestre == 3:  # Jul-Sep
            meses = [7, 8, 9]
        elif trimestre == 4:  # Oct-Dic
            meses = [10, 11, 12]
        
        datos_combined = datos_combined.filter(fecha__month__in=meses)

    # Ordenar y paginar
    datos_combined = datos_combined.order_by('-fecha')
    conteo_total = Procedimientos.objects.filter(id_division__in=divisiones).count()
    
    # Configuración de paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(datos_combined, 10)  # 15 elementos por página

    try:
        datos_paginados = paginator.page(page)
    except PageNotAnInteger:
        datos_paginados = paginator.page(1)
    except EmptyPage:
        datos_paginados = paginator.page(paginator.num_pages)

    # Manejo de eliminación por solicitud POST
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            id = data.get('id')
            procedimiento = get_object_or_404(Procedimientos, id=id)
            procedimiento.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    # Renderizar la página
    return render(request, "tablageneral.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos_paginados,
        "total": contar_procedimientos_hoy(),
        "contador_total": conteo_total,
        "filtro_parroquia": parroquia,
        "filtro_procedimiento": procedimiento,
        "procedimientos_list": Tipos_Procedimientos.objects.filter(id_division__id__in=range(1, 6)).distinct(),
        "parroquias_list": Parroquias.objects.all(),
        "filtro_trimestre": trimestre,
    })