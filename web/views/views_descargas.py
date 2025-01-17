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
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import JsonResponse
from django.db.models import Prefetch

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

def generar_excel_operaciones(request):
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

    division = 2
    # Obtener datos de los procedimientos con select_related y prefetch_related
    procedimientos = Procedimientos.objects.filter(id_division=division).select_related(
        'id_solicitante', 'id_jefe_comision', 'id_municipio', 'id_parroquia', 'id_tipo_procedimiento'
    ).prefetch_related(
        'abastecimiento_agua_set', 'apoyo_unidades_set', 'guardia_prevencion_set', 'atendido_no_efectuado_set',
        'despliegue_seguridad_set', 'fallecidos_set', 'falsa_alarma_set', 'servicios_especiales_set', 'rescate_set',
        'incendios_set', 'atenciones_paramedicas_set', 'traslado_prehospitalaria_set', 'evaluacion_riesgo_set',
        'mitigacion_riesgos_set', 'puesto_avanzada_set', 'asesoramiento_set', 'reinspeccion_prevencion_set',
        'retencion_preventiva_set', 'artificios_pirotecnicos_set', 'inspeccion_establecimiento_art_set',
        'valoracion_medica_set', 'detalles_enfermeria_set', 'procedimientos_psicologia_set',
        'procedimientos_capacitacion_set', 'procedimientos_brigada_set', 'procedimientos_frente_preventivo_set',
        'jornada_medica_set', 'inspeccion_prevencion_asesorias_tecnicas_set', 'inspeccion_habitabilidad_set',
        'inspeccion_otros_set', 'inspeccion_arbol_set', 'investigacion_set'
    )

    datos = []

    # Agregar datos a la lista
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

        # Agregar los datos al diccionario
        datos.append({
            "division": procedimiento.id_division.division,
            "solicitante": solicitante,
            "jefe_comision": jefe_comision,
            "municipio": procedimiento.id_municipio.municipio,
            "parroquia": procedimiento.id_parroquia.parroquia,
            "fecha": procedimiento.fecha,
            "hora": procedimiento.hora,
            "direccion": procedimiento.direccion,
            "tipo_procedimiento": procedimiento.id_tipo_procedimiento.tipo_procedimiento,
            "detalles": detalles_str,
            "personas_presentes": personas_presentes_str,
            "descripcion": descripcion_str,
        })

    return JsonResponse(datos, safe=False)

