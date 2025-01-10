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


def generar_excel(request):
    # Crear un libro de trabajo y una hoja
    workbook = openpyxl.Workbook()
    hoja = workbook.active
    hoja.title = "Procedimientos"

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

    # Agregar datos a la hoja
    for procedimiento in procedimientos:
        # Determinar los datos de solicitante y jefe de comisión
        solicitante = (f"{procedimiento.id_solicitante.jerarquia} "
                       f"{procedimiento.id_solicitante.nombres} "
                       f"{procedimiento.id_solicitante.apellidos}") \
                      if procedimiento.id_solicitante is not None and procedimiento.id_solicitante.id != 0 \
                      else procedimiento.solicitante_externo

        jefe_comision = (f"{procedimiento.id_jefe_comision.jerarquia} "
                         f"{procedimiento.id_jefe_comision.nombres} "
                         f"{procedimiento.id_jefe_comision.apellidos}") \
                        if procedimiento.id_jefe_comision is not None and procedimiento.id_jefe_comision.id != 0 \
                        else ""
        # Recopilar datos de "Personas Presentes" desde todas las tablas relacionadas
        personas_presentes = []
        detalles_procedimientos = []
        descripciones_proc = []

        # Abastecimiento_agua
        for detalles in procedimiento.abastecimiento_agua_set.all():
            personas_presentes.append(f"{detalles.nombres} {detalles.apellidos} {detalles.cedula}")
            detalles_procedimientos.append(f"{detalles.id_tipo_servicio.nombre_institucion}")
            descripciones_proc.append(detalles.descripcion)

        # Apoyo_Unidades
        for detalles in procedimiento.apoyo_unidades_set.all():
            detalles_procedimientos.append(detalles.id_tipo_apoyo.tipo_apoyo)
            descripciones_proc.append(detalles.descripcion)

        # Guardia_Prevencion
        for detalles in procedimiento.guardia_prevencion_set.all():
            detalles_procedimientos.append(detalles.id_motivo_prevencion.motivo)
            descripciones_proc.append(detalles.descripcion)

        # Atendido_no_Efectuado
        for detalles in procedimiento.atendido_no_efectuado_set.all():
            descripciones_proc.append(detalles.descripcion)

        # Despliegue_Seguridad
        for detalles in procedimiento.despliegue_seguridad_set.all():
            detalles_procedimientos.append(detalles.motivo_despliegue.motivo)
            descripciones_proc.append(detalles.descripcion)

        # Fallecidos
        for detalles in procedimiento.fallecidos_set.all():
            personas_presentes.append(f"{detalles.nombres} {detalles.apellidos} {detalles.cedula}")
            detalles_procedimientos.append(detalles.motivo_fallecimiento)
            descripciones_proc.append(detalles.descripcion)

        # Falsa_Alarma
        for detalles in procedimiento.falsa_alarma_set.all():
            detalles_procedimientos.append(detalles.motivo_alarma.motivo)
            descripciones_proc.append(detalles.descripcion)

        # Servicios_Especiales
        for detalles in procedimiento.servicios_especiales_set.all():
            detalles_procedimientos.append(detalles.tipo_servicio.serv_especiales)
            descripciones_proc.append(detalles.descripcion)

        for rescate in procedimiento.rescate_set.all():
            # Añadir el tipo de rescate al listado de detalles
            detalles_procedimientos.append(rescate.tipo_rescate.tipo_rescate)
            
            # Detalles de personas rescatadas
            detalles_personas = []
            for persona in rescate.rescate_persona_set.all():
                detalles_personas.append(f"{persona.nombre} {persona.apellidos} {persona.cedula}")
                descripciones_proc.append(persona.descripcion)
            
            # Añadir detalles de personas rescatadas, si existen
            if detalles_personas:
                personas_presentes.append(f"{''.join(detalles_personas)}")

            # Detalles de animales rescatados
            detalles_animales = []
            for animal in rescate.rescate_animal_set.all():
                detalles_animales.append(f"Especie: {animal.especie}")
                descripciones_proc.append(animal.descripcion)
            
            # Añadir detalles de animales rescatados, si existen
            if detalles_animales:
                detalles_procedimientos.append(f"{''.join(detalles_animales)}")

        # Incendios -> Persona_Presente
        for incendio in procedimiento.incendios_set.all():
            detalles_procedimientos.append(incendio.id_tipo_incendio.tipo_incendio)
            descripciones_proc.append(incendio.descripcion)
            for persona in incendio.persona_presente_set.all():
                personas_presentes.append(f"{persona.nombre} {persona.apellidos} {persona.cedula}")

       # Atenciones Paramédicas
        for atencion in procedimiento.atenciones_paramedicas_set.all():
            # Añadir el tipo de atención
            detalles_procedimientos.append(atencion.tipo_atencion)

            # Detalles de Emergencias Médicas
            detalles_emergencias = []
            for emergencia in atencion.emergencias_medicas_set.all():
                detalles_emergencias.append(f"{emergencia.nombres} {emergencia.apellidos} {emergencia.cedula}")
                descripciones_proc.append(emergencia.descripcion)
            
            # Añadir detalles de emergencias médicas, si existen
            if detalles_emergencias:
                personas_presentes.append(f"{''.join(detalles_emergencias)}")

            # Detalles de Accidentes de Tránsito
            for accidente in atencion.accidentes_transito_set.all():
                # Añadir tipo de accidente
                detalles_procedimientos.append(accidente.tipo_de_accidente.tipo_accidente)
                
                # Detalles de Lesionados
                detalles_lesionados = []
                for lesionado in accidente.lesionados_set.all():
                    detalles_lesionados.append(f"{lesionado.nombres} {lesionado.apellidos} {lesionado.cedula}, ")
                    descripciones_proc.append(lesionado.descripcion)
                
                # Añadir detalles de lesionados, si existen
                if detalles_lesionados:
                    personas_presentes.append(f"{''.join(detalles_lesionados)}")

        # Traslado_Prehospitalaria
        for traslado in procedimiento.traslado_prehospitalaria_set.all():
            detalles_procedimientos.append(traslado.id_tipo_traslado.tipo_traslado)
            personas_presentes.append(f"{traslado.nombre} {traslado.apellido} {traslado.cedula}")
            descripciones_proc.append(traslado.descripcion)

        # Evaluacion_Riesgo -> Persona_Presente_Eval
        for evaluacion in procedimiento.evaluacion_riesgo_set.all():
            detalles_procedimientos.append(evaluacion.id_tipo_riesgo.tipo_riesgo)
            detalles_procedimientos.append(evaluacion.tipo_estructura)
            descripciones_proc.append(evaluacion.descripcion)
            for persona in evaluacion.persona_presente_eval_set.all():
                personas_presentes.append(f"{persona.nombre} {persona.apellidos} {persona.cedula}")

        # Mitigacion_Riesgos
        for mitigacion in procedimiento.mitigacion_riesgos_set.all():
            detalles_procedimientos.append(mitigacion.id_tipo_servicio.tipo_servicio)
            descripciones_proc.append(mitigacion.descripcion)

        # Puesto_Avanzada
        for avanzada in procedimiento.puesto_avanzada_set.all():
            detalles_procedimientos.append(avanzada.id_tipo_servicio.tipo_servicio)
            descripciones_proc.append(avanzada.descripcion)

        # Asesoramiento
        for asesoramiento in procedimiento.asesoramiento_set.all():
            detalles_procedimientos.append(f"Comercio: {asesoramiento.nombre_comercio} {asesoramiento.rif_comercio}")
            personas_presentes.append(f"{asesoramiento.nombres} {asesoramiento.apellidos} {asesoramiento.cedula}")
            descripciones_proc.append(asesoramiento.descripcion)

        # Reinspeccion_Prevencion
        for detalles in procedimiento.reinspeccion_prevencion_set.all():
            detalles_procedimientos.append(f"Comercio: {detalles.nombre_comercio} {detalles.rif_comercio}")
            personas_presentes.append(f"{detalles.nombre} {detalles.apellidos} {detalles.cedula}")
            descripciones_proc.append(detalles.descripcion)

        # Retencion_Preventiva
        for detalles in procedimiento.retencion_preventiva_set.all():
            detalles_procedimientos.append(f"Tipo Cilindro: {detalles.tipo_cilindro} {detalles.capacidad}")
            personas_presentes.append(f"{detalles.nombre} {detalles.apellidos} {detalles.cedula}")
            descripciones_proc.append(detalles.descripcion)

        # Artificios_Pirotecnicos
        for artificio in procedimiento.artificios_pirotecnicos_set.all():
            detalles_procedimientos.append(f"{artificio.tipo_procedimiento.tipo}")
            
            # Incendios_Art -> Persona_Presente_Art
            for incendio in artificio.incendios_art_set.all():
                descripciones_proc.append(incendio.descripcion)
                for persona in incendio.persona_presente_art_set.all():
                    personas_presentes.append(f"{persona.nombre} {persona.apellidos} {persona.cedula}")

            # Lesionados_Art
            for lesionado in artificio.lesionados_art_set.all():
                descripciones_proc.append(lesionado.descripcion)
                personas_presentes.append(f"{lesionado.nombres} {lesionado.apellidos} {lesionado.cedula}")

            # Fallecidos_Art
            for fallecido in artificio.fallecidos_art_set.all():
                descripciones_proc.append(fallecido.descripcion)
                personas_presentes.append(f"{fallecido.nombres} {fallecido.apellidos} {fallecido.cedula}")

        # Inspeccion_Establecimiento_Art
        for inspeccion in procedimiento.inspeccion_establecimiento_art_set.all():
            detalles_procedimientos.append(f"Comercio: {inspeccion.nombre_comercio} {inspeccion.rif_comercio}")
            descripciones_proc.append(inspeccion.descripcion)
            personas_presentes.append(f"{inspeccion.encargado_nombre} {inspeccion.encargado_apellidos} {inspeccion.encargado_cedula}")

        # Valoracion_Medica
        for valoracion in procedimiento.valoracion_medica_set.all():
            detalles_procedimientos.append(procedimiento.tipo_servicio)
            personas_presentes.append(f"{valoracion.nombre} {valoracion.apellido} {valoracion.cedula}")
            descripciones_proc.append(valoracion.descripcion)

        # Detalles_Enfermeria
        for enfermeria in procedimiento.detalles_enfermeria_set.all():
            detalles_procedimientos.append(procedimiento.dependencia)
            personas_presentes.append(f"{enfermeria.nombre} {enfermeria.apellido} {enfermeria.cedula}")
            descripciones_proc.append(enfermeria.descripcion)

        # Procedimientos_Psicologia
        for psicologia in procedimiento.procedimientos_psicologia_set.all():
            detalles_procedimientos.append("Consultas Psicologicas")
            personas_presentes.append(f"{psicologia.nombre} {psicologia.apellido} {psicologia.cedula}")
            descripciones_proc.append(psicologia.descripcion)

        # Procedimientos_Capacitacion
        for capacitacion in procedimiento.procedimientos_capacitacion_set.all():
            detalles_procedimientos.append(f"Dependencia: {procedimiento.dependencia} - Capacitación: {capacitacion.tipo_capacitacion} - Clasificacion: {capacitacion.tipo_clasificacion}")
            descripciones_proc.append(capacitacion.descripcion)
        
        # Procedimientos_Capacitacion
        for brigada in procedimiento.procedimientos_brigada_set.all():
            detalles_procedimientos.append(f"Dependencia: {procedimiento.dependencia} - Capacitación: {brigada.tipo_capacitacion} - Clasificacion: {brigada.tipo_clasificacion}")
            descripciones_proc.append(capacitacion.descripcion)

        # Procedimientos_Frente_Preventivo
        for frente_preventivo in procedimiento.procedimientos_frente_preventivo_set.all():
            detalles_procedimientos.append(f"Dependencia: {procedimiento.dependencia} - Actividad: {frente_preventivo.nombre_actividad} - Estrategia: {frente_preventivo.estrategia}")
            descripciones_proc.append(frente_preventivo.descripcion)

        # Datos de la Jornada Médica
        for jornada in procedimiento.jornada_medica_set.all():
            detalles_procedimientos.append(f"{jornada.nombre_jornada} - {jornada.cant_personas_aten}")
            descripciones_proc.append(f"{jornada.descripcion}")  # Incluyendo la cantidad

        # Inspecciones
        for inspeccion in procedimiento.inspeccion_prevencion_asesorias_tecnicas_set.all():
            detalles_procedimientos.append(inspeccion.tipo_inspeccion)
            personas_presentes.append(f"{inspeccion.persona_sitio_nombre} {inspeccion.persona_sitio_apellido} ({inspeccion.persona_sitio_cedula})")
            descripciones_proc.append(inspeccion.descripcion)

        for inspeccion in procedimiento.inspeccion_habitabilidad_set.all():
            detalles_procedimientos.append(inspeccion.tipo_inspeccion)
            personas_presentes.append(f"{inspeccion.persona_sitio_nombre} {inspeccion.persona_sitio_apellido} ({inspeccion.persona_sitio_cedula})")
            descripciones_proc.append(inspeccion.descripcion)

        for inspeccion in procedimiento.inspeccion_otros_set.all():
            detalles_procedimientos.append(inspeccion.tipo_inspeccion)
            personas_presentes.append(f"{inspeccion.persona_sitio_nombre} {inspeccion.persona_sitio_apellido} ({inspeccion.persona_sitio_cedula})")
            descripciones_proc.append(inspeccion.descripcion)

        for inspeccion in procedimiento.inspeccion_arbol_set.all():
            detalles_procedimientos.append(f"{inspeccion.tipo_inspeccion} -- {inspeccion.especie} ({inspeccion.altura_aprox})")
            personas_presentes.append(f"{inspeccion.persona_sitio_nombre} {inspeccion.persona_sitio_apellido} {inspeccion.persona_sitio_cedula}")
            descripciones_proc.append(inspeccion.descripcion)

        # Para cada registro de 'Investigacion' asociado con 'Procedimientos'
        for investigacion in procedimiento.investigacion_set.all():
            # Añadir el tipo de investigación y el tipo de siniestro
            detalles_procedimientos.append(f"{investigacion.id_tipo_investigacion.tipo_investigacion} - {investigacion.tipo_siniestro}")
            
            # Investigacion -> Investigacion_Vehiculo
            detalles_propietario = []
            for vehiculo in investigacion.investigacion_vehiculo_set.all():
                detalles_propietario.append(f"{vehiculo.nombre_propietario} {vehiculo.apellido_propietario} {vehiculo.cedula_propietario}")
                descripciones_proc.append(vehiculo.descripcion)
            if detalles_propietario:
                personas_presentes.append(f"{''.join(detalles_propietario)}")
            
            # Investigacion -> Investigacion_Comercio
            detalles_comercios = []
            for comercio in investigacion.investigacion_comercio_set.all():
                detalles_comercios.append(f"{comercio.nombre_propietario} {comercio.apellido_propietario} {comercio.cedula_propietario}")
                descripciones_proc.append(comercio.descripcion)
            if detalles_comercios:
                personas_presentes.append(f"{''.join(detalles_comercios)}")
            
            # Investigacion -> Investigacion_Estructura_Vivienda
            detalles_estructuras = []
            for estructura in investigacion.investigacion_estructura_vivienda_set.all():
                detalles_estructuras.append(f"{estructura.nombre} {estructura.apellido} {estructura.cedula}")
                descripciones_proc.append(estructura.descripcion)
            if detalles_estructuras:
                personas_presentes.append(f"{''.join(detalles_estructuras)}")

        # Convertir lista de personas presentes a string separado por punto y coma
        personas_presentes_str = " -- ".join(personas_presentes)
        detalles_str = " -- ".join(detalles_procedimientos)  # Convertir descripciones a string
        descripcion_str = " -- ".join(descripciones_proc)  # Convertir descripciones a string

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
    response["Content-Disposition"] = "attachment; filename=procedimientos.xlsx"
    workbook.save(response)
    return response

