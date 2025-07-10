from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, get_object_or_404  
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.utils.timezone import now
import json
import io
import fitz  # PyMuPDF
from .forms import *
from .models import *
from .urls import *
# =============================================================================== APIS PARA LA SECCION DE DRONES ====================================================================
@login_required
def Dashboard_sarp(request):
    user = request.session.get('user')
    drones_disponibles = Drones.objects.all().count()
    operadores_totales = Personal.objects.filter(id__in=[44, 5,53,73]).exclude(id=4).count()
    if not user:
        return redirect('/')
    # Renderizar la página con los datos
    return render(request, "dashboard_sarp.html", {
        "drones_disponibles" : drones_disponibles,
        "operadores_totales" : operadores_totales,
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
    })

def Registros_sarp(request):
    user = request.session.get('user')

    if not user:
        return redirect('/')
    # Renderizar la página con los datos
    return render(request, "registros_sarp.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "formularioDrones": DronesForm,
    })


def registrar_drones(request):
    if request.method == "POST":

        nombre = request.POST.get("nombre_dron")
        id_dron = request.POST.get("id_dron")
        modelo_dron = request.POST.get("modelo_dron")

        # print(nombre, id_dron, modelo_dron)

        Drones.objects.create(
            nombre_dron = nombre,
            id_dron = id_dron,
            modelo_dron = modelo_dron
        )

        return redirect("registros_sarp")

    return HttpResponse("Método no permitido", status=405)

def api_vuelos(request):
    # Obtener parámetros de paginación de la URL (?page=1&limit=5)
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 15))  # Cambiar de 20 a 5

    # Obtener todos los registros
    vuelos = Registro_Vuelos.objects.all().order_by('id_vuelo').values(
        "id", 'id_vuelo', "sitio", 'fecha', 'id_dron__nombre_dron', 
        'id_operador__jerarquia', "id_operador__nombres",
        "id_operador__apellidos", "id_observador__jerarquia", "id_observador__nombres",
        "id_observador__apellidos", "observador_externo"
    )

    # Aplicar paginación
    paginator = Paginator(vuelos, limit)  # Cambia el valor de limit a 5
    vuelos_paginados = paginator.get_page(page)  # Obtener la página actual

    # Procesar detalles de vuelo
    vuelos_con_detalles = []
    for vuelo in vuelos_paginados:
        detalles = DetallesVuelo.objects.filter(id_vuelo=vuelo['id']).values('duracion_vuelo').first()
        vuelo['detalles'] = detalles if detalles else {}  
        vuelos_con_detalles.append(vuelo)

    # Retornar datos con metadatos de paginación
    return JsonResponse({
        "total_paginas": paginator.num_pages,
        "pagina_actual": page,
        "tiene_anterior": vuelos_paginados.has_previous(),
        "tiene_siguiente": vuelos_paginados.has_next(),
        "vuelos": vuelos_con_detalles
    }, safe=False)

