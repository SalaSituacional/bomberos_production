from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .forms import *
from .models import *
from .urls import *
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader  # Importa ImageReader


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

    if not user:
        return redirect('/')

    bienes_queryset = BienMunicipal.objects.all()

    # Get filter parameters
    filter_id = request.GET.get('filterID', '')
    filter_dependencia_id = request.GET.get('filterDependencia', '')
    filter_estado = request.GET.get('filterEstado', '')

    # Apply filters
    if filter_id:
        bienes_queryset = bienes_queryset.filter(identificador=filter_id)

    if filter_dependencia_id:
        bienes_queryset = bienes_queryset.filter(dependencia__id=filter_dependencia_id)

    if filter_estado:
        bienes_queryset = bienes_queryset.filter(estado_actual=filter_estado)

    bienes_queryset = bienes_queryset.order_by('identificador')

    # --- Pagination Implementation ---
    # 1. Get the current page number from the request (default to 1)
    page = request.GET.get('page', 1)

    # 2. Initialize Paginator with your queryset and desired items per page
    paginator = Paginator(bienes_queryset, 10) # Show 10 bienes per page (you can adjust this number)

    try:
        datos = paginator.page(page) # 'datos' will be your Page object
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        datos = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        datos = paginator.page(paginator.num_pages)
    # --- End Pagination Implementation ---


    total_bienes = bienes_queryset.count() # This now reflects the total count before pagination, but after filtering.
                                           # If you want the count of items on the current page, use datos.object_list.count()

    dependencias = Dependencia.objects.all().order_by('nombre')
    estado_choices = ["Bueno", "Regular", "Defectuoso", "Dañado"]

    # This logic needs to match the filter parameters in your pagination links.
    # It seems your pagination links are using 'filtro_parroquia', 'filtro_procedimiento', 'filtro_trimestre'.
    # We need to adapt this to your current 'filterID', 'filterDependencia', 'filterEstado'.
    # I'll create variables that align with what's in your provided pagination HTML.
    # You'll need to decide which filter variables map to which (e.g., filterDependencia could be 'filtro_parroquia'
    # if it represents a similar concept). For now, I'll map them directly.

    # Map your current filters to the names used in your pagination HTML
    filtro_parroquia_param = request.GET.get('filterDependencia', '') # Assuming filterDependencia maps to filtro_parroquia in the pagination HTML example
    filtro_procedimiento_param = '' # You don't have a 'procedimiento' filter currently, so it's empty
    filtro_trimestre_param = ''    # You don't have a 'trimestre' filter currently, so it's empty

    filters_active = bool(filter_id or filter_dependencia_id or filter_estado)

    return render(request, "bienes_municipales/inventario_bienes.html", {
        "user": user,
        "jerarquia": user.get("jerarquia"),
        "nombres": user.get("nombres"),
        "apellidos": user.get("apellidos"),
        "form_movimientos": MovimientoBienForm(),
        "form_estado": CambiarEstadoBienForm(),
        "total_bienes": total_bienes,
        "bienes_municipales": datos, # Pass the 'Page' object here!
        "dependencias": dependencias,
        "estado_choices": estado_choices,
        
        # Pass the current filter values back to the template to pre-fill the form
        "filterID_value": filter_id,
        "filterDependencia_value": filter_dependencia_id,
        "filterEstado_value": filter_estado,
        "filters_active": filters_active,
        
        # New: Pass the filter parameters used in the pagination links for persistence
        "filtro_parroquia": filtro_parroquia_param,
        "filtro_procedimiento": filtro_procedimiento_param,
        "filtro_trimestre": filtro_trimestre_param,
    })

