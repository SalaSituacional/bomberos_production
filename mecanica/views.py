from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Prefetch, Max
from .forms import *
from .models import *
from web.models import Divisiones
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseForbidden, HttpResponseNotAllowed
from django.contrib import messages
from collections import Counter
from django.utils.timezone import now, localdate
from datetime import timedelta, date
from django.forms.models import model_to_dict
from django.views.decorators.http import require_http_methods
import pandas as pd
import json
from django.db.models import Q, Count, F
from django.db import transaction
from datetime import date
from datetime import datetime

# ========================= Dashboard Mecanica ========================
def Dashboard_mecanica(request):
    user = request.session.get('user')

    if not user:
        return redirect('/')
    # Renderizar la página con los datos
    return render(request, "mecanica/dashboard_mecanica.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
    })


# ======================== Unidades ========================
def View_Unidades(request):
    user = request.session.get('user')
    if not user:
        return redirect('/')

    # 1. Obtener los parámetros de filtro de la URL
    filter_nombre_unidad = request.GET.get('filterNombreUnidad', '').strip()
    filter_division_id = request.GET.get('filterDivision', '')
    filter_estado = request.GET.get('filterEstado', '')

    # 2. Inicializar el queryset base
    unidades_queryset = Unidades.objects.exclude(id__in=[26, 30, 27]).order_by("id")

    # PREFETCH CORRECTOS SEGÚN _meta.get_fields():
    unidades_queryset = unidades_queryset.prefetch_related(
        # Para ManyToManyField 'id_division'
        Prefetch("id_division", queryset=Divisiones.objects.all(), to_attr="divisiones_prefetch"),
        # Para ForeignKey inverso 'unidades_detalles_set' (¡Aquí está el cambio!)
        Prefetch("detalles_de_unidad", queryset=Unidades_Detalles.objects.all(), to_attr="detalles_prefetch")
    )

    if user["user"] == "Operaciones01":
        unidades_queryset = unidades_queryset.filter(id_division=2)
    elif user["user"] == "Rescate03":
        unidades_queryset = unidades_queryset.filter(id_division=1)
    elif user["user"] == "Prevencion05":
        unidades_queryset = unidades_queryset.filter(id_division=3)
    elif user["user"] == "Grumae02":
        unidades_queryset = unidades_queryset.filter(id_division=4)
    elif user["user"] == "Prehospitalaria04":
        unidades_queryset = unidades_queryset.filter(id_division=5)

    # 3. Aplicar filtros si existen
    if filter_nombre_unidad:
        unidades_queryset = unidades_queryset.filter(nombre_unidad__icontains=filter_nombre_unidad)

    if filter_division_id:
        try:
            # Filtrar por el ID de la división en ManyToManyField
            unidades_queryset = unidades_queryset.filter(id_division__id=filter_division_id).distinct()
        except ValueError:
            pass

    if filter_estado:
        # Filtrar por el campo 'estado' en el modelo Unidades_Detalles a través de la relación inversa
        unidades_queryset = unidades_queryset.filter(detalles_de_unidad__estado=filter_estado).distinct()


    # 4. Ejecutar el queryset y obtener el conteo de unidades filtradas
    data = list(unidades_queryset) # Aquí es donde se evalúa el queryset y fallaría si el prefetch es malo
    conteo = len(data)

    # 5. Preparar los datos para el template
    datos = []
    for unidad in data:
        division_nombres = [div.division for div in unidad.divisiones_prefetch]

        detalles_unidad = []
        if hasattr(unidad, 'detalles_prefetch'): # Usar el 'to_attr' definido
            detalles_unidad = [
                {
                    "tipo_vehiculo": detalle.tipo_vehiculo,
                    "serial_carroceria": detalle.serial_carroceria,
                    "serial_chasis": detalle.serial_chasis,
                    "marca": detalle.marca,
                    "año": detalle.año,
                    "modelo": detalle.modelo,
                    "placas": detalle.placas,
                    "tipo_filtro_aceite": detalle.tipo_filtro_aceite,
                    "tipo_filtro_combustible": detalle.tipo_filtro_combustible,
                    "bateria": detalle.bateria,
                    "numero_tag": detalle.numero_tag,
                    "tipo_bujia": detalle.tipo_bujia,
                    "uso": detalle.uso,
                    "capacidad_carga": detalle.capacidad_carga,
                    "numero_ejes": detalle.numero_ejes,
                    "numero_puestos": detalle.numero_puestos,
                    "tipo_combustible": detalle.tipo_combustible,
                    "tipo_aceite": detalle.tipo_aceite,
                    "medida_neumaticos": detalle.medida_neumaticos,
                    "tipo_correa": detalle.tipo_correa,
                    "estado": detalle.estado,
                }
                for detalle in unidad.detalles_prefetch
            ]

        datos.append({
            "nombre_unidad": unidad.nombre_unidad,
            "id_unidad": unidad.id,
            "divisiones": division_nombres,
            "detalles": detalles_unidad,
        })

    divisiones_para_filtro = Divisiones.objects.all()

    # 6. Preparar el contexto para el template
    context = {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "datos": datos,
        "form_reportes": Reportes(),
        "form_estado": Cambiar_Estado(),
        "form_division": Cambiar_Division(),
        "conteo": conteo,
        'divisiones': divisiones_para_filtro,
        'filtroNombreUnidad': filter_nombre_unidad,
        'filtroDivision': filter_division_id,
        'filtroEstado': filter_estado,
    }

    return render(request, "unidades/unidades_inicio.html", context)

# ======================== Reportes de Unidades ========================
def View_Reportes_Unidades(request):
    user = request.session.get('user')
    if not user:
        return redirect('/')

    # 1. Obtener los parámetros de filtro de la URL
    filter_unidad_id = request.GET.get('filterUnidad', '')
    filter_tipo_reporte = request.GET.get('filterTipoReporte', '')
    filter_fecha_inicio = request.GET.get('filterFechaFin', '')

    # 2. Inicializar el queryset base
    reportes_queryset = Reportes_Unidades.objects.all().order_by("-fecha", "-hora")
    servicios_para_filtro = Servicios.objects.all().order_by("nombre_servicio") # Línea corregida

    # Prefetch y select_related
    reportes_queryset = reportes_queryset.select_related(
        'id_unidad',
        'servicio'
    ).prefetch_related(
        'id_unidad__id_division'
    )

    # Filtros por usuario según su división
    if user["user"] == "Operaciones01":
        reportes_queryset = reportes_queryset.filter(id_unidad__id_division__id=2)
    elif user["user"] == "Rescate03":
        reportes_queryset = reportes_queryset.filter(id_unidad__id_division__id=1)
    elif user["user"] == "Prevencion05":
        reportes_queryset = reportes_queryset.filter(id_unidad__id_division__id=3)
    elif user["user"] == "Grumae02":
        reportes_queryset = reportes_queryset.filter(id_unidad__id_division__id=4)
    elif user["user"] == "Prehospitalaria04":
        reportes_queryset = reportes_queryset.filter(id_unidad__id_division__id=5)

    # 3. Aplicar filtros si existen
    if filter_unidad_id:
        reportes_queryset = reportes_queryset.filter(id_unidad_id=filter_unidad_id)

    if filter_tipo_reporte:
        reportes_queryset = reportes_queryset.filter(servicio__nombre_servicio=filter_tipo_reporte)

    if filter_fecha_inicio:
        try:
            fecha_inicio = datetime.strptime(filter_fecha_inicio, '%Y-%m-%d')
            reportes_queryset = reportes_queryset.filter(fecha=fecha_inicio)
        except ValueError:
            pass

    # 4. Obtener datos para filtros
    unidades_para_filtro = Unidades.objects.exclude(id__in=[26, 30, 27]).order_by("nombre_unidad")
    
    # Aplicar filtro por división para usuarios específicos
    if user["user"] in ["Operaciones01", "Rescate03", "Prevencion05", "Grumae02", "Prehospitalaria04"]:
        division_id = {
            "Operaciones01": 2,
            "Rescate03": 1,
            "Prevencion05": 3,
            "Grumae02": 4,
            "Prehospitalaria04": 5
        }[user["user"]]
        unidades_para_filtro = unidades_para_filtro.filter(id_division=division_id)

    # 6. Preparar el contexto para el template
    paginator = Paginator(reportes_queryset, 15)  # Muestra 15 reportes por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "unidades": unidades_para_filtro,
        "tipos_reporte": servicios_para_filtro, # Corregido
        'filtroUnidad': filter_unidad_id,
        'filtroTipoReporte': filter_tipo_reporte,
        'filtroFechaFin': filter_fecha_inicio,
        "conteo": reportes_queryset.count(),
        "datos": page_obj,
        "page_obj": page_obj,
        "form_reportes": Reportes(),
    }

    return render(request, "unidades/reportesUnidades.html", context)