def obtener_reporte(request, id_vuelo):
    try:
        # Obtener los objetos relacionados
        vuelo = get_object_or_404(Registro_Vuelos, id_vuelo=id_vuelo)
        estado_dron = EstadoDron.objects.filter(id_vuelo=vuelo).first()
        estado_baterias = EstadoBaterias.objects.filter(id_vuelo=vuelo).first()
        estado_control = EstadoControl.objects.filter(id_vuelo=vuelo).first()
        detalles_vuelo = DetallesVuelo.objects.filter(id_vuelo=vuelo).first()

        # Ruta al archivo PDF plantilla
        template_path = "web/static/assets/Planilla_de_vuelo.pdf"
        doc = fitz.open(template_path)  # Abrimos la plantilla PDF

        # Datos a reemplazar en la plantilla
        data = {
            "vuelo": {
                "id_vuelo": vuelo.id_vuelo,
                "id_operador": vuelo.id_operador.id if vuelo.id_operador else None,
                "operador": f"{vuelo.id_operador.jerarquia} {vuelo.id_operador.nombres} {vuelo.id_operador.apellidos}" if vuelo.id_operador else None,
                "cedula_operador": f"{vuelo.id_operador.cedula}" if vuelo.id_operador else None,
                "id_observador": vuelo.id_observador.id if vuelo.id_observador else None,
                "observador": f"{vuelo.id_observador.jerarquia} {vuelo.id_observador.nombres} {vuelo.id_observador.apellidos}" if vuelo.id_observador else vuelo.observador_externo,
                "cedula_observador": f"{vuelo.id_observador.cedula}" if vuelo.id_observador else None,
                "fecha": str(vuelo.fecha),
                "sitio": vuelo.sitio,
                "hora_despegue": str(vuelo.hora_despegue),
                "hora_aterrizaje": str(vuelo.hora_aterrizaje),
                "id_dron": vuelo.id_dron.id_dron,
                "dron": vuelo.id_dron.nombre_dron,
                "tipo_mision": vuelo.tipo_mision,
                "observaciones": vuelo.observaciones_vuelo,
                "apoyo_realizado_a": vuelo.apoyo_realizado_a,
            },
            "estado_dron": {
                "cuerpo": estado_dron.cuerpo if estado_dron else None,
                "observacion_cuerpo": estado_dron.observacion_cuerpo if estado_dron else None,
                "camara": estado_dron.camara if estado_dron else None,
                "observacion_camara": estado_dron.observacion_camara if estado_dron else None,
                "helices": estado_dron.helices if estado_dron else None,
                "observacion_helices": estado_dron.observacion_helices if estado_dron else None,
                "sensores": estado_dron.sensores if estado_dron else None,
                "observacion_sensores": estado_dron.observacion_sensores if estado_dron else None,
                "motores": estado_dron.motores if estado_dron else None,
                "observacion_motores": estado_dron.observacion_motores if estado_dron else None,
            },
            "estado_baterias": {
                "bateria1": estado_baterias.bateria1 if estado_baterias else None,
                "bateria2": estado_baterias.bateria2 if estado_baterias else None,
                "bateria3": estado_baterias.bateria3 if estado_baterias else None,
                "bateria4": estado_baterias.bateria4 if estado_baterias else None,
            },
            "estado_control": {
                "cuerpo": estado_control.cuerpo if estado_control else None,
                "joysticks": estado_control.joysticks if estado_control else None,
                "pantalla": estado_control.pantalla if estado_control else None,
                "antenas": estado_control.antenas if estado_control else None,
                "bateria_control": estado_control.bateria if estado_control else None,
            },
            "detalles_vuelo": {
                "viento": detalles_vuelo.viento if detalles_vuelo else None,
                "nubosidad": detalles_vuelo.nubosidad if detalles_vuelo else None,
                "riesgo_vuelo": detalles_vuelo.riesgo_vuelo if detalles_vuelo else None,
                "zona_vuelo": detalles_vuelo.zona_vuelo if detalles_vuelo else None,
                "numero_satelites": detalles_vuelo.numero_satelites if detalles_vuelo else None,
                "distancia_recorrida": detalles_vuelo.distancia_recorrida if detalles_vuelo else None,
                "altitud": detalles_vuelo.altitud if detalles_vuelo else None,
                "duracion_vuelo": detalles_vuelo.duracion_vuelo if detalles_vuelo else None,
                "observaciones_vuelo": detalles_vuelo.observaciones if detalles_vuelo else None,
            },
        }

        # Parámetro para ajustar el tamaño de la fuente
        manual_font_size = 8  # Cambia este valor para ajustar el tamaño de fuente

        for page in doc:
            for grupo, valores in data.items():
                if isinstance(valores, dict):  # Manejar subdiccionarios
                    for campo, valor in valores.items():
                        if valor is None:
                            valor = ""  # Usar cadena vacía si el valor es None
                        search_str = f"{{{{{campo}}}}}"
                        text_instances = page.search_for(search_str)
                        for inst in text_instances:
                            x, y, x1, y1 = inst  # Extraemos las dimensiones exactas de la variable del PDF

                            # Crear el rectángulo blanco usando las dimensiones exactas del texto original
                            rect = fitz.Rect(x, y, x1, y1)
                            page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))  # Limpia el área con el parche

                            # Inserta el texto en la posición centrada dentro del área original
                            page.insert_text((x, y), str(valor), fontsize=manual_font_size, color=(0, 0, 0))

        # Guardar el PDF modificado en memoria
        buffer = io.BytesIO()
        doc.save(buffer)
        doc.close()
        buffer.seek(0)

        # Configurar la respuesta HTTP para mostrar el PDF en el navegador
        response = HttpResponse(buffer, content_type="application/pdf")
        response['Content-Disposition'] = 'inline; filename="Reporte_Vuelo.pdf"'

        return response
    except Exception as e:
        print(f"Error al generar el reporte: {e}")
        return HttpResponse(f"Hubo un error al generar el reporte: {str(e)}", status=500)

