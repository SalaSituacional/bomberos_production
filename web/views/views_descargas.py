from django.shortcuts import render, redirect
from django.http import HttpResponse
from ..models import *
import openpyxl
from openpyxl.utils import get_column_letter
import os
from django.conf import settings
import subprocess
from urllib.parse import urlparse
import pandas as pd

# Vista para descargar la base de datos
def descargar_base_datos(request):
    # Crear un nombre de archivo basado en la fecha actual
    fecha_actual = timezone.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Comprobamos el tipo de base de datos
    db_engine = settings.DATABASES['default']['ENGINE']
    
    if 'sqlite3' in db_engine:
        # Para SQLite, usamos el archivo .sqlite3 directamente
        db_path = settings.DATABASES['default']['NAME']
        filename = f"backup_{fecha_actual}.sqlite3"
        
        # Abrimos el archivo y lo enviamos como respuesta
        with open(db_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type="application/x-sqlite3")
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
    
    elif 'postgresql' in db_engine:
        # Obtener la URL de conexión completa de la base de datos
        db_url = "postgresql://bomberos_dbs_user:sB0cG00nvzS11aSYoROt2wNSWPnSIDyR@dpg-ctct69btq21c7380aogg-a.oregon-postgres.render.com/bomberos_dbs"
        
        url_parsed = urlparse(db_url)

        # Extraer información de la URL
        db_name = url_parsed.path[1:]  # Remueve el primer '/' de la ruta para obtener solo el nombre
        db_user = url_parsed.username
        db_password = url_parsed.password
        db_host = url_parsed.hostname

        # Configurar el nombre del archivo de respaldo
        filename = f"backup_{fecha_actual}.sql"

        # Configurar el comando pg_dump
       # Cambiar el comando pg_dump para exportar en formato de texto plano
        dump_cmd = [
            "pg_dump",
            "-h", db_host,
            "-U", db_user,
            "-d", db_name,
            "-F", "p"  # Cambiado a texto plano
        ]


        # Establecer la contraseña en la variable de entorno y ejecutar el comando
        os.environ['PGPASSWORD'] = db_password
        with subprocess.Popen(dump_cmd, stdout=subprocess.PIPE) as proc:
            response = HttpResponse(proc.stdout, content_type="application/sql")
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response    
    else:
        # Otros motores de base de datos
        return HttpResponse("Motor de base de datos no compatible", status=400)

# Api para crear el excel de exportacion de la tabla
def generar_excel_personal(request):
    # Crear un libro de trabajo y una hoja
    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = "Personal"

    # Agregar encabezados a la primera fila
    encabezados = [
        "Nombres", "Apellidos", "Jerarquia", "Cargo", 
        "Cedula", "Sexo", "Contrato", "Estado"
    ]
    hoja.append(encabezados)

    # Obtener datos de los procedimientos
    procedimientos = Personal.objects.exclude(id__in=[0, 4])

    # Agregar datos a la hoja
    for procedimiento in procedimientos:
        # Agregar la fila de datos
        hoja.append([
            procedimiento.nombres,
            procedimiento.apellidos,
            procedimiento.jerarquia,
            procedimiento.cargo,
            procedimiento.cedula,
            procedimiento.sexo,
            procedimiento.rol,
            procedimiento.status,
        ])

    # Ajustar el ancho de las columnas
    for column in hoja.columns:
        max_length = max(len(str(cell.value)) for cell in column if cell.value) + 2
        hoja.column_dimensions[get_column_letter(column[0].column)].width = max_length

    # Configurar la respuesta HTTP para descargar el archivo
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=personal.xlsx"
    workbook.save(response)
    return response

def generar_excel_capacitacion(request):
    # Crear un libro de trabajo y una hoja
    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = "Capacitacion"

    # Agregar encabezados a la primera fila
    encabezados = [
        "División", "Solicitante", "Jefe Comisión", "Municipio", 
        "Parroquia", "Fecha", "Hora", "Dirección", 
        "Tipo de Procedimiento", "Detalles", "Persona Presente", "Descripcion"
    ]
    hoja.append(encabezados)

    division = 9
    # Obtener datos de los procedimientos
    procedimientos = Procedimientos.objects.filter(id_division=division)

    def obtener_personas_y_detalles(set_relacionado, campo_descripcion=None):
        """Función auxiliar para obtener personas presentes y detalles de procedimientos"""
        personas = []
        detalles = []
        for item in set_relacionado:
            # Persona
            if hasattr(item, 'cedula'):
                personas.append(f"{item.nombres} {item.apellidos} {item.cedula}")
            if hasattr(item, 'nombre_propietario'):
                personas.append(f"{item.nombre_propietario} {item.apellido_propietario} {item.cedula_propietario}")
            # Detalle
            detalles.append(getattr(item, campo_descripcion, '') if campo_descripcion else str(item))
        return personas, detalles

    # Agregar datos a la hoja
    for procedimiento in procedimientos:
        # Obtener solicitante y jefe de comisión
        solicitante = (f"{procedimiento.id_solicitante.jerarquia} {procedimiento.id_solicitante.nombres} "
                       f"{procedimiento.id_solicitante.apellidos}") if procedimiento.id_solicitante else procedimiento.solicitante_externo
        jefe_comision = (f"{procedimiento.id_jefe_comision.jerarquia} {procedimiento.id_jefe_comision.nombres} "
                         f"{procedimiento.id_jefe_comision.apellidos}") if procedimiento.id_jefe_comision else ""

        personas_presentes, detalles_procedimientos = [], []

        # Agregar detalles de las distintas relaciones
        relaciones = [
            (procedimiento.abastecimiento_agua_set.all(), 'id_tipo_servicio.nombre_institucion'),
            (procedimiento.apoyo_unidades_set.all(), 'id_tipo_apoyo.tipo_apoyo'),
            (procedimiento.guardia_prevencion_set.all(), 'id_motivo_prevencion.motivo'),
            (procedimiento.atendido_no_efectuado_set.all(), None),
            (procedimiento.despliegue_seguridad_set.all(), 'motivo_despliegue.motivo'),
            (procedimiento.fallecidos_set.all(), 'motivo_fallecimiento'),
            (procedimiento.falsa_alarma_set.all(), 'motivo_alarma.motivo'),
            (procedimiento.servicios_especiales_set.all(), 'tipo_servicio.serv_especiales'),
            (procedimiento.rescate_set.all(), 'tipo_rescate.tipo_rescate'),
            (procedimiento.incendios_set.all(), 'id_tipo_incendio.tipo_incendio'),
            (procedimiento.atenciones_paramedicas_set.all(), 'tipo_atencion'),
            (procedimiento.traslado_prehospitalaria_set.all(), 'id_tipo_traslado.tipo_traslado'),
            (procedimiento.evaluacion_riesgo_set.all(), 'id_tipo_riesgo.tipo_riesgo'),
            (procedimiento.mitigacion_riesgos_set.all(), 'id_tipo_servicio.tipo_servicio'),
            (procedimiento.puesto_avanzada_set.all(), 'id_tipo_servicio.tipo_servicio'),
            (procedimiento.asesoramiento_set.all(), 'nombre_comercio'),
            (procedimiento.reinspeccion_prevencion_set.all(), 'nombre_comercio'),
            (procedimiento.retencion_preventiva_set.all(), 'tipo_cilindro'),
            (procedimiento.artificios_pirotecnicos_set.all(), 'tipo_procedimiento.tipo'),
            (procedimiento.inspeccion_establecimiento_art_set.all(), 'nombre_comercio'),
            (procedimiento.valoracion_medica_set.all(), None),
            (procedimiento.detalles_enfermeria_set.all(), None),
            (procedimiento.procedimientos_psicologia_set.all(), None),
            (procedimiento.procedimientos_capacitacion_set.all(), None),
            (procedimiento.procedimientos_brigada_set.all(), None),
            (procedimiento.procedimientos_frente_preventivo_set.all(), None),
            (procedimiento.jornada_medica_set.all(), None),
            (procedimiento.inspeccion_prevencion_asesorias_tecnicas_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_habitabilidad_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_otros_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_arbol_set.all(), 'tipo_inspeccion'),
            (procedimiento.investigacion_set.all(), 'id_tipo_investigacion.tipo_investigacion')
        ]
        
        # Procesar cada conjunto de datos
        for relacion, campo_descripcion in relaciones:
            personas_relacionadas, detalles_relacionados = obtener_personas_y_detalles(relacion, campo_descripcion)
            personas_presentes.extend(personas_relacionadas)
            detalles_procedimientos.extend(detalles_relacionados)

        # Convertir listas a cadenas separadas por ' -- '
        personas_presentes_str = " -- ".join(personas_presentes)
        detalles_str = " -- ".join(detalles_procedimientos)
        descripcion_str = " -- ".join(detalles_procedimientos)

        # Agregar la fila de datos
        hoja.append([
            procedimiento.id_division.division,
            solicitante,
            jefe_comision,
            procedimiento.id_municipio.municipio,
            procedimiento.id_parroquia.parroquia,
            procedimiento.fecha,
            procedimiento.hora,
            procedimiento.direccion,
            procedimiento.id_tipo_procedimiento.tipo_procedimiento,
            detalles_str,
            personas_presentes_str,
            descripcion_str,
        ])

    # Ajustar el ancho de las columnas
    for column in hoja.columns:
        max_length = max(len(str(cell.value)) for cell in column if cell.value) + 2
        hoja.column_dimensions[get_column_letter(column[0].column)].width = max_length

    # Configurar la respuesta HTTP para descargar el archivo
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=Capacitacion.xlsx"
    workbook.save(response)
    return response

