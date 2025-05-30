from django.shortcuts import render, redirect
from .models import *
from .forms import *
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
import io
import json
from web.views.views import *
from web.views.views_descargas import *

# Create your views here.
def certificados_prevencion(request):
    user = request.session.get('user')
    if not user:
        return redirect('/')

    numero_expediente = request.GET.get('numero_expediente', '')
    rif_empresarial = request.GET.get('rif_empresarial', '').strip()
    
    # Obtener el total de registros en la base de datos
    total_comercios = Comercio.objects.count()
    # Inicialmente, la tabla estará vacía
    comercios = Comercio.objects.none()

    # Si el usuario busca, filtra los resultados
    if numero_expediente == "GET ALL":
        comercios = list(Comercio.objects.all())
        comercios = [{'id': comercio.id, 'id_comercio': comercio.id_comercio, 'nombre_comercio': comercio.nombre_comercio, 'rif_empresarial': comercio.rif_empresarial} for comercio in comercios]
    
    if numero_expediente and numero_expediente!="GET ALL":
        # Filtra por numero_expediente
        comercios = Comercio.objects.filter(id_comercio__icontains=numero_expediente)

    elif rif_empresarial:
        # Filtra por rif_empresarial
        comercios = Comercio.objects.filter(rif_empresarial__icontains=rif_empresarial)

    return render(request, "Seguridad-prevencion/solicitudes.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "comercios": comercios,
        "conteo": total_comercios,  # Mantiene el conteo total fijo
        "numero_expediente": numero_expediente,
        "rif_empresarial": rif_empresarial,
    })


def formulario_certificado_prevencion(request):
    user = request.session.get('user')
    if not user:
            return redirect('/')


    return render(request, "Seguridad-prevencion/formularioSolicitud.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "solicitud": Formulario_Solicitud,
        "requisitos": Formularia_Requisitos,
        "comercio": Comercios,
    })


def planilla_certificado(request):
    user = request.session.get('user')
    if not user:
            return redirect('/')

    return render(request, "Seguridad-prevencion/planillaCertificadoDeConformidad.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
    })


def obtener_ultimo_reporte_solicitudes(request):
    ultimo = Solicitudes.objects.select_related('id_solicitud').order_by('-id').first()

    if not ultimo:
        return JsonResponse({'error': 'No existen reportes aún'}, status=404)

    data = {
        'id': ultimo.id,
        'fecha_solicitud': ultimo.fecha_solicitud,
        'hora_solicitud': ultimo.hora_solicitud,
        'tipo_servicio': ultimo.tipo_servicio,
        'solicitante': ultimo.solicitante_nombre_apellido,
        'comercio': ultimo.id_solicitud.nombre_comercio,
        'id_comercio': ultimo.id_solicitud.id_comercio,
    }

    return JsonResponse(data)


