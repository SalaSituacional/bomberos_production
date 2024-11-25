from django.shortcuts import render, redirect
from django.http import HttpResponse
from ..models import *
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from datetime import datetime
import json
from datetime import timedelta

# Vista de la Seccion de Operaciones
def View_Operaciones(request):
    user = request.session.get('user')
    if not user:
            return redirect('/')

    datos = Procedimientos.objects.filter(id_division=2)
    total = datos.count()

    # Obtener la fecha de hoy
    hoy = datetime.now().date()

    # Filtrar procedimientos con la fecha de hoy
    fechas = datos.values_list("fecha", flat=True)
    procedimientos_hoy = [fecha for fecha in fechas if fecha == hoy]

    hoy = len(procedimientos_hoy)

    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        procedimiento = get_object_or_404(Procedimientos, id=id)
        try:
            procedimiento.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    datos = list(datos)[::-1]

    return render(request, "Divisiones/operaciones.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos,
        "total": total,
        "hoy": hoy
    })
# Vista de la Seccion de Operaciones

def View_Rescate(request):
    user = request.session.get('user')
    if not user:
            return redirect('/')

    datos = Procedimientos.objects.filter(id_division = 1)

    total = datos.count()

    # Obtener la fecha de hoy
    hoy = datetime.now().date()

    # Filtrar procedimientos con la fecha de hoy
    fechas = datos.values_list("fecha", flat=True)
    procedimientos_hoy = [fecha for fecha in fechas if fecha == hoy]

    hoy = len(procedimientos_hoy)

    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        procedimiento = get_object_or_404(Procedimientos, id=id)
        try:
            procedimiento.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    datos = list(datos)[::-1]

    return render(request, "Divisiones/rescate.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos,
        "total": total,
        "hoy": hoy
    })

def View_Prevencion(request):
    user = request.session.get('user')
    if not user:
            return redirect('/')

    datos = Procedimientos.objects.filter(id_division = 3)
    total = datos.count()

    # Obtener la fecha de hoy
    hoy = datetime.now().date()

    # Filtrar procedimientos con la fecha de hoy
    fechas = datos.values_list("fecha", flat=True)
    procedimientos_hoy = [fecha for fecha in fechas if fecha == hoy]

    hoy = len(procedimientos_hoy)

    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        procedimiento = get_object_or_404(Procedimientos, id=id)
        try:
            procedimiento.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
    datos = list(datos)[::-1]

    return render(request, "Divisiones/prevencion.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos,
        "total": total,
        "hoy": hoy
    })

def View_grumae(request):
    user = request.session.get('user')
    if not user:
            return redirect('/')

    datos = Procedimientos.objects.filter(id_division = 4)

    total = datos.count()

    # Obtener la fecha de hoy
    hoy = datetime.now().date()

    # Filtrar procedimientos con la fecha de hoy
    fechas = datos.values_list("fecha", flat=True)
    procedimientos_hoy = [fecha for fecha in fechas if fecha == hoy]

    hoy = len(procedimientos_hoy)

    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        procedimiento = get_object_or_404(Procedimientos, id=id)
        try:
            procedimiento.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
    datos = list(datos)[::-1]

    return render(request, "Divisiones/grumae.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos,
        "total": total,
        "hoy": hoy
    })

def View_prehospitalaria(request):
    user = request.session.get('user')
    if not user:
            return redirect('/')

    datos = Procedimientos.objects.filter(id_division = 5)

    total = datos.count()

    # Obtener la fecha de hoy
    hoy = datetime.now().date()

    # Filtrar procedimientos con la fecha de hoy
    fechas = datos.values_list("fecha", flat=True)
    procedimientos_hoy = [fecha for fecha in fechas if fecha == hoy]

    hoy = len(procedimientos_hoy)


    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        procedimiento = get_object_or_404(Procedimientos, id=id)
        try:
            procedimiento.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
    datos = list(datos)[::-1]

    return render(request, "Divisiones/prehospitalaria.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos,
        "total": total,
        "hoy": hoy
    })