def generar_excel_grumae(request):
    # Crear un libro de trabajo y una hoja
    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = "Grumae"

    # Agregar encabezados a la primera fila
    encabezados = [
        "División", "Solicitante", "Jefe Comisión", "Municipio", 
        "Parroquia", "Fecha", "Hora", "Dirección", 
        "Tipo de Procedimiento", "Detalles", "Persona Presente", "Descripcion"
    ]
    hoja.append(encabezados)

    division = 4
    # Obtener datos de los procedimientos
    procedimientos = Procedimientos.objects.filter(id_division=division)

    def obtener_personas_y_detalles(set_relacionado, campo_descripcion=None):
        """Función auxiliar para obtener personas presentes y detalles de procedimientos"""
        personas = []
        detalles = []
        for item in set_relacionado:
            # Persona
            if hasattr(item, 'cedula'):
                personas.append(f"{item.nombres} {item.apellidos} {item.cedula}")
            if hasattr(item, 'nombre_propietario'):
                personas.append(f"{item.nombre_propietario} {item.apellido_propietario} {item.cedula_propietario}")
            # Detalle
            detalles.append(getattr(item, campo_descripcion, '') if campo_descripcion else str(item))
        return personas, detalles

    # Agregar datos a la hoja
    for procedimiento in procedimientos:
        # Obtener solicitante y jefe de comisión
        solicitante = (f"{procedimiento.id_solicitante.jerarquia} {procedimiento.id_solicitante.nombres} "
                       f"{procedimiento.id_solicitante.apellidos}") if procedimiento.id_solicitante else procedimiento.solicitante_externo
        jefe_comision = (f"{procedimiento.id_jefe_comision.jerarquia} {procedimiento.id_jefe_comision.nombres} "
                         f"{procedimiento.id_jefe_comision.apellidos}") if procedimiento.id_jefe_comision else ""

        personas_presentes, detalles_procedimientos = [], []

        # Agregar detalles de las distintas relaciones
        relaciones = [
            (procedimiento.abastecimiento_agua_set.all(), 'id_tipo_servicio.nombre_institucion'),
            (procedimiento.apoyo_unidades_set.all(), 'id_tipo_apoyo.tipo_apoyo'),
            (procedimiento.guardia_prevencion_set.all(), 'id_motivo_prevencion.motivo'),
            (procedimiento.atendido_no_efectuado_set.all(), None),
            (procedimiento.despliegue_seguridad_set.all(), 'motivo_despliegue.motivo'),
            (procedimiento.fallecidos_set.all(), 'motivo_fallecimiento'),
            (procedimiento.falsa_alarma_set.all(), 'motivo_alarma.motivo'),
            (procedimiento.servicios_especiales_set.all(), 'tipo_servicio.serv_especiales'),
            (procedimiento.rescate_set.all(), 'tipo_rescate.tipo_rescate'),
            (procedimiento.incendios_set.all(), 'id_tipo_incendio.tipo_incendio'),
            (procedimiento.atenciones_paramedicas_set.all(), 'tipo_atencion'),
            (procedimiento.traslado_prehospitalaria_set.all(), 'id_tipo_traslado.tipo_traslado'),
            (procedimiento.evaluacion_riesgo_set.all(), 'id_tipo_riesgo.tipo_riesgo'),
            (procedimiento.mitigacion_riesgos_set.all(), 'id_tipo_servicio.tipo_servicio'),
            (procedimiento.puesto_avanzada_set.all(), 'id_tipo_servicio.tipo_servicio'),
            (procedimiento.asesoramiento_set.all(), 'nombre_comercio'),
            (procedimiento.reinspeccion_prevencion_set.all(), 'nombre_comercio'),
            (procedimiento.retencion_preventiva_set.all(), 'tipo_cilindro'),
            (procedimiento.artificios_pirotecnicos_set.all(), 'tipo_procedimiento.tipo'),
            (procedimiento.inspeccion_establecimiento_art_set.all(), 'nombre_comercio'),
            (procedimiento.valoracion_medica_set.all(), None),
            (procedimiento.detalles_enfermeria_set.all(), None),
            (procedimiento.procedimientos_psicologia_set.all(), None),
            (procedimiento.procedimientos_capacitacion_set.all(), None),
            (procedimiento.procedimientos_brigada_set.all(), None),
            (procedimiento.procedimientos_frente_preventivo_set.all(), None),
            (procedimiento.jornada_medica_set.all(), None),
            (procedimiento.inspeccion_prevencion_asesorias_tecnicas_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_habitabilidad_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_otros_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_arbol_set.all(), 'tipo_inspeccion'),
            (procedimiento.investigacion_set.all(), 'id_tipo_investigacion.tipo_investigacion')
        ]
        
        # Procesar cada conjunto de datos
        for relacion, campo_descripcion in relaciones:
            personas_relacionadas, detalles_relacionados = obtener_personas_y_detalles(relacion, campo_descripcion)
            personas_presentes.extend(personas_relacionadas)
            detalles_procedimientos.extend(detalles_relacionados)

        # Convertir listas a cadenas separadas por ' -- '
        personas_presentes_str = " -- ".join(personas_presentes)
        detalles_str = " -- ".join(detalles_procedimientos)
        descripcion_str = " -- ".join(detalles_procedimientos)

        # Agregar la fila de datos
        hoja.append([
            procedimiento.id_division.division,
            solicitante,
            jefe_comision,
            procedimiento.id_municipio.municipio,
            procedimiento.id_parroquia.parroquia,
            procedimiento.fecha,
            procedimiento.hora,
            procedimiento.direccion,
            procedimiento.id_tipo_procedimiento.tipo_procedimiento,
            detalles_str,
            personas_presentes_str,
            descripcion_str,
        ])

    # Ajustar el ancho de las columnas
    for column in hoja.columns:
        max_length = max(len(str(cell.value)) for cell in column if cell.value) + 2
        hoja.column_dimensions[get_column_letter(column[0].column)].width = max_length

    # Configurar la respuesta HTTP para descargar el archivo
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=Grumae.xlsx"
    workbook.save(response)
    return response