def api_get_solicitudes(request, referencia):
    solicitudes = Solicitudes.objects.filter(id_solicitud__id_comercio=referencia)
    data = []
    documentos = True
    hoy = datetime.today().date()
    proximo_mes = hoy + timedelta(days=30)

    for solicitud in solicitudes:
        requisitos = Requisitos.objects.filter(id_solicitud=solicitud)
        
        requisitos_faltantes = []
        documentos_proximos_vencer = []
        documentos_vencidos = []

        if requisitos.exists():
            req = requisitos.first()
            
            # Verificar requisitos faltantes
            if not req.cedula_identidad:
                requisitos_faltantes.append("Cédula de identidad")
            if not req.rif_representante:
                requisitos_faltantes.append("RIF del representante")
            if not req.rif_comercio:
                requisitos_faltantes.append("RIF del comercio")
            if not req.permiso_anterior:
                requisitos_faltantes.append("Permiso anterior")
            if not req.registro_comercio:
                requisitos_faltantes.append("Registro de comercio")
            if not req.documento_propiedad:
                requisitos_faltantes.append("Documento de propiedad")
            if not req.cedula_catastral:
                requisitos_faltantes.append("Cédula catastral")
            if not req.carta_autorizacion:
                requisitos_faltantes.append("Carta de autorización")
            if not req.plano_bomberil:
                requisitos_faltantes.append("Plano bomberil")

            # Verificar documentos próximos a vencer o ya vencidos
            documentos_vencimiento = {
                "Cédula de identidad": req.cedula_vencimiento,
                "RIF del representante": req.rif_representante_vencimiento,
                "RIF del comercio": req.rif_comercio_vencimiento,
                "Documento de propiedad": req.documento_propiedad_vencimiento,
                "Cédula catastral": req.cedula_catastral_vencimiento,
            }

            for nombre_doc, fecha_vencimiento in documentos_vencimiento.items():
                if fecha_vencimiento:
                    if fecha_vencimiento < hoy:
                        documentos_vencidos.append(f"{nombre_doc} (venció el {fecha_vencimiento})")
                    elif hoy <= fecha_vencimiento <= proximo_mes:
                        documentos_proximos_vencer.append(f"{nombre_doc} (vence el {fecha_vencimiento})")

        else:
            requisitos_faltantes.append("No hay requisitos registrados para esta solicitud")
            documentos = False
        
        data.append({
            "id_solicitud": solicitud.id,
            "id": solicitud.id_solicitud.id_comercio,
            "fecha": solicitud.fecha_solicitud,
            "solicitante": solicitud.solicitante_nombre_apellido,
            "tipo_solicitud": solicitud.tipo_servicio,
            "papeles_incompletos": bool(requisitos_faltantes),
            "documentos_faltantes": requisitos_faltantes if requisitos_faltantes else ["Todos los documentos están en orden"],
            "documentos_proximos_vencer": documentos_proximos_vencer if documentos_proximos_vencer else ["No hay documentos próximos a vencer"],
            "documentos_vencidos": documentos_vencidos if documentos_vencidos else ["No hay documentos vencidos"],
            "documentos": documentos
        })
    
    return JsonResponse(data, safe=False)


def doc_Guia(request, id):
    solicitud = get_object_or_404(Solicitudes, id=id)
    datos_solicitud = get_object_or_404(Comercio, id_comercio=solicitud.id_solicitud.id_comercio)
    requisitos = get_object_or_404(Requisitos, id_solicitud=solicitud.id)
    
    # Ruta al archivo PDF plantilla en tu directorio estático
    template_path = "web/static/assets/Solictud_2025.pdf"
    doc = fitz.open(template_path)  # Abrimos la plantilla PDF

    # Datos para reemplazar en la plantilla
    datos = {
            "ID_Comercio": str(datos_solicitud.id_comercio),
            "Fecha_Solicitud": str(solicitud.fecha_solicitud),
            "Hora": str(solicitud.hora_solicitud),
            "Tipo_Servicio": str(solicitud.tipo_servicio),
            "Solicitante": str(solicitud.solicitante_nombre_apellido),
            "CI": str(solicitud.solicitante_cedula),
            "Tipo_Representante": str(solicitud.tipo_representante),
            "Nombre_Comercio": str(datos_solicitud.nombre_comercio),
            "Rif_Empresarial": str(datos_solicitud.rif_empresarial),
            "Rif_Representante_Legal": str(solicitud.rif_representante_legal),
            "Direccion": str(solicitud.direccion),
            "Estado": str(solicitud.estado),
            "Municipio": str(solicitud.municipio),
            "Parroquia": str(solicitud.parroquia),
            "Telefono": str(solicitud.numero_telefono),
            "Correo_Electronico": str(solicitud.correo_electronico),
            "Pago_Tasa_Servicio": str(solicitud.pago_tasa),
            "Metodo_Pago": str(solicitud.metodo_pago),
            "Referencia": str(solicitud.referencia),
            "Status_Cedula": "Completado" if requisitos.cedula_identidad else "Incompleto",
            "Status_Rif": "Completado" if requisitos.rif_representante else "Incompleto",
            "Status_Comercio": "Completado" if requisitos.rif_comercio else "Incompleto",
            "Status_Permiso": "Completado" if requisitos.permiso_anterior else "Incompleto",
            "Status_Registro_Comercio": "Completado" if requisitos.registro_comercio else "Incompleto",
            "Status_Documento_Propiedad": "Completado" if requisitos.documento_propiedad else "Incompleto",
            "Status_Cedula_Catastral": "Completado" if requisitos.cedula_catastral else "Incompleto",
            "Status_Carta_Autorizacion": "Completado" if requisitos.carta_autorizacion else "Incompleto",
            "Status_Plano": "Completado" if requisitos.plano_bomberil else "Incompleto",
    }

    # Rellenar la plantilla PDF
    for page in doc:
        for campo, valor in datos.items():
            # Buscar las etiquetas sin espacios, como {{ID_Comercio}}
            search_str = f"{{{{{campo}}}}}" 
            text_instances = page.search_for(search_str)

            for inst in text_instances:
                x, y, x1, y1 = inst  # Obtener coordenadas
                y_adjusted = y + 7.5  # Ajustar la coordenada Y hacia abajo en 7.5 unidades (ajusta este valor según sea necesario)
                # Borrar el texto anterior
                rect = fitz.Rect(x, y, x1, y1)
                page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                # Insertar el nuevo texto en la posición ajustada
                page.insert_text((x, y_adjusted), valor, fontsize=8, color=(0, 0, 0))

    # Guardar el PDF modificado en memoria
    buffer = io.BytesIO()
    doc.save(buffer)
    doc.close()
    buffer.seek(0)

    # Configurar la respuesta HTTP para descargar el PDF
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="Guia_Solicitud.pdf"'

    return response


