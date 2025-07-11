from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
from .urls import *

@login_required
# Vista para el Dashboard
def Dashboard_bienes(request):
    # Filtrar bienes por estado y contar el total de cada uno
    bienes_buenos = BienMunicipal.objects.filter(estado_actual="Bueno").count()
    bienes_regulares = BienMunicipal.objects.filter(estado_actual="Regular").count()
    bienes_defectuosos = BienMunicipal.objects.filter(estado_actual="Defectuoso").count()
    bienes_dañados = BienMunicipal.objects.filter(estado_actual="Dañado").count()  # Corregido para contar correctamente

     # Contar bienes por dependencia
    cuartelcentral = BienMunicipal.objects.filter(dependencia__nombre="Cuartel Central").count()
    estacion01 = BienMunicipal.objects.filter(dependencia__nombre="Estacion 01").count()
    estacion02 = BienMunicipal.objects.filter(dependencia__nombre="Estacion 02").count()
    estacion03 = BienMunicipal.objects.filter(dependencia__nombre="Estacion 03").count()


    # Verificar si hay un usuario autenticado en la sesión
    user = request.session.get('user')
    if not user:
        return redirect('/')

    # Renderizar la página con los datos
    return render(request, "bienes_municipales/dashboard_bienes.html", {
        "user": user,
        "jerarquia": user.get("jerarquia", ""),  # Agregado un valor predeterminado
        "nombres": user.get("nombres", ""),
        "apellidos": user.get("apellidos", ""),
        "bienes_buenos": bienes_buenos,
        "bienes_regulares": bienes_regulares,
        "bienes_defectuosos": bienes_defectuosos,
        "bienes_dañados": bienes_dañados,
        "count_cuartelcentral": cuartelcentral,
        "count_estacion01": estacion01,
        "count_estacion02": estacion02,
        "count_estacion03": estacion03,
    })

@login_required
def Registros_bienes(request):
    user = request.session.get('user')

    if not user:
        return redirect('/')
    # Renderizar la página con los datos

    if request.method == "POST":
        form = BienMunicipalForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            responsable_id = data['responsable']
            responsable_obj = Personal.objects.get(id=responsable_id)

            bien = BienMunicipal.objects.create(
                identificador=data['identificador'],
                descripcion=data['descripcion'],
                cantidad=data['cantidad'],
                dependencia=data['dependencia'],
                departamento=data['departamento'],
                responsable=responsable_obj,
                fecha_registro=data['fecha_registro'],
                estado_actual=data['estado_actual']
            )
            return redirect("inventario_bienes")
        else:
            return JsonResponse({"errores": form.errors}, status=400)
    
    else:
        form = BienMunicipalForm()
        return render(request, "bienes_municipales/registro_inventario.html", {
            "user": user,
            "jerarquia": user["jerarquia"],
            "nombres": user["nombres"],
            "apellidos": user["apellidos"],
            "form_bienes": BienMunicipalForm()
            })

def Inventario_bienes(request):
    user = request.session.get('user')
    total_bienes = BienMunicipal.objects.all().count()

    if not user:
        return redirect('/')
    # Renderizar la página con los datos
    return render(request, "bienes_municipales/inventario_bienes.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "form_movimientos": MovimientoBienForm(),
        "form_estado": CambiarEstadoBienForm(),
        "total_bienes": total_bienes,
    })

def listar_bienes(request):
    identificador = request.GET.get("identificador")
    page = int(request.GET.get("page", 1))
    per_page = 15

    bienes_queryset = BienMunicipal.objects.select_related('dependencia', 'responsable').order_by("id")

    if identificador:
        bienes_queryset = bienes_queryset.filter(identificador__icontains=identificador)
        if not bienes_queryset.exists():
            return JsonResponse({"error": "No se encontraron bienes con ese identificador."}, status=404)

    paginator = Paginator(bienes_queryset, per_page if not identificador else bienes_queryset.count())
    bienes = paginator.get_page(page)

    data = {
        "total_pages": paginator.num_pages,
        "current_page": bienes.number,
        "bienes": []
    }

    for index, bien in enumerate(bienes, start=bienes.start_index()):
        data["bienes"].append({
            "numero": index,
            "identificador": bien.identificador,
            "cantidad": bien.cantidad,
            "descripcion": bien.descripcion,
            "dependencia": bien.dependencia.nombre,
            "departamento": bien.departamento,
            "responsable": f"{bien.responsable.nombres} {bien.responsable.apellidos}",
            "fecha_registro": bien.fecha_registro.strftime('%d/%m/%Y'),
            "estado_actual": bien.estado_actual,
        })

    return JsonResponse(data)