def generar_excel_rescate(request):
    # Crear un libro de trabajo y una hoja
    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = "Rescate"

    # Agregar encabezados a la primera fila
    encabezados = [
        "División", "Solicitante", "Jefe Comisión", "Municipio", 
        "Parroquia", "Fecha", "Hora", "Dirección", 
        "Tipo de Procedimiento", "Detalles", "Persona Presente", "Descripcion"
    ]
    hoja.append(encabezados)

    division = 1
    # Obtener datos de los procedimientos
    procedimientos = Procedimientos.objects.filter(id_division=division)

    def obtener_personas_y_detalles(set_relacionado, campo_descripcion=None):
        """Función auxiliar para obtener personas presentes y detalles de procedimientos"""
        personas = []
        detalles = []
        for item in set_relacionado:
            # Persona
            if hasattr(item, 'cedula'):
                personas.append(f"{item.nombres} {item.apellidos} {item.cedula}")
            if hasattr(item, 'nombre_propietario'):
                personas.append(f"{item.nombre_propietario} {item.apellido_propietario} {item.cedula_propietario}")
            # Detalle
            detalles.append(getattr(item, campo_descripcion, '') if campo_descripcion else str(item))
        return personas, detalles

    # Agregar datos a la hoja
    for procedimiento in procedimientos:
        # Obtener solicitante y jefe de comisión
        solicitante = (f"{procedimiento.id_solicitante.jerarquia} {procedimiento.id_solicitante.nombres} "
                       f"{procedimiento.id_solicitante.apellidos}") if procedimiento.id_solicitante else procedimiento.solicitante_externo
        jefe_comision = (f"{procedimiento.id_jefe_comision.jerarquia} {procedimiento.id_jefe_comision.nombres} "
                         f"{procedimiento.id_jefe_comision.apellidos}") if procedimiento.id_jefe_comision else ""

        personas_presentes, detalles_procedimientos = [], []

        # Agregar detalles de las distintas relaciones
        relaciones = [
            (procedimiento.abastecimiento_agua_set.all(), 'id_tipo_servicio.nombre_institucion'),
            (procedimiento.apoyo_unidades_set.all(), 'id_tipo_apoyo.tipo_apoyo'),
            (procedimiento.guardia_prevencion_set.all(), 'id_motivo_prevencion.motivo'),
            (procedimiento.atendido_no_efectuado_set.all(), None),
            (procedimiento.despliegue_seguridad_set.all(), 'motivo_despliegue.motivo'),
            (procedimiento.fallecidos_set.all(), 'motivo_fallecimiento'),
            (procedimiento.falsa_alarma_set.all(), 'motivo_alarma.motivo'),
            (procedimiento.servicios_especiales_set.all(), 'tipo_servicio.serv_especiales'),
            (procedimiento.rescate_set.all(), 'tipo_rescate.tipo_rescate'),
            (procedimiento.incendios_set.all(), 'id_tipo_incendio.tipo_incendio'),
            (procedimiento.atenciones_paramedicas_set.all(), 'tipo_atencion'),
            (procedimiento.traslado_prehospitalaria_set.all(), 'id_tipo_traslado.tipo_traslado'),
            (procedimiento.evaluacion_riesgo_set.all(), 'id_tipo_riesgo.tipo_riesgo'),
            (procedimiento.mitigacion_riesgos_set.all(), 'id_tipo_servicio.tipo_servicio'),
            (procedimiento.puesto_avanzada_set.all(), 'id_tipo_servicio.tipo_servicio'),
            (procedimiento.asesoramiento_set.all(), 'nombre_comercio'),
            (procedimiento.reinspeccion_prevencion_set.all(), 'nombre_comercio'),
            (procedimiento.retencion_preventiva_set.all(), 'tipo_cilindro'),
            (procedimiento.artificios_pirotecnicos_set.all(), 'tipo_procedimiento.tipo'),
            (procedimiento.inspeccion_establecimiento_art_set.all(), 'nombre_comercio'),
            (procedimiento.valoracion_medica_set.all(), None),
            (procedimiento.detalles_enfermeria_set.all(), None),
            (procedimiento.procedimientos_psicologia_set.all(), None),
            (procedimiento.procedimientos_capacitacion_set.all(), None),
            (procedimiento.procedimientos_brigada_set.all(), None),
            (procedimiento.procedimientos_frente_preventivo_set.all(), None),
            (procedimiento.jornada_medica_set.all(), None),
            (procedimiento.inspeccion_prevencion_asesorias_tecnicas_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_habitabilidad_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_otros_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_arbol_set.all(), 'tipo_inspeccion'),
            (procedimiento.investigacion_set.all(), 'id_tipo_investigacion.tipo_investigacion')
        ]
        
        # Procesar cada conjunto de datos
        for relacion, campo_descripcion in relaciones:
            personas_relacionadas, detalles_relacionados = obtener_personas_y_detalles(relacion, campo_descripcion)
            personas_presentes.extend(personas_relacionadas)
            detalles_procedimientos.extend(detalles_relacionados)

        # Convertir listas a cadenas separadas por ' -- '
        personas_presentes_str = " -- ".join(personas_presentes)
        detalles_str = " -- ".join(detalles_procedimientos)
        descripcion_str = " -- ".join(detalles_procedimientos)

        # Agregar la fila de datos
        hoja.append([
            procedimiento.id_division.division,
            solicitante,
            jefe_comision,
            procedimiento.id_municipio.municipio,
            procedimiento.id_parroquia.parroquia,
            procedimiento.fecha,
            procedimiento.hora,
            procedimiento.direccion,
            procedimiento.id_tipo_procedimiento.tipo_procedimiento,
            detalles_str,
            personas_presentes_str,
            descripcion_str,
        ])

    # Ajustar el ancho de las columnas
    for column in hoja.columns:
        max_length = max(len(str(cell.value)) for cell in column if cell.value) + 2
        hoja.column_dimensions[get_column_letter(column[0].column)].width = max_length

    # Configurar la respuesta HTTP para descargar el archivo
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=Rescate.xlsx"
    workbook.save(response)
    return response

