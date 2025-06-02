from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db.models import Case, When
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Max
from django.db.models import Count
from django.utils.timezone import localdate
from django.forms.models import model_to_dict
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Q, Sum
from datetime import time
from .urls import *
from .forms import *
from django.db.models import Prefetch
from openpyxl import Workbook
import json
from openpyxl.styles import Font, Alignment
from datetime import timedelta # Importa timedelta para operaciones de fecha

# Vista del dashboard Ven911
@login_required
def ven911(request):
    user = request.session.get('user')
    if not user:
        return redirect('/')
    # Renderizar la página con los datos
    return render(request, "Dashboard_ven911.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
    })
# Vista del formulario con su metodo de guardado
@never_cache  # Evita que la vista se cachee
@login_required
def form_services(request):
    user = request.session.get('user')
    if not user:
        return redirect('/')

    servicio_id = request.GET.get('id') or request.POST.get('id')
    servicio_instance = None
    
    if servicio_id:
        try:
            servicio_instance = Servicio.objects.get(id=servicio_id)
        except Servicio.DoesNotExist:
            messages.error(request, 'El servicio a editar no existe')
            return redirect('table_911')

    if request.method == 'POST':
        form_services = ServicioForm(request.POST, instance=servicio_instance)
        if form_services.is_valid():
            try:
                servicio = form_services.save(commit=False)
                servicio.save()
                action = 'editado' if servicio_id else 'registrado'
                messages.success(request, f'Servicio {action} correctamente!')
                return redirect('form_services')
            except Exception as e:
                messages.error(request, f'Error al guardar: {str(e)}')
        else:
            messages.error(request, 'Error en el formulario. Revise los datos.')
    else:
        form_services = ServicioForm(instance=servicio_instance)

    return render(request, "formulario_servicios.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "formulario_servicios": form_services,
        "modo_edicion": servicio_id is not None
    })

# Vista de informacion de los servicios
@login_required
def view_table_911(request):
    registros_totales = Servicio.objects.all().count()
    registros_hoy = Servicio.objects.filter(fecha=localdate()).count()
    # Verificar si el usuario está en la sesión
    user = request.session.get('user')
    if not user:
        return redirect('/')
    # Renderizar la página con los datos
    return render(request, "table_911.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "registros_totales" : registros_totales,
        "registros_hoy" : registros_hoy,
    })

def obtener_servicios_json(request):
    try:
        fecha_str = request.GET.get('fecha') 
        if fecha_str:
            try:
                hoy = timezone.datetime.strptime(fecha_str, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'error': 'Formato de fecha inválido. Usa YYYY-MM-DD'}, status=400)
        else:
            hoy = timezone.localdate() # Usa la fecha actual si no hay parámetro

        # ... (Tu lógica existente para obtener servicios) ...
        servicios = Servicio.objects.filter(
            fecha=hoy
        ).select_related(
            'tipo_servicio',
            'operador_de_guardia'
        ).order_by('-hora', '-id')

        # Construcción de datos...
        datos_servicios = []
        for servicio in servicios:
            operador_data = None
            if servicio.operador_de_guardia:
                nombre_completo = f"{servicio.operador_de_guardia.nombres} {servicio.operador_de_guardia.apellidos}"
                jerarquia = getattr(servicio.operador_de_guardia, 'jerarquia', '')
                if jerarquia:
                    nombre_completo += f" - {jerarquia}"
                
                operador_data = {
                    'id': servicio.operador_de_guardia.id,
                    'nombre_completo': nombre_completo
                }

            servicio_data = {
                'id': servicio.id,
                'tipo_servicio': {
                    'id': servicio.tipo_servicio.id,
                    'nombre': servicio.tipo_servicio.nombre
                } if servicio.tipo_servicio else None,
                'cantidad_tipo_servicio': servicio.cantidad_tipo_servicio,
                'operador_de_guardia': operador_data,
                'fecha': servicio.fecha.strftime('%Y-%m-%d') if servicio.fecha else None, # Asegúrate de que la fecha se formatee aquí
                'hora': servicio.hora.strftime('%H:%M') if servicio.hora else None,
            }
            datos_servicios.append(servicio_data)

        return JsonResponse({
            'servicios': datos_servicios,
            'fecha_consultada': hoy.strftime('%Y-%m-%d'), # <-- **Asegúrate de que esta línea esté presente**
            'count': len(datos_servicios)
        }, safe=False)

    except Exception as e:
        import logging
        logging.exception("Error en obtener_servicios_json")
        return JsonResponse({
            'error': 'Error al obtener servicios',
            'details': str(e),
            'fecha_consultada': timezone.localdate().strftime('%Y-%m-%d') # Devuelve una fecha incluso en error
        }, status=500)

# api para elmininar servicio
@csrf_exempt  # Solo si no usas CSRF en APIs (o configura CSRF correctamente)
def eliminar_servicio(request, id):
    if request.method == 'DELETE':
        try:
            servicio = Servicio.objects.get(id=id)
            servicio.delete()
            return JsonResponse({"status": "success"}, status=200)
        except Servicio.DoesNotExist:
            return JsonResponse({"error": "Servicio no encontrado"}, status=404)
    return JsonResponse({"error": "Método no permitido"}, status=405)

# api conteo de servicios para dashboard y exportacion de pdf