def api_detalle_reporte_unidad(request, reporte_id):
    try:
        reporte = Reportes_Unidades.objects.select_related(
            'id_unidad'
        ).prefetch_related(
            'id_unidad__id_division'
        ).get(id=reporte_id)
        
        data = {
            "id": reporte.id,
            "unidad": reporte.id_unidad.nombre_unidad if reporte.id_unidad else "N/A",
            "division": ", ".join([div.division for div in reporte.id_unidad.id_division.all()]) if reporte.id_unidad else "N/A",
            "tipo_reporte": reporte.servicio.nombre_servicio,
            "personal_responsable": reporte.persona_responsable,
            "descripcion": reporte.descripcion,
            "fecha_reporte": reporte.fecha.strftime('%d-%m-%Y') if reporte.fecha else "N/A",
            "hora_reporte": str(reporte.hora) if reporte.hora else "N/A",
        }
        
        return JsonResponse(data)
        
    except Reportes_Unidades.DoesNotExist:
        return JsonResponse({"error": "Reporte no encontrado"}, status=404)

def Eliminar_Reporte_Unidad(request, reporteId):
    # La decoración @csrf_exempt se usa aquí para simplificar,
    # pero para un entorno de producción, considera usar un token CSRF
    # si la petición se envía desde el mismo sitio web.

    # 1. Autenticación y Autorización
    # Obtener el usuario de la sesión
    user = request.session.get('user')
    if not user:
        # Si no hay usuario en sesión, no está autorizado
        return HttpResponseForbidden(json.dumps({'error': 'No autorizado'}), content_type="application/json")

    # Autorización basada en el rol del usuario
    # Solo ciertos roles pueden eliminar reportes
    roles_autorizados = ["SeRvEr", "Sala_Situacional", "Comandancia"]
    if user["user"] not in roles_autorizados:
        return HttpResponseForbidden(json.dumps({'error': 'No tiene permisos para realizar esta acción'}), content_type="application/json")

    # 2. Buscar el reporte a eliminar
    try:
        reporte = Reportes_Unidades.objects.get(id=reporteId)
    except Reportes_Unidades.DoesNotExist:
        return HttpResponseBadRequest(json.dumps({'error': 'El reporte no existe.'}), content_type="application/json")

    # 3. Eliminar el reporte
    try:
        reporte.delete()
        return JsonResponse({'success': True, 'message': 'Reporte eliminado con éxito.'})
    except Exception as e:
        # En caso de cualquier otro error al intentar eliminar
        return JsonResponse({'success': False, 'message': f'Error al eliminar el reporte: {str(e)}'}, status=500)

def editar_reporte(request, reporteId):
    try:
        # 1. Buscar el reporte por su ID
        reporte = Reportes_Unidades.objects.get(id=reporteId)
    except Reportes_Unidades.DoesNotExist:
        return JsonResponse({"error": "El reporte no existe"}, status=404)

    # 2. Decodificar los datos JSON enviados en el cuerpo de la solicitud
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponseBadRequest("Datos JSON inválidos.")

    # 3. Extraer y validar los datos
    servicio_id = data.get('servicio')
    fecha = data.get('fecha')
    hora = data.get('hora')
    responsable = data.get('responsable')
    descripcion = data.get('descripcion')
    
    # Valida que los datos necesarios existan
    if not all([servicio_id, fecha, hora, responsable, descripcion]):
        return HttpResponseBadRequest("Faltan campos obligatorios.")

    # 4. Actualizar el reporte
    try:
        # Obtener el objeto Servicio
        servicio = Servicios.objects.get(id=servicio_id)
        
        # Actualizar los campos del modelo
        reporte.servicio = servicio
        reporte.fecha = fecha
        reporte.hora = hora
        reporte.persona_responsable = responsable
        reporte.descripcion = descripcion
        
        # Guardar los cambios en la base de datos
        reporte.save()
        
        return JsonResponse({"message": "Reporte actualizado con éxito"}, status=200)
    except Servicios.DoesNotExist:
        return JsonResponse({"error": "El servicio seleccionado no existe."}, status=400)
    except Exception as e:
        # Manejo de errores genérico para depuración
        print(f"Error al actualizar: {e}")
        return JsonResponse({"error": "Error interno del servidor"}, status=500)



def View_Form_unidades(request):
    user = request.session.get('user')
    if not user:
            return redirect('/')

    return render(request, "unidades/unidades_form.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "agregar_unidades": Unidades_Informacion(),
    })

def agregar_unidades(request):
    if request.method == "POST":
        unidad_id = request.POST.get("id_unidad")  # Si existe, se edita; si no, se crea
        nombre_unidad = request.POST.get("nombre_unidad")
        division_ids = request.POST.getlist("division")  # Obtener múltiples valores
        tipo_vehiculo = request.POST.get("tipo_vehiculo")
        serial_carroceria = request.POST.get("serial_carroceria")
        serial_chasis = request.POST.get("serial_chasis")
        marca = request.POST.get("marca")
        año = request.POST.get("año")
        modelo = request.POST.get("modelo")
        placas = request.POST.get("placas")
        tipo_filtro_aceite = request.POST.get("tipo_filtro_aceite")
        tipo_filtro_combustible = request.POST.get("tipo_filtro_combustible")
        bateria = request.POST.get("bateria")
        numero_tag = request.POST.get("numero_tag")
        tipo_bujia = request.POST.get("tipo_bujia")
        uso = request.POST.get("uso")
        capacidad_carga = request.POST.get("capacidad_carga")
        numero_ejes = request.POST.get("numero_ejes")
        numero_puestos = request.POST.get("numero_puestos")
        tipo_combustible = request.POST.get("tipo_combustible")
        tipo_aceite = request.POST.get("tipo_aceite")
        medida_neumaticos = request.POST.get("medida_neumaticos")
        tipo_correa = request.POST.get("tipo_correa")
        estado = request.POST.get("estado")

        # Si unidad_id existe, buscar la unidad para editarla; si no, crear una nueva
        if unidad_id:
            unidad = get_object_or_404(Unidades, id=unidad_id)
            unidad.nombre_unidad = nombre_unidad
            unidad.save()
        else:
            unidad = Unidades.objects.create(nombre_unidad=nombre_unidad)

        # Asignar divisiones a la unidad
        if division_ids:
            divisiones_seleccionadas = Divisiones.objects.filter(id__in=division_ids)
            unidad.id_division.set(divisiones_seleccionadas)

        # Buscar si la unidad ya tiene detalles
        detalles, created = Unidades_Detalles.objects.get_or_create(id_unidad=unidad)

        # Actualizar o asignar detalles
        detalles.tipo_vehiculo = tipo_vehiculo
        detalles.serial_carroceria = serial_carroceria
        detalles.serial_chasis = serial_chasis
        detalles.marca = marca
        detalles.año = año
        detalles.modelo = modelo
        detalles.placas = placas
        detalles.tipo_filtro_aceite = tipo_filtro_aceite
        detalles.tipo_filtro_combustible = tipo_filtro_combustible
        detalles.bateria = bateria
        detalles.numero_tag = numero_tag
        detalles.tipo_bujia = tipo_bujia
        detalles.uso = uso
        detalles.capacidad_carga = capacidad_carga
        detalles.numero_ejes = numero_ejes
        detalles.numero_puestos = numero_puestos
        detalles.tipo_combustible = tipo_combustible
        detalles.tipo_aceite = tipo_aceite
        detalles.medida_neumaticos = medida_neumaticos
        detalles.tipo_correa = tipo_correa
        detalles.estado = estado
        detalles.save()

        return redirect("/mecanica/unidades/")

def agregar_reportes(request):
    if request.method == "POST":

        unidad = request.POST.get("unidad_id")
        servicio = request.POST.get("servicio")
        fecha = request.POST.get("fecha")
        hora = request.POST.get("hora")
        responsable = request.POST.get("responsable")
        descripcion = request.POST.get("descripcion")


        unidad_instance = get_object_or_404(Unidades, id=unidad)
        servicio_instance = get_object_or_404(Servicios, id=servicio)

        Reportes_Unidades.objects.create(
            id_unidad = unidad_instance,
            servicio = servicio_instance,
            fecha = fecha,
            hora = hora,
            descripcion = descripcion,
            persona_responsable = responsable
        )

        return redirect("/mecanica/unidades/")
        # return redirect(f"/formulariocertificados/?comercio_id={nuevo_comercio.id_comercio}")

    return HttpResponse("Método no permitido", status=405)