def generar_excel_enfermeria(request):
    division = 6

    # Optimización de consultas con select_related y prefetch_related
    procedimientos = (
        Procedimientos.objects.filter(id_division=division)
        .select_related(
            "id_division",
            "id_solicitante",
            "id_jefe_comision",
            "id_municipio",
            "id_parroquia",
            "id_tipo_procedimiento",
        )
        .prefetch_related(
            "abastecimiento_agua_set__id_tipo_servicio",
            "apoyo_unidades_set__id_tipo_apoyo",
            "guardia_prevencion_set__id_motivo_prevencion",
            "despliegue_seguridad_set__motivo_despliegue",
            "fallecidos_set",
            "falsa_alarma_set__motivo_alarma",
            "servicios_especiales_set__tipo_servicio",
            "rescate_set__tipo_rescate",
            "incendios_set__id_tipo_incendio",
            "atenciones_paramedicas_set",
            "traslado_prehospitalaria_set__id_tipo_traslado",
            "evaluacion_riesgo_set__id_tipo_riesgo",
            "mitigacion_riesgos_set__id_tipo_servicio",
            "puesto_avanzada_set__id_tipo_servicio",
            "asesoramiento_set",
            "reinspeccion_prevencion_set",
            "retencion_preventiva_set",
            "artificios_pirotecnicos_set__tipo_procedimiento",
            "inspeccion_establecimiento_art_set",
            "detalles_enfermeria_set",
            "investigacion_set__id_tipo_investigacion",
        )
    )

    def obtener_personas_y_detalles(set_relacionado, campo_descripcion=None):
        """Función auxiliar para obtener personas presentes y detalles de procedimientos"""
        personas = []
        detalles = []
        for item in set_relacionado:
            if hasattr(item, "cedula"):
                if hasattr(item, "nombre") and hasattr(item, "apellido") and hasattr(item, "cedula"):
                    personas.append(f"{item.nombre} {item.apellido} {item.cedula}")
            detalles.append(getattr(item, campo_descripcion, "") if campo_descripcion else str(item))
        return personas, detalles

    datos = []

    for procedimiento in procedimientos:
        solicitante = (
            f"{procedimiento.id_solicitante.jerarquia} {procedimiento.id_solicitante.nombres} {procedimiento.id_solicitante.apellidos}"
            if procedimiento.id_solicitante
            else procedimiento.solicitante_externo
        )
        jefe_comision = (
            f"{procedimiento.id_jefe_comision.jerarquia} {procedimiento.id_jefe_comision.nombres} {procedimiento.id_jefe_comision.apellidos}"
            if procedimiento.id_jefe_comision
            else ""
        )

        personas_presentes, detalles_procedimientos = [], []

        relaciones = [
            (procedimiento.abastecimiento_agua_set.all(), "id_tipo_servicio.nombre_institucion"),
            (procedimiento.apoyo_unidades_set.all(), "id_tipo_apoyo.tipo_apoyo"),
            (procedimiento.guardia_prevencion_set.all(), "id_motivo_prevencion.motivo"),
            (procedimiento.despliegue_seguridad_set.all(), "motivo_despliegue.motivo"),
            (procedimiento.falsa_alarma_set.all(), "motivo_alarma.motivo"),
            (procedimiento.rescate_set.all(), "tipo_rescate.tipo_rescate"),
            (procedimiento.incendios_set.all(), "id_tipo_incendio.tipo_incendio"),
            (procedimiento.traslado_prehospitalaria_set.all(), "id_tipo_traslado.tipo_traslado"),
            (procedimiento.evaluacion_riesgo_set.all(), "id_tipo_riesgo.tipo_riesgo"),
            (procedimiento.artificios_pirotecnicos_set.all(), "tipo_procedimiento.tipo"),
            (procedimiento.inspeccion_establecimiento_art_set.all(), "nombre_comercio"),
            (procedimiento.detalles_enfermeria_set.all(), None),
        ]

        for relacion, campo_descripcion in relaciones:
            personas_relacionadas, detalles_relacionados = obtener_personas_y_detalles(relacion, campo_descripcion)
            personas_presentes.extend(personas_relacionadas)
            detalles_procedimientos.extend(detalles_relacionados)

        datos.append(
            {
                "division": procedimiento.id_division.division,
                "solicitante": solicitante,
                "jefe_comision": jefe_comision,
                "municipio": procedimiento.id_municipio.municipio,
                "parroquia": procedimiento.id_parroquia.parroquia,
                "fecha": procedimiento.fecha,
                "hora": procedimiento.hora,
                "direccion": procedimiento.direccion,
                "tipo_procedimiento": procedimiento.id_tipo_procedimiento.tipo_procedimiento,
                "detalles": " -- ".join(detalles_procedimientos),
                "personas_presentes": " -- ".join(personas_presentes),
            }
        )

    return JsonResponse(datos, safe=False)

def generar_excel_rescate(request):
    # Optimizar consultas con select_related y prefetch_related
    procedimientos = Procedimientos.objects.filter(id_division=1).select_related(
        "id_division", "id_solicitante", "id_jefe_comision", "id_municipio", 
        "id_parroquia", "id_tipo_procedimiento"
    ).prefetch_related(
        Prefetch("rescate_set", to_attr="rescate_data"),
        Prefetch("abastecimiento_agua_set", to_attr="agua_data"),
        Prefetch("apoyo_unidades_set", to_attr="apoyo_data"),
        # Agrega más relaciones aquí según sea necesario
    )

    # Crear una lista para los datos
    datos = []

    # Función auxiliar para extraer detalles
    def obtener_detalles_y_personas(set_relacionado, campo_descripcion=None):
        personas = []
        detalles = []
        for item in set_relacionado:
            if hasattr(item, "nombres") and hasattr(item, "apellidos"):
                personas.append(f"{item.nombres} {item.apellidos}")
            if hasattr(item, campo_descripcion):
                detalles.append(getattr(item, campo_descripcion, ""))
        return personas, detalles

    # Procesar los procedimientos
    for procedimiento in procedimientos:
        # Solicitante y jefe de comisión
        solicitante = (
            f"{procedimiento.id_solicitante.jerarquia} {procedimiento.id_solicitante.nombres} {procedimiento.id_solicitante.apellidos}"
            if procedimiento.id_solicitante else procedimiento.solicitante_externo or "N/A"
        )
        jefe_comision = (
            f"{procedimiento.id_jefe_comision.jerarquia} {procedimiento.id_jefe_comision.nombres} {procedimiento.id_jefe_comision.apellidos}"
            if procedimiento.id_jefe_comision else "N/A"
        )

        # Detalles y personas
        personas_presentes = []
        detalles = []

        # Procesar rescate
        for rescate in procedimiento.rescate_data:
            detalles.append(rescate.tipo_rescate.tipo_rescate)
        
        # Otros conjuntos relacionados (agregar más si aplica)
        for agua in procedimiento.agua_data:
            detalles.append(agua.id_tipo_servicio.nombre_institucion)

        # Combinar datos
        detalles_str = " -- ".join(detalles) or "N/A"
        personas_str = " -- ".join(personas_presentes) or "N/A"

        # Agregar datos al JSON
        datos.append({
            "division": procedimiento.id_division.division or "N/A",
            "solicitante": solicitante,
            "jefe_comision": jefe_comision,
            "municipio": procedimiento.id_municipio.municipio or "N/A",
            "parroquia": procedimiento.id_parroquia.parroquia or "N/A",
            "fecha": procedimiento.fecha or "N/A",
            "hora": procedimiento.hora or "N/A",
            "direccion": procedimiento.direccion or "N/A",
            "tipo_procedimiento": procedimiento.id_tipo_procedimiento.tipo_procedimiento or "N/A",
            "detalles": detalles_str,
            "personas_presentes": personas_str,
            "descripcion": detalles_str,
        })

    # Devolver los datos como JSON
    return JsonResponse(datos, safe=False)

