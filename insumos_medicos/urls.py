from django.urls import path, include
from .views import *

urlpatterns = [
   path('dashboard_insumos_medicos/', DashboardInventariosView.as_view(), name='dashboard_insumos_medicos'),
    path('lote/agregar/', LotePrincipalCreateView.as_view(), name='lote_agregar'),
    path('insumos/asignar/', AsignarInsumoView.as_view(), name='asignar_insumos'),



]
