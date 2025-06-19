from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django.http import JsonResponse, HttpResponse
from datetime import datetime, timedelta
import io
import json
from web.views.views import *
from web.views.views_descargas import *
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
import logging
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.views import View
import os
from dateutil.relativedelta import relativedelta
import io
import fitz  # PyMuPDF

from io import BytesIO
import qrcode
from qrcode.image.pil import PilImage


try:
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False



logger = logging.getLogger(__name__)

def certificados_prevencion(request):
    user = request.session.get('user')
    if not user:
        return redirect('/')

    numero_expediente = request.GET.get('numero_expediente', '')
    rif_empresarial = request.GET.get('rif_empresarial', '').strip()
    dependencia = request.GET.get('dependencia', '')
    page = request.GET.get('page', 1)
    
    # Consulta base - filtrar por dependencia si no es administrador
    if user['user'] == 'SeRvEr' or user['user'] == "Sala_Situacional":
        comercios_query = Comercio.objects.all().order_by('id_comercio')
    elif user['user'] == 'Prevencion05':
        # Asumimos que el modelo Comercio tiene un campo 'dependencia'
        comercios_query = Comercio.objects.filter(departamento = 'San Cristobal').order_by('id_comercio')
    elif user['user'] == 'ComandanciaJunin':
        # Asumimos que el modelo Comercio tiene un campo 'dependencia'
        comercios_query = Comercio.objects.filter(departamento = 'Junin').order_by('id_comercio')
    

    
    # Aplicar filtros adicionales si existen
    if numero_expediente == "GET ALL":
        pass  # Mostrar todos sin filtro
    elif numero_expediente and numero_expediente != "GET ALL":
        comercios_query = comercios_query.filter(id_comercio__icontains=numero_expediente)
    elif rif_empresarial:
        comercios_query = comercios_query.filter(rif_empresarial__icontains=rif_empresarial)
    
    # Filtro adicional de dependencia para administradores
    if (user['user'] == 'SeRvEr' or user['user'] == 'Sala_Situacional') and dependencia:
        comercios_query = comercios_query.filter(departamento=dependencia)
    
    # Obtener el total de registros después de aplicar los filtros
    total_comercios = comercios_query.count()
    
    # Configurar paginación (25 registros por página)
    paginator = Paginator(comercios_query, 25)
    
    try:
        comercios = paginator.page(page)
    except PageNotAnInteger:
        comercios = paginator.page(1)
    except EmptyPage:
        comercios = paginator.page(paginator.num_pages)
    
    return render(request, "Seguridad-prevencion/solicitudes.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "comercios": comercios,
        "conteo": total_comercios,
        "numero_expediente": numero_expediente,
        "rif_empresarial": rif_empresarial,
        "dependencia": dependencia,
    })


def formulario_certificado_prevencion(request):
    # Verificación de usuario y sesión
    user = request.session.get('user')
    if not user:
        logger.warning('Intento de acceso no autenticado a formulario_certificado_prevencion')
        return redirect('/')
    
    try:
        comercios = Comercio.objects.all()
        logger.debug(f'Obtenidos {len(comercios)} comercios para el formulario')
    except Exception as e:
        logger.error(f'Error al obtener comercios: {str(e)}')
        comercios = []
        messages.error(request, 'Error al cargar la lista de comercios')
    
    if request.method == 'POST':
        logger.info('Inicio de procesamiento de formulario POST')
        
        # Creamos una copia mutable del POST
        post_data = request.POST.copy()
        
        # Verificamos si el método de pago requiere referencia
        metodo_pago = post_data.get('metodo_pago', '')
        requiere_referencia = metodo_pago in ['Transferencia', 'Deposito']
        
        # Si no requiere referencia, eliminamos el campo del POST para evitar validación
        if not requiere_referencia:
            post_data['referencia'] = 'No Hay Referencia'
        
        solicitud_form = SolicitudForm(post_data)
        requisitos_form = RequisitosForm(post_data)
        
        if solicitud_form.is_valid() and requisitos_form.is_valid():
            try:
                # Guardamos la solicitud PRIMERO
                solicitud = solicitud_form.save(commit=False)
                
                # Validación adicional del comercio
                comercio_id = post_data.get('id_solicitud')
                if not comercio_id:
                    raise ValueError("Debe seleccionar un comercio válido")
                
                solicitud.id_solicitud_id = comercio_id
                solicitud.save()  # Guardamos para obtener el ID
                logger.info(f'Solicitud creada con ID: {solicitud.id}')
                
                # Ahora guardamos los requisitos ASOCIADOS a la solicitud
                requisitos = requisitos_form.save(commit=False)
                requisitos.id_solicitud = solicitud  # Asignamos la instancia completa
                requisitos.save()
                logger.info(f'Requisitos creados con ID: {requisitos.id} para solicitud {solicitud.id}')
                
                messages.success(request, 'Solicitud creada exitosamente!')
                return redirect('certificados_prevencion')
                
            except ValueError as ve:
                error_msg = f'Error de validación: {str(ve)}'
                logger.error(error_msg)
                messages.error(request, error_msg)
            except Exception as e:
                error_msg = f'Error al guardar la solicitud: {str(e)}'
                logger.error(error_msg, exc_info=True)
                messages.error(request, 'Ocurrió un error al procesar tu solicitud')
                
                # Guardamos los datos del formulario en la sesión para recuperarlos
                request.session['comercio_form_data'] = {
                    'solicitud_form_data': request.POST,  # Usamos el POST original aquí
                    'requisitos_form_data': request.POST
                }
                return redirect(request.path)
        else:
            # Procesar errores de validación
            for field, errors in solicitud_form.errors.items():
                for error in errors:
                    # Omitimos el error de referencia si no es requerido
                    if field != 'referencia' or requiere_referencia:
                        messages.error(request, f"{field}: {error}")
            
            for field, errors in requisitos_form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            
            request.session['comercio_form_data'] = request.POST  # POST original
            return redirect(request.path)
    
    # Manejo del GET (mostrar formulario)
    context = {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "comercio_form": ComercioForm(),
        "comercios": comercios,
        "solicitud_form": SolicitudForm(request.session.pop('comercio_form_data', None)),
        "requisitos_form": RequisitosForm(request.session.pop('comercio_form_data', None)),
    }
    
    return render(request, 'Seguridad-prevencion/formularioSolicitud.html', context)


