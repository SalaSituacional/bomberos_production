from django.urls import path
from .views import *

urlpatterns = [
    # vistas
    path('dashboard_mecanica/', Dashboard_mecanica,name='dashboard_mecanica'),

        # Unidades
    path('unidades/', View_Unidades, name='unidades'),

    path('conductores/', conductores, name='conductores'),
    path('agregar_conductores/', agregar_conductor, name='agregar_conductor'),
    path('conductores/<int:id>/editar/', editar_conductor, name='editar_conductor'),

    # API Endpoints
    path('api/conductores/', api_conductores, name='api_conductores'),
    path('api/conductores/<int:id>/', api_eliminar_conductor, name='api_eliminar_conductor'),

    path('formularioUnidades/', View_Form_unidades, name='formulario_unidades'),
    path('agregar_reportes/', agregar_reportes, name="agregar_reportes"),
    path('agregar_unidades/', agregar_unidades, name="agregar_unidades"),
    path('cambiar_estado/', cambiar_estado, name="cambiar_estado"),
    path('reasignar_division/', reasignar_division, name="reasignar_division"),
    path('obtener_info_unidad/<int:id>/', obtener_info_unidad, name="obtener_info_unidad"),
    path('mostrar_informacion/<int:id>/', mostrar_informacion, name="mostrar_informacion"),
    path('unidades/eliminar_reporte/<int:reporte_id>/', eliminar_reporte, name='eliminar_reporte'),

    path("api/conteo_unidades/", contar_estados_unidades, name="conteo_unidades"),
    path("api/reportes_combustible/", contar_reportes_combustible, name="reportes_combustible"),
    path("api/reportes_lubricantes/", contar_reporte_lubricantes, name="reportes_lubricantes"),
    path("api/reportes_neumaticos/", contar_reporte_neumaticos, name="reportes_neumaticos"),
    path("api/reportes_reparaciones/", contar_reporte_reparaciones, name="reportes_reparaciones"),
    path("api/reportes_electricas/", contar_reporte_electricas, name="reportes_electricas"),
    path("api/reportes_cambio_repuestos/", contar_reporte_cambio_repuestos, name="reportes_cambio_repuestos"),
    path("api/reportes_colisiones_daños/", contar_reporte_colisiones_danos, name="reportes_colisiones_daños"),

    path('generar-excel-reportes-unidades/', generar_excel_reportes_unidades, name='generar_excel_reportes'),

    # Urls Para el Area de Invenario de Unidades
    # # Herramientas
    path('herramientas/', listar_herramientas, name='listar-herramientas'),
    path('herramientas/nueva/', crear_herramienta, name='crear-herramienta'),
    path('herramientas/editar/<int:pk>/', editar_herramienta, name='editar-herramienta'),
    path('herramientas/eliminar/<int:pk>/', eliminar_herramienta, name='eliminar-herramienta'),
    
    # # Asignaciones
    path('asignaciones/', asignacion_unidades, name='asignacion-unidades'),
    path('asignaciones/<int:unidad_id>/', detalle_asignacion, name='detalle-asignacion'),
    path('asignaciones/devolver/<int:asignacion_id>/', devolver_herramienta, name='devolver-herramienta'),
]