def cambiar_estado(request):
    if request.method == "POST":

        unidad = request.POST.get("unidad_id_estatus")
    
        unidad_instance = get_object_or_404(Unidades, id=unidad)
        unidad_detalles = get_object_or_404(Unidades_Detalles, id_unidad=unidad_instance.id)

        unidad_detalles.estado = request.POST.get("nuevo")
        unidad_detalles.save()

        return redirect("/mecanica/unidades/")
        # return redirect(f"/formulariocertificados/?comercio_id={nuevo_comercio.id_comercio}")

    return HttpResponse("Método no permitido", status=405)

def reasignar_division(request):
    if request.method == "POST":
        unidad = request.POST.get("unidad_id_division")
        # nueva_division = request.POST.get("nuevo")
    
        # Obtener la unidad que queremos actualizar
        unidad_instance = get_object_or_404(Unidades, id=unidad)

        # Obtener la lista de divisiones seleccionadas en el formulario
        divisiones_ids = request.POST.getlist("nuevo")  # Lista de IDs

        # Obtener los objetos Divisiones basados en los IDs
        nuevas_divisiones = Divisiones.objects.filter(id__in=divisiones_ids)

        # Asignar las divisiones a la unidad
        unidad_instance.id_division.set(nuevas_divisiones)  # Reemplaza las anteriores

        # # Guardar la unidad con las nuevas divisiones asignadas
        unidad_instance.save()

        return redirect("/mecanica/unidades/")
        # return redirect(f"/formulariocertificados/?comercio_id={nuevo_comercio.id_comercio}")

    return HttpResponse("Método no permitido", status=405)

def obtener_info_unidad(request, id):
    unidad = get_object_or_404(Unidades, id=id)
    detalles = Unidades_Detalles.objects.filter(id_unidad=unidad).first()  # Obtener detalles si existen

    datos = {
        "id": unidad.id,
        "nombre_unidad": unidad.nombre_unidad,
        "divisiones": list(unidad.id_division.values("id", "division")),
        "tipo_vehiculo": detalles.tipo_vehiculo if detalles else "",
        "serial_carroceria": detalles.serial_carroceria if detalles else "",
        "serial_chasis": detalles.serial_chasis if detalles else "",
        "marca": detalles.marca if detalles else "",
        "año": detalles.año if detalles else "",
        "modelo": detalles.modelo if detalles else "",
        "placas": detalles.placas if detalles else "",
        "tipo_filtro_aceite": detalles.tipo_filtro_aceite if detalles else "",
        "tipo_filtro_combustible": detalles.tipo_filtro_combustible if detalles else "",
        "bateria": detalles.bateria if detalles else "",
        "numero_tag": detalles.numero_tag if detalles else "",
        "tipo_bujia": detalles.tipo_bujia if detalles else "",
        "uso": detalles.uso if detalles else "",
        "capacidad_carga": detalles.capacidad_carga if detalles else "",
        "numero_ejes": detalles.numero_ejes if detalles else "",
        "numero_puestos": detalles.numero_puestos if detalles else "",
        "tipo_combustible": detalles.tipo_combustible if detalles else "",
        "tipo_aceite": detalles.tipo_aceite if detalles else "",
        "medida_neumaticos": detalles.medida_neumaticos if detalles else "",
        "tipo_correa": detalles.tipo_correa if detalles else "",
        "estado": detalles.estado if detalles else "",
    }

    return JsonResponse(datos, safe=False)

def mostrar_informacion(request, id):
    # Obtener la unidad y sus detalles
    unidad = get_object_or_404(Unidades, id=id)
    detalles = get_object_or_404(Unidades_Detalles, id_unidad=unidad)

    # Obtener los últimos reportes de cada servicio asociado a la unidad
    ultimos_reportes = (
        Reportes_Unidades.objects
        .filter(id_unidad=unidad)
        .values("servicio")  # Agrupamos por servicio
        .annotate(ultima_fecha=Max("fecha"))  # Obtenemos la última fecha de cada servicio
    )

    # Ahora, obtenemos el reporte más reciente para cada servicio con la fecha obtenida
    reportes_finales = []
    for reporte in ultimos_reportes:
        ultimo_reporte = Reportes_Unidades.objects.filter(
            id_unidad=unidad,
            servicio=reporte["servicio"],
            fecha=reporte["ultima_fecha"]
        ).order_by("-hora").first()  # Si hay más de uno en la misma fecha, toma el más reciente por hora

        if ultimo_reporte:
            reportes_finales.append({
                "id": ultimo_reporte.id,
                "servicio": ultimo_reporte.servicio.nombre_servicio,
                "fecha": ultimo_reporte.fecha.strftime("%Y-%m-%d"),
                "hora": ultimo_reporte.hora.strftime("%H:%M"),
                "descripcion": ultimo_reporte.descripcion,
                "persona_responsable": ultimo_reporte.persona_responsable,
            })

    # Crear la estructura de datos para la respuesta JSON
    datos = {
        "id": unidad.id,
        "nombre_unidad": unidad.nombre_unidad,
        "divisiones": list(unidad.id_division.values("id", "division")),
        "tipo_vehiculo": detalles.tipo_vehiculo,
        "serial_carroceria": detalles.serial_carroceria,
        "serial_chasis": detalles.serial_chasis,
        "marca": detalles.marca,
        "año": detalles.año,
        "modelo": detalles.modelo,
        "placas": detalles.placas,
        "tipo_filtro_aceite": detalles.tipo_filtro_aceite,
        "tipo_filtro_combustible": detalles.tipo_filtro_combustible,
        "bateria": detalles.bateria,
        "numero_tag": detalles.numero_tag,
        "tipo_bujia": detalles.tipo_bujia,
        "uso": detalles.uso,
        "capacidad_carga": detalles.capacidad_carga,
        "numero_ejes": detalles.numero_ejes,
        "numero_puestos": detalles.numero_puestos,
        "tipo_combustible": detalles.tipo_combustible,
        "tipo_aceite": detalles.tipo_aceite,
        "medida_neumaticos": detalles.medida_neumaticos,
        "tipo_correa": detalles.tipo_correa,
        "estado": detalles.estado,
        "ultimos_reportes": reportes_finales  # Se agrega la lista de reportes al JSON final
    }

    return JsonResponse(datos, safe=False)

def eliminar_reporte(request, reporte_id):
    user = request.session.get('user')
    if not user:
        return redirect('/')

    reporte = get_object_or_404(Reportes_Unidades, id=reporte_id)
    reporte.delete()

    return JsonResponse({
        "mensaje": "Reporte Eliminado Correctamente..."
    })



# ========================== Herramientas e Inventario =========================

# 1- Gestion Herramientas
def listar_herramientas(request):
    user = request.session.get('user')
    if not user:
        return redirect('/')

    # --- Capture parameters from the form ---
    nombre_herramienta_query = request.GET.get('nombreHerramienta', '').strip() # Use .strip() to remove leading/trailing whitespace
    serial_herramienta_query = request.GET.get('serialHerramienta', '').strip()
    categoria_seleccionada_id = request.GET.get('categoria', '').strip() # This name matches the form, but let's be explicit

    # Get all categories for the dropdown filter
    categorias = CategoriaHerramienta.objects.all().order_by('nombre')

    # Start with all tools, annotated for available count
    herramientas = Herramienta.objects.annotate(
        asignadas=Count('asignaciones', filter=Q(asignaciones__fecha_devolucion__isnull=True))
    ).order_by('nombre')

    # --- Apply filters based on captured parameters ---

    # Filter by nombreHerramienta (tool name)
    if nombre_herramienta_query:
        herramientas = herramientas.filter(nombre__icontains=nombre_herramienta_query)

    # Filter by serialHerramienta (tool serial number)
    if serial_herramienta_query:
        herramientas = herramientas.filter(numero_serie__icontains=serial_herramienta_query)
        # You might also want to search other fields if 'serialHerramienta' could apply to them,
        # but based on the name, numero_serie seems most appropriate.

    # Filter by categoria (category)
    if categoria_seleccionada_id:
        try:
            # Ensure the category ID is an integer
            categoria_seleccionada_id = int(categoria_seleccionada_id)
            herramientas = herramientas.filter(categoria__id=categoria_seleccionada_id)
        except ValueError:
            # Handle cases where 'categoria' is not a valid integer (e.g., malformed URL)
            pass # Or log an error, ignore the filter, etc.

    # --- Prepare context for the template ---
    return render(request, 'inventario_herramientas/listar_herramientas.html', {
        'herramientas': herramientas,
        'user': user,
        'jerarquia': user.get('jerarquia'), # Use .get() for safer dictionary access
        'nombres': user.get('nombres'),
        'apellidos': user.get('apellidos'),
        
        # Pass back the specific query parameters for form persistence
        'nombreHerramienta': nombre_herramienta_query,
        'serialHerramienta': serial_herramienta_query,
        'categorias': categorias,
        'categoria_seleccionada': categoria_seleccionada_id # Pass the ID back for 'selected' option
    })