def editar_reporte(request, id_vuelo):
    vuelo = get_object_or_404(Registro_Vuelos, id_vuelo=id_vuelo)
    
    estado_dron = EstadoDron.objects.filter(id_vuelo=vuelo).first()
    estado_baterias = EstadoBaterias.objects.filter(id_vuelo=vuelo).first()
    estado_control = EstadoControl.objects.filter(id_vuelo=vuelo).first()
    detalles_vuelo = DetallesVuelo.objects.filter(id_vuelo=vuelo).first()

    data = {
        "vuelo": {
            "id_vuelo": vuelo.id_vuelo,
            "id_operador": vuelo.id_operador.id if vuelo.id_operador else None,
            "operador": f'{vuelo.id_operador.jerarquia} {vuelo.id_operador.nombres} {vuelo.id_operador.apellidos}' if vuelo.id_observador else None,
            "id_observador": vuelo.id_observador.id if vuelo.id_observador else None,
            "observador": f'{vuelo.id_observador.jerarquia} {vuelo.id_observador.nombres} {vuelo.id_observador.apellidos}' if vuelo.id_observador else None,
            "observador_externo": vuelo.observador_externo,
            "fecha": str(vuelo.fecha),
            "sitio": vuelo.sitio,
            "hora_despegue": str(vuelo.hora_despegue),
            "hora_aterrizaje": str(vuelo.hora_aterrizaje),
            "id_dron": vuelo.id_dron.id_dron,
            "dron": vuelo.id_dron.nombre_dron,
            "tipo_mision": vuelo.tipo_mision,
            "observaciones_vuelo": vuelo.observaciones_vuelo,
            "apoyo_realizado_a": vuelo.apoyo_realizado_a,
        },
        "estado_dron": {
            "cuerpo": estado_dron.cuerpo,
            "observacion_cuerpo": estado_dron.observacion_cuerpo,
            "camara": estado_dron.camara,
            "observacion_camara": estado_dron.observacion_camara,
            "helices": estado_dron.helices,
            "observacion_helices": estado_dron.observacion_helices,
            "sensores": estado_dron.sensores,
            "observacion_sensores": estado_dron.observacion_sensores,
            "motores": estado_dron.motores,
            "observacion_motores": estado_dron.observacion_motores,
        } if estado_dron else None,
        "estado_baterias": {
            "bateria1": estado_baterias.bateria1,
            "bateria2": estado_baterias.bateria2,
            "bateria3": estado_baterias.bateria3,
            "bateria4": estado_baterias.bateria4,
        } if estado_baterias else None,
        "estado_control": {
            "cuerpo": estado_control.cuerpo,
            "joysticks": estado_control.joysticks,
            "pantalla": estado_control.pantalla,
            "antenas": estado_control.antenas,
            "bateria": estado_control.bateria,
        } if estado_control else None,
        "detalles_vuelo": {
            "viento": detalles_vuelo.viento,
            "nubosidad": detalles_vuelo.nubosidad,
            "riesgo_vuelo": detalles_vuelo.riesgo_vuelo,
            "zona_vuelo": detalles_vuelo.zona_vuelo,
            "numero_satelites": detalles_vuelo.numero_satelites,
            "distancia_recorrida": detalles_vuelo.distancia_recorrida,
            "altitud": detalles_vuelo.altitud,
            "duracion_vuelo": detalles_vuelo.duracion_vuelo,
            "observaciones": detalles_vuelo.observaciones,
        } if detalles_vuelo else None,
    }

    return JsonResponse(data, safe=False)