def generar_excel_prehospitalaria(request):
    # Crear un libro de trabajo y una hoja
    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = "Prehospitalaria"

    # Agregar encabezados a la primera fila
    encabezados = [
        "División", "Solicitante", "Jefe Comisión", "Municipio", 
        "Parroquia", "Fecha", "Hora", "Dirección", 
        "Tipo de Procedimiento", "Detalles", "Persona Presente", "Descripcion"
    ]
    hoja.append(encabezados)

    division = 5
    # Obtener datos de los procedimientos
    procedimientos = Procedimientos.objects.filter(id_division=division)

    def obtener_personas_y_detalles(set_relacionado, campo_descripcion=None):
        """Función auxiliar para obtener personas presentes y detalles de procedimientos"""
        personas = []
        detalles = []
        for item in set_relacionado:
            # Verifica los atributos según el modelo
            if hasattr(item, 'cedula'):
                # Para el modelo Traslado_Prehospitalaria, usa 'nombre', 'apellido' y 'cedula'
                if hasattr(item, 'nombre') and hasattr(item, 'apellido') and hasattr(item, 'cedula'):
                    personas.append(f"{item.nombre} {item.apellido} {item.cedula}")
                # Otros modelos pueden tener un formato diferente para los datos
                elif hasattr(item, 'nombre_propietario') and hasattr(item, 'apellido_propietario'):
                    personas.append(f"{item.nombre_propietario} {item.apellido_propietario} {item.cedula_propietario}")
            # Detalle
            detalles.append(getattr(item, campo_descripcion, '') if campo_descripcion else str(item))
        return personas, detalles

    # Agregar datos a la hoja
    for procedimiento in procedimientos:
        # Obtener solicitante y jefe de comisión
        solicitante = (f"{procedimiento.id_solicitante.jerarquia} {procedimiento.id_solicitante.nombres} "
                       f"{procedimiento.id_solicitante.apellidos}") if procedimiento.id_solicitante else procedimiento.solicitante_externo
        jefe_comision = (f"{procedimiento.id_jefe_comision.jerarquia} {procedimiento.id_jefe_comision.nombres} "
                         f"{procedimiento.id_jefe_comision.apellidos}") if procedimiento.id_jefe_comision else ""

        personas_presentes, detalles_procedimientos = [], []

        # Agregar detalles de las distintas relaciones
        relaciones = [
            (procedimiento.abastecimiento_agua_set.all(), 'id_tipo_servicio.nombre_institucion'),
            (procedimiento.apoyo_unidades_set.all(), 'id_tipo_apoyo.tipo_apoyo'),
            (procedimiento.guardia_prevencion_set.all(), 'id_motivo_prevencion.motivo'),
            (procedimiento.atendido_no_efectuado_set.all(), None),
            (procedimiento.despliegue_seguridad_set.all(), 'motivo_despliegue.motivo'),
            (procedimiento.fallecidos_set.all(), 'motivo_fallecimiento'),
            (procedimiento.falsa_alarma_set.all(), 'motivo_alarma.motivo'),
            (procedimiento.servicios_especiales_set.all(), 'tipo_servicio.serv_especiales'),
            (procedimiento.rescate_set.all(), 'tipo_rescate.tipo_rescate'),
            (procedimiento.incendios_set.all(), 'id_tipo_incendio.tipo_incendio'),
            (procedimiento.atenciones_paramedicas_set.all(), 'tipo_atencion'),
            (procedimiento.traslado_prehospitalaria_set.all(), 'id_tipo_traslado.tipo_traslado'),  # Aquí agregamos Traslado_Prehospitalaria
            (procedimiento.evaluacion_riesgo_set.all(), 'id_tipo_riesgo.tipo_riesgo'),
            (procedimiento.mitigacion_riesgos_set.all(), 'id_tipo_servicio.tipo_servicio'),
            (procedimiento.puesto_avanzada_set.all(), 'id_tipo_servicio.tipo_servicio'),
            (procedimiento.asesoramiento_set.all(), 'nombre_comercio'),
            (procedimiento.reinspeccion_prevencion_set.all(), 'nombre_comercio'),
            (procedimiento.retencion_preventiva_set.all(), 'tipo_cilindro'),
            (procedimiento.artificios_pirotecnicos_set.all(), 'tipo_procedimiento.tipo'),
            (procedimiento.inspeccion_establecimiento_art_set.all(), 'nombre_comercio'),
            (procedimiento.valoracion_medica_set.all(), None),
            (procedimiento.detalles_enfermeria_set.all(), None),
            (procedimiento.procedimientos_psicologia_set.all(), None),
            (procedimiento.procedimientos_capacitacion_set.all(), None),
            (procedimiento.procedimientos_brigada_set.all(), None),
            (procedimiento.procedimientos_frente_preventivo_set.all(), None),
            (procedimiento.jornada_medica_set.all(), None),
            (procedimiento.inspeccion_prevencion_asesorias_tecnicas_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_habitabilidad_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_otros_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_arbol_set.all(), 'tipo_inspeccion'),
            (procedimiento.investigacion_set.all(), 'id_tipo_investigacion.tipo_investigacion')
        ]
        
        # Procesar cada conjunto de datos
        for relacion, campo_descripcion in relaciones:
            personas_relacionadas, detalles_relacionados = obtener_personas_y_detalles(relacion, campo_descripcion)
            personas_presentes.extend(personas_relacionadas)
            detalles_procedimientos.extend(detalles_relacionados)

        # Convertir listas a cadenas separadas por ' -- '
        personas_presentes_str = " -- ".join(personas_presentes)
        detalles_str = " -- ".join(detalles_procedimientos)
        descripcion_str = " -- ".join(detalles_procedimientos)

        # Agregar la fila de datos
        hoja.append([
            procedimiento.id_division.division,
            solicitante,
            jefe_comision,
            procedimiento.id_municipio.municipio,
            procedimiento.id_parroquia.parroquia,
            procedimiento.fecha,
            procedimiento.hora,
            procedimiento.direccion,
            procedimiento.id_tipo_procedimiento.tipo_procedimiento,
            detalles_str,
            personas_presentes_str,
            descripcion_str,
        ])

    # Ajustar el ancho de las columnas
    for column in hoja.columns:
        max_length = max(len(str(cell.value)) for cell in column if cell.value) + 2
        hoja.column_dimensions[get_column_letter(column[0].column)].width = max_length

    # Configurar la respuesta HTTP para descargar el archivo
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=Prehospitalaria.xlsx"
    workbook.save(response)
    return response

