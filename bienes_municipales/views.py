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

    bienes_queryset = bienes_queryset.order_by('id')

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
        # Si no hay ID, no se puede generar el PDF.
        return HttpResponse("Error: No se proporcionó una dependencia válida.", status=404)

    try:
        dependencia = get_object_or_404(Dependencia, id=dependencia_id)
        bienes = BienMunicipal.objects.filter(dependencia=dependencia).select_related('dependencia', 'responsable').order_by('identificador')

        if not bienes:
            pass

    except Dependencia.DoesNotExist:
        return HttpResponse("Error: La dependencia seleccionada no existe.", status=404)

    # Crea el buffer para el PDF y el canvas
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Añade un título al PDF
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 750, f"Bienes de la dependencia: {dependencia.nombre}")
    p.setFont("Helvetica", 12)
    
    y_position = 700
    for bien in bienes:
        # Si no hay suficiente espacio para el siguiente QR, crea una nueva página
        if y_position < 100:
            p.showPage()
            y_position = 750
            p.setFont("Helvetica-Bold", 16)
            p.setFont("Helvetica", 12)

        # Prepara los datos para el código QR
        # Se usa un formato de texto simple para que el QR sea legible
        data_qr = f"Identificador: {bien.identificador}\nDependencia: {bien.dependencia.nombre}\nDepartamento: {bien.departamento}\nResponsable: {bien.responsable if bien.responsable else 'Sin asignar'}"
        
        # Genera el código QR
        qr_img = qrcode.make(data_qr)
        qr_img_buffer = BytesIO()
        qr_img.save(qr_img_buffer, "PNG")
        qr_img_buffer.seek(0)
        
        # Convierte el buffer de la imagen en un objeto ImageReader para ReportLab
        qr_reader = ImageReader(qr_img_buffer)
        
        # Dibuja la imagen del QR y la información del bien en el PDF
        p.drawImage(qr_reader, 100, y_position - 80, width=80, height=80)
        
        p.drawString(200, y_position - 10, f"Identificador: {bien.identificador}")
        p.drawString(200, y_position - 30, f"Descripción: {bien.descripcion}")
        p.drawString(200, y_position - 50, f"Departamento: {bien.departamento}")
        p.drawString(200, y_position - 70, f"Responsable: {bien.responsable.nombres} {bien.responsable.apellidos}" if bien.responsable else "Responsable: Sin asignar")
        
        y_position -= 100 # Mueve la posición para el siguiente bien

    # Guarda el canvas y cierra el buffer
    p.showPage() # Muestra la última página
    p.save()
    buffer.seek(0)

    # Devuelve el PDF como respuesta para su descarga
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="bienes_{dependencia.nombre}.pdf" pagename="bienes_municipales"'
    return response