def api_eliminar_vuelo(request, id_vuelo):
    if request.method == "DELETE":
        vuelo = Registro_Vuelos.objects.filter(id_vuelo=id_vuelo).first()
        if vuelo:
            vuelo.delete()
            return JsonResponse({"message": "Vuelo eliminado correctamente"}, status=200)
        else:
            return JsonResponse({"error": "Vuelo no encontrado"}, status=404)
    return JsonResponse({"error": "Método no permitido"},status=405)

def obtener_estadisticas_misiones(request):
    """
    API que devuelve la cantidad de misiones diarias, semanales y mensuales.
    """
    hoy = now().date()
    inicio_semana = hoy - timedelta(days=hoy.weekday())  # Lunes de la semana actual
    inicio_mes = hoy.replace(day=1)  # Primer día del mes actual

    misiones_diarias = Registro_Vuelos.objects.filter(fecha=hoy).count()
    misiones_semanales = Registro_Vuelos.objects.filter(fecha__gte=inicio_semana).count()
    misiones_mensuales = Registro_Vuelos.objects.filter(fecha__gte=inicio_mes).count()

    return JsonResponse({
        "mision_diario": misiones_diarias,
        "mision_semanal": misiones_semanales,
        "mision_mensual": misiones_mensuales
    })

def obtener_ultimo_reporte(request):
    """
    API que devuelve la información del último vuelo registrado.
    """
    ultimo_vuelo = Registro_Vuelos.objects.order_by('-fecha', '-id').first()

    if not ultimo_vuelo:
        return JsonResponse({
            "error": "No hay reportes disponibles",
            "status": "empty"
        }, status=200)  # Cambiado a 200 para manejar más fácil en el frontend

    return JsonResponse({
        "id_vuelo": ultimo_vuelo.id_vuelo,
        "fecha": str(ultimo_vuelo.fecha),
        "sitio": ultimo_vuelo.sitio,
        "dron": ultimo_vuelo.id_dron.nombre_dron,
        "tipo_mision": ultimo_vuelo.tipo_mision,
        "status": "success"
    })

def buscar_vuelo_por_id(request, vuelo_id):
    # Verifica si existe el vuelo
    if not Registro_Vuelos.objects.filter(id_vuelo=vuelo_id).exists():
        return JsonResponse({'error': 'No existe ningún vuelo con ese ID'}, status=200)

    vuelo_buscador = Registro_Vuelos.objects.filter(id_vuelo=vuelo_id).values(
        "id", 'id_vuelo', "sitio", 'fecha', 'id_dron__nombre_dron', 
        'id_operador__jerarquia', "id_operador__nombres",
        "id_operador__apellidos", "id_observador__jerarquia", "id_observador__nombres",
        "id_observador__apellidos", "observador_externo"
    )

    # Procesar detalles de vuelo
    vuelos_con_detalles = []
    for vuelo in vuelo_buscador:
        detalles = DetallesVuelo.objects.filter(id_vuelo=vuelo['id']).values('duracion_vuelo').first()
        vuelo['detalles'] = detalles if detalles else {}  
        vuelos_con_detalles.append(vuelo)

    return JsonResponse(vuelos_con_detalles, safe=False)