# def planilla_certificado(request):
#     user = request.session.get('user')
#     if not user:
#             return redirect('/')

#     return render(request, "Seguridad-prevencion/planillaCertificadoDeConformidad.html", {
#         "user": user,
#         "jerarquia": user["jerarquia"],
#         "nombres": user["nombres"],
#         "apellidos": user["apellidos"],
#     })


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
    try:
        solicitudes = Solicitudes.objects.filter(
            id_solicitud__id_comercio=referencia
        ).select_related('id_solicitud').prefetch_related('requisitos_set')
        
        hoy = datetime.today().date()
        proximo_mes = hoy + timedelta(days=30)
        
        data = []
        for solicitud in solicitudes:
            requisito = solicitud.requisitos_set.first()
            
            # Documentos faltantes
            documentos_faltantes = []
            if not requisito:
                documentos_faltantes = ["No hay requisitos registrados"]
            else:
                campos_faltantes = [
                    ('Cédula de identidad', requisito.cedula_identidad),
                    ('RIF del representante', requisito.rif_representante),
                    ('RIF del comercio', requisito.rif_comercio),
                    ('Permiso anterior', requisito.permiso_anterior),
                    ('Registro de comercio', requisito.registro_comercio),
                    ('Documento de propiedad', requisito.documento_propiedad),
                    ('Cédula catastral', requisito.cedula_catastral),
                    ('Carta de autorización', requisito.carta_autorizacion),
                    ('Plano bomberil', requisito.plano_bomberil)
                ]
                documentos_faltantes = [nombre for nombre, existe in campos_faltantes if not existe]

            # Documentos con vencimiento
            documentos_vencimiento = []
            documentos_prox_vencer = []
            
            if requisito:
                vencimientos = [
                    ('Cédula de identidad', requisito.cedula_vencimiento),
                    ('RIF del representante', requisito.rif_representante_vencimiento),
                    ('RIF del comercio', requisito.rif_comercio_vencimiento),
                    ('Documento de propiedad', requisito.documento_propiedad_vencimiento),
                    ('Cédula catastral', requisito.cedula_catastral_vencimiento)
                ]
                
                for nombre, fecha in vencimientos:
                    if fecha:
                        if fecha < hoy:
                            documentos_vencimiento.append(f"{nombre} (venció el {fecha.strftime('%d/%m/%Y')}")
                        elif fecha <= proximo_mes:
                            documentos_prox_vencer.append(f"{nombre} (vence el {fecha.strftime('%d/%m/%Y')}")

            data.append({
                "id": solicitud.id_solicitud.id_comercio,
                "id_solicitud": solicitud.id,
                "comercio_departamento": solicitud.id_solicitud.departamento, 
                "fecha": solicitud.fecha_solicitud.strftime('%d/%m/%Y'),
                "solicitante": solicitud.solicitante_nombre_apellido,
                "tipo_solicitud": solicitud.tipo_servicio,
                "documentos_faltantes": documentos_faltantes or ["Todos los documentos están en orden"],
                "documentos_proximos_vencer": documentos_prox_vencer or ["No hay documentos próximos a vencer"],
                "documentos_vencidos": documentos_vencimiento or ["No hay documentos vencidos"],
                "tiene_requisitos": requisito is not None
            })
            
        return JsonResponse(data, safe=False)
    
    except Exception as e:
        logger.error(f"Error en api_get_solicitudes: {str(e)}")
        return JsonResponse({"error": str(e)}, status=500)




