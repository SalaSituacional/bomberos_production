from django.urls import path, include
from .views import *

urlpatterns = [
    path('dashboard_insumos_medicos/', DashboardInventariosView.as_view(), name='dashboard_insumos_medicos'),
    path('lote/agregar/', LotePrincipalCreateView.as_view(), name='lote_agregar'),
    path('insumos/asignar/', AsignarInsumoView.as_view(), name='asignar_insumos'),
    path('inventarios/<str:inventario_name>/', InventarioConsumoView.as_view(), name='inventario_consumo'),
    path('obtener_lotes/', obtener_lotes_ajax, name='obtener_lotes_insumos_medicos'),
    path('insumos/registrar/', InsumoCreateView.as_view(), name='registrar_insumo'),
    path('movimientos/historial/', MovimientoListView.as_view(), name='historial_movimientos'),


]