def doc_Inspeccion(request, id):
    # id = int(id)
    solicitud = get_object_or_404(Solicitudes, id=id)
    datos_solicitud = get_object_or_404(Comercio, id_comercio=solicitud.id_solicitud.id_comercio)

    template_path = "web/static/assets/Inspeccion_2025.pdf"
    doc = fitz.open(template_path)

    datos = {
        "ID_Comercio": str(datos_solicitud.id_comercio),
        "Fecha_Solicitud": str(solicitud.fecha_solicitud),
        "Hora": str(solicitud.hora_solicitud),
        "Tipo_Servicio": str(solicitud.tipo_servicio),
        "Solicitante": str(solicitud.solicitante_nombre_apellido),
        "CI": str(solicitud.solicitante_cedula),
        "Tipo_Representante": str(solicitud.tipo_representante),
        "Nombre_Comercio": str(datos_solicitud.nombre_comercio),
        "Rif_Empresarial": str(datos_solicitud.rif_empresarial),
        "Rif_Representante_Legal": str(solicitud.rif_representante_legal),
        "Direccion": str(solicitud.direccion),
        "Estado": str(solicitud.estado),
        "Municipio": str(solicitud.municipio),
        "Parroquia": str(solicitud.parroquia),
        "Telefono": str(solicitud.numero_telefono),
        "Correo_Electronico": str(solicitud.correo_electronico),
        "Pago_Tasa_Servicio": str(solicitud.pago_tasa),
        "Metodo_Pago": str(solicitud.metodo_pago),
        "Referencia": str(solicitud.referencia),
    }
    for page in doc:
        for campo, valor in datos.items():
            # Buscar las etiquetas sin espacios, como {{ID_Comercio}}
            search_str = f"{{{{{campo}}}}}" 
            text_instances = page.search_for(search_str)

            for inst in text_instances:
                x, y, x1, y1 = inst  # Obtener coordenadas
                y_adjusted = y + 7.5  # Ajustar la coordenada Y hacia abajo en 2 unidades (ajusta este valor según sea necesario)
                # Borrar el texto anterior
                rect = fitz.Rect(x, y, x1, y1)
                page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                # Insertar el nuevo texto en la posición ajustada
                page.insert_text((x, y_adjusted), valor, fontsize=8, color=(0, 0, 0))

    buffer = io.BytesIO()
    doc.save(buffer)
    doc.close()
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="Solicitud_inspeccion.pdf"'


    return response