def generar_excel_enfermeria(request):
    # Crear un libro de trabajo y una hoja
    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = "Enfermeria"

    # Agregar encabezados a la primera fila
    encabezados = [
        "División", "Solicitante", "Jefe Comisión", "Municipio", 
        "Parroquia", "Fecha", "Hora", "Dirección", 
        "Tipo de Procedimiento", "Detalles", "Persona Presente", "Descripcion"
    ]
    hoja.append(encabezados)

    division = 6
    # Obtener datos de los procedimientos
    procedimientos = Procedimientos.objects.filter(id_division=division)

    def obtener_personas_y_detalles(set_relacionado, campo_descripcion=None):
        """Función auxiliar para obtener personas presentes y detalles de procedimientos"""
        personas = []
        detalles = []
        for item in set_relacionado:
            # Persona
            if hasattr(item, 'cedula'):
                # Usar los campos de 'Detalles_Enfermeria' según los detalles proporcionados
                if hasattr(item, 'nombre') and hasattr(item, 'apellido') and hasattr(item, 'cedula'):
                    personas.append(f"{item.nombre} {item.apellido} {item.cedula}")
            # Detalle
            detalles.append(getattr(item, campo_descripcion, '') if campo_descripcion else str(item))
        return personas, detalles

    # Agregar datos a la hoja
    for procedimiento in procedimientos:
        # Obtener solicitante y jefe de comisión
        solicitante = (f"{procedimiento.id_solicitante.jerarquia} {procedimiento.id_solicitante.nombres} "
                       f"{procedimiento.id_solicitante.apellidos}") if procedimiento.id_solicitante else procedimiento.solicitante_externo
        jefe_comision = (f"{procedimiento.id_jefe_comision.jerarquia} {procedimiento.id_jefe_comision.nombres} "
                         f"{procedimiento.id_jefe_comision.apellidos}") if procedimiento.id_jefe_comision else ""

        personas_presentes, detalles_procedimientos = [], []

        # Agregar detalles de las distintas relaciones
        relaciones = [
            (procedimiento.abastecimiento_agua_set.all(), 'id_tipo_servicio.nombre_institucion'),
            (procedimiento.apoyo_unidades_set.all(), 'id_tipo_apoyo.tipo_apoyo'),
            (procedimiento.guardia_prevencion_set.all(), 'id_motivo_prevencion.motivo'),
            (procedimiento.atendido_no_efectuado_set.all(), None),
            (procedimiento.despliegue_seguridad_set.all(), 'motivo_despliegue.motivo'),
            (procedimiento.fallecidos_set.all(), 'motivo_fallecimiento'),
            (procedimiento.falsa_alarma_set.all(), 'motivo_alarma.motivo'),
            (procedimiento.servicios_especiales_set.all(), 'tipo_servicio.serv_especiales'),
            (procedimiento.rescate_set.all(), 'tipo_rescate.tipo_rescate'),
            (procedimiento.incendios_set.all(), 'id_tipo_incendio.tipo_incendio'),
            (procedimiento.atenciones_paramedicas_set.all(), 'tipo_atencion'),
            (procedimiento.traslado_prehospitalaria_set.all(), 'id_tipo_traslado.tipo_traslado'),
            (procedimiento.evaluacion_riesgo_set.all(), 'id_tipo_riesgo.tipo_riesgo'),
            (procedimiento.mitigacion_riesgos_set.all(), 'id_tipo_servicio.tipo_servicio'),
            (procedimiento.puesto_avanzada_set.all(), 'id_tipo_servicio.tipo_servicio'),
            (procedimiento.asesoramiento_set.all(), 'nombre_comercio'),
            (procedimiento.reinspeccion_prevencion_set.all(), 'nombre_comercio'),
            (procedimiento.retencion_preventiva_set.all(), 'tipo_cilindro'),
            (procedimiento.artificios_pirotecnicos_set.all(), 'tipo_procedimiento.tipo'),
            (procedimiento.inspeccion_establecimiento_art_set.all(), 'nombre_comercio'),
            (procedimiento.valoracion_medica_set.all(), None),
            (procedimiento.detalles_enfermeria_set.all(), None),
            (procedimiento.procedimientos_psicologia_set.all(), None),
            (procedimiento.procedimientos_capacitacion_set.all(), None),
            (procedimiento.procedimientos_brigada_set.all(), None),
            (procedimiento.procedimientos_frente_preventivo_set.all(), None),
            (procedimiento.jornada_medica_set.all(), None),
            (procedimiento.inspeccion_prevencion_asesorias_tecnicas_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_habitabilidad_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_otros_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_arbol_set.all(), 'tipo_inspeccion'),
            (procedimiento.investigacion_set.all(), 'id_tipo_investigacion.tipo_investigacion')
        ]
        
        # Procesar cada conjunto de datos
        for relacion, campo_descripcion in relaciones:
            personas_relacionadas, detalles_relacionados = obtener_personas_y_detalles(relacion, campo_descripcion)
            personas_presentes.extend(personas_relacionadas)
            detalles_procedimientos.extend(detalles_relacionados)

        # Convertir listas a cadenas separadas por ' -- '
        personas_presentes_str = " -- ".join(personas_presentes)
        detalles_str = " -- ".join(detalles_procedimientos)
        descripcion_str = " -- ".join(detalles_procedimientos)

        # Agregar la fila de datos
        hoja.append([
            procedimiento.id_division.division,
            solicitante,
            jefe_comision,
            procedimiento.id_municipio.municipio,
            procedimiento.id_parroquia.parroquia,
            procedimiento.fecha,
            procedimiento.hora,
            procedimiento.direccion,
            procedimiento.id_tipo_procedimiento.tipo_procedimiento,
            detalles_str,
            personas_presentes_str,
            descripcion_str,
        ])

    # Ajustar el ancho de las columnas
    for column in hoja.columns:
        max_length = max(len(str(cell.value)) for cell in column if cell.value) + 2
        hoja.column_dimensions[get_column_letter(column[0].column)].width = max_length

    # Configurar la respuesta HTTP para descargar el archivo
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=Enfermeria.xlsx"
    workbook.save(response)
    return response