# def generar_excel_capacitacion(request):
#     # Filtramos la división de capacitación (ID 9)
#     division_capacitacion = Divisiones.objects.get(id=9)

#     # Obtenemos todos los procedimientos relacionados con la división de capacitación
#     procedimientos = Procedimientos.objects.filter(id_division=division_capacitacion)

#     # Mostramos los datos en consola
#     for procedimiento in procedimientos:
#         print(f"Division: {procedimiento.id_division.division}, "
#               f"Solicitante: {procedimiento.id_solicitante if procedimiento.id_solicitante else 'N/A'}, "
#               f"Solicitante Externo: {procedimiento.solicitante_externo}, "
#               f"Unidad: {procedimiento.unidad}, "
#               f"Fecha: {procedimiento.fecha}, "
#               f"Hora: {procedimiento.hora}, "
#               f"Dirección: {procedimiento.direccion}, "
#               f"Tipo Procedimiento: {procedimiento.id_tipo_procedimiento.tipo_procedimiento}")

#     # Crear DataFrame con los datos de los procedimientos
#     data = []
#     for procedimiento in procedimientos:
#         # Formateamos la fecha en un formato estándar
#         fecha_formateada = procedimiento.fecha.strftime('%Y-%m-%d')  # Ajustar formato de la fecha
#         data.append({
#             'Division': procedimiento.id_division.division,
#             'Solicitante': procedimiento.id_solicitante if procedimiento.id_solicitante else 'N/A',
#             'Solicitante Externo': procedimiento.solicitante_externo,
#             'Unidad': procedimiento.unidad,
#             'Fecha': fecha_formateada,  # Usamos la fecha formateada
#             'Hora': procedimiento.hora,
#             'Dirección': procedimiento.direccion,
#             'Tipo Procedimiento': procedimiento.id_tipo_procedimiento.tipo_procedimiento
#         })