def api_eliminar_solicitudes(request, id):
    solicitud = get_object_or_404(Solicitudes, id=id)
    solicitud.delete()
    return JsonResponse({"message": "Solicitud eliminada correctamente"}, status=200)


def validar_cedula(request):
    cedula = request.GET.get("cedula", "").strip()
    comercio_id = request.GET.get("comercio", "").strip()  # Obtener comercio enviado desde el frontend

    # print(f"Cédula recibida: {cedula}")
    # print(f"Comercio recibido: {comercio_id}")

    if not cedula or not cedula.startswith(("V-", "E-")):
        return JsonResponse({"error": "Formato inválido. Use V-12345678 o E-12345678."}, status=400)

    # Obtener los comercios asociados a la cédula
    solicitudes = Solicitudes.objects.filter(solicitante_cedula=cedula)
    comercios_asociados = set(solicitudes.values_list("id_solicitud__id_comercio", flat=True))
    cantidad_comercios = len(comercios_asociados)

    # print(f"Comercios asociados encontrados: {comercios_asociados}")
    # print(f"Cantidad de comercios asociados: {cantidad_comercios}")

    # Si la cédula ya está en 3 comercios y el comercio actual no está en la lista, bloquear registro
    if cantidad_comercios >= 3 and comercio_id not in comercios_asociados:
        return JsonResponse({
            "existe": True,
            "cantidad_comercios": cantidad_comercios,
            "valido": False,  # Bloquear el registro
            "mensaje": "❌ La cédula ya está asociada a 3 comercios distintos."
        })

    return JsonResponse({
        "existe": cantidad_comercios > 0,
        "cantidad_comercios": cantidad_comercios,
        "valido": True  # Permitir el registro
    })


def validar_rif(request):
    rif = request.GET.get("rif", "").strip()

    if not rif:
        return JsonResponse({"error": "El RIF no puede estar vacío."}, status=400)

    # Verificar si el RIF ya existe en la base de datos
    existe = Comercio.objects.filter(rif_empresarial=rif).exists()

    return JsonResponse({"existe": existe})


def api_modificar_solicitudes(request, id):
    solicitud = get_object_or_404(Solicitudes, id=id)
    datos_solicitud = get_object_or_404(Comercio, id_comercio=solicitud.id_solicitud.id_comercio)
    requisitos = get_object_or_404(Requisitos, id_solicitud=solicitud.id)

     # Datos para reemplazar en la plantilla
    datos = {
            "Id_Solicitud": solicitud.id,

            "ID_Comercio": str(datos_solicitud.id_comercio),
            "Fecha_Solicitud": str(solicitud.fecha_solicitud),
            "Hora": str(solicitud.hora_solicitud),
            "Tipo_Servicio": str(solicitud.tipo_servicio),
            "Solicitante": str(solicitud.solicitante_nombre_apellido),
            "CI": str(solicitud.solicitante_cedula),
            "Tipo_Representante": str(solicitud.tipo_representante),
            "Nombre_Comercio": str(datos_solicitud.nombre_comercio),
            "Rif_Empresarial": str(datos_solicitud.rif_empresarial),
            "Rif_Representante_Legal": str(solicitud.rif_representante_legal),
            "Direccion": str(solicitud.direccion),
            "Estado": str(solicitud.estado),
            "Municipio": solicitud.municipio.id,
            "Parroquia": solicitud.parroquia.id,
            "Telefono": str(solicitud.numero_telefono),
            "Correo_Electronico": str(solicitud.correo_electronico),
            "Pago_Tasa_Servicio": str(solicitud.pago_tasa),
            "Metodo_Pago": str(solicitud.metodo_pago),
            "Referencia": str(solicitud.referencia),

            "Status_Cedula": requisitos.cedula_identidad,
            "Status_Rif": requisitos.rif_representante,
            "Status_Comercio": requisitos.rif_comercio,
            "Status_Permiso": requisitos.permiso_anterior,
            "Status_Registro_Comercio": requisitos.registro_comercio,
            "Status_Documento_Propiedad": requisitos.documento_propiedad,
            "Status_Cedula_Catastral": requisitos.cedula_catastral,
            "Status_Carta_Autorizacion": requisitos.carta_autorizacion,
            "Status_Plano": requisitos.plano_bomberil,

            "Fecha_Vencimiento_Cedula": requisitos.cedula_vencimiento,
            "Fecha_Vencimiento_Rif": requisitos.rif_representante_vencimiento,
            "Fecha_Vencimiento_Rif_Comercio": requisitos.rif_comercio_vencimiento,
            "Fecha_Vencimiento_Documento_Propiedad": requisitos.documento_propiedad_vencimiento,
            "Fecha_Vencimiento_Cedula_Catastral": requisitos.cedula_catastral_vencimiento,
    }

    return JsonResponse(datos, safe=False)


