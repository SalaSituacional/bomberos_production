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

def contar_procedimientos_hoy_division(division):
    hoy_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    hoy_fin = hoy_inicio + timedelta(days=1)
    
    conteo_hoy = Procedimientos.objects.filter(
        id_division__id=division,
        fecha__gte=hoy_inicio,
        fecha__lt=hoy_fin
    ).count()
    
    return conteo_hoy

# Tablas
def View_Operaciones(request):
    user = request.session.get('user')
    if not user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
        return redirect('/')

    # Obtener parámetros de filtrado
    parroquia = request.GET.get('parroquia', '')
    procedimiento = request.GET.get('procedimiento', '')
    trimestre = request.GET.get('trimestre', '')

    # Consulta base (filtramos por división 2 - Operaciones)
    datos_combined = Procedimientos.objects.filter(id_division=2)

    # Filtrar por fecha según el rol del usuario
    if user.get('user') == 'Operaciones01':
        # Solo mostrar procedimientos del día actual para usuarios de Operaciones
        hoy = timezone.now().date()
        fecha_inicio = datetime.combine(hoy, datetime.min.time())
        fecha_fin = datetime.combine(hoy, datetime.max.time())
        datos_combined = datos_combined.filter(fecha__range=(fecha_inicio, fecha_fin))
    # Para Admin y Sala Situacional no se aplica filtro de fecha (ven todo)

    # Aplicar filtros adicionales
    if parroquia:
        datos_combined = datos_combined.filter(id_parroquia__id=parroquia)

    if procedimiento:
        datos_combined = datos_combined.filter(id_tipo_procedimiento__id=procedimiento)

    if trimestre:
        trimestre = int(trimestre)
        meses = {
            1: [1, 2, 3],   # Ene-Mar
            2: [4, 5, 6],    # Abr-Jun
            3: [7, 8, 9],    # Jul-Sep
            4: [10, 11, 12]  # Oct-Dic
        }.get(trimestre, [])
        datos_combined = datos_combined.filter(fecha__month__in=meses)

    # Ordenar y contar
    datos_combined = datos_combined.order_by('-fecha')
    conteo_total = Procedimientos.objects.filter(id_division=2).count()

    # Configuración de paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(datos_combined, 10)

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

    return render(request, "Divisiones/operaciones.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos_paginados,
        "total": contar_procedimientos_hoy_division(2),  # Conteo de procedimientos de hoy para la división Operaciones
        "contador_total": conteo_total,
        "filtro_parroquia": parroquia,
        "filtro_procedimiento": procedimiento,
        "filtro_trimestre": trimestre,
        "procedimientos_list": Tipos_Procedimientos.objects.filter(id_division=2).distinct(),
        "parroquias_list": Parroquias.objects.all(),
    })

def View_Rescate(request):
    user = request.session.get('user')
    if not user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
        return redirect('/')

    # Obtener parámetros de filtrado
    parroquia = request.GET.get('parroquia', '')
    procedimiento = request.GET.get('procedimiento', '')
    trimestre = request.GET.get('trimestre', '')

    # Consulta base (filtramos por división 1 - Rescate)
    datos_combined = Procedimientos.objects.filter(id_division=1)

    # Filtrar por fecha según el rol del usuario
    if user.get('user') == 'Rescate03':
        # Solo mostrar procedimientos del día actual para usuarios de Rescate
        hoy = timezone.now().date()
        fecha_inicio = datetime.combine(hoy, datetime.min.time())
        fecha_fin = datetime.combine(hoy, datetime.max.time())
        datos_combined = datos_combined.filter(fecha__range=(fecha_inicio, fecha_fin))
    # Para Admin y Sala Situacional no se aplica filtro de fecha (ven todo)

    # Aplicar filtros adicionales
    if parroquia:
        datos_combined = datos_combined.filter(id_parroquia__id=parroquia)

    if procedimiento:
        datos_combined = datos_combined.filter(id_tipo_procedimiento__id=procedimiento)

    if trimestre:
        trimestre = int(trimestre)
        meses = {
            1: [1, 2, 3],   # Ene-Mar
            2: [4, 5, 6],    # Abr-Jun
            3: [7, 8, 9],    # Jul-Sep
            4: [10, 11, 12]  # Oct-Dic
        }.get(trimestre, [])
        datos_combined = datos_combined.filter(fecha__month__in=meses)

    # Ordenar y contar
    datos_combined = datos_combined.order_by('-fecha')
    conteo_total = Procedimientos.objects.filter(id_division=1).count()

    # Configuración de paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(datos_combined, 10)

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

    # Renderizar la página normal
    return render(request, "Divisiones/rescate.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos_paginados,
        "total": contar_procedimientos_hoy_division(1),  # Conteo de procedimientos de hoy para la división Operaciones
        "contador_total": conteo_total,
        "filtro_parroquia": parroquia,
        "filtro_procedimiento": procedimiento,
        "filtro_trimestre": trimestre,
        "procedimientos_list": Tipos_Procedimientos.objects.filter(id_division=1).distinct(),
        "parroquias_list": Parroquias.objects.all(),
    })

