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

def generar_excel_capacitacion(request):
    # Filtramos la división de capacitación (ID 9)
    division_capacitacion = Divisiones.objects.get(id=9)

    # Obtenemos todos los procedimientos relacionados con la división de capacitación
    procedimientos = Procedimientos.objects.filter(id_division=division_capacitacion)

    # Crear DataFrame con los datos de los procedimientos
    data = []
    for procedimiento in procedimientos:
        # Obtenemos los detalles adicionales del procedimiento desde Procedimientos_Capacitacion
        try:
            procedimiento_capacitacion = Procedimientos_Capacitacion.objects.get(id_procedimientos=procedimiento)
            tipo_capacitacion = procedimiento_capacitacion.tipo_capacitacion
            tipo_clasificacion = procedimiento_capacitacion.tipo_clasificacion
            personas_beneficiadas = procedimiento_capacitacion.personas_beneficiadas
            descripcion = procedimiento_capacitacion.descripcion
            material_utilizado = procedimiento_capacitacion.material_utilizado
            status = procedimiento_capacitacion.status
        except Procedimientos_Capacitacion.DoesNotExist:
            # Si no hay datos en Procedimientos_Capacitacion, asignamos valores por defecto
            tipo_capacitacion = 'N/A'
            tipo_clasificacion = 'N/A'
            personas_beneficiadas = '0'
            descripcion = 'N/A'
            material_utilizado = 'N/A'
            status = 'N/A'

        # Formateamos la fecha en un formato estándar
        fecha_formateada = procedimiento.fecha.strftime('%Y-%m-%d')

        # Agregamos los datos al DataFrame
        data.append({
            'Division': procedimiento.id_division.division,
            'Solicitante': procedimiento.id_solicitante if procedimiento.id_solicitante else 'N/A',
            'Solicitante Externo': procedimiento.solicitante_externo,
            'Unidad': procedimiento.unidad,
            'Fecha': fecha_formateada,
            'Hora': procedimiento.hora,
            'Dirección': procedimiento.direccion,
            'Tipo Procedimiento': procedimiento.id_tipo_procedimiento.tipo_procedimiento,
            'Tipo Capacitación': tipo_capacitacion,
            'Tipo Clasificación': tipo_clasificacion,
            'Personas Beneficiadas': personas_beneficiadas,
            'Descripción': descripcion,
            'Material Utilizado': material_utilizado,
            'Status': status,
        })

    # Convertir el DataFrame a Excel
    df = pd.DataFrame(data)

    # Crear la respuesta de Excel
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="procedimientos_capacitacion.xlsx"'
    
    # Usamos pandas para escribir el DataFrame en un archivo Excel
    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Procedimientos')

        # Accedemos al libro de trabajo y la hoja activa
        workbook = writer.book
        worksheet = writer.sheets['Procedimientos']

        # Ajustar el ancho de las columnas automáticamente
        for col_num, col_name in enumerate(df.columns.values):
            max_len = max(df[col_name].astype(str).apply(len).max(), len(col_name))  # Encuentra el máximo tamaño
            worksheet.set_column(col_num, col_num, max_len + 2)  # Añade un pequeño margen

    return response

def generar_excel_capacitacion(request):
    # Filtramos la división de capacitación (ID 9)
    division_capacitacion = Divisiones.objects.get(id=9)

    # Obtenemos todos los procedimientos relacionados con la división de capacitación
    procedimientos = Procedimientos.objects.filter(id_division=division_capacitacion)

    # Crear DataFrame con los datos de los procedimientos
    data = []
    for procedimiento in procedimientos:
        # Obtenemos los detalles adicionales del procedimiento desde Procedimientos_Capacitacion
        procedimiento_capacitacion = Procedimientos_Capacitacion.objects.filter(id_procedimientos=procedimiento).first()
        
        if procedimiento_capacitacion:
            tipo_capacitacion = procedimiento_capacitacion.tipo_capacitacion
            tipo_clasificacion = procedimiento_capacitacion.tipo_clasificacion
            personas_beneficiadas = procedimiento_capacitacion.personas_beneficiadas
            descripcion = procedimiento_capacitacion.descripcion
            material_utilizado = procedimiento_capacitacion.material_utilizado
            status = procedimiento_capacitacion.status
        else:
            # Si no hay datos en Procedimientos_Capacitacion, asignamos valores por defecto
            tipo_capacitacion = 'N/A'
            tipo_clasificacion = 'N/A'
            personas_beneficiadas = '0'
            descripcion = 'N/A'
            material_utilizado = 'N/A'
            status = 'N/A'

        # Formateamos la fecha en un formato estándar
        fecha_formateada = procedimiento.fecha.strftime('%Y-%m-%d')

        # Agregamos los datos al DataFrame
        data.append({
            'Division': procedimiento.id_division.division,
            'Solicitante': procedimiento.id_solicitante if procedimiento.id_solicitante else 'N/A',
            'Solicitante Externo': procedimiento.solicitante_externo,
            'Unidad': procedimiento.unidad,
            'Fecha': fecha_formateada,
            'Hora': procedimiento.hora,
            'Dirección': procedimiento.direccion,
            'Tipo Procedimiento': procedimiento.id_tipo_procedimiento.tipo_procedimiento,
            'Tipo Capacitación': tipo_capacitacion,
            'Tipo Clasificación': tipo_clasificacion,
            'Personas Beneficiadas': personas_beneficiadas,
            'Descripción': descripcion,
            'Material Utilizado': material_utilizado,
            'Status': status,
        })

    # Convertir el DataFrame a Excel
    df = pd.DataFrame(data)

    # Crear la respuesta de Excel
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="procedimientos_capacitacion.xlsx"'
    
    # Usamos pandas para escribir el DataFrame en un archivo Excel
    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Procedimientos')

        # Accedemos al libro de trabajo y la hoja activa
        workbook = writer.book
        worksheet = writer.sheets['Procedimientos']

        # Ajustar el ancho de las columnas automáticamente
        for col_num, col_name in enumerate(df.columns.values):
            max_len = max(df[col_name].astype(str).apply(len).max(), len(col_name))  # Encuentra el máximo tamaño
            worksheet.set_column(col_num, col_num, max_len + 2)  # Añade un pequeño margen

    return response