def crear_herramienta(request):
    user = request.session.get('user')
    if not user:
        return redirect('/')
    
    if request.method == 'POST':
        form = HerramientaForm(request.POST, request.FILES)
        if form.is_valid():
            herramienta = form.save()
            messages.success(request, f'Herramienta {herramienta.nombre} creada correctamente')
            return redirect('listar-herramientas')
    else:
        form = HerramientaForm()

    return render(request, 'inventario_herramientas/formulario_herramientas.html', {
        'form': form,
        'titulo': 'Nueva Herramienta',
        'user': user,
        'jerarquia': user['jerarquia'],
        'nombres': user['nombres'],
        'apellidos': user['apellidos'],
    })


def editar_herramienta(request, pk):
    user = request.session.get('user')
    if not user:
        return redirect('/')
    
    herramienta = get_object_or_404(Herramienta, pk=pk)
    
    if request.method == 'POST':
        form = HerramientaForm(request.POST, request.FILES, instance=herramienta)
        if form.is_valid():
            herramienta = form.save()
            messages.success(request, f'Herramienta {herramienta.nombre} actualizada')
            return redirect('listar-herramientas')
    else:
        form = HerramientaForm(instance=herramienta)

    return render(request, 'inventario_herramientas/formulario_herramientas.html', {
        'form': form,
        'user': user,
        'titulo': 'Editar Herramienta',
        'jerarquia': user['jerarquia'],
        'nombres': user['nombres'],
        'apellidos': user['apellidos'],
    })


def eliminar_herramienta(request, pk):
    user = request.session.get('user')
    if not user:
        return redirect('/')
    
    herramienta = get_object_or_404(Herramienta, pk=pk)
    
    if request.method == 'POST':
        nombre = herramienta.nombre
        herramienta.delete()
        messages.success(request, f'Herramienta {nombre} eliminada')
        return redirect('listar-herramientas')

    return render(request, 'inventario_herramientas/eliminar_herramienta.html', {
        'herramienta': herramienta,
        'user': user,
        'jerarquia': user['jerarquia'],
        'nombres': user['nombres'],
        'apellidos': user['apellidos'],
    })



def asignacion_unidades(request):
    user = request.session.get('user')
    if not user:
        return redirect('/')

    # Fetch all categories to dynamically create table headers in the template
    categorias = CategoriaHerramienta.objects.all().order_by('nombre')

    # Start with all relevant units, excluding the specified IDs
    unidades_queryset = Unidades.objects.exclude(id__in=[26, 30, 27]).order_by('nombre_unidad')

    if user["user"] == "Operaciones01":
        unidades_queryset = unidades_queryset.filter(id_division=2)
    elif user["user"] == "Rescate03":
        unidades_queryset = unidades_queryset.filter(id_division=1)
    elif user["user"] == "Prevencion05":
        unidades_queryset = unidades_queryset.filter(id_division=3)
    elif user["user"] == "Grumae02":
        unidades_queryset = unidades_queryset.filter(id_division=4)
    elif user["user"] == "Prehospitalaria04":
        unidades_queryset = unidades_queryset.filter(id_division=5)

    unidades_con_detalle = []

    for unidad in unidades_queryset:
        # 1. Calculate the total number of *assigned quantities* for the current unit
        #    We need to SUM the 'cantidad' from AsignacionHerramienta records
        total_asignadas = AsignacionHerramienta.objects.filter(
            unidad=unidad,
            fecha_devolucion__isnull=True
        ).aggregate(
            total_cantidad=Coalesce(Sum('cantidad'), 0) # Sum 'cantidad' field, default to 0 if no assignments
        )['total_cantidad']

        # 2. Get category-wise counts (sum of quantities) for currently assigned tools for THIS unit
        #    This will give us rows like: {'categoria_id': 1, 'categoria_nombre': 'Martillos', 'cantidad_asignada': 5}
        categoria_asignaciones_list = AsignacionHerramienta.objects.filter(
            unidad=unidad,
            fecha_devolucion__isnull=True
        ).values(
            categoria_id=F('herramienta__categoria__id'),
            categoria_nombre=F('herramienta__categoria__nombre')
        ).annotate(
            cantidad_asignada=Coalesce(Sum('cantidad'), 0)
        ).order_by('categoria_nombre')

        # Convert the list of category assignments into a dictionary for easy lookup by category ID
        # e.g., {categoria_id: cantidad_asignada, ...}
        categorias_counts_dict = {
            item['categoria_id']: item['cantidad_asignada']
            for item in categoria_asignaciones_list
        }

        unidades_con_detalle.append({
            'id': unidad.id,
            'nombre_unidad': unidad.nombre_unidad,
            'num_herramientas_total_asignadas': total_asignadas, # Renamed for clarity
            'categorias_counts': categorias_counts_dict,
        })

    return render(request, 'inventario_herramientas/asignar_herramientas.html', {
        "user": user,
        'jerarquia': user.get('jerarquia'), # Use .get() for safer dictionary access
        'nombres': user.get('nombres'),
        'apellidos': user.get('apellidos'),
        'unidades': unidades_con_detalle, # Pass the enriched list
        'categorias': categorias, # Pass all categories for dynamic header
        'seccion_activa': 'asignaciones'
    })


def detalle_asignacion(request, unidad_id):
    user = request.session.get('user')
    if not user:
        return redirect('/')

    unidad = get_object_or_404(Unidades, pk=unidad_id)
    
    # Obtener asignaciones activas
    asignaciones = AsignacionHerramienta.objects.filter(
        unidad=unidad,
        fecha_devolucion__isnull=True
    ).select_related('herramienta', 'herramienta__categoria').order_by('herramienta__nombre')
    
    if request.method == 'POST':
        form = AsignacionMasivaForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    for tool_id, cantidad in form.cleaned_data['selected_tools']:
                        herramienta = Herramienta.objects.get(id=tool_id)
                        
                        # Verificar disponibilidad nuevamente (por si cambió)
                        if cantidad > herramienta.cantidad_disponible:
                            raise ValidationError(f"No hay suficientes unidades de {herramienta.nombre}")
                        
                        # Buscar asignación existente
                        asignacion_existente = AsignacionHerramienta.objects.filter(
                            herramienta=herramienta,
                            unidad=unidad,
                            fecha_devolucion__isnull=True
                        ).first()
                        
                        if asignacion_existente:
                            asignacion_existente.cantidad += cantidad
                            asignacion_existente.save()
                        else:
                            AsignacionHerramienta.objects.create(
                                herramienta=herramienta,
                                unidad=unidad,
                                cantidad=cantidad,
                                fecha_asignacion=timezone.now().date()
                            )
                            
                messages.success(request, 'Asignación completada correctamente')
                return redirect('detalle-asignacion', unidad_id=unidad.id)
            except Exception as e:
                messages.error(request, f'Error durante la asignación: {str(e)}')
    else:
        form = AsignacionMasivaForm()
        formDevolucion = DevolucionCompletaForm()

    context = {
        "user": user,
        'jerarquia': user['jerarquia'],
        'nombres': user['nombres'],
        'apellidos': user['apellidos'],
        'unidad': unidad,
        'asignaciones': asignaciones,
        'form': form,
        'formDevolucion': formDevolucion,
        'seccion_activa': 'asignaciones'
    }
    return render(request, 'inventario_herramientas/detalles_asignacion.html', context)