def View_prehospitalaria(request):
    user = request.session.get('user')
    if not user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
        return redirect('/')

    # Obtener parámetros de filtrado
    parroquia = request.GET.get('parroquia', '')
    procedimiento = request.GET.get('procedimiento', '')
    trimestre = request.GET.get('trimestre', '')

    # Consulta base (filtramos por división 5 - Prehospitalaria)
    datos_combined = Procedimientos.objects.filter(id_division=5)

    # Filtrar por fecha según el rol del usuario
    if user.get('user') == 'Prehospitalaria04':
        # Solo mostrar procedimientos del día actual para usuarios de Prehospitalaria
        hoy = timezone.now().date()
        fecha_inicio = datetime.combine(hoy, datetime.min.time())
        fecha_fin = datetime.combine(hoy, datetime.max.time())
        datos_combined = datos_combined.filter(fecha__range=(fecha_inicio, fecha_fin))
    # Para Admin y Sala Situacional no se aplica filtro de fecha (ven todo)

    # Aplicar filtros adicionales
    if parroquia:
        datos_combined = datos_combined.filter(id_parroquia__id=parroquia)

    if procedimiento:
        datos_combined = datos_combined.filter(id_tipo_procedimiento__id=procedimiento)

    if trimestre:
        trimestre = int(trimestre)
        meses = {
            1: [1, 2, 3],   # Ene-Mar
            2: [4, 5, 6],    # Abr-Jun
            3: [7, 8, 9],    # Jul-Sep
            4: [10, 11, 12]  # Oct-Dic
        }.get(trimestre, [])
        datos_combined = datos_combined.filter(fecha__month__in=meses)

    # Ordenar y contar
    datos_combined = datos_combined.order_by('-fecha')
    conteo_total = Procedimientos.objects.filter(id_division=5).count()

    # Configuración de paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(datos_combined, 10)

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
    
    
    # Renderizar la página normal
    return render(request, "Divisiones/prehospitalaria.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos_paginados,
        "total": contar_procedimientos_hoy_division(5),  # Conteo de procedimientos de hoy para la división Prehospitalaria
        "contador_total": conteo_total,
        "filtro_parroquia": parroquia,
        "filtro_procedimiento": procedimiento,
        "filtro_trimestre": trimestre,
        "procedimientos_list": Tipos_Procedimientos.objects.filter(id_division=5).distinct(),
        "parroquias_list": Parroquias.objects.all(),
    })

def View_grumae(request):
    user = request.session.get('user')
    if not user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
        return redirect('/')

    # Obtener parámetros de filtrado
    parroquia = request.GET.get('parroquia', '')
    procedimiento = request.GET.get('procedimiento', '')
    trimestre = request.GET.get('trimestre', '')

    # Consulta base (filtramos por división 4 - Grumae)
    datos_combined = Procedimientos.objects.filter(id_division=4)

    # Filtrar por fecha según el rol del usuario
    if user.get('user') == 'Grumae02':
        # Solo mostrar procedimientos del día actual para usuarios de Prehospitalaria
        hoy = timezone.now().date()
        fecha_inicio = datetime.combine(hoy, datetime.min.time())
        fecha_fin = datetime.combine(hoy, datetime.max.time())
        datos_combined = datos_combined.filter(fecha__range=(fecha_inicio, fecha_fin))
    # Para Admin y Sala Situacional no se aplica filtro de fecha (ven todo)

    # Aplicar filtros adicionales
    if parroquia:
        datos_combined = datos_combined.filter(id_parroquia__id=parroquia)

    if procedimiento:
        datos_combined = datos_combined.filter(id_tipo_procedimiento__id=procedimiento)

    if trimestre:
        trimestre = int(trimestre)
        meses = {
            1: [1, 2, 3],   # Ene-Mar
            2: [4, 5, 6],    # Abr-Jun
            3: [7, 8, 9],    # Jul-Sep
            4: [10, 11, 12]  # Oct-Dic
        }.get(trimestre, [])
        datos_combined = datos_combined.filter(fecha__month__in=meses)

    # Ordenar y contar
    datos_combined = datos_combined.order_by('-fecha')
    conteo_total = Procedimientos.objects.filter(id_division=4).count()

    # Configuración de paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(datos_combined, 10)

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
    
    
    # Renderizar la página normal
    return render(request, "Divisiones/grumae.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos_paginados,
        "total": contar_procedimientos_hoy_division(4),  # Conteo de procedimientos de hoy para la división Prehospitalaria
        "contador_total": conteo_total,
        "filtro_parroquia": parroquia,
        "filtro_procedimiento": procedimiento,
        "filtro_trimestre": trimestre,
        "procedimientos_list": Tipos_Procedimientos.objects.filter(id_division=4).distinct(),
        "parroquias_list": Parroquias.objects.all(),
    })

