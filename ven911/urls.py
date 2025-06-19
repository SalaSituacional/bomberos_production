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
    # vistas
    path('home/', ven911, name='home_911'),
    path('table_911/', view_table_911, name='table_911'),
    
    # formulario con vistas
    path('servicios_form/', form_services, name='form_services'),

    # apis envio de datos al frontend
    path('api/servicios_ven911/', obtener_servicios_json, name='obtener_servicios_json'),
    
    # api para eliminar
    path('servicios-eliminar/<int:id>/',eliminar_servicio, name='eliminar_servicio'),

    # api para total de servicios
    path('total_servicios/', api_conteo_servicios, name='obtener_total_servicios'),
    
    # api para la grafica por mes
    path('servicios_grafica/', api_servicios_grafico_mes, name='obtener_servicios_grafica'),
    # api para la grafica por dia
    path('servicios_grafica_dia/', api_servicios_grafico_dia, name='obtener_servicios_grafica_dia'),
    # api para la grafica por year
    path('servicios_grafica_year/', api_servicios_grafico_year, name='api_servicios_grafico_year'),


    # api para exportar excel
    path('exportar-servicios-excel/', exportar_servicios_excel, name='exportar_servicios_excel'),

]
