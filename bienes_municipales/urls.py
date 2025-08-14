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
    # Bienes Municipales
    # renderizado
    path('dashboard_bienes/', Dashboard_bienes,name='dashboard_bienes'),
    path('inventario_bienes/', Inventario_bienes,name='inventario_bienes'),
    path('registro_bienes/', Registros_bienes,name='registro_inventario'),
    # funciones crud
    path('reasignar-bien/', reasignar_bien, name='reasignar_bien'),
    path('cambiar-bien/', cambiar_estado_bienes, name='cambiar_estado_bien'),
    path('eliminar-bien/', eliminar_bien, name='eliminar_bien'),
    # APIs internas
    path('api/bienes/', listar_bienes, name='api_bienes'),
    path('api/historial-bien/<str:bien_id>/', historial_bien_api, name='historial_bien_api'),
    path('api/verificar-identificador/', verificar_identificador, name='verificar_identificador'),
    # Api Generar Excel
    path('generar-excel-bienesmunicipales/', generar_excel_bienes_municipales, name='generar_excel_bienesmunicipales'),
    # Api generar PDF
    path('generar-pdf-bienesmunicipales/', generar_pdf_qr_bienes, name='generar_pdf_bienesmunicipales'),

]