def api_conteo_servicios(request):
    # Primero obtenemos todos los tipos de servicio
    tipos_servicio = TipoServicio.objects.all().order_by('nombre')
    
    # Inicializamos el filtro vacío
    filtro_servicios = Q()
    
    # Obtenemos los parámetros de fecha
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    
    if fecha_inicio and fecha_fin:
        try:
            # Convertimos las fechas de string a objetos date
            start_date = timezone.datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            end_date = timezone.datetime.strptime(fecha_fin, "%Y-%m-%d").date()
            
            # Validamos que la fecha inicio <= fecha fin
            if start_date <= end_date:
                # Construimos los filtros para los servicios
                
                # Caso 1: Rango de múltiples días (días completos intermedios)
                filtro_intermedio = Q(servicio__fecha__gt=start_date, 
                                    servicio__fecha__lt=end_date)
                
                # Caso 2: Día inicial (solo horas >= 8:00 AM)
                filtro_dia_inicio = Q(servicio__fecha=start_date, 
                                    servicio__hora__gte=time(5, 0))
                
                # Caso 3: Día final (solo horas < 8:00 AM)
                filtro_dia_fin = Q(servicio__fecha=end_date, 
                                 servicio__hora__lt=time(5, 0))
                
                # Caso especial: Si es el mismo día (24 horas desde 8:00 AM a 8:00 AM del día siguiente)
                if start_date == end_date:
                    filtro_servicios = (
                        Q(servicio__fecha=start_date, servicio__hora__gte=time(5, 0)) |
                        Q(servicio__fecha=start_date + timezone.timedelta(days=1), 
                         servicio__hora__lt=time(5, 0))
                    )
                else:
                    # Combinamos todos los casos para rangos de múltiples días
                    filtro_servicios = (filtro_intermedio | filtro_dia_inicio | filtro_dia_fin)
        except ValueError:
            pass  # Si hay error en el formato, ignoramos el filtro
    
    # Anotamos cada tipo de servicio con la suma de las cantidades de servicios que cumplen el filtro
    datos = tipos_servicio.annotate(
        total=Sum('servicio__cantidad_tipo_servicio', 
                filter=filtro_servicios)
    ).values('nombre', 'total')
    
    # Convertimos a un diccionario {nombre_tipo: total}
    conteo = {item['nombre']: item['total'] or 0 for item in datos}
    
    return JsonResponse(conteo)

# api servicios de grafica
def api_servicios_grafico(request):
    # Obtener parámetro de mes
    month_filter = request.GET.get('month')
    
    # Filtrar servicios basados en el mes si se proporciona
    servicios_query = Servicio.objects.all()
    
    if month_filter:
        try:
            # Convertir string 'YYYY-MM' a objeto date
            filter_date = datetime.strptime(month_filter, '%Y-%m').date()
            year, month = filter_date.year, filter_date.month
            
            # Filtrar servicios por año y mes
            servicios_query = servicios_query.filter(
                fecha__year=year,
                fecha__month=month
            )
        except (ValueError, TypeError):
            # Manejar error si el formato de fecha es incorrecto
            pass
    
    # Anotar y contar los tipos de servicio
    datos = TipoServicio.objects.filter(
        servicio__in=servicios_query
    ).annotate(
        total=Sum('servicio__cantidad_tipo_servicio', filter=Q(servicio__fecha__isnull=False)
        )
    ).values_list('nombre', 'total').order_by('nombre')

    # Preparar datos para la respuesta
    labels = []
    valores = []
    for nombre, total in datos:
        labels.append(nombre)
        valores.append(total)

    return JsonResponse({
        'labels': labels,
        'data': valores,
        'count': len(labels)
    })
    
# api para exportar y descargar excel

def exportar_servicios_excel(request):
    try:
        # Obtener el mes y año del parámetro GET
        mes_param = request.GET.get('mes')
        if not mes_param:
            return HttpResponse("Debe especificar un mes (formato YYYY-MM)", status=400)
        
        # Parsear la fecha
        try:
            fecha_seleccionada = datetime.strptime(mes_param, '%Y-%m')
            anio = fecha_seleccionada.year
            mes = fecha_seleccionada.month
        except ValueError:
            return HttpResponse("Formato de fecha inválido. Use YYYY-MM", status=400)
        
        # Filtrar servicios por mes y año
        servicios = Servicio.objects.filter(
            fecha__year=anio,
            fecha__month=mes
        ).select_related('tipo_servicio', 'operador_de_guardia').order_by('fecha', 'hora')
        
        # Crear el libro de Excel
        wb = Workbook()
        ws = wb.active
        ws.title = f"Servicios {mes_param}"
        
        # Encabezados con estilo
        headers = [
            '#', 'Fecha', 'Hora', 'Tipo de Servicio', 
            'Cantidad', 'Operador de Guardia', 'Jerarquía'
        ]
        ws.append(headers)
        
        # Aplicar estilos a los encabezados
        for col in range(1, len(headers) + 1):
            cell = ws.cell(row=1, column=col)
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')
        
        # Datos
        for index, servicio in enumerate(servicios, start=1):
            operador_nombre = ''
            operador_jerarquia = ''
            
            if servicio.operador_de_guardia:
                operador_nombre = f"{servicio.operador_de_guardia.nombres} {servicio.operador_de_guardia.apellidos}"
                if hasattr(servicio.operador_de_guardia, 'jerarquia'):
                    operador_jerarquia = servicio.operador_de_guardia.jerarquia
            
            ws.append([
                index,  # Número secuencial en lugar del ID real
                servicio.fecha.strftime('%Y-%m-%d') if servicio.fecha else '',
                servicio.hora.strftime('%H:%M:%S') if servicio.hora else '',
                servicio.tipo_servicio.nombre if servicio.tipo_servicio else '',
                servicio.cantidad_tipo_servicio,
                operador_nombre,
                operador_jerarquia
            ])
        
        # Autoajustar el ancho de las columnas
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = (max_length + 2) * 1.2
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Preparar la respuesta
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename=servicios_{mes_param}.xlsx'
        wb.save(response)
        
        return response
        
    except Exception as e:
        return HttpResponse(f"Error: {str(e)}", status=500)
    


