from django.urls import path, include
from .views import *

urlpatterns = [
    # Renderizado de vistan (Paginas) (Funciones)
    
    path('dashboard_insumos_medicos/', InventarioPrincipalListView.as_view(), name='dashboard_insumos_medicos'),
    path('insumos_cuartel/', cuartel_central, name='insumos_cuartel'),
    path('insumos_estacion_1/', estacion_1, name='insumos_estacion_1'),
    path('insumos_estacion_2/', estacion_2, name='insumos_estacion_2'),
    path('insumos_estacion_3/', estacion_3, name='insumos_estacion_3'),
    path('insumos_enfermeria/', enfermeria, name='insumos_enfermeria'),
    path('insumos_servicios_medicos/', servicios_medicos, name='insumos_servicios_medicos'),

# =================================================================================
                                # CBVs (Componentes)
# ===================================================================================    
    # Lote de insumos Principal
    
    # Crea un nuevo lote de insumos en el inventario principal
    path('lote/agregar/', LotePrincipalCreateView.as_view(), name='lote_agregar'),
    # path('insumos/asignar/', AsignarInsumoView.as_view(), name='asignar_insumos'),


]