def View_capacitacion(request):
    user = request.session.get('user')
    if not user:
            return redirect('/')

    datos = Procedimientos.objects.filter(id_division = 9)

    total = datos.count()

    # Obtener la fecha de hoy
    hoy = datetime.now().date()

    # Filtrar procedimientos con la fecha de hoy
    fechas = datos.values_list("fecha", flat=True)
    procedimientos_hoy = [fecha for fecha in fechas if fecha == hoy]

    hoy = len(procedimientos_hoy)

    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        procedimiento = get_object_or_404(Procedimientos, id=id)
        try:
            procedimiento.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
    datos = list(datos)[::-1]

    return render(request, "Divisiones/capacitacion.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos,
        "total": total,
        "hoy": hoy
    })

def View_enfermeria(request):
    user = request.session.get('user')
    if not user:
            return redirect('/')

    datos = Procedimientos.objects.filter(id_division = 6)

    total = datos.count()

    # Obtener la fecha de hoy
    hoy = datetime.now().date()

    # Filtrar procedimientos con la fecha de hoy
    fechas = datos.values_list("fecha", flat=True)
    procedimientos_hoy = [fecha for fecha in fechas if fecha == hoy]

    hoy = len(procedimientos_hoy)

    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        procedimiento = get_object_or_404(Procedimientos, id=id)
        try:
            procedimiento.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
    datos = list(datos)[::-1]

    return render(request, "Divisiones/enfermeria.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos,
        "total": total,
        "hoy": hoy
    })

def View_serviciosmedicos(request):
    user = request.session.get('user')
    if not user:
            return redirect('/')

    datos = Procedimientos.objects.filter(id_division = 7)

    total = datos.count()

    # Obtener la fecha de hoy
    hoy = datetime.now().date()

    # Filtrar procedimientos con la fecha de hoy
    fechas = datos.values_list("fecha", flat=True)
    procedimientos_hoy = [fecha for fecha in fechas if fecha == hoy]

    hoy = len(procedimientos_hoy)


    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        procedimiento = get_object_or_404(Procedimientos, id=id)
        try:
            procedimiento.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
    datos = list(datos)[::-1]

    return render(request, "Divisiones/serviciosmedicos.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos,
        "total": total,
        "hoy": hoy
    })

def View_psicologia(request):
    user = request.session.get('user')
    if not user:
            return redirect('/')

    datos = Procedimientos.objects.filter(id_division = 8)

    total = datos.count()

    # Obtener la fecha de hoy
    hoy = datetime.now().date()

    # Filtrar procedimientos con la fecha de hoy
    fechas = datos.values_list("fecha", flat=True)
    procedimientos_hoy = [fecha for fecha in fechas if fecha == hoy]

    hoy = len(procedimientos_hoy)


    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        procedimiento = get_object_or_404(Procedimientos, id=id)
        try:
            procedimiento.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
        
    datos = list(datos)[::-1]

    return render(request, "Divisiones/psicologia.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos,
        "total": total,
        "hoy": hoy
    })

def tabla_general(request):
    user = request.session.get('user')
    if not user:
        return redirect('/')

    # Filtra los procedimientos de las divisiones 1 a 5
    divisiones = range(1, 6)
    datos_combined = Procedimientos.objects.filter(id_division__in=divisiones).order_by('-fecha')  # Orden descendente

    # Corrige el conteo
    total = datos_combined.count()

    # Obtener la fecha de hoy
    hoy_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    hoy_fin = hoy_inicio + timedelta(days=1)


    # Filtrar procedimientos con la fecha de hoy
    procedimientos_hoy = datos_combined.filter(fecha__gte=hoy_inicio, fecha__lt=hoy_fin)
    hoy_count = procedimientos_hoy.count()

    if request.method == 'POST':
        data = json.loads(request.body)
        id = data.get('id')
        procedimiento = get_object_or_404(Procedimientos, id=id)
        try:
            procedimiento.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=400)

    return render(request, "tablageneral.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos_combined,  # Ya en orden descendente
        "total": total,
        "hoy": hoy_count
    })