# Exporar reportes en excel
def generar_excel_reportes_sarp(request):
    mes_str = request.GET.get('mes', None)
    
    vuelos_queryset = Registro_Vuelos.objects.select_related('id_dron', 'id_operador').order_by('-fecha', '-hora_despegue')

    if mes_str:
        try:
            year, month = map(int, mes_str.split('-'))
            
            # --- DEPURACIÓN: Qué año y mes estamos usando para filtrar ---

            vuelos_queryset = vuelos_queryset.filter(
                fecha__year=year,
                fecha__month=month
            )
        except (ValueError, IndexError):
            # Esto debería ser capturado por tu frontend si hay un error de formato
            return JsonResponse({'error': 'Formato de mes incorrecto. Se espera YYYY-MM.'}, status=400)
    
    vuelos_encontrados = list(vuelos_queryset) 

    data = []

    # Iteramos sobre la lista ya materializada para construir la respuesta
    for vuelo in vuelos_encontrados: # Usamos vuelos_encontrados aquí
        nombre_operador = vuelo.id_operador.nombres if vuelo.id_operador else "Sin asignar"

        data.append({
            'fecha': vuelo.fecha.isoformat(),
            'hora': vuelo.hora_despegue.isoformat(timespec='minutes'),
            'encargado': nombre_operador,
            'descripcion': vuelo.observaciones_vuelo,
            'tipo_mision': vuelo.tipo_mision,
        })

    return JsonResponse(data, safe=False)