def generar_excel_prevencion(request):
    division = 3
    # Obtén los procedimientos filtrados por división, utilizando select_related para optimizar las relaciones de uno a uno y prefetch_related para las relaciones de uno a muchos
    procedimientos = Procedimientos.objects.filter(id_division=division).select_related(
        "id_solicitante", "id_jefe_comision", "id_municipio", "id_parroquia", "id_tipo_procedimiento"
    ).prefetch_related("retencion_preventiva_set")

    datos = []
    for procedimiento in procedimientos:
        solicitante = (f"{procedimiento.id_solicitante.jerarquia} {procedimiento.id_solicitante.nombres} "
                       f"{procedimiento.id_solicitante.apellidos}") if procedimiento.id_solicitante else procedimiento.solicitante_externo
        jefe_comision = (f"{procedimiento.id_jefe_comision.jerarquia} {procedimiento.id_jefe_comision.nombres} "
                         f"{procedimiento.id_jefe_comision.apellidos}") if procedimiento.id_jefe_comision else ""

        detalles = []
        personas_presentes = []
        for retencion in procedimiento.retencion_preventiva_set.all():  # Iterar sobre todas las retenciones preventivas
            detalles.append(retencion.tipo_cilindro)
            personas_presentes.append(f"{retencion.nombre} {retencion.apellidos} ({retencion.cedula})")

        # Accede a la descripción de la retención preventiva (si existe, si no, asigna "N/A")
        retenciones = list(procedimiento.retencion_preventiva_set.all())
        descripcion = "N/A"
        if retenciones:
            descripcion = retenciones[0].descripcion

        datos.append({
            "division": procedimiento.id_division.division,
            "solicitante": solicitante,
            "jefe_comision": jefe_comision,
            "municipio": procedimiento.id_municipio.municipio,
            "parroquia": procedimiento.id_parroquia.parroquia,
            "fecha": procedimiento.fecha,
            "hora": procedimiento.hora,
            "direccion": procedimiento.direccion,
            "tipo_procedimiento": procedimiento.id_tipo_procedimiento.tipo_procedimiento,
            "detalles": " -- ".join(detalles),
            "personas_presentes": " -- ".join(personas_presentes),
            "descripcion": descripcion,
        })

    return JsonResponse(datos, safe=False, encoder=DjangoJSONEncoder)