def agregar_comercio(request):
    if request.method == "POST":
        comercio = request.POST.get("nombre_comercio")  # Obtener el valor del formulario
        rif_empresarial = request.POST.get("rif_empresarial")  # Obtener el valor del formulario

        # Guardar en la base de datos y obtener el objeto creado
        nuevo_comercio = Comercio.objects.create(
            nombre_comercio=comercio,
            rif_empresarial=rif_empresarial
        )

        # Redirigir a la misma página con el ID del comercio en la URL
        return redirect(f"/formulariocertificados/?comercio_id={nuevo_comercio.id_comercio}")

    return HttpResponse("Método no permitido", status=405)


def agregar_o_actualizar_solicitud(request):
    if request.method == "POST":
        # Obtener el ID de la solicitud (si existe, para actualización)
        id_solicitud = request.POST.get("id_solicitud")  # ID de la tabla Solicitudes (no de Comercio)
        
        # Datos del formulario de Solicitud
        comercio_id = request.POST.get("comercio")
        fecha_solicitud = request.POST.get("fecha_solicitud")
        hora_solicitud = request.POST.get("hora_solicitud")
        tipo_servicio = request.POST.get("tipo_servicio")
        solicitante = request.POST.get("solicitante_nombre_apellido")
        solicitante_cedula = request.POST.get("solicitante_cedula")
        nacionalidad = request.POST.get("nacionalidad")
        tipo_representante = request.POST.get("tipo_representante")
        rif_representante = request.POST.get("rif_representante_legal")
        direccion = request.POST.get("direccion")
        estado = request.POST.get("estado")
        municipio_id = request.POST.get("municipio")
        parroquia_id = request.POST.get("parroquia")
        numero_telefono = request.POST.get("numero_telefono")
        correo = request.POST.get("correo_electronico")
        pago = request.POST.get("pago_tasa")
        metodo_pago = request.POST.get("metodo_pago")
        referencia = request.POST.get("referencia") or "SIN REFERENCIA"

        # Función auxiliar para checkboxes
        def get_checkbox_value(field_name):
            return request.POST.get(field_name) == "on"

        # Obtener instancias de modelos relacionados
        comercio_instance = get_object_or_404(Comercio, id_comercio=comercio_id)
        municipio_instance = get_object_or_404(Municipios, id=municipio_id)
        parroquia_instance = get_object_or_404(Parroquias, id=parroquia_id)

        # ===== CREAR O ACTUALIZAR SOLICITUD =====
        if id_solicitud:  # ACTUALIZAR solicitud existente
            solicitud = get_object_or_404(Solicitudes, id=id_solicitud)
            solicitud.id_solicitud = comercio_instance  # ✅ Campo correcto
           
            solicitud.fecha_solicitud = fecha_solicitud
            solicitud.hora_solicitud = hora_solicitud
            solicitud.tipo_servicio = tipo_servicio
            solicitud.solicitante_nombre_apellido = solicitante
            solicitud.solicitante_cedula = f"{nacionalidad}-{solicitante_cedula}"
            solicitud.tipo_representante = tipo_representante
            solicitud.rif_representante_legal = rif_representante
            solicitud.direccion = direccion
            solicitud.estado = estado
            solicitud.municipio = municipio_instance
            solicitud.parroquia = parroquia_instance
            solicitud.numero_telefono = numero_telefono
            solicitud.correo_electronico = correo
            solicitud.pago_tasa = pago
            solicitud.metodo_pago = metodo_pago
            solicitud.referencia = referencia
            
            solicitud.save()
            
            created = False
        else:  # CREAR nueva solicitud
            solicitud = Solicitudes.objects.create(
                id_solicitud=comercio_instance,  # ✅ Campo correcto
                fecha_solicitud=request.POST.get("fecha_solicitud"),
                hora_solicitud=hora_solicitud,
                tipo_servicio=tipo_servicio,
                solicitante_nombre_apellido=solicitante,
                solicitante_cedula=f"{nacionalidad}-{solicitante_cedula}",
                tipo_representante=tipo_representante,
                rif_representante_legal=rif_representante,
                direccion=direccion,
                estado=estado,
                municipio=municipio_instance,
                parroquia=parroquia_instance,
                numero_telefono=numero_telefono,
                correo_electronico=correo,
                pago_tasa=pago,
                metodo_pago=metodo_pago,
                referencia=referencia
            )
            
            created = True

        # ===== ACTUALIZAR O CREAR REQUISITOS =====
        Requisitos.objects.update_or_create(
            id_solicitud=solicitud,
            defaults={
                "cedula_identidad": get_checkbox_value("cedula_identidad"),
                "cedula_vencimiento": request.POST.get("cedula_vecimiento"),
                "rif_representante": get_checkbox_value("rif_representante"),
                "rif_representante_vencimiento": request.POST.get("rif_representante_vencimiento"),
                "rif_comercio": get_checkbox_value("rif_comercio"),
                "rif_comercio_vencimiento": request.POST.get("rif_comercio_vencimiento"),
                "permiso_anterior": get_checkbox_value("permiso_anterior"),
                "registro_comercio": get_checkbox_value("registro_comercio"),
                "documento_propiedad": get_checkbox_value("documento_propiedad"),
                "documento_propiedad_vencimiento": request.POST.get("documento_propiedad_vencimiento"),
                "cedula_catastral": get_checkbox_value("cedula_catastral"),
                "cedula_catastral_vencimiento": request.POST.get("cedula_catastral_vencimiento"),
                "carta_autorizacion": get_checkbox_value("carta_autorizacion"),
                "plano_bomberil": get_checkbox_value("plano_bomberil"),
            }
        )

        return redirect("/certificadosprevencion/")

    return HttpResponse("Método no permitido", status=405)


