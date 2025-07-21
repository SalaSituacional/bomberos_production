from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, get_object_or_404  
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
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

    # --- Captura de parámetros de filtro ---
    filter_registro = request.GET.get('filterRegistro')
    filter_fecha_registro = request.GET.get('filterFechaRegistro')
    filter_operador_id = request.GET.get('filterOperador')

    # --- Construcción del queryset base ---
    registros_vuelos_list = Registro_Vuelos.objects.all().order_by('-fecha', '-hora_despegue') # Good practice to order your results

    # --- Aplicación de filtros condicionales ---
    if filter_registro:
        registros_vuelos_list = registros_vuelos_list.filter(
            Q(id_vuelo__icontains=filter_registro) | 
            Q(observaciones_vuelo__icontains=filter_registro) # Added back observations filter for completeness
        )

    if filter_fecha_registro:
        registros_vuelos_list = registros_vuelos_list.filter(fecha=filter_fecha_registro)

    if filter_operador_id:
        try:
            filter_operador_id = int(filter_operador_id)
            registros_vuelos_list = registros_vuelos_list.filter(id_operador__id=filter_operador_id)
        except (ValueError, TypeError):
            pass

    # --- Pagination Logic ---
    paginator = Paginator(registros_vuelos_list, 10)  # Show 10 records per page, adjust as needed
    page = request.GET.get('page') # Get the current page number from the URL

    try:
        registros_vuelos_paginated = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        registros_vuelos_paginated = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        registros_vuelos_paginated = paginator.page(paginator.num_pages)

    operadores_disponibles = Personal.objects.filter(
        id__in=[44,5,53,73]
    ).exclude(id=4)

    # Renderizar la página con los datos paginados y los valores de filtro
    return render(request, "registros_sarp.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "formularioDrones": DronesForm,
        "registros_vuelos": registros_vuelos_paginated, # *** THIS IS THE KEY CHANGE ***
        "filterRegistro": filter_registro,
        "filterFechaRegistro": filter_fecha_registro,
        "filterOperador": filter_operador_id, 
        "operadores_disponibles": operadores_disponibles,
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

def crear_o_editar_reporte(request, id_vuelo=None): # id_vuelo is optional for creation
    user = request.session.get('user')

    if not user:
        return redirect('/')

    editing = False
    vuelo = None
    estado_dron_instance = None
    estado_baterias_instance = None
    estado_control_instance = None
    detalles_vuelo_instance = None

    if id_vuelo: # If an id_vuelo is provided, we are in edit mode
        editing = True
        vuelo = get_object_or_404(Registro_Vuelos, id_vuelo=id_vuelo)
        
        # Get related instances, or None if they don't exist
        estado_dron_instance = EstadoDron.objects.filter(id_vuelo=vuelo).first()
        estado_baterias_instance = EstadoBaterias.objects.filter(id_vuelo=vuelo).first()
        estado_control_instance = EstadoControl.objects.filter(id_vuelo=vuelo).first()
        detalles_vuelo_instance = DetallesVuelo.objects.filter(id_vuelo=vuelo).first()

    if request.method == 'POST':
        # If editing, pass the instance to the form to pre-populate and update
        form_vuelos = RegistroVuelosForm(request.POST, instance=vuelo)
        form_estado_dron = EstadoDronForm(request.POST, instance=estado_dron_instance)
        form_estado_baterias = EstadoBateriasForm(request.POST, instance=estado_baterias_instance)
        form_estado_control = EstadoControlForm(request.POST, instance=estado_control_instance)
        form_detalles_vuelo = DetallesVueloForm(request.POST, instance=detalles_vuelo_instance)

        # Validate all forms
        if (form_vuelos.is_valid() and 
            form_estado_dron.is_valid() and 
            form_estado_baterias.is_valid() and 
            form_estado_control.is_valid() and 
            form_detalles_vuelo.is_valid()):
            
            # Save the main flight record
            vuelo_obj = form_vuelos.save(commit=False)
            if not editing: # Only generate id_vuelo for new records
                # The save method of Registro_Vuelos model handles id_vuelo generation
                pass 
            vuelo_obj.save() # Save Registro_Vuelos instance first

            # Save related forms, linking them to the main flight record
            # For related objects, use get_or_create or filter().first() based on your logic
            # Here, we create/update based on whether an instance already existed
            
            print(vuelo_obj)

            estado_dron_obj = form_estado_dron.save(commit=False)
            estado_dron_obj.id_vuelo = vuelo_obj
            estado_dron_obj.id_dron = vuelo_obj.id_dron
            estado_dron_obj.save()

            estado_baterias_obj = form_estado_baterias.save(commit=False)
            estado_baterias_obj.id_vuelo = vuelo_obj
            estado_baterias_obj.id_dron = vuelo_obj.id_dron
            estado_baterias_obj.save()

            estado_control_obj = form_estado_control.save(commit=False)
            estado_control_obj.id_vuelo = vuelo_obj
            estado_control_obj.id_dron = vuelo_obj.id_dron
            estado_control_obj.save()

            detalles_vuelo_obj = form_detalles_vuelo.save(commit=False)
            detalles_vuelo_obj.id_vuelo = vuelo_obj
            detalles_vuelo_obj.save()

            # Optional: Add a success message
            if editing:
                # messages.success(request, 'Reporte de vuelo actualizado exitosamente!')
                return redirect('registros_sarp') # Redirect to the list view after update
            else:
                # messages.success(request, 'Reporte de vuelo creado exitosamente!')
                return redirect('registros_sarp') # Redirect to the list view after creation

    else: # GET request: instantiate forms with existing data for editing or blank for creation
        form_vuelos = RegistroVuelosForm(instance=vuelo)
        form_estado_dron = EstadoDronForm(instance=estado_dron_instance)
        form_estado_baterias = EstadoBateriasForm(instance=estado_baterias_instance)
        form_estado_control = EstadoControlForm(instance=estado_control_instance)
        form_detalles_vuelo = DetallesVueloForm(instance=detalles_vuelo_instance)

    # Pass all forms to the template
    return render(request, "formulario_sarp.html", { # Assuming 'formularios_sarp.html' is your form template
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "formularioDrones": DronesForm, # For the 'Agregar Dron' modal
        "formularioVuelos": form_vuelos,
        "formularioEstadoDron": form_estado_dron,
        "formularioEstadoBaterias": form_estado_baterias,
        "formularioEstadoControl": form_estado_control,
        "formularioDetallesVuelo": form_detalles_vuelo,
        "editing": editing, # Pass this flag to the template for conditional display
        # You might also want to pass the original vuelo object if needed for context
        "vuelo_original": vuelo
    })

# =================================== APIs ================================================
def api_eliminar_vuelo(request, id_vuelo):
    if request.method == "GET":
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

# ================================== Exporar reportes en excel =============================
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