def devolver_herramienta_completa(request, asignacion_id):
    
    # 1. Obtener la asignación. Esto fallará con un 404 si el ID no existe o ya ha sido devuelto.
    asignacion = get_object_or_404(
        AsignacionHerramienta,
        pk=asignacion_id,
        fecha_devolucion__isnull=True
    )
    
    if request.method == 'POST':   
        # 2. Instancia el formulario con los datos recibidos del POST
        form = DevolucionCompletaForm(request.POST) 

        if form.is_valid():
            try:
                # 4. Iniciar la transacción atómica
                with transaction.atomic():
                    # El formulario ya validó que `responsable` es un objeto Personal válido
                    responsable = form.cleaned_data['responsable'] 
                    observaciones = form.cleaned_data.get('observaciones', '')

                    responsable_instance = Personal.objects.get(pk=responsable.id)
                    
                    # 5. Registrar la devolución
                    devolucion = DevolucionHerramienta.objects.create(
                        asignacion=asignacion,
                        cantidad=asignacion.cantidad,
                        recibido_por=responsable_instance,
                        observaciones=observaciones or "Devolución completa"
                    )
                    
                    # 6. Marcar la asignación como devuelta
                    asignacion.fecha_devolucion = timezone.now().date()
                    asignacion.save()
                    
            except Exception as e:
                messages.error(request, f'Error durante la devolución: {str(e)}')
        else:
            # Mostrar los errores detallados al usuario
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en '{form.fields[field].label}': {error}")

    return redirect('detalle-asignacion', unidad_id=asignacion.unidad.id)


def devolver_herramienta_parcial(request, asignacion_id):
    user = request.session.get('user')
    if not user:
        return redirect('/')

    asignacion = get_object_or_404(
        AsignacionHerramienta,
        pk=asignacion_id,
        fecha_devolucion__isnull=True
    )
    
    if request.method == 'POST':
        form = DevolucionParcialForm(request.POST, instance=asignacion)
        if form.is_valid():
            cantidad_devolver = form.cleaned_data['cantidad_devolver']
            observaciones = form.cleaned_data['observaciones']
            ordenado_por = form.cleaned_data['ordenado_por']

            ordenado_por_instance = Personal.objects.get(id=ordenado_por.id) if ordenado_por else None

            if cantidad_devolver > asignacion.cantidad:
                messages.error(request, 'No puedes devolver más de lo asignado')
                return redirect('detalle-asignacion', unidad_id=asignacion.unidad.id)
            
            # Registrar la devolución
            DevolucionHerramienta.objects.create(
                asignacion=asignacion,
                cantidad=cantidad_devolver,
                observaciones=observaciones,
                recibido_por=ordenado_por_instance
            )
            
            # Actualizar la asignación
            if cantidad_devolver == asignacion.cantidad:
                # Devolución completa
                asignacion.fecha_devolucion = now().date()
                asignacion.save()
                messages.success(request, f'Herramienta devuelta completamente')
            else:
                # Devolución parcial
                asignacion.cantidad -= cantidad_devolver
                asignacion.save()
                messages.success(request, f'Devueltas {cantidad_devolver} unidades de {asignacion.herramienta.nombre}')
            
            return redirect('detalle-asignacion', unidad_id=asignacion.unidad.id)
    else:
        form = DevolucionParcialForm(instance=asignacion)
    
    return render(request, 'inventario_herramientas/devolucion_parcial.html', {
        "user": user,
        'jerarquia': user.get('jerarquia'), # Use .get() for safer dictionary access
        'nombres': user.get('nombres'),
        'apellidos': user.get('apellidos'),
        'form': form,
        'asignacion': asignacion
    })

def reasignar_herramienta(request, asignacion_id):
    user = request.session.get('user')
    if not user:
        return redirect('/')

    asignacion = get_object_or_404(
        AsignacionHerramienta,
        pk=asignacion_id,
        fecha_devolucion__isnull=True
    )
    
    if request.method == 'POST':
        form = ReasignacionForm(
            request.POST, 
            herramienta=asignacion.herramienta,
            unidad_origen=asignacion.unidad  # Pasar la unidad de origen
        )
        if form.is_valid():
            cantidad_reasignar = form.cleaned_data['cantidad_reasignar']
            unidad_destino = form.cleaned_data['unidad_destino']
            observaciones = form.cleaned_data['observaciones']
            ordenado_por = form.cleaned_data['ordenado_por']
            
            ordenado_por_instance = Personal.objects.get(id=ordenado_por.id) if ordenado_por else None

            if cantidad_reasignar > asignacion.cantidad:
                messages.error(request, 'No puedes reasignar más de lo asignado')
                return redirect('detalle-asignacion', unidad_id=asignacion.unidad.id)
            
            try:
                # Verificar si ya existe una asignación activa para la misma herramienta en la unidad destino
                asignacion_existente = AsignacionHerramienta.objects.get(
                    herramienta=asignacion.herramienta,
                    unidad=unidad_destino,
                    fecha_devolucion__isnull=True
                )
                
                # Si existe, sumar la cantidad en lugar de crear nueva asignación
                asignacion_existente.cantidad += cantidad_reasignar
                asignacion_existente.observaciones = f"{asignacion_existente.observaciones or ''}\nReasignación desde {asignacion.unidad.nombre_unidad} el {timezone.now().date()}: +{cantidad_reasignar} unidades. {observaciones}".strip()
                asignacion_existente.save()
                
                mensaje_tipo = 'sumada'
                
            except AsignacionHerramienta.DoesNotExist:
                # Si no existe, crear nueva asignación
                nueva_asignacion = AsignacionHerramienta.objects.create(
                    herramienta=asignacion.herramienta,
                    unidad=unidad_destino,
                    cantidad=cantidad_reasignar,
                    fecha_asignacion=timezone.now().date(),
                    observaciones=f"Reasignado desde {asignacion.unidad.nombre_unidad}. {observaciones}"
                )
                mensaje_tipo = 'reasignada'
            
            # Registrar la reasignación en el historial
            ReasignacionHerramienta.objects.create(
                herramienta=asignacion.herramienta,
                cantidad=cantidad_reasignar,
                unidad_origen=asignacion.unidad,
                unidad_destino=unidad_destino,
                observaciones=observaciones,
                responsable=ordenado_por_instance,
                tipo_operacion='suma' if mensaje_tipo == 'sumada' else 'nueva'
            )
            
            # Actualizar la asignación original
            if cantidad_reasignar == asignacion.cantidad:
                # Reasignación completa
                asignacion.fecha_devolucion = timezone.now().date()
                asignacion.save()
                messages.success(request, f'Herramienta {mensaje_tipo} completamente a {unidad_destino.nombre_unidad}')
            else:
                # Reasignación parcial
                asignacion.cantidad -= cantidad_reasignar
                asignacion.save()
                messages.success(request, f'Reasignadas {cantidad_reasignar} unidades a {unidad_destino.nombre_unidad} ({mensaje_tipo})')
            
            return redirect('detalle-asignacion', unidad_id=asignacion.unidad.id)
    else:
        form = ReasignacionForm(herramienta=asignacion.herramienta, unidad_origen=asignacion.unidad)
    
    return render(request, 'inventario_herramientas/reasignacion.html', {
        "user": user,
        'jerarquia': user.get('jerarquia'), # Use .get() for safer dictionary access
        'nombres': user.get('nombres'),
        'apellidos': user.get('apellidos'),
        'form': form,
        'asignacion': asignacion
    })


def historial_movimientos(request):
    user = request.session.get('user')
    if not user:
        return redirect('/')
    
    # Obtener todas las unidades para el filtro
    unidades = Unidades.objects.all().order_by('nombre_unidad')
    
    # Obtener parámetros de filtro
    unidad_id = request.GET.get('unidad')
    tipo_movimiento = request.GET.get('tipo', 'todos')
    
    # Filtrar devoluciones
    devoluciones = DevolucionHerramienta.objects.select_related(
        'asignacion__herramienta', 'asignacion__unidad'
    ).order_by('-fecha_devolucion')
    
    # Filtrar reasignaciones
    reasignaciones = ReasignacionHerramienta.objects.select_related(
        'herramienta', 'unidad_origen', 'unidad_destino'
    ).order_by('-fecha_reasignacion')
    
    # Aplicar filtros si se especifican
    if unidad_id and unidad_id != 'todas':
        unidad_id = int(unidad_id)
        devoluciones = devoluciones.filter(asignacion__unidad__id=unidad_id)
        reasignaciones = reasignaciones.filter(
            models.Q(unidad_origen__id=unidad_id) | 
            models.Q(unidad_destino__id=unidad_id)
        )
    
    # Filtrar por tipo de movimiento
    if tipo_movimiento != 'todos':
        if tipo_movimiento == 'devoluciones':
            reasignaciones = reasignaciones.none()
        elif tipo_movimiento == 'reasignaciones':
            devoluciones = devoluciones.none()
    
    return render(request, 'inventario_herramientas/historial_movimientos.html', {
        "user": user,
        'jerarquia': user.get('jerarquia'),
        'nombres': user.get('nombres'),
        'apellidos': user.get('apellidos'),
        'devoluciones': devoluciones,
        'reasignaciones': reasignaciones,
        'unidades': unidades,
        'unidad_seleccionada': unidad_id,
        'tipo_seleccionado': tipo_movimiento
    })