#     df = pd.DataFrame(data)

#     # Convertir el DataFrame a Excel
#     response = HttpResponse(content_type='application/vnd.ms-excel')
#     response['Content-Disposition'] = 'attachment; filename="procedimientos_capacitacion.xlsx"'
    
#     # Usamos pandas para escribir el DataFrame en un archivo Excel
#     with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
#         df.to_excel(writer, index=False, sheet_name='Procedimientos')

#         # Accedemos al libro de trabajo y la hoja activa
#         workbook  = writer.book
#         worksheet = writer.sheets['Procedimientos']

#         # Ajustar el ancho de las columnas automáticamente
#         for col_num, col_name in enumerate(df.columns.values):
#             max_len = max(df[col_name].astype(str).apply(len).max(), len(col_name))  # Encuentra el máximo tamaño
#             worksheet.set_column(col_num, col_num, max_len + 2)  # Añade un pequeño margen

#     return response

# def generar_excel_capacitacion(request):
#     # Filtramos la división de capacitación (ID 9)
#     division_capacitacion = Divisiones.objects.get(id=9)

#     # Obtenemos todos los procedimientos relacionados con la división de capacitación
#     procedimientos = Procedimientos.objects.filter(id_division=division_capacitacion)

#     # Crear DataFrame con los datos de los procedimientos
#     data = []

    
#     for procedimiento in procedimientos:
#         # Obtenemos los detalles adicionales del procedimiento desde Procedimientos_Capacitacion
#         try:
#             procedimiento_capacitacion = Procedimientos_Capacitacion.objects.get(id_procedimientos=procedimiento)
#             tipo_capacitacion = procedimiento_capacitacion.tipo_capacitacion
#             tipo_clasificacion = procedimiento_capacitacion.tipo_clasificacion
#             personas_beneficiadas = procedimiento_capacitacion.personas_beneficiadas
#             descripcion = procedimiento_capacitacion.descripcion
#             material_utilizado = procedimiento_capacitacion.material_utilizado
#             status = procedimiento_capacitacion.status
#         except Procedimientos_Capacitacion.DoesNotExist:
#             # Si no hay datos en Procedimientos_Capacitacion, asignamos valores por defecto
#             tipo_capacitacion = 'N/A'
#             tipo_clasificacion = 'N/A'
#             personas_beneficiadas = '0'
#             descripcion = 'N/A'
#             material_utilizado = 'N/A'
#             status = 'N/A'

