from django.urls import path, include
from Web_App.urls import *
from .views import *

urlpatterns = [
    # Bienes Municipales
    # renderizado
    path('dashboard_bienes/', Dashboard_bienes,name='dashboardBienes'),
    path('inventario_bienes/', Inventario_bienes,name='inventarioBienes'),
    path('registro_bienes/', Registros_bienes,name='registroInventario'),
    # funciones crud
    path('reasignar-bien/', reasignar_bien, name='reasignarBien'),
    path('cambiar-bien/', cambiar_estado_bienes, name='cambiarEstadoBien'),
    path('eliminar-bien/', eliminar_bien, name='eliminarBien'),
    # APIs internas
    path('api/bienes/', listar_bienes, name='api_bienes'),
    path('api/verificar-identificador/', verificar_identificador, name='verificar_identificador'),
    path('api/historial-bien/<str:bien_id>/', historial_bien_api, name='historial_bien_api'),
    # Api Generar Excel
    path('generar-excel-bienesmunicipales/', generar_excel_bienes_municipales, name='generar_excel_bienesmunicipales'),

]