# ======================== Conductores ========================

def conductores(request):
    user_data = request.session.get('user')
    if not user_data:
        return redirect('/') # Redirigir a login si no hay sesión

    hoy = date.today()

    # Obtener todos los conductores inicialmente
    # Optimizamos la consulta con select_related y prefetch_related
    conductores_qs = Conductor.objects.select_related('personal').prefetch_related(
        'licencias', 'certificados_medicos'
    ).order_by('personal__nombres', 'personal__apellidos') # Opcional: ordenar para consistencia

    # --- Lógica de Filtrado (la misma que ya tenías) ---
    filter_nombre_conductor = request.GET.get('nombreConductor', '').strip()
    filter_cedula_conductor = request.GET.get('cedulaConductor', '').strip()
    filter_grado_licencia = request.GET.get('gradoLicencia', '').strip() # El valor es '2', '3', '4', '5'

    if filter_nombre_conductor:
        conductores_qs = conductores_qs.filter(
            Q(personal__nombres__icontains=filter_nombre_conductor) |
            Q(personal__apellidos__icontains=filter_nombre_conductor)
        )

    if filter_cedula_conductor:
        conductores_qs = conductores_qs.filter(personal__cedula__icontains=filter_cedula_conductor)

    if filter_grado_licencia:
        # Filtra por el tipo_licencia de las licencias activas y vigentes
        conductores_qs = conductores_qs.filter(
            licencias__tipo_licencia=filter_grado_licencia,
            licencias__activa=True,
            licencias__fecha_vencimiento__gte=hoy # Considera solo licencias vigentes
        ).distinct()
        
    total_conductores = conductores_qs.count()

    # --- Preparar datos para el template ---
    # Esto es similar a lo que hacía tu JS, pero ahora lo hacemos en Python
    conductores_list_for_template = []
    for conductor in conductores_qs:
        licencia_info = {
            'existe': False,
            'badge_class': 'bg-secondary',
            'text': 'Sin licencia',
            'tipo_display': '',
            'vencida': False,
            'multiple_licencias': False,
            'licencia_id': None # Para el modal de detalles
        }
        
        # Encuentra la licencia activa y vigente si existe
        # Nota: Tus @property en el modelo Conductor son útiles aquí
        licencia_activa_vigente = conductor.licencia_activa 
        
        if licencia_activa_vigente:
            vencida = licencia_activa_vigente.fecha_vencimiento < hoy
            licencia_info['existe'] = True
            licencia_info['vencida'] = vencida
            licencia_info['tipo_display'] = licencia_activa_vigente.get_tipo_licencia_display()
            licencia_info['badge_class'] = 'bg-danger' if vencida else 'bg-success'
            licencia_info['text'] = licencia_info['tipo_display']
            if vencida:
                licencia_info['text'] += ' (Vencida)'
            
            # Comprobar si hay más de una licencia (activa o inactiva)
            if conductor.licencias.count() > 1:
                licencia_info['multiple_licencias'] = True
            licencia_info['licencia_id'] = licencia_activa_vigente.id # Puedes necesitar esto para detalles

        certificado_info = {
            'existe': False,
            'badge_class': 'bg-secondary',
            'text': 'Sin certificado',
            'vencido': False,
            'certificado_id': None # Para el modal de detalles
        }
        
        # Encuentra el certificado activo y vigente si existe
        certificado_activo_vigente = conductor.certificado_medico_activo

        if certificado_activo_vigente:
            vencido_cert = certificado_activo_vigente.fecha_vencimiento < hoy
            certificado_info['existe'] = True
            certificado_info['vencido'] = vencido_cert
            certificado_info['badge_class'] = 'bg-danger' if vencido_cert else 'bg-success'
            certificado_info['text'] = 'Vencido' if vencido_cert else 'Vigente'
            certificado_info['certificado_id'] = certificado_activo_vigente.id # Puedes necesitar esto para detalles

        conductores_list_for_template.append({
            'id': conductor.id,
            'nombres': conductor.personal.nombres,
            'apellidos': conductor.personal.apellidos,
            'jerarquia': conductor.personal.jerarquia,
            'cedula': conductor.personal.cedula,
            'licencia': licencia_info,
            'certificado': certificado_info,
            'activo': conductor.activo,
            'estado_badge_class': 'bg-success' if conductor.activo else 'bg-danger',
            'estado_text': 'Activo' if conductor.activo else 'Inactivo',
            # Puedes añadir más datos del conductor aquí si los necesitas en los detalles
            'observaciones_generales': conductor.observaciones_generales,
            'fecha_vencimiento_conductor': conductor.fecha_vencimiento.strftime('%Y-%m-%d') if conductor.fecha_vencimiento else None,
            'todas_las_licencias': [{
                'id': lic.id,
                'tipo_licencia_display': lic.get_tipo_licencia_display(),
                'numero_licencia': lic.numero_licencia,
                'fecha_emision': lic.fecha_emision.strftime('%Y-%m-%d'),
                'fecha_vencimiento': lic.fecha_vencimiento.strftime('%Y-%m-%d'),
                'organismo_emisor': lic.organismo_emisor,
                'restricciones': lic.restricciones,
                'observaciones': lic.observaciones,
                'activa': lic.activa,
                'vencida': lic.fecha_vencimiento < hoy
            } for lic in conductor.licencias.all()],
            'todos_los_certificados': [{
                'id': cert.id,
                'fecha_emision': cert.fecha_emision.strftime('%Y-%m-%d'),
                'fecha_vencimiento': cert.fecha_vencimiento.strftime('%Y-%m-%d'),
                'centro_medico': cert.centro_medico,
                'medico': cert.medico,
                'observaciones': cert.observaciones,
                'activo': cert.activo,
                'vencido': cert.fecha_vencimiento < hoy
            } for cert in conductor.certificados_medicos.all()],
        })

    return render(request, "mecanica/conductores.html", {
        "user": user_data,
        "jerarquia": user_data["jerarquia"],
        "nombres": user_data["nombres"],
        "apellidos": user_data["apellidos"],
        "conductores": conductores_list_for_template, # Pasamos la lista preparada
        "total": total_conductores,
        "hoy": hoy,
        "filterNombreConductor": filter_nombre_conductor,
        "filterCedulaConductor": filter_cedula_conductor,
        "filtro_trimestre": filter_grado_licencia,
    })

def agregar_conductor(request):
    user = request.session.get('user')
    if not user:
        return redirect('/')
    
    if request.method == 'POST':
        form = ConductorForm(request.POST, request.FILES)
        licencia_formset = LicenciaFormSet(request.POST, request.FILES, prefix='licencias')
        certificado_formset = CertificadoMedicoFormSet(
            request.POST, 
            request.FILES, 
            instance=form.instance if form.is_valid() else None,
            prefix='certificados'
        )
        
        if form.is_valid() and licencia_formset.is_valid() and certificado_formset.is_valid():
            conductor = form.save()
            
            # Guardar licencias
            licencias = licencia_formset.save(commit=False)
            for licencia in licencias:
                licencia.conductor = conductor
                licencia.save()
            
            # Guardar certificados
            certificados = certificado_formset.save(commit=False)
            for certificado in certificados:
                certificado.conductor = conductor
                certificado.save()
            
            messages.success(request, 'Conductor registrado exitosamente!')
            return redirect('conductores')
    else:
        form = ConductorForm()
        licencia_formset = LicenciaFormSet(prefix='licencias')
        certificado_formset = CertificadoMedicoFormSet(
            prefix='certificados',
            instance=None  # Para nuevo conductor
        )
    
    return render(request, "mecanica/agregar_conductor.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "form": form,
        "licencia_formset": licencia_formset,
        "certificado_formset": certificado_formset,
    })