def generar_excel_prehospitalaria(request):
    # Crear una lista para almacenar los datos
    datos = []

    division = 5

    # Consulta optimizada usando select_related y prefetch_related
    procedimientos = Procedimientos.objects.filter(id_division=division).select_related(
        'id_division', 'id_solicitante', 'id_jefe_comision', 'id_municipio', 'id_parroquia', 'id_tipo_procedimiento'
    ).prefetch_related(
        'abastecimiento_agua_set__id_tipo_servicio',
        'apoyo_unidades_set__id_tipo_apoyo',
        'guardia_prevencion_set__id_motivo_prevencion',
        'atendido_no_efectuado_set',
        'despliegue_seguridad_set__motivo_despliegue',
        'fallecidos_set',
        'falsa_alarma_set__motivo_alarma',
        'servicios_especiales_set__tipo_servicio',
        'rescate_set__tipo_rescate',
        'incendios_set__id_tipo_incendio',
        'atenciones_paramedicas_set',
        'traslado_prehospitalaria_set__id_tipo_traslado',
        'evaluacion_riesgo_set__id_tipo_riesgo',
        'mitigacion_riesgos_set__id_tipo_servicio',
        'puesto_avanzada_set__id_tipo_servicio',
        'asesoramiento_set',
        'reinspeccion_prevencion_set',
        'retencion_preventiva_set',
        'artificios_pirotecnicos_set__tipo_procedimiento',
        'inspeccion_establecimiento_art_set',
        'valoracion_medica_set',
        'detalles_enfermeria_set',
        'procedimientos_psicologia_set',
        'procedimientos_capacitacion_set',
        'procedimientos_brigada_set',
        'procedimientos_frente_preventivo_set',
        'jornada_medica_set',
        'inspeccion_prevencion_asesorias_tecnicas_set',
        'inspeccion_habitabilidad_set',
        'inspeccion_otros_set',
        'inspeccion_arbol_set',
        'investigacion_set__id_tipo_investigacion',
    )

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

    # Agregar datos a la lista
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

        # Agregar los datos al diccionario
        datos.append({
            "division": procedimiento.id_division.division,
            "solicitante": solicitante,
            "jefe_comision": jefe_comision,
            "municipio": procedimiento.id_municipio.municipio,
            "parroquia": procedimiento.id_parroquia.parroquia,
            "fecha": procedimiento.fecha,
            "hora": procedimiento.hora,
            "direccion": procedimiento.direccion,
            "tipo_procedimiento": procedimiento.id_tipo_procedimiento.tipo_procedimiento,
            "detalles": detalles_str,
            "personas_presentes": personas_presentes_str,
            "descripcion": descripcion_str,
        })

    # Configurar la respuesta HTTP para enviar el archivo JSON
    return JsonResponse(datos, safe=False)

