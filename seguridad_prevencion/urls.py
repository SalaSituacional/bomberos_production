from django.urls import path, include
from Web_App.urls import *
from .views import *

urlpatterns = [
    # vistas
    # Certificados Prevencion
    path('certificadosprevencion/', certificados_prevencion, name='certificados_prevencion'),
    path('formulariocertificados/', formulario_certificado_prevencion, name='formulario_certificado_prevencion'),

    path('agregar_comercio/', agregar_comercio , name='agregar_comercio'),
    
    path('api/ultimo_reporte_solicitudes/', obtener_ultimo_reporte_solicitudes, name='obtener_ultimo_reporte_solicitudes'),
    path("validar-cedula/", validar_cedula, name="validar_cedula"),
    
    path('api/get_solicitudes/<str:referencia>/', api_get_solicitudes, name='get_solicitudes'),
    
    # path('planillacertificado/', planilla_certificado, name='planilla_certificado_prevencion'),
    path('generar_documento_guia/<int:id>/', doc_Guia, name='generar_documento_guia'),
    path('generar_documento_inspeccion/<int:id>/', doc_Inspeccion, name='generar_documento_inspeccion'),
    path('generar_credencial/<int:id>/', doc_Credencial, name='generar_credencial'),

    path('api/eliminar_solicitudes/<int:id>/', api_eliminar_solicitudes, name='api_eliminar_solicitudes'),

    path('editar_solicitud/<int:id>/', editar_solicitud, name='editar_solicitud'),
    # path('api/modificar_solicitudes/<int:id>/', api_modificar_solicitudes, name='api_modificar_solicitudes'),


    path('generar-excel-solicitudes/', generar_excel_solicitudes, name='generar_excel_solicitudes'),
]