def listar_bienes(request):
    identificador = request.GET.get("identificador")
    page = int(request.GET.get("page", 1))
    per_page = 15

    bienes_queryset = BienMunicipal.objects.select_related('dependencia', 'responsable').order_by("identificador")

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

    for bien in bienes:
        data["bienes"].append({
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

            ordenado_por_instance = Personal.objects.get(id=int(ordenado_por))

            # Guardar el movimiento
            movimiento = MovimientoBien.objects.create(
                bien=bien,
                nueva_dependencia=nueva_dependencia,
                nuevo_departamento=nuevo_departamento,
                ordenado_por=ordenado_por_instance,
                fecha_orden=fecha_orden
            )

            # Actualizar el bien
            bien.dependencia = nueva_dependencia
            bien.departamento = nuevo_departamento
            bien.save()

            return redirect('/bienesMunicipales/inventario_bienes/')  # Cambia esta ruta al destino deseado

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

            return redirect('/bienesMunicipales/inventario_bienes/')  # Cambia esta ruta al destino deseado

    else:
        form = CambiarEstadoBienForm()
    return render(request, 'reasignar_form.html', {'form': form})

def eliminar_bien(request):
    bien_id = request.POST.get('bien_id')
    bien = get_object_or_404(BienMunicipal, identificador=bien_id)
    bien.delete()
    return redirect('/bienesMunicipales/inventario_bienes/')  # Cambia a la vista que quieras recargar

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
            'fecha_registro': bien.fecha_registro,
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

    print(existe)
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

def generar_pdf_qr_bienes(request):
    dependencia_id = request.GET.get('dependencia_id')

    if not dependencia_id:
        return HttpResponse("Error: No se proporcionó una dependencia válida.", status=404)

    try:
        dependencia = get_object_or_404(Dependencia, id=dependencia_id)
        bienes = BienMunicipal.objects.filter(dependencia=dependencia).select_related('dependencia', 'responsable').order_by('identificador')

        if not bienes:
            # Puedes retornar un PDF vacío con un mensaje si no hay bienes.
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=letter)
            p.drawString(100, 750, f"No se encontraron bienes para la dependencia: {dependencia.nombre}")
            p.showPage()
            p.save()
            buffer.seek(0)
            return HttpResponse(buffer, content_type='application/pdf')

    except Dependencia.DoesNotExist:
        return HttpResponse("Error: La dependencia seleccionada no existe.", status=404)

    # Crea el buffer para el PDF y el canvas
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Añade un título al PDF
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, f"Códigos QR de Bienes: {dependencia.nombre}")
    p.setFont("Helvetica", 10)
    
    # Define las dimensiones y el espaciado
    qr_width = 80
    qr_height = 80
    id_height = 12  # Altura para el texto del identificador
    margin = 50     # Margen superior e inferior
    padding_x = 20  # Espacio entre códigos en horizontal
    padding_y = 40  # Espacio entre filas en vertical
    
    start_x = 70
    start_y = 700
    current_x = start_x
    current_y = start_y

    for bien in bienes:
        # Prepara los datos para el código QR
        # El formato se mantiene para que el QR sea funcional
        data_qr = f"Identificador: {bien.identificador}\nDependencia: {bien.dependencia.nombre}\nDescripción: {bien.descripcion}\nDepartamento: {bien.departamento}\nResponsable: {bien.responsable.nombres} {bien.responsable.apellidos}" if bien.responsable else f"Identificador: {bien.identificador}\nDependencia: {bien.dependencia.nombre}\nDescripción: {bien.descripcion}\nDepartamento: {bien.departamento}\nResponsable: Sin asignar"

        # Genera el código QR
        qr_img = qrcode.make(data_qr)
        qr_img_buffer = BytesIO()
        qr_img.save(qr_img_buffer, "PNG")
        qr_img_buffer.seek(0)
        
        # Convierte el buffer de la imagen en un objeto ImageReader
        qr_reader = ImageReader(qr_img_buffer)
        
        # Dibuja el QR y el identificador
        p.drawImage(qr_reader, current_x, current_y - qr_height, width=qr_width, height=qr_height)
        
        # Muestra el identificador debajo del QR
        p.drawCentredString(current_x + qr_width / 2, current_y - qr_height - 10, f"ID: {bien.identificador}")
        
        # Mueve la posición para el siguiente QR en la misma fila
        current_x += qr_width + padding_x
        
        # Si no hay suficiente espacio horizontal, se mueve a la siguiente fila
        if current_x + qr_width > letter[0] - margin:
            current_x = start_x
            current_y -= (qr_height + id_height + padding_y)
            
        # Si no hay suficiente espacio para la siguiente fila, crea una nueva página
        if current_y - (qr_height + id_height) < margin:
            p.showPage()
            current_x = start_x
            current_y = start_y
            
    # Guarda el canvas y cierra el buffer
    p.showPage() 
    p.save()
    buffer.seek(0)

    # Devuelve el PDF como respuesta para su descarga
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="bienes_qr_{dependencia.nombre}.pdf"'
    return response