def reasignar_bien(request):
    if request.method == 'POST':
        form = MovimientoBienForm(request.POST)
        if form.is_valid():
            bien_id = form.cleaned_data['bien']
            bien = get_object_or_404(BienMunicipal, identificador=bien_id)

            nueva_dependencia = form.cleaned_data['nueva_dependencia']
            nuevo_departamento = form.cleaned_data['nuevo_departamento']
            ordenado_por = form.cleaned_data['ordenado_por']
            fecha_orden = form.cleaned_data['fecha_orden']

            # Guardar el movimiento
            movimiento = MovimientoBien.objects.create(
                bien=bien,
                nueva_dependencia=nueva_dependencia,
                nuevo_departamento=nuevo_departamento,
                ordenado_por=ordenado_por,
                fecha_orden=fecha_orden
            )

            # Actualizar el bien
            bien.dependencia = nueva_dependencia
            bien.departamento = nuevo_departamento
            bien.save()

            return redirect('/inventario_bienes/')  # Cambia esta ruta al destino deseado

    else:
        form = MovimientoBienForm()
    return render(request, 'reasignar_form.html', {'form': form})

def cambiar_estado_bienes(request):
    if request.method == 'POST':
        form = CambiarEstadoBienForm(request.POST)
        if form.is_valid():
            bien_id = form.cleaned_data['bien_cambiar_estado']
            bien = get_object_or_404(BienMunicipal, identificador=bien_id)

            nuevo_estado = form.cleaned_data['nuevo_estado']
            fecha_orden = form.cleaned_data['fecha_orden']

            # Guardar el movimiento
            movimiento = CambiarEstadoBien.objects.create(
                bien=bien,
                nuevo_estado=nuevo_estado,
                fecha_orden=fecha_orden
            )

            # Actualizar el bien
            bien.estado_actual = nuevo_estado
            bien.save()

            return redirect('/inventario_bienes/')  # Cambia esta ruta al destino deseado

    else:
        form = CambiarEstadoBienForm()
    return render(request, 'reasignar_form.html', {'form': form})

def eliminar_bien(request):
    bien_id = request.POST.get('bien_id')
    bien = get_object_or_404(BienMunicipal, identificador=bien_id)
    bien.delete()
    return redirect('/inventario_bienes/')  # Cambia a la vista que quieras recargar

def historial_bien_api(request, bien_id):
    bien = BienMunicipal.objects.get(identificador=bien_id)
    movimientos = MovimientoBien.objects.filter(bien=bien).order_by('-fecha_orden')[:3]

    data = {
        'bien': {
            'identificador': bien.identificador,
            'descripcion': bien.descripcion,
            'cantidad': bien.cantidad,
            'dependencia': bien.dependencia.nombre,
            'departamento': bien.departamento,
            'responsable': str(bien.responsable.jerarquia) + " " + str(bien.responsable.nombres) + " " + str(bien.responsable.apellidos),
            'estado_actual': bien.estado_actual,
        },
        'movimientos': [
            {
                'fecha_orden': m.fecha_orden.strftime('%d-%m-%Y'),
                'nueva_dependencia': m.nueva_dependencia.nombre,
                'nuevo_departamento': m.nuevo_departamento,
                'ordenado_por': f"{m.ordenado_por.jerarquia} {m.ordenado_por.nombres} {m.ordenado_por.apellidos}",
            } for m in movimientos
        ]
    }

    return JsonResponse(data)

def verificar_identificador(request):
    identificador = request.GET.get("identificador", "")
    existe = BienMunicipal.objects.filter(identificador=identificador).exists()
    return JsonResponse({"existe": existe})


def generar_excel_bienes_municipales(request):
    bienes = BienMunicipal.objects.select_related('dependencia', 'responsable').order_by('-fecha_registro')
    data = []

    for bien in bienes:
        movimientos = MovimientoBien.objects.filter(bien=bien).select_related('nueva_dependencia', 'ordenado_por').order_by('-fecha_orden')
        movimientos_data = [
            {
                'nueva_dependencia': movimiento.nueva_dependencia.nombre,
                'nuevo_departamento': movimiento.nuevo_departamento,
                'ordenado_por': str(movimiento.ordenado_por),  # Asegúrate de que esto sea serializable
                'fecha_orden': movimiento.fecha_orden.isoformat(),
            }
            for movimiento in movimientos
        ]

        data.append({
            'identificador': bien.identificador,
            'descripcion': bien.descripcion,
            'cantidad': bien.cantidad,
            'dependencia': bien.dependencia.nombre,
            'departamento': bien.departamento,
            'responsable': str(bien.responsable) if bien.responsable else "Sin asignar",
            'fecha_registro': bien.fecha_registro.isoformat(),
            'estado_actual': bien.estado_actual,
            'movimientos': movimientos_data,
        })

    return JsonResponse(data, safe=False)