def View_Prevencion(request):
    user = request.session.get('user')
    if not user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
        return redirect('/')

    # Obtener parámetros de filtrado
    parroquia = request.GET.get('parroquia', '')
    procedimiento = request.GET.get('procedimiento', '')
    trimestre = request.GET.get('trimestre', '')

    # Consulta base (filtramos por división 3 - Prevencion)
    datos_combined = Procedimientos.objects.filter(id_division=3)

    # Filtrar por fecha según el rol del usuario
    if user.get('user') == 'Prevencion05':
        # Solo mostrar procedimientos del día actual para usuarios de Prevencion
        hoy = timezone.now().date()
        fecha_inicio = datetime.combine(hoy, datetime.min.time())
        fecha_fin = datetime.combine(hoy, datetime.max.time())
        datos_combined = datos_combined.filter(fecha__range=(fecha_inicio, fecha_fin))
    # Para Admin y Sala Situacional no se aplica filtro de fecha (ven todo)

    # Aplicar filtros adicionales
    if parroquia:
        datos_combined = datos_combined.filter(id_parroquia__id=parroquia)

    if procedimiento:
        datos_combined = datos_combined.filter(id_tipo_procedimiento__id=procedimiento)

    if trimestre:
        trimestre = int(trimestre)
        meses = {
            1: [1, 2, 3],   # Ene-Mar
            2: [4, 5, 6],    # Abr-Jun
            3: [7, 8, 9],    # Jul-Sep
            4: [10, 11, 12]  # Oct-Dic
        }.get(trimestre, [])
        datos_combined = datos_combined.filter(fecha__month__in=meses)

    # Ordenar y contar
    datos_combined = datos_combined.order_by('-fecha')
    conteo_total = Procedimientos.objects.filter(id_division=3).count()

    # Configuración de paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(datos_combined, 10)

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
    
    
    # Renderizar la página normal
    return render(request, "Divisiones/prevencion.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos_paginados,
        "total": contar_procedimientos_hoy_division(3),  # Conteo de procedimientos de hoy para la división Prehospitalaria
        "contador_total": conteo_total,
        "filtro_parroquia": parroquia,
        "filtro_procedimiento": procedimiento,
        "filtro_trimestre": trimestre,
        "procedimientos_list": Tipos_Procedimientos.objects.filter(id_division=3).distinct(),
        "parroquias_list": Parroquias.objects.all(),
    })