#         # Formateamos la fecha en un formato estándar
#         fecha_formateada = procedimiento.fecha.strftime('%Y-%m-%d')

#         # Agregamos los datos al DataFrame
#         data.append({
#             'Division': procedimiento.id_division.division,
#             'Solicitante': procedimiento.id_solicitante if procedimiento.id_solicitante else 'N/A',
#             'Solicitante Externo': procedimiento.solicitante_externo,
#             'Unidad': procedimiento.unidad,
#             'Fecha': fecha_formateada,
#             'Hora': procedimiento.hora,
#             'Dirección': procedimiento.direccion,
#             'Tipo Procedimiento': procedimiento.id_tipo_procedimiento.tipo_procedimiento,
#             'Tipo Capacitación': tipo_capacitacion,
#             'Tipo Clasificación': tipo_clasificacion,
#             'Personas Beneficiadas': personas_beneficiadas,
#             'Descripción': descripcion,
#             'Material Utilizado': material_utilizado,
#             'Status': status,
#         })

#     # Convertir el DataFrame a Excel
#     df = pd.DataFrame(data)

#     # Crear la respuesta de Excel
#     response = HttpResponse(content_type='application/vnd.ms-excel')
#     response['Content-Disposition'] = 'attachment; filename="procedimientos_capacitacion.xlsx"'
    