class DocumentGenerator:
    """Clase base para generación de documentos PDF con soporte para múltiples dependencias"""
    
    TEMPLATES = {
        'San Cristobal': {
            'solicitud': 'web/static/assets/Solictud_2025.pdf',
            'inspeccion': 'web/static/assets/Inspeccion_2025.pdf',
            'credencial': 'web/static/assets/Certificado_Sistema_SC.pdf'
        },
        'Junin': {
            'solicitud': 'web/static/assets/documentos_junin/Solictud_2025 (junin).pdf',
            'inspeccion': 'web/static/assets/documentos_junin/Inspeccion_2025 (junin).pdf',
            'credencial': 'web/static/assets/documentos_junin/Certificado_Sistema_Junin.pdf'
        },
        'default': {
            'solicitud': 'web/static/assets/Solictud.pdf',
            'inspeccion': 'web/static/assets/Inspeccion.pdf',
            'credencial': 'web/static/assets/Certificado_Sistema.pdf'
        }
    }
    
    def __init__(self, solicitud_id, dependencia=None):
        self.solicitud = get_object_or_404(Solicitudes, id=solicitud_id)
        self.datos_comercio = get_object_or_404(
            Comercio, 
            id_comercio=self.solicitud.id_solicitud.id_comercio
        )
        self.dependencia = dependencia or self.datos_comercio.departamento
        self.template_path = self.get_template_path()
    
    def get_template_path(self):
        """Obtiene la ruta de la plantilla según la dependencia"""
        template_type = self.get_template_type()
        try:
            templates = self.TEMPLATES.get(self.dependencia, self.TEMPLATES['default'])
            if template_type not in templates:
                raise ValueError(f"Plantilla '{template_type}' no definida para dependencia '{self.dependencia}'")
            return templates[template_type]
        except KeyError as e:
            raise ValueError(f"Error al acceder a plantillas: {str(e)}")
    
    def get_template_type(self):
        """Método abstracto para definir el tipo de plantilla"""
        raise NotImplementedError("Debe implementarse en las clases hijas")
    
    def get_document_data(self):
        """Obtiene los datos comunes para todos los documentos"""
        return {
            "ID_Comercio": str(self.datos_comercio.id_comercio),
            "Fecha_Solicitud": str(self.solicitud.fecha_solicitud),
            "Hora": str(self.solicitud.hora_solicitud),
            "Tipo_Servicio": str(self.solicitud.tipo_servicio),
            "Solicitante": str(self.solicitud.solicitante_nombre_apellido),
            "CI": str(self.solicitud.solicitante_cedula),
            "Tipo_Representante": str(self.solicitud.tipo_representante),
            "Nombre_Comercio": str(self.datos_comercio.nombre_comercio),
            "Rif_Empresarial": str(self.datos_comercio.rif_empresarial),
            "Rif_Representante_Legal": str(self.solicitud.rif_representante_legal),
            "Direccion": str(self.solicitud.direccion),
            "Estado": str(self.solicitud.estado),
            "Municipio": str(self.solicitud.municipio),
            "Parroquia": str(self.solicitud.parroquia),
            "Telefono": str(self.solicitud.numero_telefono),
            "Correo_Electronico": str(self.solicitud.correo_electronico),
            "Pago_Tasa_Servicio": str(self.solicitud.pago_tasa),
            "Metodo_Pago": str(self.solicitud.metodo_pago),
            "Referencia": str(self.solicitud.referencia),
        }
    
    def fill_pdf_template(self, additional_data=None):
        """Rellena la plantilla PDF con los datos"""
        doc = fitz.open(self.template_path)
        data = self.get_document_data()
        
        if additional_data:
            data.update(additional_data)
        
        for page in doc:
            for campo, valor in data.items():
                search_str = f"{{{{{campo}}}}}"
                text_instances = page.search_for(search_str)
                
                for inst in text_instances:
                    x, y, x1, y1 = inst
                    y_adjusted = y + 7.5  # Ajuste de posición vertical
                    
                    # Borrar texto anterior
                    rect = fitz.Rect(x, y, x1, y1)
                    page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1))
                    
                    # Insertar nuevo texto
                    page.insert_text(
                        point=(x, y_adjusted),
                        text=valor,
                        fontsize=7,
                        color=(0, 0, 0)
                    )
        
        return doc
    
    def generate_response(self):
        """Genera la respuesta HTTP con el PDF"""
        doc = self.fill_pdf_template()
        buffer = io.BytesIO()
        doc.save(buffer)
        doc.close()
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type="application/pdf")
        response["Content-Disposition"] = f'inline; filename="{self.get_output_filename()}"'
        return response
    
    def get_output_filename(self):
        """Método abstracto para definir el nombre del archivo de salida"""
        raise NotImplementedError("Debe implementarse en las clases hijas")