def generar_excel_serviciosmedicos(request):
    # Crear un libro de trabajo y una hoja
    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = "Servicios Medicos"

    # Agregar encabezados a la primera fila
    encabezados = [
        "División", "Solicitante", "Jefe Comisión", "Municipio", 
        "Parroquia", "Fecha", "Hora", "Dirección", 
        "Tipo de Procedimiento", "Detalles", "Persona Presente", "Descripcion"
    ]
    hoja.append(encabezados)

    division = 7
    # Obtener datos de los procedimientos
    procedimientos = Procedimientos.objects.filter(id_division=division)

    def obtener_personas_y_detalles(set_relacionado, campo_descripcion=None):
        """Función auxiliar para obtener personas presentes y detalles de procedimientos"""
        personas = []
        detalles = []
        for item in set_relacionado:
            # Persona
            if hasattr(item, 'cedula'):
                # Verificar si el objeto tiene los atributos 'nombres' y 'apellidos'
                if hasattr(item, 'nombres') and hasattr(item, 'apellidos') and hasattr(item, 'cedula'):
                    personas.append(f"{item.nombres} {item.apellidos} {item.cedula}")
                elif hasattr(item, 'nombre') and hasattr(item, 'apellido') and hasattr(item, 'cedula'):
                    # Si no tiene 'nombres' y 'apellidos', pero tiene 'nombre' y 'apellido'
                    personas.append(f"{item.nombre} {item.apellido} {item.cedula}")
                else:
                    # Si no tiene esos campos, agregar una forma genérica
                    personas.append(f"{item.cedula}")  # Solo agregar la cédula
            # Detalle
            detalles.append(getattr(item, campo_descripcion, '') if campo_descripcion else str(item))
        return personas, detalles

    # Agregar datos a la hoja
    for procedimiento in procedimientos:
        # Obtener solicitante y jefe de comisión
        solicitante = (f"{procedimiento.id_solicitante.jerarquia} {procedimiento.id_solicitante.nombres} "
                       f"{procedimiento.id_solicitante.apellidos}") if procedimiento.id_solicitante else procedimiento.solicitante_externo
        jefe_comision = (f"{procedimiento.id_jefe_comision.jerarquia} {procedimiento.id_jefe_comision.nombres} "
                         f"{procedimiento.id_jefe_comision.apellidos}") if procedimiento.id_jefe_comision else ""

        personas_presentes, detalles_procedimientos = [], []

        # Agregar detalles de las distintas relaciones
        relaciones = [
            (procedimiento.abastecimiento_agua_set.all(), 'id_tipo_servicio.nombre_institucion'),
            (procedimiento.apoyo_unidades_set.all(), 'id_tipo_apoyo.tipo_apoyo'),
            (procedimiento.guardia_prevencion_set.all(), 'id_motivo_prevencion.motivo'),
            (procedimiento.atendido_no_efectuado_set.all(), None),
            (procedimiento.despliegue_seguridad_set.all(), 'motivo_despliegue.motivo'),
            (procedimiento.fallecidos_set.all(), 'motivo_fallecimiento'),
            (procedimiento.falsa_alarma_set.all(), 'motivo_alarma.motivo'),
            (procedimiento.servicios_especiales_set.all(), 'tipo_servicio.serv_especiales'),
            (procedimiento.rescate_set.all(), 'tipo_rescate.tipo_rescate'),
            (procedimiento.incendios_set.all(), 'id_tipo_incendio.tipo_incendio'),
            (procedimiento.atenciones_paramedicas_set.all(), 'tipo_atencion'),
            (procedimiento.traslado_prehospitalaria_set.all(), 'id_tipo_traslado.tipo_traslado'),
            (procedimiento.evaluacion_riesgo_set.all(), 'id_tipo_riesgo.tipo_riesgo'),
            (procedimiento.mitigacion_riesgos_set.all(), 'id_tipo_servicio.tipo_servicio'),
            (procedimiento.puesto_avanzada_set.all(), 'id_tipo_servicio.tipo_servicio'),
            (procedimiento.asesoramiento_set.all(), 'nombre_comercio'),
            (procedimiento.reinspeccion_prevencion_set.all(), 'nombre_comercio'),
            (procedimiento.retencion_preventiva_set.all(), 'tipo_cilindro'),
            (procedimiento.artificios_pirotecnicos_set.all(), 'tipo_procedimiento.tipo'),
            (procedimiento.inspeccion_establecimiento_art_set.all(), 'nombre_comercio'),
            (procedimiento.valoracion_medica_set.all(), None),
            (procedimiento.detalles_enfermeria_set.all(), None),
            (procedimiento.procedimientos_psicologia_set.all(), None),
            (procedimiento.procedimientos_capacitacion_set.all(), None),
            (procedimiento.procedimientos_brigada_set.all(), None),
            (procedimiento.procedimientos_frente_preventivo_set.all(), None),
            (procedimiento.jornada_medica_set.all(), None),
            (procedimiento.inspeccion_prevencion_asesorias_tecnicas_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_habitabilidad_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_otros_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_arbol_set.all(), 'tipo_inspeccion'),
            (procedimiento.investigacion_set.all(), 'id_tipo_investigacion.tipo_investigacion')
        ]
        
        # Procesar cada conjunto de datos
        for relacion, campo_descripcion in relaciones:
            personas_relacionadas, detalles_relacionados = obtener_personas_y_detalles(relacion, campo_descripcion)
            personas_presentes.extend(personas_relacionadas)
            detalles_procedimientos.extend(detalles_relacionados)

        # Convertir listas a cadenas separadas por ' -- '
        personas_presentes_str = " -- ".join(personas_presentes)
        detalles_str = " -- ".join(detalles_procedimientos)
        descripcion_str = " -- ".join(detalles_procedimientos)

        # Agregar la fila de datos
        hoja.append([
            procedimiento.id_division.division,
            solicitante,
            jefe_comision,
            procedimiento.id_municipio.municipio,
            procedimiento.id_parroquia.parroquia,
            procedimiento.fecha,
            procedimiento.hora,
            procedimiento.direccion,
            procedimiento.id_tipo_procedimiento.tipo_procedimiento,
            detalles_str,
            personas_presentes_str,
            descripcion_str,
        ])

    # Ajustar el ancho de las columnas
    for column in hoja.columns:
        max_length = max(len(str(cell.value)) for cell in column if cell.value) + 2
        hoja.column_dimensions[get_column_letter(column[0].column)].width = max_length

    # Configurar la respuesta HTTP para descargar el archivo
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=Servicios_Medicos.xlsx"
    workbook.save(response)
    return response

def generar_excel_psicologia(request):
    # Crear un libro de trabajo y una hoja
    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = "Psicologia"

    # Agregar encabezados a la primera fila
    encabezados = [
        "División", "Solicitante", "Jefe Comisión", "Municipio", 
        "Parroquia", "Fecha", "Hora", "Dirección", 
        "Tipo de Procedimiento", "Detalles", "Persona Presente", "Descripcion"
    ]
    hoja.append(encabezados)

    division = 8
    # Obtener datos de los procedimientos
    procedimientos = Procedimientos.objects.filter(id_division=division)

    def obtener_personas_y_detalles(set_relacionado, campo_descripcion=None):
        """Función auxiliar para obtener personas presentes y detalles de procedimientos"""
        personas = []
        detalles = []
        for item in set_relacionado:
            # Persona (en este caso del modelo Procedimientos_Psicologia)
            if hasattr(item, 'cedula'):
                # Accedemos a los campos correctos: 'nombre' y 'apellido' en lugar de 'nombres' y 'apellidos'
                personas.append(f"{item.nombre} {item.apellido} {item.cedula}")
            # Detalle
            detalles.append(getattr(item, campo_descripcion, '') if campo_descripcion else str(item))
        return personas, detalles

    # Agregar datos a la hoja
    for procedimiento in procedimientos:
        # Obtener solicitante y jefe de comisión
        solicitante = (f"{procedimiento.id_solicitante.jerarquia} {procedimiento.id_solicitante.nombres} "
                       f"{procedimiento.id_solicitante.apellidos}") if procedimiento.id_solicitante else procedimiento.solicitante_externo
        jefe_comision = (f"{procedimiento.id_jefe_comision.jerarquia} {procedimiento.id_jefe_comision.nombres} "
                         f"{procedimiento.id_jefe_comision.apellidos}") if procedimiento.id_jefe_comision else ""

        personas_presentes, detalles_procedimientos = [], []

        # Agregar detalles de las distintas relaciones
        relaciones = [
            (procedimiento.abastecimiento_agua_set.all(), 'id_tipo_servicio.nombre_institucion'),
            (procedimiento.apoyo_unidades_set.all(), 'id_tipo_apoyo.tipo_apoyo'),
            (procedimiento.guardia_prevencion_set.all(), 'id_motivo_prevencion.motivo'),
            (procedimiento.atendido_no_efectuado_set.all(), None),
            (procedimiento.despliegue_seguridad_set.all(), 'motivo_despliegue.motivo'),
            (procedimiento.fallecidos_set.all(), 'motivo_fallecimiento'),
            (procedimiento.falsa_alarma_set.all(), 'motivo_alarma.motivo'),
            (procedimiento.servicios_especiales_set.all(), 'tipo_servicio.serv_especiales'),
            (procedimiento.rescate_set.all(), 'tipo_rescate.tipo_rescate'),
            (procedimiento.incendios_set.all(), 'id_tipo_incendio.tipo_incendio'),
            (procedimiento.atenciones_paramedicas_set.all(), 'tipo_atencion'),
            (procedimiento.traslado_prehospitalaria_set.all(), 'id_tipo_traslado.tipo_traslado'),
            (procedimiento.evaluacion_riesgo_set.all(), 'id_tipo_riesgo.tipo_riesgo'),
            (procedimiento.mitigacion_riesgos_set.all(), 'id_tipo_servicio.tipo_servicio'),
            (procedimiento.puesto_avanzada_set.all(), 'id_tipo_servicio.tipo_servicio'),
            (procedimiento.asesoramiento_set.all(), 'nombre_comercio'),
            (procedimiento.reinspeccion_prevencion_set.all(), 'nombre_comercio'),
            (procedimiento.retencion_preventiva_set.all(), 'tipo_cilindro'),
            (procedimiento.artificios_pirotecnicos_set.all(), 'tipo_procedimiento.tipo'),
            (procedimiento.inspeccion_establecimiento_art_set.all(), 'nombre_comercio'),
            (procedimiento.valoracion_medica_set.all(), None),
            (procedimiento.detalles_enfermeria_set.all(), None),
            (procedimiento.procedimientos_psicologia_set.all(), None),
            (procedimiento.procedimientos_capacitacion_set.all(), None),
            (procedimiento.procedimientos_brigada_set.all(), None),
            (procedimiento.procedimientos_frente_preventivo_set.all(), None),
            (procedimiento.jornada_medica_set.all(), None),
            (procedimiento.inspeccion_prevencion_asesorias_tecnicas_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_habitabilidad_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_otros_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_arbol_set.all(), 'tipo_inspeccion'),
            (procedimiento.investigacion_set.all(), 'id_tipo_investigacion.tipo_investigacion')
        ]
        
        # Procesar cada conjunto de datos
        for relacion, campo_descripcion in relaciones:
            personas_relacionadas, detalles_relacionados = obtener_personas_y_detalles(relacion, campo_descripcion)
            personas_presentes.extend(personas_relacionadas)
            detalles_procedimientos.extend(detalles_relacionados)

        # Convertir listas a cadenas separadas por ' -- '
        personas_presentes_str = " -- ".join(personas_presentes)
        detalles_str = " -- ".join(detalles_procedimientos)
        descripcion_str = " -- ".join(detalles_procedimientos)

        # Agregar la fila de datos
        hoja.append([
            procedimiento.id_division.division,
            solicitante,
            jefe_comision,
            procedimiento.id_municipio.municipio,
            procedimiento.id_parroquia.parroquia,
            procedimiento.fecha,
            procedimiento.hora,
            procedimiento.direccion,
            procedimiento.id_tipo_procedimiento.tipo_procedimiento,
            detalles_str,
            personas_presentes_str,
            descripcion_str,
        ])

    # Ajustar el ancho de las columnas
    for column in hoja.columns:
        max_length = max(len(str(cell.value)) for cell in column if cell.value) + 2
        hoja.column_dimensions[get_column_letter(column[0].column)].width = max_length

    # Configurar la respuesta HTTP para descargar el archivo
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=Psicologia.xlsx"
    workbook.save(response)
    return response