#     # Usamos pandas para escribir el DataFrame en un archivo Excel
#     with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
#         df.to_excel(writer, index=False, sheet_name='Procedimientos')

#         # Accedemos al libro de trabajo y la hoja activa
#         workbook = writer.book
#         worksheet = writer.sheets['Procedimientos']

#         # Ajustar el ancho de las columnas automáticamente
#         for col_num, col_name in enumerate(df.columns.values):
#             max_len = max(df[col_name].astype(str).apply(len).max(), len(col_name))  # Encuentra el máximo tamaño
#             worksheet.set_column(col_num, col_num, max_len + 2)  # Añade un pequeño margen

#     return response

# def generar_excel_capacitacion(request):
#     # Filtramos la división de capacitación (ID 9)
#     division_capacitacion = Divisiones.objects.get(id=9)

#     # Obtenemos todos los procedimientos relacionados con la división de capacitación
#     procedimientos = Procedimientos.objects.filter(id_division=division_capacitacion)

#     # Crear DataFrame con los datos de los procedimientos
#     data = []
#     for procedimiento in procedimientos:
#         # Obtenemos los detalles adicionales del procedimiento desde Procedimientos_Capacitacion
#         procedimiento_capacitacion = Procedimientos_Capacitacion.objects.filter(id_procedimientos=procedimiento).first()
        