def editar_conductor(request, id):
    user = request.session.get('user')
    if not user:
        return redirect('/')

    if id:
        conductor = get_object_or_404(Conductor, pk=id)
        formset_extra = 0  # Modo edición: no agregar formularios extra
    else:
        conductor = None
        formset_extra = 1  # Modo creación: agregar 1 formulario vacío


    LicenciaFormSet = inlineformset_factory(
        Conductor,
        LicenciaConductor,
        form=LicenciaConductorForm,
        formset=LicenciaConductorFormSet,
        extra=formset_extra,  # Dinámico según creación/edición
        can_delete=True
    )
    
    conductor = get_object_or_404(Conductor, id=id)
    
    if request.method == 'POST':
        form = ConductorForm(request.POST, request.FILES, instance=conductor)
        licencia_formset = LicenciaFormSet(request.POST, request.FILES, instance=conductor, prefix='licencias')
        certificado_formset = CertificadoMedicoFormSet(request.POST, request.FILES, instance=conductor, prefix='certificados')
        
        # Validación mejorada
        if form.is_valid():
            conductor = form.save()
            saved = True
            
            # Procesar licencias
            if licencia_formset.is_valid():
                for licencia_form in licencia_formset:
                    if licencia_form.has_changed():
                        if licencia_form.cleaned_data.get('DELETE'):
                            if licencia_form.instance.pk:
                                licencia_form.instance.delete()
                        else:
                            licencia = licencia_form.save(commit=False)
                            licencia.conductor = conductor
                            # Validación manual para evitar duplicados
                            if not licencia.pk:  # Solo para nuevas licencias
                                if LicenciaConductor.objects.filter(
                                    numero_licencia=licencia.numero_licencia,
                                    tipo_licencia=licencia.tipo_licencia
                                ).exists():
                                    messages.error(request, f'La licencia {licencia.numero_licencia} ya existe')
                                    saved = False
                                    break
                            licencia.save()
            else:
                saved = False
                for error in licencia_formset.errors:
                    if '__all__' in error:
                        messages.error(request, error['__all__'])
            
            # Procesar certificados
            if saved and certificado_formset.is_valid():
                for certificado_form in certificado_formset:
                    if certificado_form.has_changed():
                        if certificado_form.cleaned_data.get('DELETE'):
                            if certificado_form.instance.pk:
                                certificado_form.instance.delete()
                        else:
                            certificado = certificado_form.save(commit=False)
                            certificado.conductor = conductor
                            certificado.save()
            elif saved:
                saved = False
                messages.error(request, 'Error en los certificados médicos')
            
            if saved:
                messages.success(request, 'Conductor actualizado exitosamente!')
                return redirect('conductores')
        else:
            messages.error(request, 'Error en el formulario principal')
    
    else:
        form = ConductorForm(instance=conductor)
        licencia_formset = LicenciaFormSet(instance=conductor, prefix='licencias')
        certificado_formset = CertificadoMedicoFormSet(instance=conductor, prefix='certificados')
    
    context = {
        "user": user,
        "form": form,
        "licencia_formset": licencia_formset,
        "certificado_formset": certificado_formset,
        "conductor": conductor,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
    }
    return render(request, "mecanica/editar_conductor.html", context)

def api_conductores(request, id):
    try:
        # Use .get() to retrieve a single object. This raises DoesNotExist if not found.
        # Select_related for 'personal' (one-to-one) and prefetch_related for 'licencias'/'certificados_medicos' (one-to-many)
        conductor = Conductor.objects.select_related('personal').prefetch_related(
            'licencias', 'certificados_medicos'
        ).get(id=id)

        conductor_dict = {
            'id': conductor.id,
            'activo': conductor.activo,
            'observaciones_generales': conductor.observaciones_generales,
            'personal': model_to_dict(conductor.personal), # Convert related 'Personal' object to dictionary
            'licencias': [],
            'certificados_medicos': []
        }

        # Manually serialize licenses and medical certificates
        # This is more efficient than calling model_to_dict on each related object
        # if you only need specific fields.
        for licencia in conductor.licencias.all():
            conductor_dict['licencias'].append({
                'id': licencia.id,
                'tipo_licencia_display': licencia.get_tipo_licencia_display(),
                'numero_licencia': licencia.numero_licencia,
                'fecha_emision': licencia.fecha_emision.isoformat(),
                'fecha_vencimiento': licencia.fecha_vencimiento.isoformat(),
                'organismo_emisor': licencia.organismo_emisor,
                'activa': licencia.activa
            })

        for certificado in conductor.certificados_medicos.all():
            conductor_dict['certificados_medicos'].append({
                'id': certificado.id,
                'fecha_emision': certificado.fecha_emision.isoformat(),
                'fecha_vencimiento': certificado.fecha_vencimiento.isoformat(),
                'centro_medico': certificado.centro_medico,
                'medico': certificado.medico,
                'activo': certificado.activo
            })
            
        # Return the dictionary directly, as it's for a single conductor
        return JsonResponse(conductor_dict, safe=False)

    except Conductor.DoesNotExist:
        # Return a 404 Not Found response if the conductor doesn't exist
        return JsonResponse({'error': 'Conductor no encontrado'}, status=404)
    except Exception as e:
        # Catch any other unexpected errors and return a 500 Internal Server Error
        return JsonResponse({'error': str(e)}, status=500)

@require_http_methods(["DELETE"])
def api_eliminar_conductor(request, id):
    try:
        conductor = Conductor.objects.get(id=id)
        conductor.delete()
        return JsonResponse({'success': True})
    except Conductor.DoesNotExist:
        return JsonResponse({'error': 'Conductor no encontrado'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)





# ====================================================== APIs ======================================================================================

def contar_estados_unidades(request):
    # Obtener todos los estados de las unidades
    estados = Unidades_Detalles.objects.values_list("estado", flat=True)

    # Contar cuántas unidades hay en cada estado
    conteo_estados = Counter(estados)

    # Crear la respuesta JSON
    datos = {
        "activa": conteo_estados.get("🟢 Activo", 0),
        "fuera_de_servicio": conteo_estados.get("🔴 Fuera de Servicio", 0),
        "en_mantenimiento": conteo_estados.get("🟡 Mantenimiento", 0),
    }

    return JsonResponse(datos)

def contar_reportes_combustible(request):
    # Obtener el servicio "Suministro de Combustible"
    try:
        servicio_combustible = Servicios.objects.get(nombre_servicio="Suministro de Combustible")
    except Servicios.DoesNotExist:
        return JsonResponse({"error": "El servicio no existe"}, status=404)

    # Obtener fechas
    hoy = now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())  # Lunes de esta semana
    inicio_mes = hoy.replace(day=1)  # Primer día del mes

    # Contar reportes por día
    reportes_hoy = Reportes_Unidades.objects.filter(
        servicio=servicio_combustible, fecha=hoy
    ).count()

    # Contar reportes por semana
    reportes_semana = Reportes_Unidades.objects.filter(
        servicio=servicio_combustible, fecha__range=[inicio_semana, hoy]
    ).count()

    # Contar reportes por mes
    reportes_mes = Reportes_Unidades.objects.filter(
        servicio=servicio_combustible, fecha__range=[inicio_mes, hoy]
    ).count()

    # Crear respuesta JSON
    datos = {
        "reportes_hoy": reportes_hoy,
        "reportes_semana": reportes_semana,
        "reportes_mes": reportes_mes,
    }

    return JsonResponse(datos)

def contar_reporte_lubricantes(request):
    # Obtener el servicio "Suministro de Combustible"
    try:
        servicio_combustible = Servicios.objects.get(nombre_servicio="Suministro de Lubricantes")
    except Servicios.DoesNotExist:
        return JsonResponse({"error": "El servicio no existe"}, status=404)

    # Obtener fechas
    hoy = now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())  # Lunes de esta semana
    inicio_mes = hoy.replace(day=1)  # Primer día del mes

    # Contar reportes por día
    reportes_hoy = Reportes_Unidades.objects.filter(
        servicio=servicio_combustible, fecha=hoy
    ).count()

    # Contar reportes por semana
    reportes_semana = Reportes_Unidades.objects.filter(
        servicio=servicio_combustible, fecha__range=[inicio_semana, hoy]
    ).count()

    # Contar reportes por mes
    reportes_mes = Reportes_Unidades.objects.filter(
        servicio=servicio_combustible, fecha__range=[inicio_mes, hoy]
    ).count()

    # Crear respuesta JSON
    datos = {
        "reportes_hoy": reportes_hoy,
        "reportes_semana": reportes_semana,
        "reportes_mes": reportes_mes,
    }

    return JsonResponse(datos)