# operaciones 
def obtener_personas_y_detalles(set_relacionado, campo_descripcion=None):
    """Función auxiliar para obtener personas presentes y detalles de procedimientos"""
    personas = []
    detalles = []
    
    for item in set_relacionado:
        # Verificar si el objeto tiene los atributos 'nombres', 'apellidos' y 'cedula'
        if hasattr(item, 'nombres') and hasattr(item, 'apellidos') and hasattr(item, 'cedula'):
            # Persona con 'nombres', 'apellidos' y 'cedula'
            personas.append(f"{item.nombres} {item.apellidos} {item.cedula}")
        elif hasattr(item, 'nombre') and hasattr(item, 'apellido') and hasattr(item, 'cedula_propietario'):
            # Persona con 'nombre', 'apellido' y 'cedula_propietario' (para objetos como 'Retencion_Preventiva')
            personas.append(f"{item.nombre} {item.apellido} {item.cedula_propietario}")
        else:
            # Si no tiene esos atributos, agregar algo por defecto o vacío
            personas.append("Persona desconocida")

        # Detalle
        detalles.append(getattr(item, campo_descripcion, '') if campo_descripcion else str(item))

    return personas, detalles

def generar_excel_operaciones(request):
    # Crear un libro de trabajo y una hoja
    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = "Operaciones"

    # Agregar encabezados a la primera fila
    encabezados = [
        "División", "Solicitante", "Jefe Comisión", "Municipio", 
        "Parroquia", "Fecha", "Hora", "Dirección", 
        "Tipo de Procedimiento", "Detalles", "Persona Presente", "Descripcion"
    ]
    hoja.append(encabezados)

    division = 2
    # Obtener datos de los procedimientos
    procedimientos = Procedimientos.objects.filter(id_division=division)

    # Agregar datos a la hoja
    for procedimiento in procedimientos:
        # Obtener solicitante y jefe de comisión
        solicitante = (f"{procedimiento.id_solicitante.jerarquia} {procedimiento.id_solicitante.nombres} "
                       f"{procedimiento.id_solicitante.apellidos}") if procedimiento.id_solicitante else procedimiento.solicitante_externo
        jefe_comision = (f"{procedimiento.id_jefe_comision.jerarquia} {procedimiento.id_jefe_comision.nombres} "
                         f"{procedimiento.id_jefe_comision.apellidos}") if procedimiento.id_jefe_comision else ""

        personas_presentes, detalles_procedimientos = [], []

        # Agregar detalles de las distintas relaciones
        relaciones = [
            (procedimiento.abastecimiento_agua_set.all(), 'id_tipo_servicio.nombre_institucion'),
            (procedimiento.apoyo_unidades_set.all(), 'id_tipo_apoyo.tipo_apoyo'),
            (procedimiento.guardia_prevencion_set.all(), 'id_motivo_prevencion.motivo'),
            (procedimiento.atendido_no_efectuado_set.all(), None),
            (procedimiento.despliegue_seguridad_set.all(), 'motivo_despliegue.motivo'),
            (procedimiento.fallecidos_set.all(), 'motivo_fallecimiento'),
            (procedimiento.falsa_alarma_set.all(), 'motivo_alarma.motivo'),
            (procedimiento.servicios_especiales_set.all(), 'tipo_servicio.serv_especiales'),
            (procedimiento.rescate_set.all(), 'tipo_rescate.tipo_rescate'),
            (procedimiento.incendios_set.all(), 'id_tipo_incendio.tipo_incendio'),
            (procedimiento.atenciones_paramedicas_set.all(), 'tipo_atencion'),
            (procedimiento.traslado_prehospitalaria_set.all(), 'id_tipo_traslado.tipo_traslado'),
            (procedimiento.evaluacion_riesgo_set.all(), 'id_tipo_riesgo.tipo_riesgo'),
            (procedimiento.mitigacion_riesgos_set.all(), 'id_tipo_servicio.tipo_servicio'),
            (procedimiento.puesto_avanzada_set.all(), 'id_tipo_servicio.tipo_servicio'),
            (procedimiento.asesoramiento_set.all(), 'nombre_comercio'),
            (procedimiento.reinspeccion_prevencion_set.all(), 'nombre_comercio'),
            (procedimiento.retencion_preventiva_set.all(), 'tipo_cilindro'),
            (procedimiento.artificios_pirotecnicos_set.all(), 'tipo_procedimiento.tipo'),
            (procedimiento.inspeccion_establecimiento_art_set.all(), 'nombre_comercio'),
            (procedimiento.valoracion_medica_set.all(), None),
            (procedimiento.detalles_enfermeria_set.all(), None),
            (procedimiento.procedimientos_psicologia_set.all(), None),
            (procedimiento.procedimientos_capacitacion_set.all(), None),
            (procedimiento.procedimientos_brigada_set.all(), None),
            (procedimiento.procedimientos_frente_preventivo_set.all(), None),
            (procedimiento.jornada_medica_set.all(), None),
            (procedimiento.inspeccion_prevencion_asesorias_tecnicas_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_habitabilidad_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_otros_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_arbol_set.all(), 'tipo_inspeccion'),
            (procedimiento.investigacion_set.all(), 'id_tipo_investigacion.tipo_investigacion')
        ]
        
        # Procesar cada conjunto de datos
        for relacion, campo_descripcion in relaciones:
            personas_relacionadas, detalles_relacionados = obtener_personas_y_detalles(relacion, campo_descripcion)
            personas_presentes.extend(personas_relacionadas)
            detalles_procedimientos.extend(detalles_relacionados)

        # Convertir listas a cadenas separadas por ' -- '
        personas_presentes_str = " -- ".join(personas_presentes)
        detalles_str = " -- ".join(detalles_procedimientos)
        descripcion_str = " -- ".join(detalles_procedimientos)

        # Agregar la fila de datos
        hoja.append([
            procedimiento.id_division.division,
            solicitante,
            jefe_comision,
            procedimiento.id_municipio.municipio,
            procedimiento.id_parroquia.parroquia,
            procedimiento.fecha,
            procedimiento.hora,
            procedimiento.direccion,
            procedimiento.id_tipo_procedimiento.tipo_procedimiento,
            detalles_str,
            personas_presentes_str,
            descripcion_str,
        ])

    # Ajustar el ancho de las columnas
    for column in hoja.columns:
        max_length = max(len(str(cell.value)) for cell in column if cell.value) + 2
        hoja.column_dimensions[get_column_letter(column[0].column)].width = max_length

    # Configurar la respuesta HTTP para descargar el archivo
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=Operaciones.xlsx"
    workbook.save(response)
    return response