def generar_excel_serviciosmedicos(request):

    division_id = 7  # División correspondiente a "Servicios Médicos"

    # Optimización de consultas usando `select_related` y `prefetch_related`
    procedimientos = Procedimientos.objects.filter(id_division=division_id).select_related(
        "id_division", "id_solicitante", "id_jefe_comision", "id_municipio", 
        "id_parroquia", "id_tipo_procedimiento"
    ).prefetch_related(
        Prefetch("abastecimiento_agua_set", to_attr="abastecimiento_agua_temp"),
        Prefetch("apoyo_unidades_set", to_attr="apoyo_unidades_temp"),
        Prefetch("guardia_prevencion_set", to_attr="guardia_prevencion_temp"),
        Prefetch("atendido_no_efectuado_set", to_attr="atendido_no_efectuado_temp"),
        Prefetch("despliegue_seguridad_set", to_attr="despliegue_seguridad_temp"),
        Prefetch("fallecidos_set", to_attr="fallecidos_temp"),
        Prefetch("falsa_alarma_set", to_attr="falsa_alarma_temp"),
        Prefetch("servicios_especiales_set", to_attr="servicios_especiales_temp"),
        Prefetch("rescate_set", to_attr="rescate_temp"),
        Prefetch("incendios_set", to_attr="incendios_temp"),
        Prefetch("atenciones_paramedicas_set", to_attr="atenciones_paramedicas_temp"),
        Prefetch("traslado_prehospitalaria_set", to_attr="traslado_prehospitalaria_temp"),
        Prefetch("evaluacion_riesgo_set", to_attr="evaluacion_riesgo_temp"),
        Prefetch("mitigacion_riesgos_set", to_attr="mitigacion_riesgos_temp"),
        Prefetch("puesto_avanzada_set", to_attr="puesto_avanzada_temp"),
        Prefetch("asesoramiento_set", to_attr="asesoramiento_temp"),
        Prefetch("reinspeccion_prevencion_set", to_attr="reinspeccion_prevencion_temp"),
        Prefetch("retencion_preventiva_set", to_attr="retencion_preventiva_temp"),
        Prefetch("artificios_pirotecnicos_set", to_attr="artificios_pirotecnicos_temp"),
        Prefetch("inspeccion_establecimiento_art_set", to_attr="inspeccion_establecimiento_art_temp"),
        Prefetch("valoracion_medica_set", to_attr="valoracion_medica_temp"),
        Prefetch("detalles_enfermeria_set", to_attr="detalles_enfermeria_temp"),
        Prefetch("procedimientos_psicologia_set", to_attr="procedimientos_psicologia_temp"),
        Prefetch("procedimientos_capacitacion_set", to_attr="procedimientos_capacitacion_temp"),
        Prefetch("procedimientos_brigada_set", to_attr="procedimientos_brigada_temp"),
        Prefetch("procedimientos_frente_preventivo_set", to_attr="procedimientos_frente_preventivo_temp"),
        Prefetch("jornada_medica_set", to_attr="jornada_medica_temp"),
        Prefetch("inspeccion_prevencion_asesorias_tecnicas_set", to_attr="inspeccion_prevencion_asesorias_tecnicas_temp"),
        Prefetch("inspeccion_habitabilidad_set", to_attr="inspeccion_habitabilidad_temp"),
        Prefetch("inspeccion_otros_set", to_attr="inspeccion_otros_temp"),
        Prefetch("inspeccion_arbol_set", to_attr="inspeccion_arbol_temp"),
        Prefetch("investigacion_set", to_attr="investigacion_temp"),
    )

    def obtener_personas_y_detalles(set_relacionado, campo_descripcion=None):
        """Función auxiliar para obtener personas presentes y detalles de procedimientos"""
        personas = []
        detalles = []
        for item in set_relacionado:
            # Persona
            if hasattr(item, 'cedula'):
                if hasattr(item, 'nombres') and hasattr(item, 'apellidos'):
                    personas.append(f"{item.nombres} {item.apellidos} {item.cedula}")
                elif hasattr(item, 'nombre') and hasattr(item, 'apellido'):
                    personas.append(f"{item.nombre} {item.apellido} {item.cedula}")
                else:
                    personas.append(f"{item.cedula}")
            # Detalle
            detalles.append(getattr(item, campo_descripcion, '') if campo_descripcion else str(item))
        return personas, detalles

    # Crear una lista para almacenar los datos
    datos = []

    for procedimiento in procedimientos:
        # Obtener solicitante y jefe de comisión
        solicitante = (f"{procedimiento.id_solicitante.jerarquia} {procedimiento.id_solicitante.nombres} "
                       f"{procedimiento.id_solicitante.apellidos}") if procedimiento.id_solicitante else procedimiento.solicitante_externo
        jefe_comision = (f"{procedimiento.id_jefe_comision.jerarquia} {procedimiento.id_jefe_comision.nombres} "
                         f"{procedimiento.id_jefe_comision.apellidos}") if procedimiento.id_jefe_comision else ""

        personas_presentes, detalles_procedimientos = [], []

        # Procesar las relaciones
        relaciones = [
            (procedimiento.abastecimiento_agua_temp, 'id_tipo_servicio.nombre_institucion'),
            (procedimiento.apoyo_unidades_temp, 'id_tipo_apoyo.tipo_apoyo'),
            (procedimiento.guardia_prevencion_temp, 'id_motivo_prevencion.motivo'),
            (procedimiento.atendido_no_efectuado_temp, None),
            (procedimiento.despliegue_seguridad_temp, 'motivo_despliegue.motivo'),
            (procedimiento.fallecidos_temp, 'motivo_fallecimiento'),
            (procedimiento.falsa_alarma_temp, 'motivo_alarma.motivo'),
            (procedimiento.servicios_especiales_temp, 'tipo_servicio.serv_especiales'),
            (procedimiento.rescate_temp, 'tipo_rescate.tipo_rescate'),
            (procedimiento.incendios_temp, 'id_tipo_incendio.tipo_incendio'),
            (procedimiento.atenciones_paramedicas_temp, 'tipo_atencion'),
            (procedimiento.traslado_prehospitalaria_temp, 'id_tipo_traslado.tipo_traslado'),
            (procedimiento.evaluacion_riesgo_temp, 'id_tipo_riesgo.tipo_riesgo'),
            (procedimiento.mitigacion_riesgos_temp, 'id_tipo_servicio.tipo_servicio'),
            (procedimiento.puesto_avanzada_temp, 'id_tipo_servicio.tipo_servicio'),
            (procedimiento.asesoramiento_temp, 'nombre_comercio'),
            (procedimiento.reinspeccion_prevencion_temp, 'nombre_comercio'),
            (procedimiento.retencion_preventiva_temp, 'tipo_cilindro'),
            (procedimiento.artificios_pirotecnicos_temp, 'tipo_procedimiento.tipo'),
            (procedimiento.inspeccion_establecimiento_art_temp, 'nombre_comercio'),
            (procedimiento.valoracion_medica_temp, None),
            (procedimiento.detalles_enfermeria_temp, None),
            (procedimiento.procedimientos_psicologia_temp, None),
            (procedimiento.procedimientos_capacitacion_temp, None),
            (procedimiento.procedimientos_brigada_temp, None),
            (procedimiento.procedimientos_frente_preventivo_temp, None),
            (procedimiento.jornada_medica_temp, None),
            (procedimiento.inspeccion_prevencion_asesorias_tecnicas_temp, 'tipo_inspeccion'),
            (procedimiento.inspeccion_habitabilidad_temp, 'tipo_inspeccion'),
            (procedimiento.inspeccion_otros_temp, 'tipo_inspeccion'),
            (procedimiento.inspeccion_arbol_temp, 'tipo_inspeccion'),
            (procedimiento.investigacion_temp, 'id_tipo_investigacion.tipo_investigacion')
        ]

        for relacion, campo_descripcion in relaciones:
            personas_relacionadas, detalles_relacionados = obtener_personas_y_detalles(relacion, campo_descripcion)
            personas_presentes.extend(personas_relacionadas)
            detalles_procedimientos.extend(detalles_relacionados)

        # Agregar datos a la lista
        datos.append({
            "division": procedimiento.id_division.division,
            "solicitante": solicitante,
            "jefe_comision": jefe_comision,
            "municipio": procedimiento.id_municipio.municipio,
            "parroquia": procedimiento.id_parroquia.parroquia,
            "fecha": procedimiento.fecha,
            "hora": procedimiento.hora,
            "direccion": procedimiento.direccion,
            "tipo_procedimiento": procedimiento.id_tipo_procedimiento.tipo_procedimiento,
            "detalles": " -- ".join(detalles_procedimientos),
            "personas_presentes": " -- ".join(personas_presentes),
            "descripcion": " -- ".join(detalles_procedimientos),
        })

    # Devolver los datos como JSON
    return JsonResponse(datos, safe=False)