#         if procedimiento_capacitacion:
#             tipo_capacitacion = procedimiento_capacitacion.tipo_capacitacion
#             tipo_clasificacion = procedimiento_capacitacion.tipo_clasificacion
#             personas_beneficiadas = procedimiento_capacitacion.personas_beneficiadas
#             descripcion = procedimiento_capacitacion.descripcion
#             material_utilizado = procedimiento_capacitacion.material_utilizado
#             status = procedimiento_capacitacion.status
#         else:
#             # Si no hay datos en Procedimientos_Capacitacion, asignamos valores por defecto
#             tipo_capacitacion = 'N/A'
#             tipo_clasificacion = 'N/A'
#             personas_beneficiadas = '0'
#             descripcion = 'N/A'
#             material_utilizado = 'N/A'
#             status = 'N/A'

#         # Formateamos la fecha en un formato estándar
#         fecha_formateada = procedimiento.fecha.strftime('%Y-%m-%d')

#         # Agregamos los datos al DataFrame
#         data.append({
#             'Division': procedimiento.id_division.division,
#             'Solicitante': procedimiento.id_solicitante if procedimiento.id_solicitante else 'N/A',
#             'Solicitante Externo': procedimiento.solicitante_externo,
#             'Unidad': procedimiento.unidad,
#             'Fecha': fecha_formateada,
#             'Hora': procedimiento.hora,
#             'Dirección': procedimiento.direccion,
#             'Tipo Procedimiento': procedimiento.id_tipo_procedimiento.tipo_procedimiento,
#             'Tipo Capacitación': tipo_capacitacion,
#             'Tipo Clasificación': tipo_clasificacion,
#             'Personas Beneficiadas': personas_beneficiadas,
#             'Descripción': descripcion,
#             'Material Utilizado': material_utilizado,
#             'Status': status,
#         })

#     # Convertir el DataFrame a Excel
#     df = pd.DataFrame(data)

#     # Crear la respuesta de Excel
#     response = HttpResponse(content_type='application/vnd.ms-excel')
#     response['Content-Disposition'] = 'attachment; filename="procedimientos_capacitacion.xlsx"'
    
#     # Usamos pandas para escribir el DataFrame en un archivo Excel
#     with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
#         df.to_excel(writer, index=False, sheet_name='Procedimientos')

#         # Accedemos al libro de trabajo y la hoja activa
#         workbook = writer.book
#         worksheet = writer.sheets['Procedimientos']

#         # Ajustar el ancho de las columnas automáticamente
#         for col_num, col_name in enumerate(df.columns.values):
#             max_len = max(df[col_name].astype(str).apply(len).max(), len(col_name))  # Encuentra el máximo tamaño
#             worksheet.set_column(col_num, col_num, max_len + 2)  # Añade un pequeño margen

#     return response