def contar_reporte_neumaticos(request):
    # Obtener el servicio "Suministro de Combustible"
    try:
        servicio_combustible = Servicios.objects.get(nombre_servicio="Cambios de Neumáticos")
    except Servicios.DoesNotExist:
        return JsonResponse({"error": "El servicio no existe"}, status=404)

    # Obtener fechas
    hoy = now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())  # Lunes de esta semana
    inicio_mes = hoy.replace(day=1)  # Primer día del mes

    # Contar reportes por día
    reportes_hoy = Reportes_Unidades.objects.filter(
        servicio=servicio_combustible, fecha=hoy
    ).count()

    # Contar reportes por semana
    reportes_semana = Reportes_Unidades.objects.filter(
        servicio=servicio_combustible, fecha__range=[inicio_semana, hoy]
    ).count()

    # Contar reportes por mes
    reportes_mes = Reportes_Unidades.objects.filter(
        servicio=servicio_combustible, fecha__range=[inicio_mes, hoy]
    ).count()

    # Crear respuesta JSON
    datos = {
        "reportes_hoy": reportes_hoy,
        "reportes_semana": reportes_semana,
        "reportes_mes": reportes_mes,
    }

    return JsonResponse(datos)

def contar_reporte_reparaciones(request):
    # Obtener el servicio "Suministro de Combustible"
    try:
        servicio_combustible = Servicios.objects.get(nombre_servicio="Reparaciones Mecánicas")
    except Servicios.DoesNotExist:
        return JsonResponse({"error": "El servicio no existe"}, status=404)

    # Obtener fechas
    hoy = now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())  # Lunes de esta semana
    inicio_mes = hoy.replace(day=1)  # Primer día del mes

    # Contar reportes por día
    reportes_hoy = Reportes_Unidades.objects.filter(
        servicio=servicio_combustible, fecha=hoy
    ).count()

    # Contar reportes por semana
    reportes_semana = Reportes_Unidades.objects.filter(
        servicio=servicio_combustible, fecha__range=[inicio_semana, hoy]
    ).count()

    # Contar reportes por mes
    reportes_mes = Reportes_Unidades.objects.filter(
        servicio=servicio_combustible, fecha__range=[inicio_mes, hoy]
    ).count()

    # Crear respuesta JSON
    datos = {
        "reportes_hoy": reportes_hoy,
        "reportes_semana": reportes_semana,
        "reportes_mes": reportes_mes,
    }

    return JsonResponse(datos)

def contar_reporte_electricas(request):
    # Obtener el servicio "Suministro de Combustible"
    try:
        servicio_combustible = Servicios.objects.get(nombre_servicio="Reparaciones Eléctricas")
    except Servicios.DoesNotExist:
        return JsonResponse({"error": "El servicio no existe"}, status=404)

    # Obtener fechas
    hoy = now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())  # Lunes de esta semana
    inicio_mes = hoy.replace(day=1)  # Primer día del mes

    # Contar reportes por día
    reportes_hoy = Reportes_Unidades.objects.filter(
        servicio=servicio_combustible, fecha=hoy
    ).count()

    # Contar reportes por semana
    reportes_semana = Reportes_Unidades.objects.filter(
        servicio=servicio_combustible, fecha__range=[inicio_semana, hoy]
    ).count()

    # Contar reportes por mes
    reportes_mes = Reportes_Unidades.objects.filter(
        servicio=servicio_combustible, fecha__range=[inicio_mes, hoy]
    ).count()

    # Crear respuesta JSON
    datos = {
        "reportes_hoy": reportes_hoy,
        "reportes_semana": reportes_semana,
        "reportes_mes": reportes_mes,
    }

    return JsonResponse(datos)

def contar_reporte_cambio_repuestos(request):
    # Obtener el servicio "Suministro de Combustible"
    try:
        servicio_combustible = Servicios.objects.get(nombre_servicio="Cambio de Repuestos")
    except Servicios.DoesNotExist:
        return JsonResponse({"error": "El servicio no existe"}, status=404)

    # Obtener fechas
    hoy = now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())  # Lunes de esta semana
    inicio_mes = hoy.replace(day=1)  # Primer día del mes

    # Contar reportes por día
    reportes_hoy = Reportes_Unidades.objects.filter(
        servicio=servicio_combustible, fecha=hoy
    ).count()

    # Contar reportes por semana
    reportes_semana = Reportes_Unidades.objects.filter(
        servicio=servicio_combustible, fecha__range=[inicio_semana, hoy]
    ).count()

    # Contar reportes por mes
    reportes_mes = Reportes_Unidades.objects.filter(
        servicio=servicio_combustible, fecha__range=[inicio_mes, hoy]
    ).count()

    # Crear respuesta JSON
    datos = {
        "reportes_hoy": reportes_hoy,
        "reportes_semana": reportes_semana,
        "reportes_mes": reportes_mes,
    }

    return JsonResponse(datos)

def contar_reporte_colisiones_danos(request):
    # Obtener el servicio "Colisiones o Daños"
    try:
        servicio_colisiones = Servicios.objects.get(nombre_servicio="Colisiones o Daños")
    except Servicios.DoesNotExist:
        return JsonResponse({"error": "El servicio no existe"}, status=404)

    # Obtener fechas
    hoy = now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())  # Lunes de esta semana
    inicio_mes = hoy.replace(day=1)  # Primer día del mes

    # Contar reportes por día
    reportes_hoy = Reportes_Unidades.objects.filter(
        servicio=servicio_colisiones, fecha=hoy
    ).count()

    # Contar reportes por semana
    reportes_semana = Reportes_Unidades.objects.filter(
        servicio=servicio_colisiones, fecha__range=[inicio_semana, hoy]
    ).count()

    # Contar reportes por mes
    reportes_mes = Reportes_Unidades.objects.filter(
        servicio=servicio_colisiones, fecha__range=[inicio_mes, hoy]
    ).count()

    # Crear respuesta JSON
    datos = {
        "reportes_hoy": reportes_hoy,
        "reportes_semana": reportes_semana,
        "reportes_mes": reportes_mes,
    }

    return JsonResponse(datos)



# =================================== DESCARGAS =================================================
def generar_excel_reportes_unidades(request):
    user = request.session.get('user')
    if not user:
        return redirect('/')

    mes_str = request.GET.get('mes', None)

    # Obtener todos los reportes con las relaciones necesarias
    reportes = Reportes_Unidades.objects.select_related(
        'id_unidad', 'servicio'
    ).prefetch_related('id_unidad__id_division').order_by('-fecha', '-hora')

    # Filtrar por división según el usuario
    if user["user"] == "Operaciones01":
        reportes = reportes.filter(id_unidad__id_division__id=2)
    elif user["user"] == "Rescate03":
        reportes = reportes.filter(id_unidad__id_division__id=1)
    elif user["user"] == "Prevencion05":
        reportes = reportes.filter(id_unidad__id_division__id=3)
    elif user["user"] == "Grumae02":
        reportes = reportes.filter(id_unidad__id_division__id=4)
    elif user["user"] == "Prehospitalaria04":
        reportes = reportes.filter(id_unidad__id_division__id=5)
    else:
        # Para otros usuarios, mostrar todos los reportes
        reportes = reportes.all()

    # Filtrar por mes si se proporciona (manera más eficiente con Django ORM)
    if mes_str:
        try:
            año_mes = mes_str.split('-')
            if len(año_mes) == 2:
                año = int(año_mes[0])
                mes = int(año_mes[1])
                reportes = reportes.filter(fecha__year=año, fecha__month=mes)
            else:
                return JsonResponse({'error': 'Formato de mes incorrecto'}, status=400)
        except (ValueError, IndexError):
            return JsonResponse({'error': 'Formato de mes incorrecto'}, status=400)

    data = []

    for reporte in reportes:
        data.append({
            'nombre unidad': reporte.id_unidad.nombre_unidad,
            'servicio': reporte.servicio.nombre_servicio,
            'fecha': reporte.fecha.isoformat(),
            'hora': reporte.hora.isoformat() if hasattr(reporte.hora, 'isoformat') else str(reporte.hora),
            'descripcion': reporte.descripcion,
            'persona responsable': reporte.persona_responsable,
        })

    df = pd.DataFrame(data)
    
    # Si hay datos, ordenar por fecha
    if not df.empty:
        df = df.sort_values(by=['fecha'], ascending=[False])

    json_data = df.to_json(orient='records', date_format='iso', force_ascii=False)

    return JsonResponse(json.loads(json_data), safe=False)