def generar_excel_prevencion(request):
    # Crear un libro de trabajo y una hoja
    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = "Prevencion"

    # Agregar encabezados a la primera fila
    encabezados = [
        "División", "Solicitante", "Jefe Comisión", "Municipio", 
        "Parroquia", "Fecha", "Hora", "Dirección", 
        "Tipo de Procedimiento", "Detalles", "Persona Presente", "Descripcion"
    ]
    hoja.append(encabezados)

    division = 3
    # Obtener datos de los procedimientos
    procedimientos = Procedimientos.objects.filter(id_division=division)

    def obtener_personas_y_detalles(set_relacionado, campo_descripcion=None):
        """Función auxiliar para obtener personas presentes y detalles de procedimientos"""
        personas = []
        detalles = []
        for item in set_relacionado:
            # Persona
            if hasattr(item, 'nombre') and hasattr(item, 'apellidos') and hasattr(item, 'cedula'):
                personas.append(f"{item.nombre} {item.apellidos} {item.cedula}")
            elif hasattr(item, 'persona_sitio_nombre') and hasattr(item, 'persona_sitio_apellido') and hasattr(item, 'persona_sitio_cedula'):
                # Para InspeccionPrevencionAsesoriasTecnicas
                personas.append(f"{item.persona_sitio_nombre} {item.persona_sitio_apellido} {item.persona_sitio_cedula}")
            # Detalle
            detalles.append(getattr(item, campo_descripcion, '') if campo_descripcion else str(item))
        return personas, detalles

    # Agregar datos a la hoja
    for procedimiento in procedimientos:
        # Obtener solicitante y jefe de comisión
        solicitante = (f"{procedimiento.id_solicitante.jerarquia} {procedimiento.id_solicitante.nombres} "
                       f"{procedimiento.id_solicitante.apellidos}") if procedimiento.id_solicitante else procedimiento.solicitante_externo
        jefe_comision = (f"{procedimiento.id_jefe_comision.jerarquia} {procedimiento.id_jefe_comision.nombres} "
                         f"{procedimiento.id_jefe_comision.apellidos}") if procedimiento.id_jefe_comision else ""

        personas_presentes, detalles_procedimientos = [], []

        # Agregar detalles de las distintas relaciones
        relaciones = [
            (procedimiento.abastecimiento_agua_set.all(), 'id_tipo_servicio.nombre_institucion'),
            (procedimiento.apoyo_unidades_set.all(), 'id_tipo_apoyo.tipo_apoyo'),
            (procedimiento.guardia_prevencion_set.all(), 'id_motivo_prevencion.motivo'),  # Usar 'motivo'
            (procedimiento.atendido_no_efectuado_set.all(), None),
            (procedimiento.despliegue_seguridad_set.all(), 'motivo_despliegue.motivo'),
            (procedimiento.fallecidos_set.all(), 'motivo_fallecimiento'),
            (procedimiento.falsa_alarma_set.all(), 'motivo_alarma.motivo'),
            (procedimiento.servicios_especiales_set.all(), 'tipo_servicio.serv_especiales'),
            (procedimiento.rescate_set.all(), 'tipo_rescate.tipo_rescate'),
            (procedimiento.incendios_set.all(), 'id_tipo_incendio.tipo_incendio'),
            (procedimiento.atenciones_paramedicas_set.all(), 'tipo_atencion'),
            (procedimiento.traslado_prehospitalaria_set.all(), 'id_tipo_traslado.tipo_traslado'),
            (procedimiento.evaluacion_riesgo_set.all(), 'id_tipo_riesgo.tipo_riesgo'),
            (procedimiento.mitigacion_riesgos_set.all(), 'id_tipo_servicio.tipo_servicio'),
            (procedimiento.puesto_avanzada_set.all(), 'id_tipo_servicio.tipo_servicio'),
            (procedimiento.asesoramiento_set.all(), 'nombre_comercio'),
            (procedimiento.reinspeccion_prevencion_set.all(), 'nombre_comercio'),
            (procedimiento.retencion_preventiva_set.all(), 'tipo_cilindro'),
            (procedimiento.artificios_pirotecnicos_set.all(), 'tipo_procedimiento.tipo'),
            (procedimiento.inspeccion_establecimiento_art_set.all(), 'nombre_comercio'),
            (procedimiento.valoracion_medica_set.all(), None),
            (procedimiento.detalles_enfermeria_set.all(), None),
            (procedimiento.procedimientos_psicologia_set.all(), None),
            (procedimiento.procedimientos_capacitacion_set.all(), None),
            (procedimiento.procedimientos_brigada_set.all(), None),
            (procedimiento.procedimientos_frente_preventivo_set.all(), None),
            (procedimiento.jornada_medica_set.all(), None),
            (procedimiento.inspeccion_prevencion_asesorias_tecnicas_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_habitabilidad_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_otros_set.all(), 'tipo_inspeccion'),
            (procedimiento.inspeccion_arbol_set.all(), 'tipo_inspeccion'),
            (procedimiento.investigacion_set.all(), 'id_tipo_investigacion.tipo_investigacion')
        ]
        
        # Procesar cada conjunto de datos
        for relacion, campo_descripcion in relaciones:
            personas_relacionadas, detalles_relacionados = obtener_personas_y_detalles(relacion, campo_descripcion)
            personas_presentes.extend(personas_relacionadas)
            detalles_procedimientos.extend(detalles_relacionados)

        # Convertir listas a cadenas separadas por ' -- '
        personas_presentes_str = " -- ".join(personas_presentes)
        detalles_str = " -- ".join(detalles_procedimientos)
        descripcion_str = " -- ".join(detalles_procedimientos)

        # Agregar la fila de datos
        hoja.append([
            procedimiento.id_division.division,
            solicitante,
            jefe_comision,
            procedimiento.id_municipio.municipio,
            procedimiento.id_parroquia.parroquia,
            procedimiento.fecha,
            procedimiento.hora,
            procedimiento.direccion,
            procedimiento.id_tipo_procedimiento.tipo_procedimiento,
            detalles_str,
            personas_presentes_str,
            descripcion_str,
        ])

    # Ajustar el ancho de las columnas
    for column in hoja.columns:
        max_length = max(len(str(cell.value)) for cell in column if cell.value) + 2
        hoja.column_dimensions[get_column_letter(column[0].column)].width = max_length

    # Configurar la respuesta HTTP para descargar el archivo
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response["Content-Disposition"] = "attachment; filename=Prevencion.xlsx"
    workbook.save(response)
    return response