def View_capacitacion(request):
    user = request.session.get('user')
    if not user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
        return redirect('/')

    # Obtener parámetros de filtrado
    parroquia = request.GET.get('parroquia', '')
    procedimiento = request.GET.get('procedimiento', '')
    trimestre = request.GET.get('trimestre', '')

    # Consulta base (filtramos por división 9 - Capacitacion)
    datos_combined = Procedimientos.objects.filter(id_division=9)

    # Filtrar por fecha según el rol del usuario
    if user.get('user') == 'Capacitacion07':
        # Solo mostrar procedimientos del día actual para usuarios de Prevencion
        hoy = timezone.now().date()
        fecha_inicio = datetime.combine(hoy, datetime.min.time())
        fecha_fin = datetime.combine(hoy, datetime.max.time())
        datos_combined = datos_combined.filter(fecha__range=(fecha_inicio, fecha_fin))
    # Para Admin y Sala Situacional no se aplica filtro de fecha (ven todo)

    # Aplicar filtros adicionales
    if parroquia:
        datos_combined = datos_combined.filter(id_parroquia__id=parroquia)

    if procedimiento:
        datos_combined = datos_combined.filter(dependencia=procedimiento)

    if trimestre:
        trimestre = int(trimestre)
        meses = {
            1: [1, 2, 3],   # Ene-Mar
            2: [4, 5, 6],    # Abr-Jun
            3: [7, 8, 9],    # Jul-Sep
            4: [10, 11, 12]  # Oct-Dic
        }.get(trimestre, [])
        datos_combined = datos_combined.filter(fecha__month__in=meses)

    # Ordenar y contar
    datos_combined = datos_combined.order_by('-fecha')
    conteo_total = Procedimientos.objects.filter(id_division=9).count()

    # Configuración de paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(datos_combined, 10)

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
    
    
    # Renderizar la página normal
    return render(request, "Divisiones/capacitacion.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos_paginados,
        "total": contar_procedimientos_hoy_division(9),  # Conteo de procedimientos de hoy para la división Prehospitalaria
        "contador_total": conteo_total,
        "filtro_parroquia": parroquia,
        "filtro_procedimiento": procedimiento,
        "filtro_trimestre": trimestre,
        "procedimientos_list": Tipos_Procedimientos.objects.filter(id_division=9).distinct(),
        "parroquias_list": Parroquias.objects.all(),
    })

def View_enfermeria(request):
    user = request.session.get('user')
    if not user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
        return redirect('/')

    # Obtener parámetros de filtrado
    parroquia = request.GET.get('parroquia', '')
    procedimiento = request.GET.get('procedimiento', '')
    trimestre = request.GET.get('trimestre', '')

    # Consulta base (filtramos por división 6 - Enfermeria)
    datos_combined = Procedimientos.objects.filter(id_division=6)

    # Filtrar por fecha según el rol del usuario
    if user.get('user') == 'Enfermeria08':
        # Solo mostrar procedimientos del día actual para usuarios de Prevencion
        hoy = timezone.now().date()
        fecha_inicio = datetime.combine(hoy, datetime.min.time())
        fecha_fin = datetime.combine(hoy, datetime.max.time())
        datos_combined = datos_combined.filter(fecha__range=(fecha_inicio, fecha_fin))
    # Para Admin y Sala Situacional no se aplica filtro de fecha (ven todo)

    # Aplicar filtros adicionales
    if parroquia:
        datos_combined = datos_combined.filter(id_parroquia__id=parroquia)

    if procedimiento:
        datos_combined = datos_combined.filter(id_tipo_procedimiento__id=procedimiento)

    if trimestre:
        trimestre = int(trimestre)
        meses = {
            1: [1, 2, 3],   # Ene-Mar
            2: [4, 5, 6],    # Abr-Jun
            3: [7, 8, 9],    # Jul-Sep
            4: [10, 11, 12]  # Oct-Dic
        }.get(trimestre, [])
        datos_combined = datos_combined.filter(fecha__month__in=meses)

    # Ordenar y contar
    datos_combined = datos_combined.order_by('-fecha')
    conteo_total = Procedimientos.objects.filter(id_division=6).count()

    # Configuración de paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(datos_combined, 10)

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
    
    
    # Renderizar la página normal
    return render(request, "Divisiones/enfermeria.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos_paginados,
        "total": contar_procedimientos_hoy_division(6),  # Conteo de procedimientos de hoy para la división Enfermeria
        "contador_total": conteo_total,
        "filtro_parroquia": parroquia,
        "filtro_procedimiento": procedimiento,
        "filtro_trimestre": trimestre,
        "procedimientos_list": Tipos_Procedimientos.objects.filter(id_division=6).distinct(),
        "parroquias_list": Parroquias.objects.all(),
    })

