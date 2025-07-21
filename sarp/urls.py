"""
URL configuration for Web_App project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from Web_App.urls import *
from .views import *

urlpatterns = [
    # SARP
    path('dashboard_sarp/', Dashboard_sarp,name='dashboard_sarp'),
    path('registros_sarp/', Registros_sarp, name='registros_sarp'),
    # URL para crear un nuevo reporte
    path('formularios_sarp/', crear_o_editar_reporte, name='crear_reporte_sarp'),
    path('reportes/editar/<str:id_vuelo>/', crear_o_editar_reporte, name='editar_reporte_sarp'),
    
    path('registrar_dron/', registrar_drones, name="registrar_dron"),
    path('reporte/<str:id_vuelo>/', obtener_reporte, name='reporte'),
    path("api/eliminar_vuelo/<str:id_vuelo>/", api_eliminar_vuelo, name="api_eliminar_vuelo"),
    path('api/estadisticas-misiones/', obtener_estadisticas_misiones, name="estadisticas-misiones"),
    path('api/ultimo_reporte/', obtener_ultimo_reporte, name="ultimo_reporte_sarp"),
    
    # Funcion de generar excel
    path('generar-excel-reportes-sarp/', generar_excel_reportes_sarp, name='generar_excel_sarp'),

]