def Formularios_sarp(request):
    user = request.session.get('user')

    if not user:
        return redirect('/')

    vuelo_instance = None

    if request.method == "POST":
        vuelo_id = request.POST.get("id_vuelo")  # Verifica si hay un vuelo existente

        # Cargar datos del formulario
        vuelo_form = RegistroVuelosForm(request.POST)
        dron_form = EstadoDronForm(request.POST)
        baterias_form = EstadoBateriasForm(request.POST)
        control_form = EstadoControlForm(request.POST)
        detalles_form = DetallesVueloForm(request.POST)

        if (vuelo_form.is_valid() and dron_form.is_valid() and
            baterias_form.is_valid() and control_form.is_valid() and detalles_form.is_valid()):

            dron = vuelo_form.cleaned_data["id_dron"]
            operador = vuelo_form.cleaned_data["id_operador"]
            observador = vuelo_form.cleaned_data["id_observador"]

            dron_instance = Drones.objects.get(id_dron=dron)
            operador_instance = Personal.objects.get(id=operador)
            observador_instance = Personal.objects.get(id=observador)

            if vuelo_id:  # Si hay un ID de vuelo, actualizarlo
                vuelo_instance = Registro_Vuelos.objects.get(id_vuelo=vuelo_id)
                vuelo_instance.id_operador = operador_instance
                vuelo_instance.id_observador = observador_instance
                vuelo_instance.observador_externo = vuelo_form.cleaned_data["observador_externo"]
                vuelo_instance.fecha = vuelo_form.cleaned_data["fecha"]
                vuelo_instance.sitio = vuelo_form.cleaned_data["sitio"]
                vuelo_instance.hora_despegue = vuelo_form.cleaned_data["hora_despegue"]
                vuelo_instance.hora_aterrizaje = vuelo_form.cleaned_data["hora_aterrizaje"]
                vuelo_instance.id_dron = dron_instance
                vuelo_instance.tipo_mision = vuelo_form.cleaned_data["tipo_mision"]
                vuelo_instance.observaciones_vuelo = vuelo_form.cleaned_data["observaciones_vuelo"]
                vuelo_instance.apoyo_realizado_a = vuelo_form.cleaned_data["apoyo_realizado_a"]
                vuelo_instance.save()  # Guardar los cambios

            else:  # Si no hay ID, crear un nuevo vuelo
                vuelo_instance = Registro_Vuelos.objects.create(
                    id_operador=operador_instance,
                    id_observador=observador_instance,
                    observador_externo=vuelo_form.cleaned_data["observador_externo"],
                    fecha=vuelo_form.cleaned_data["fecha"],
                    sitio=vuelo_form.cleaned_data["sitio"],
                    hora_despegue=vuelo_form.cleaned_data["hora_despegue"],
                    hora_aterrizaje=vuelo_form.cleaned_data["hora_aterrizaje"],
                    id_dron=dron_instance,
                    tipo_mision=vuelo_form.cleaned_data["tipo_mision"],
                    observaciones_vuelo=vuelo_form.cleaned_data["observaciones_vuelo"],
                    apoyo_realizado_a=vuelo_form.cleaned_data["apoyo_realizado_a"]
                )

            # Actualizar o crear Estado del Dron
            EstadoDron.objects.update_or_create(
                id_vuelo=vuelo_instance,
                id_dron=vuelo_instance.id_dron,
                defaults={
                    "cuerpo": dron_form.cleaned_data["cuerpo"],
                    "observacion_cuerpo": dron_form.cleaned_data["observacion_cuerpo"],
                    "camara": dron_form.cleaned_data["camara"],
                    "observacion_camara": dron_form.cleaned_data["observacion_camara"],
                    "helices": dron_form.cleaned_data["helices"],
                    "observacion_helices": dron_form.cleaned_data["observacion_helices"],
                    "sensores": dron_form.cleaned_data["sensores"],
                    "observacion_sensores": dron_form.cleaned_data["observacion_sensores"],
                    "motores": dron_form.cleaned_data["motores"],
                    "observacion_motores": dron_form.cleaned_data["observacion_motores"],
                }
            )

            # Actualizar o crear Estado de las Baterías
            EstadoBaterias.objects.update_or_create(
                id_vuelo=vuelo_instance,
                id_dron=vuelo_instance.id_dron,
                defaults={
                    "bateria1": baterias_form.cleaned_data["bateria1"],
                    "bateria2": baterias_form.cleaned_data["bateria2"],
                    "bateria3": baterias_form.cleaned_data["bateria3"],
                    "bateria4": baterias_form.cleaned_data["bateria4"],
                }
            )

            # Actualizar o crear Estado del Control
            EstadoControl.objects.update_or_create(
                id_vuelo=vuelo_instance,
                id_dron=vuelo_instance.id_dron,
                defaults={
                    "cuerpo": control_form.cleaned_data["cuerpo_control"],
                    "joysticks": control_form.cleaned_data["joysticks"],
                    "pantalla": control_form.cleaned_data["pantalla"],
                    "antenas": control_form.cleaned_data["antenas"],
                    "bateria": control_form.cleaned_data["bateria"],
                }
            )

            # Actualizar o crear Detalles del Vuelo
            DetallesVuelo.objects.update_or_create(
                id_vuelo=vuelo_instance,
                defaults={
                    "viento": detalles_form.cleaned_data["viento"],
                    "nubosidad": detalles_form.cleaned_data["nubosidad"],
                    "riesgo_vuelo": detalles_form.cleaned_data["riesgo_vuelo"],
                    "zona_vuelo": detalles_form.cleaned_data["zona_vuelo"],
                    "numero_satelites": detalles_form.cleaned_data["numero_satelites"],
                    "distancia_recorrida": f"{detalles_form.cleaned_data['distancia_recorrida']} {detalles_form.cleaned_data['magnitud_distancia']}",
                    "altitud": detalles_form.cleaned_data["altitud"],
                    "duracion_vuelo": detalles_form.cleaned_data["duracion_vuelo"],
                    "observaciones": detalles_form.cleaned_data["observaciones"],
                }
            )

            return redirect("registros_sarp")

    else:
        vuelo_form = RegistroVuelosForm()
        dron_form = EstadoDronForm()
        baterias_form = EstadoBateriasForm()
        control_form = EstadoControlForm()
        detalles_form = DetallesVueloForm()

    return render(request, "formulario_sarp.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "formularioVuelos": vuelo_form,
        "formularioEstadoDron": dron_form,
        "formularioEstadoBaterias": baterias_form,
        "formularioEstadoControl": control_form,
        "formularioDetallesVuelo": detalles_form,
    })