class GuiaDocumentGenerator(DocumentGenerator):
    """Generador específico para documentos de Guía"""
    
    def get_template_type(self):
        return 'solicitud'
    
    def get_output_filename(self):
        return f"Guia_Solicitud_{self.solicitud.id}.pdf"
    
    def get_document_data(self):
        base_data = super().get_document_data()
        requisitos = get_object_or_404(Requisitos, id_solicitud=self.solicitud.id)
        
        # Datos adicionales específicos para la Guía
        additional_data = {
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
        
        base_data.update(additional_data)
        return base_data

class InspeccionDocumentGenerator(DocumentGenerator):
    """Generador específico para documentos de Inspección"""
    
    def get_template_type(self):
        return 'inspeccion'
    
    def get_output_filename(self):
        return f"Solicitud_inspeccion_{self.solicitud.id}.pdf"

class CredencialDocumentGenerator(DocumentGenerator):
    """Generador optimizado para documentos de Credencial"""
    
    def get_template_type(self):
        return 'credencial'
    
    def get_output_filename(self):
        return f"Credencial_{self.datos_comercio.nombre_comercio}_{self.solicitud.id}.pdf"
    
    def get_document_data(self):
        """Obtiene todos los datos necesarios para la credencial"""
        base_data = super().get_document_data()
        
        fecha_emision = date.today()
        
        additional_data = {
            "Fecha_Emision": fecha_emision.strftime('%d/%m/%Y'),
            "Q": self.generate_qr_content(fecha_emision, fecha_emision + relativedelta(years=1))
        }
    
        base_data.update(additional_data)
        return base_data
    
    def generate_qr_content(self, fecha_emision, fecha_vencimiento):
        """Genera el contenido estructurado para el QR"""
        return (
            f"CERTIFICADO DE CONFORMIDAD\n"
            f"Comercio: {self.datos_comercio.nombre_comercio}\n"
            f"RIF: {self.datos_comercio.rif_empresarial}\n"
            f"Dirección: {self.solicitud.direccion}\n"
            f"Emisión: {fecha_emision.strftime('%d/%m/%Y')}\n"
            f"Vencimiento: {fecha_vencimiento.strftime('%d/%m/%Y')}\n"
            f"ID: {str(self.datos_comercio.id_comercio).zfill(6)}"
        )

    #----------------- ESTA FUNCION SE ENCARGA DE LOS ESTILOS DEL TEXTO_--------------------------
    def fill_pdf_template(self, additional_data=None):
        """
        Rellena la plantilla PDF con los datos, aplicando estilos profesionales
        y manejando el centrado del texto de manera mejorada.
        """
        doc = fitz.open(self.template_path)
        data = self.get_document_data()
        
        if additional_data:
            data.update(additional_data)
        
        # Configuración de estilos profesionales
        styles = {
            "Nombre_Comercio": {
                "size": 35,
                "font": "Times-Roman", # O la ruta a tu fuente personalizada, ej: os.path.join(settings.BASE_DIR, 'web', 'static', 'fonts', 'GreatVibes-Regular.ttf')
                "color": (0.2, 0.2, 0.6), # Color de relleno del texto (azul oscuro)
                "align": 1, # Alineación centrada (se maneja en _insert_centered_text)
            },
            "Rif_Empresarial": {
                "size": 20,
                "font": "Calibri-Bold",
                "color": (0.1, 0.1, 0.1),  # Negro suave
                "align": 1  # Centrado
            },
            "Direccion": {
                "size": 14,
                "font": "Calibri",
                "color": (0.3, 0.3, 0.3),  # Gris oscuro
                "align": 1 # Cambiado a centrado para que funcione con el nuevo rect
            },
            "Fecha_Solicitud": {
                "size": 12,
                "font": "Calibri",
                "color": (0, 0, 0),
                "align": 1  # Centrado
            },
            "ID_Comercio": {
                "size": 11,
                "font": "Calibri-Bold",
                "color": (0, 0, 0),  # Rojo oscuro
                "align": 1  # Centrado
            },
            "Fecha_Emision": { # Asegúrate de tener estilo para Fecha_Emision si la usas como placeholder
                "size": 12,
                "font": "Calibri",
                "color": (0, 0, 0),
                "align": 1
            }
        }

        for page in doc:
            page_width = page.rect.width  # Ancho total de la página
            
            for field, value in data.items():
                if field == "Q":  # Saltar el QR, ya que se maneja por separado
                    continue
                    
                placeholder = f"({field})"
                instances = page.search_for(placeholder) # Busca todas las instancias del placeholder
                
                for rect in instances: # Itera sobre cada ocurrencia del placeholder
                    if not rect.is_valid:
                        print(f"Rectángulo inválido para el campo {field}. Saltando.")
                        continue
                    
                    # Obtén el estilo para el campo o un estilo por defecto
                    style = styles.get(field, {
                        "size": 11,
                        "font": "Times-Roman",
                        "color": (0, 0, 0),
                    })

                    # Limpieza del área del placeholder original: dibuja un rectángulo blanco sobre él
                    # Esto es crucial para eliminar el texto del placeholder antes de insertar el nuevo.
                    page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1), overlay=False)
                    
                    if field == "Nombre_Comercio":
                        # Este campo tiene su propia lógica de centrado con _insert_centered_text
                        self._insert_centered_text(
                            page=page,
                            text=value,
                            y_position=rect.y0, # Usar el y0 (coordenada superior) del placeholder original
                            style=styles["Nombre_Comercio"],
                            page_width=page_width
                        )
                    else:
                        # Para otros campos que se quieren centrar horizontalmente en la página:
                        # Se define un nuevo rectángulo que abarca todo el ancho de la página (0 a page_width)
                        # y mantiene la posición vertical del placeholder original (rect.y0).
                        # La altura se expande un poco para asegurar suficiente espacio para el texto.
                        
                        # Ajusta el factor 1.5 si el texto se corta o tiene demasiado espacio vertical.
                        # Este rect permite que 'align=1' (centrado) funcione para toda la página.
                        target_rect = fitz.Rect(0, rect.y0, page_width, rect.y1 + style["size"] * 1.5) 

                        try:
                            page.insert_textbox(
                                target_rect, # Usa el nuevo rectángulo que abarca todo el ancho
                                str(value),
                                fontsize=style["size"],
                                fontname=style["font"],
                                color=style["color"],
                                align=style["align"], # Usa la alineación definida en los estilos (idealmente 1 para centrado)
                                overlay=True # Superpone el nuevo texto
                            )
                            # print(f"Texto '{value}' insertado para el campo '{field}' en {target_rect}")
                        except Exception as e:
                            # print(f"ERROR: No se pudo insertar texto para {field}: {e}. Cayendo a fallback.")
                            # Fallback simple si insert_textbox falla.
                            # Este fallback no es centrado automáticamente, solo inserta en un punto.
                            # Si necesitas un fallback centrado, deberías replicar la lógica de _insert_centered_text aquí.
                            page.insert_text(
                                point=(rect.x0 + 2, rect.y0 + style["size"]), # Punto relativo al placeholder original
                                text=str(value),
                                fontsize=style["size"],
                                color=style["color"]
                            )
            
            # Generación e inserción del QR
            if QR_AVAILABLE and "Q" in data:
                self._insert_qr_code(page, data["Q"])
        
        return doc
    # -------------- ESTA FUNCION SE ENCARGA DEL POSICIONAMIENTO Y ESTILOS DEL TEXTO----------------
    def _insert_centered_text(self, page, text, y_position, style, page_width):
        """
        Inserta texto centrado horizontalmente en la página,
        manejando fuentes personalizadas y estándar.
        """
        print(f"\n=== Iniciando inserción de texto centrado: '{text}' ===")
        
        # Asegurarse de que el texto no tenga espacios extra que afecten el cálculo del ancho
        text_to_measure = str(text).strip() # Convertir a string y limpiar espacios

        # Determina si la fuente es un archivo (.ttf) o un nombre estándar de PyMuPDF
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # IMPORTANTE: Si la fuente aquí es la que causa el problema de renderizado (texto duplicado),
        # asegúrate de que sea una fuente válida y que PyMuPDF pueda procesarla.
        # Intenta usar "Helvetica" o "Times-Roman" para verificar si la fuente es el problema.
        # Si usas un archivo TTF, la ruta debe ser correcta y el archivo accesible.
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        font_name_or_path = style.get("font", "Times-Roman") 
        is_font_file = font_name_or_path.lower().endswith('.ttf')

        # Detección de método de medición de texto disponible
        has_get_text_length = hasattr(page, 'get_text_length')
        print(f"• Método de medición de texto disponible: {'get_text_length' if has_get_text_length else 'estimación aproximada'}")
        
        # Cálculo del ancho del texto para centrado
        text_width = 0
        if has_get_text_length:
            try:
                if is_font_file:
                    text_width = page.get_text_length(text_to_measure, fontsize=style["size"], fontfile=font_name_or_path)
                else:
                    text_width = page.get_text_length(text_to_measure, fontsize=style["size"], fontname=font_name_or_path)
                print(f"  Ancho de texto calculado con precisión: {text_width:.2f}")
            except Exception as e:
                # Este 'except' se activa si get_text_length falla (posiblemente por la fuente)
                print(f"  ADVERTENCIA: Error al calcular text_length para '{font_name_or_path}' con texto '{text_to_measure}': {e}. Usando estimación.")
                text_width = len(text_to_measure) * style["size"] * 0.8 # Fallback de estimación (menos preciso)
        else:
            text_width = len(text_to_measure) * style["size"] * 0.6 # Fallback si get_text_length no existe
            print(f"  Ancho de texto estimado: {text_width:.2f}")
            
        # Cálculo del x_center para centrado horizontal
        # Si page_width es el ancho total de la página, esto centrará en toda la página.
        # Si necesitas centrar dentro de márgenes específicos de la plantilla,
        # deberías pasar un 'ancho_area_centrado' diferente y un 'offset_x_inicial'.
        x_center = (page_width - text_width) / 2   
        
        # Ajuste vertical: y_position es la parte superior del placeholder.
        # Añadimos un offset para posicionar la línea base del texto.
        y_pos = y_position + style["size"] * 1 

        # --- Debugging Final (mantener para monitoreo) ---
        print(f"DEBUG FINAL: Texto a insertar: '{text_to_measure}'")
        print(f"DEBUG FINAL: text_width: {text_width:.2f}")
        print(f"DEBUG FINAL: page_width (usado para centrado): {page_width:.2f}")
        print(f"DEBUG FINAL: x_center calculado: {x_center:.2f}")
        print(f"DEBUG FINAL: y_pos calculado: {y_pos:.2f}")
        # --- Fin Debugging Final ---

        # Inserción del texto con los estilos definidos
        try:
            insert_params = {
                "point": (x_center, y_pos),
                "text": text_to_measure, # Usar el texto limpio
                "fontsize": style["size"],
                "color": style["color"],
                "overlay": True,
            }
            if is_font_file:
                insert_params["fontfile"] = font_name_or_path
            else:
                insert_params["fontname"] = font_name_or_path

            page.insert_text(**insert_params)
            
            print(f"✅ Texto insertado en ({x_center:.2f}, {y_pos:.2f})") # Mensaje de éxito simplificado
        except Exception as e:
            # Este 'except' se activará si hay un problema al insertar el texto
            # incluso con los parámetros simplificados.
            print(f"❌ ERROR CRÍTICO al insertar texto en _insert_centered_text (incluso sin render_mode): {e}. Fallback simple.")
            # Fallback simple sin parámetros especiales, solo lo esencial
            page.insert_text(
                (x_center, y_pos),
                text_to_measure,
                fontsize=style["size"],
                color=style["color"],
                overlay=True
            )
        return

    def _wrap_text(self, text, max_chars):
        """Divide el texto en líneas según el máximo de caracteres"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            if len(current_line) + len(word) + 1 <= max_chars:
                current_line = f"{current_line} {word}".strip()
            else:
                lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return "\n".join(lines)

    def _insert_qr_code(self, page, qr_content):
        """Método mejorado para inserción de QR con validación"""
        # Buscar área designada para el QR
        qr_markers = ["[Q]", "QR_CODE", "QR_IMAGE"]
        qr_area = None
        
        for marker in qr_markers:
            qr_area = page.search_for(marker)
            if qr_area:
                qr_area = qr_area[0]  # Tomar la primera coincidencia
                break
        
        # Si no se encuentra marcador, usar área predeterminada
        if not qr_area:
            page_center_x = page.rect.width / 2
            qr_size = 100  # Tamaño predeterminado
            qr_area = fitz.Rect(
                page_center_x - qr_size/2,
                400,  # Posición Y aproximada
                page_center_x + qr_size/2,
                400 + qr_size
            )
        
        try:
            # Validar área del QR
            if not qr_area.is_valid or qr_area.is_empty:
                raise ValueError("Área QR inválida")
            
            # Generar imagen QR
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=6,
                border=1,
            )
            qr.add_data(qr_content)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Insertar imagen
            page.insert_image(
                qr_area,
                stream=img_bytes.getvalue(),
                keep_proportion=True
            )
            
        except Exception as e:
            # print(f"Error generando QR: {e}")
            # Insertar mensaje de fallback
            fallback_text = "CÓDIGO QR\nNO DISPONIBLE"
            fallback_rect = fitz.Rect(
                qr_area.x0,
                qr_area.y0,
                qr_area.x1,
                qr_area.y0 + 40  # Altura suficiente para el texto
            )
            
            if fallback_rect.is_valid and not fallback_rect.is_empty:
                page.insert_textbox(
                    fallback_rect,
                    fallback_text,
                    fontsize=8,
                    color=(1, 0, 0),
                    align=1
                )
  
# Vistas
def doc_Guia(request, id):
    dependencia = request.GET.get('dependencia')
    generator = GuiaDocumentGenerator(id, dependencia)
    return generator.generate_response()

def doc_Inspeccion(request, id):
    dependencia = request.GET.get('dependencia')
    generator = InspeccionDocumentGenerator(id, dependencia)
    return generator.generate_response()

def doc_Credencial(request, id):
    dependencia = request.GET.get('dependencia')
    generator = CredencialDocumentGenerator(id, dependencia)
    return generator.generate_response()




def api_eliminar_solicitudes(request, id):
    solicitud = get_object_or_404(Solicitudes, id=id)
    solicitud.delete()
    return JsonResponse({
        "message": "Solicitud eliminada correctamente",
        "status": "success"
    }, status=200)


def validar_cedula(request):
    cedula = request.GET.get("cedula", "").strip()
    comercio_id = request.GET.get("comercio", "").strip()  # Obtener comercio enviado desde el frontend


    if not cedula or not cedula.startswith(("V-", "E-")):
        return JsonResponse({"error": "Formato inválido. Use V-12345678 o E-12345678."}, status=400)

    # Obtener los comercios asociados a la cédula
    solicitudes = Solicitudes.objects.filter(solicitante_cedula=cedula)
    comercios_asociados = set(solicitudes.values_list("id_solicitud__id_comercio", flat=True))
    cantidad_comercios = len(comercios_asociados)

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


def editar_solicitud(request, id):
    user = request.session.get('user')
    if not user:
        return redirect('/')

    # Obtener los objetos necesarios
    solicitud = get_object_or_404(Solicitudes, id=id)
    datos_solicitud = get_object_or_404(Comercio, id_comercio=solicitud.id_solicitud.id_comercio)
    requisitos = get_object_or_404(Requisitos, id_solicitud=solicitud.id)
    
    if request.method == 'POST':
        # Procesar el formulario enviado
        form = SolicitudForm(request.POST, instance=solicitud)
        requisitos_form = RequisitosForm(request.POST, instance=requisitos)
        
        if form.is_valid() and requisitos_form.is_valid():
            form.save()
            requisitos_form.save()
            messages.success(request, 'Solicitud actualizada correctamente')
            return redirect('certificados_prevencion')
    else:
        # Mostrar formulario con datos iniciales
        form = SolicitudForm(instance=solicitud)
        requisitos_form = RequisitosForm(instance=requisitos)
    
    # Contexto para la plantilla
    context = {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        'form': form,
        'requisitos_form': requisitos_form,
        'comercio': datos_solicitud,
        'editing': True,
        'solicitud_id': id
    }
    
    return render(request, 'Seguridad-prevencion/editar_solicitud.html', context)


def agregar_comercio(request):
    if request.method == "POST":
        comercio = request.POST.get("nombre_comercio")
        rif_empresarial = request.POST.get("rif_empresarial").strip()
        departamento = request.POST.get("departamento", "")

        # Validar si el RIF ya existe
        if Comercio.objects.filter(rif_empresarial=rif_empresarial).exists():
            messages.error(request, "Este RIF ya está registrado en el sistema.")
            
            # Guardar los datos del formulario en la sesión
            request.session['comercio_form_data'] = {
                'nombre_comercio': comercio,
                'rif_empresarial': rif_empresarial,
                'departamento': departamento
            }
            
            return redirect(f"/seguridad_prevencion/formulariocertificados/?rif_error=true")

        # Guardar en la base de datos si no existe
        nuevo_comercio = Comercio.objects.create(
            nombre_comercio=comercio,
            rif_empresarial=rif_empresarial,
            departamento=departamento
        )

        # Limpiar datos de sesión si existían
        if 'comercio_form_data' in request.session:
            del request.session['comercio_form_data']

        return redirect(f"/seguridad_prevencion/formulariocertificados/?comercio_id={nuevo_comercio.id_comercio}")

    return HttpResponse("Método no permitido", status=405)


def generar_excel_solicitudes(request):
    # print("=== INICIO DE generar_excel_solicitudes ===")
    
    user = request.session.get('user')
    # print(f"Datos de usuario en sesión: {user}")
    
    if not user:
        # print("Redireccionando: No hay usuario en sesión")
        return JsonResponse({'error': 'No autenticado'}, status=401)
    
    # Obtener parámetros de filtro
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    solo_ultimos = request.GET.get('solo_ultimos', 'true').lower() == 'true'
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 500))
    departamento_filtro = request.GET.get('departamento', '').strip()
    # print(f"Valor recibido de departamento: '{departamento_filtro}'")  # Debe mostrar 'Junin'
    
    # print(f"Parámetros recibidos - fecha_inicio: {fecha_inicio}, fecha_fin: {fecha_fin}, solo_ultimos: {solo_ultimos}, departamento: {departamento_filtro}")
    
    # Determinar departamentos permitidos según el usuario
    username = user.get('user', '')
    # print(f"Username obtenido: {username}")
    
    if username in ['SeRvEr', 'Sala_Situacional']:
        # print("Usuario identificado como Admin/Sala_Situacional")
        if departamento_filtro:
            departamentos_permitidos = [departamento_filtro]
        else:
            departamentos_permitidos = ['Junin', 'San Cristobal']
    elif username == 'Prevencion05':
        # print("Usuario identificado como Prevencion05")
        departamentos_permitidos = ['San Cristobal']
    elif username == 'ComandanciaJunin':
        # print("Usuario identificado como ComandanciaJunin")
        departamentos_permitidos = ['Junin']
    else:
        # print(f"Usuario no reconocido: {username}. Devolviendo lista vacía")
        return JsonResponse([], safe=False)

    # print(f"Departamentos permitidos: {departamentos_permitidos}")

    # Construir consulta base
    queryset = Solicitudes.objects.select_related(
        'id_solicitud', 'municipio', 'parroquia'
    ).filter(
        id_solicitud__departamento__in=departamentos_permitidos
    ).order_by('-fecha_solicitud')

    # print(f"Total registros inicial: {queryset.count()}")

    # Aplicar filtros de fecha si existen
    if fecha_inicio:
        try:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
            queryset = queryset.filter(fecha_solicitud__gte=fecha_inicio)
            # print(f"Filtro fecha_inicio aplicado: {fecha_inicio}")
        except ValueError:
            print("Formato de fecha inicio inválido")

    if fecha_fin:
        try:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
            queryset = queryset.filter(fecha_solicitud__lte=fecha_fin)
            # print(f"Filtro fecha_fin aplicado: {fecha_fin}")
        except ValueError:
            print("Formato de fecha fin inválido")

    # print(f"Total registros después de filtros fecha: {queryset.count()}")

    # Manejar diferentes modos de exportación
    if solo_ultimos:
        # print("Modo: Solo últimas solicitudes")
        # Obtener solo la última solicitud por comercio
        subquery = Solicitudes.objects.filter(
            id_solicitud=models.OuterRef('id_solicitud')
        ).order_by('-fecha_solicitud').values('id')[:1]

        queryset = queryset.filter(id__in=subquery)
    else:
        # print("Modo: Todas las solicitudes")
        # Para exportar todo, usamos paginación
        paginator = Paginator(queryset, page_size)
        page_obj = paginator.get_page(page)
        queryset = page_obj.object_list

    # print(f"Total registros final: {queryset.count()}")

    # Preparar datos
    data = []
    for solicitud in queryset:
        try:
            comercio = solicitud.id_solicitud
            data.append({
                'ID Comercio': comercio.id_comercio,
                'Nombre Comercio': comercio.nombre_comercio,
                'RIF Comercio': comercio.rif_empresarial,
                'Departamento': comercio.departamento,
                'Número de Teléfono': solicitud.numero_telefono,
                'Nombre y Apellido del Solicitante': solicitud.solicitante_nombre_apellido,
                'Fecha de Solicitud': solicitud.fecha_solicitud.strftime('%Y-%m-%d') if solicitud.fecha_solicitud else None,
                'Dirección': solicitud.direccion,
                'Estado': solicitud.estado,
                'Municipio': solicitud.municipio.municipio if solicitud.municipio else 'N/A',
                'Parroquia': solicitud.parroquia.parroquia if solicitud.parroquia else 'N/A',
            })
        except Exception as e:
            # print(f"Error procesando solicitud {solicitud.id}: {str(e)}")
            continue

    # print(f"Total de registros a exportar: {len(data)}")
    # print("=== FIN DE generar_excel_solicitudes ===")
    
    return JsonResponse(data, safe=False)