def generar_excel_psicologia(request):
    division = 8

    # Utilizar select_related para relaciones de uno a uno y prefetch_related para relaciones de muchos a muchos
    procedimientos = Procedimientos.objects.filter(id_division=division).select_related(
        'id_division', 'id_solicitante', 'id_jefe_comision', 'id_municipio', 'id_parroquia', 'id_tipo_procedimiento'
    ).prefetch_related(
        Prefetch('abastecimiento_agua_set'),
        Prefetch('apoyo_unidades_set'),
        # Eliminar 'guardi_prevencion_set' que da problemas
        Prefetch('atendido_no_efectuado_set'),
        Prefetch('despliegue_seguridad_set'),
        Prefetch('fallecidos_set'),
        Prefetch('falsa_alarma_set'),
        Prefetch('servicios_especiales_set'),
        Prefetch('rescate_set'),
        Prefetch('incendios_set'),
        Prefetch('atenciones_paramedicas_set'),
        Prefetch('traslado_prehospitalaria_set'),
        Prefetch('evaluacion_riesgo_set'),
        Prefetch('mitigacion_riesgos_set'),
        Prefetch('puesto_avanzada_set'),
        Prefetch('asesoramiento_set'),
        Prefetch('reinspeccion_prevencion_set'),
        Prefetch('retencion_preventiva_set'),
        Prefetch('artificios_pirotecnicos_set'),
        Prefetch('inspeccion_establecimiento_art_set'),
        Prefetch('valoracion_medica_set'),
        Prefetch('detalles_enfermeria_set'),
        Prefetch('procedimientos_psicologia_set'),
        Prefetch('procedimientos_capacitacion_set'),
        Prefetch('procedimientos_brigada_set'),
        Prefetch('procedimientos_frente_preventivo_set'),
        Prefetch('jornada_medica_set'),
        Prefetch('inspeccion_prevencion_asesorias_tecnicas_set'),
        Prefetch('inspeccion_habitabilidad_set'),
        Prefetch('inspeccion_otros_set'),
        Prefetch('inspeccion_arbol_set'),
        Prefetch('investigacion_set')
    )

    def obtener_personas_y_detalles(set_relacionado, campo_descripcion=None):
        """Función auxiliar para obtener personas presentes y detalles de procedimientos"""
        personas = []
        detalles = []
        for item in set_relacionado:
            if hasattr(item, 'cedula'):
                personas.append(f"{item.nombre} {item.apellido} {item.cedula}")
            detalles.append(getattr(item, campo_descripcion, '') if campo_descripcion else str(item))
        return personas, detalles

    # Preparar lista de datos a enviar
    datos = []

    for procedimiento in procedimientos:
        # Obtener solicitante y jefe de comisión
        solicitante = (f"{procedimiento.id_solicitante.jerarquia} {procedimiento.id_solicitante.nombres} "
                       f"{procedimiento.id_solicitante.apellidos}") if procedimiento.id_solicitante else procedimiento.solicitante_externo
        jefe_comision = (f"{procedimiento.id_jefe_comision.jerarquia} {procedimiento.id_jefe_comision.nombres} "
                         f"{procedimiento.id_jefe_comision.apellidos}") if procedimiento.id_jefe_comision else ""

        personas_presentes, detalles_procedimientos = [], []

        # Procesar cada conjunto de datos
        relaciones = [
            (procedimiento.abastecimiento_agua_set.all(), 'id_tipo_servicio.nombre_institucion'),
            (procedimiento.apoyo_unidades_set.all(), 'id_tipo_apoyo.tipo_apoyo'),
            # Eliminar 'guardi_prevencion_set' de las relaciones
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

        # Procesar cada relación
        for relacion, campo_descripcion in relaciones:
            personas_relacionadas, detalles_relacionados = obtener_personas_y_detalles(relacion, campo_descripcion)
            personas_presentes.extend(personas_relacionadas)
            detalles_procedimientos.extend(detalles_relacionados)

        # Convertir listas a cadenas separadas por ' -- '
        personas_presentes_str = " -- ".join(personas_presentes)
        detalles_str = " -- ".join(detalles_procedimientos)
        descripcion_str = " -- ".join(detalles_procedimientos)

        # Agregar datos al arreglo
        datos.append({
            'division': procedimiento.id_division.division,
            'solicitante': solicitante,
            'jefe_comision': jefe_comision,
            'municipio': procedimiento.id_municipio.municipio,
            'parroquia': procedimiento.id_parroquia.parroquia,
            'fecha': procedimiento.fecha,
            'hora': procedimiento.hora,
            'direccion': procedimiento.direccion,
            'tipo_procedimiento': procedimiento.id_tipo_procedimiento.tipo_procedimiento,
            'detalles': detalles_str,
            'personas_presentes': personas_presentes_str,
            'descripcion': descripcion_str
        })

    return JsonResponse({'data': datos})

def generar_excel_grumae(request):
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

    division = 4
    
    # Optimizar la consulta usando select_related y prefetch_related
    procedimientos = Procedimientos.objects.filter(id_division=division).select_related(
        'id_division', 'id_solicitante', 'id_jefe_comision', 'id_municipio', 'id_parroquia', 'id_tipo_procedimiento'
    ).prefetch_related(
        Prefetch('abastecimiento_agua_set'),
        Prefetch('apoyo_unidades_set'),
        Prefetch('guardia_prevencion_set'),
        Prefetch('atendido_no_efectuado_set'),
        Prefetch('despliegue_seguridad_set'),
        Prefetch('fallecidos_set'),
        Prefetch('falsa_alarma_set'),
        Prefetch('servicios_especiales_set'),
        Prefetch('rescate_set'),
        Prefetch('incendios_set'),
        Prefetch('atenciones_paramedicas_set'),
        Prefetch('traslado_prehospitalaria_set'),
        Prefetch('evaluacion_riesgo_set'),
        Prefetch('mitigacion_riesgos_set'),
        Prefetch('puesto_avanzada_set'),
        Prefetch('asesoramiento_set'),
        Prefetch('reinspeccion_prevencion_set'),
        Prefetch('retencion_preventiva_set'),
        Prefetch('artificios_pirotecnicos_set'),
        Prefetch('inspeccion_establecimiento_art_set'),
        Prefetch('valoracion_medica_set'),
        Prefetch('detalles_enfermeria_set'),
        Prefetch('procedimientos_psicologia_set'),
        Prefetch('procedimientos_capacitacion_set'),
        Prefetch('procedimientos_brigada_set'),
        Prefetch('procedimientos_frente_preventivo_set'),
        Prefetch('jornada_medica_set'),
        Prefetch('inspeccion_prevencion_asesorias_tecnicas_set'),
        Prefetch('inspeccion_habitabilidad_set'),
        Prefetch('inspeccion_otros_set'),
        Prefetch('inspeccion_arbol_set'),
        Prefetch('investigacion_set')
    )

    # Preparar lista de datos a enviar
    datos = []

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

        # Agregar datos al arreglo
        datos.append({
            'division': procedimiento.id_division.division,
            'solicitante': solicitante,
            'jefe_comision': jefe_comision,
            'municipio': procedimiento.id_municipio.municipio,
            'parroquia': procedimiento.id_parroquia.parroquia,
            'fecha': procedimiento.fecha,
            'hora': procedimiento.hora,
            'direccion': procedimiento.direccion,
            'tipo_procedimiento': procedimiento.id_tipo_procedimiento.tipo_procedimiento,
            'detalles': detalles_str,
            'personas_presentes': personas_presentes_str,
            'descripcion': descripcion_str
        })

    return JsonResponse({'data': datos})

def generar_excel_capacitacion(request):
    division = 9
    # Obtener los procedimientos de la división especificada con prefetching
    procedimientos = Procedimientos.objects.filter(id_division=division).prefetch_related(
        'abastecimiento_agua_set',
        'apoyo_unidades_set',
        'guardia_prevencion_set',
        'atendido_no_efectuado_set',
        'despliegue_seguridad_set',
        'fallecidos_set',
        'falsa_alarma_set',
        'servicios_especiales_set',
        'rescate_set',
        'incendios_set',
        'atenciones_paramedicas_set',
        'traslado_prehospitalaria_set',
        'evaluacion_riesgo_set',
        'mitigacion_riesgos_set',
        'puesto_avanzada_set',
        'asesoramiento_set',
        'reinspeccion_prevencion_set',
        'retencion_preventiva_set',
        'artificios_pirotecnicos_set',
        'inspeccion_establecimiento_art_set',
        'valoracion_medica_set',
        'detalles_enfermeria_set',
        'procedimientos_psicologia_set',
        'procedimientos_capacitacion_set',
        'procedimientos_brigada_set',
        'procedimientos_frente_preventivo_set',
        'jornada_medica_set',
        'inspeccion_prevencion_asesorias_tecnicas_set',
        'inspeccion_habitabilidad_set',
        'inspeccion_otros_set',
        'inspeccion_arbol_set',
        'investigacion_set'
    )

    def obtener_personas_y_detalles(set_relacionado, campo_descripcion=None):
        """Función auxiliar para obtener personas presentes y detalles de procedimientos"""
        personas = []
        detalles = []
        for item in set_relacionado:
            if hasattr(item, 'cedula'):
                personas.append(f"{item.nombres} {item.apellidos} {item.cedula}")
            if hasattr(item, 'nombre_propietario'):
                personas.append(f"{item.nombre_propietario} {item.apellido_propietario} {item.cedula_propietario}")
            detalles.append(getattr(item, campo_descripcion, '') if campo_descripcion else str(item))
        return personas, detalles

    datos = []
    for procedimiento in procedimientos:
        solicitante = (f"{procedimiento.id_solicitante.jerarquia} {procedimiento.id_solicitante.nombres} "
                       f"{procedimiento.id_solicitante.apellidos}") if procedimiento.id_solicitante else procedimiento.solicitante_externo
        jefe_comision = (f"{procedimiento.id_jefe_comision.jerarquia} {procedimiento.id_jefe_comision.nombres} "
                         f"{procedimiento.id_jefe_comision.apellidos}") if procedimiento.id_jefe_comision else ""

        personas_presentes, detalles_procedimientos = [], []
        relaciones = [
            (procedimiento.abastecimiento_agua_set.all(), 'id_tipo_servicio.nombre_institucion'),
            # Agrega las demás relaciones...
        ]

        for relacion, campo_descripcion in relaciones:
            personas_relacionadas, detalles_relacionados = obtener_personas_y_detalles(relacion, campo_descripcion)
            personas_presentes.extend(personas_relacionadas)
            detalles_procedimientos.extend(detalles_relacionados)

        personas_presentes_str = " -- ".join(personas_presentes)
        detalles_str = " -- ".join(detalles_procedimientos)
        descripcion_str = " -- ".join(detalles_procedimientos)

        datos.append({
            "division": procedimiento.id_division.division,
            "solicitante": solicitante,
            "jefe_comision": jefe_comision,
            "municipio": procedimiento.id_municipio.municipio,
            "parroquia": procedimiento.id_parroquia.parroquia,
            "fecha": procedimiento.fecha,
            "hora": procedimiento.hora,
            "direccion": procedimiento.direccion,
            "tipo_procedimiento": procedimiento.id_tipo_procedimiento.tipo_procedimiento,
            "detalles": detalles_str,
            "personas_presentes": personas_presentes_str,
            "descripcion": descripcion_str,
        })

    return JsonResponse(datos, safe=False)