def View_serviciosmedicos(request):
    user = request.session.get('user')
    if not user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
        return redirect('/')

    # Obtener parámetros de filtrado
    parroquia = request.GET.get('parroquia', '')
    procedimiento = request.GET.get('procedimiento', '')
    trimestre = request.GET.get('trimestre', '')

    # Consulta base (filtramos por división 7 - Servicios Medicos)
    datos_combined = Procedimientos.objects.filter(id_division=7)

    # Filtrar por fecha según el rol del usuario
    if user.get('user') == 'Serviciosmedicos06':
        # Solo mostrar procedimientos del día actual para usuarios de Prevencion
        hoy = timezone.now().date()
        fecha_inicio = datetime.combine(hoy, datetime.min.time())
        fecha_fin = datetime.combine(hoy, datetime.max.time())
        datos_combined = datos_combined.filter(fecha__range=(fecha_inicio, fecha_fin))
    # Para Admin y Sala Situacional no se aplica filtro de fecha (ven todo)

    # Aplicar filtros adicionales
    if parroquia:
        datos_combined = datos_combined.filter(id_parroquia__id=parroquia)

    if procedimiento:
        datos_combined = datos_combined.filter(id_tipo_procedimiento__id=procedimiento)

    if trimestre:
        trimestre = int(trimestre)
        meses = {
            1: [1, 2, 3],   # Ene-Mar
            2: [4, 5, 6],    # Abr-Jun
            3: [7, 8, 9],    # Jul-Sep
            4: [10, 11, 12]  # Oct-Dic
        }.get(trimestre, [])
        datos_combined = datos_combined.filter(fecha__month__in=meses)

    # Ordenar y contar
    datos_combined = datos_combined.order_by('-fecha')
    conteo_total = Procedimientos.objects.filter(id_division=7).count()

    # Configuración de paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(datos_combined, 10)

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
    
    
    # Renderizar la página normal
    return render(request, "Divisiones/serviciosmedicos.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos_paginados,
        "total": contar_procedimientos_hoy_division(7),  # Conteo de procedimientos de hoy para la división Prehospitalaria
        "contador_total": conteo_total,
        "filtro_parroquia": parroquia,
        "filtro_procedimiento": procedimiento,
        "filtro_trimestre": trimestre,
        "procedimientos_list": Tipos_Procedimientos.objects.filter(id_division=7).distinct(),
        "parroquias_list": Parroquias.objects.all(),
    })

def View_psicologia(request):
    user = request.session.get('user')
    if not user:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
        return redirect('/')

    # Obtener parámetros de filtrado
    parroquia = request.GET.get('parroquia', '')
    procedimiento = request.GET.get('procedimiento', '')
    trimestre = request.GET.get('trimestre', '')

    # Consulta base (filtramos por división 8 - Psicologia)
    datos_combined = Procedimientos.objects.filter(id_division=8)

    # Filtrar por fecha según el rol del usuario
    if user.get('user') == 'Psicologia09':
        # Solo mostrar procedimientos del día actual para usuarios de Prevencion
        hoy = timezone.now().date()
        fecha_inicio = datetime.combine(hoy, datetime.min.time())
        fecha_fin = datetime.combine(hoy, datetime.max.time())
        datos_combined = datos_combined.filter(fecha__range=(fecha_inicio, fecha_fin))
    # Para Admin y Sala Situacional no se aplica filtro de fecha (ven todo)

    # Aplicar filtros adicionales
    if parroquia:
        datos_combined = datos_combined.filter(id_parroquia__id=parroquia)

    if procedimiento:
        datos_combined = datos_combined.filter(id_tipo_procedimiento__id=procedimiento)

    if trimestre:
        trimestre = int(trimestre)
        meses = {
            1: [1, 2, 3],   # Ene-Mar
            2: [4, 5, 6],    # Abr-Jun
            3: [7, 8, 9],    # Jul-Sep
            4: [10, 11, 12]  # Oct-Dic
        }.get(trimestre, [])
        datos_combined = datos_combined.filter(fecha__month__in=meses)

    # Ordenar y contar
    datos_combined = datos_combined.order_by('-fecha')
    conteo_total = Procedimientos.objects.filter(id_division=8).count()

    # Configuración de paginación
    page = request.GET.get('page', 1)
    paginator = Paginator(datos_combined, 10)

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
    
    
    # Renderizar la página normal
    return render(request, "Divisiones/psicologia.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos_paginados,
        "total": contar_procedimientos_hoy_division(8),  # Conteo de procedimientos de hoy para la división Enfermeria
        "contador_total": conteo_total,
        "filtro_parroquia": parroquia,
        "filtro_procedimiento": procedimiento,
        "filtro_trimestre": trimestre,
        "procedimientos_list": Tipos_Procedimientos.objects.filter(id_division=8).distinct(),
        "parroquias_list": Parroquias.objects.all(),
    })

# Tabla general
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