def generar_excel_solicitudes(request):
    # Obtener todas las solicitudes con la información del comercio relacionada, ordenadas por fecha descendente
    solicitudes = Solicitudes.objects.select_related('id_solicitud').order_by('-fecha_solicitud')
    
    # Crear un diccionario para almacenar la solicitud más reciente por comercio
    comercio_dict = {}
    
    for solicitud in solicitudes:
        comercio = solicitud.id_solicitud  # Comercio asociado a la solicitud
        if comercio.id_comercio not in comercio_dict:
            comercio_dict[comercio.id_comercio] = {
                'ID Comercio': comercio.id_comercio,
                'Nombre Comercio': comercio.nombre_comercio,
                'RIF Comercio': comercio.rif_empresarial,
                'Número de Teléfono': solicitud.numero_telefono,
                'Nombre y Apellido del Solicitante': solicitud.solicitante_nombre_apellido,
                'Fecha de Solicitud': solicitud.fecha_solicitud,
                'Dirección': solicitud.direccion,
            }
    
    # Convertir el diccionario en una lista de valores
    data = list(comercio_dict.values())
    
    # Crear DataFrame de pandas y ordenarlo por fecha de solicitud descendente
    df = pd.DataFrame(data).sort_values(by='ID Comercio', ascending=True)

    # Convertir DataFrame a JSON
    json_data = df.to_json(orient='records', date_format='iso')

    # Devolver los datos como JSON
    return JsonResponse(json.loads(json_data), safe=False)

