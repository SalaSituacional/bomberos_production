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
from django.contrib import admin
from django.conf.urls import handler404
from django.urls import path, include
from web.views.views import *
from web.views.views_api import *
from web.views.views_blog import *
from web.views.views_descargas import *
from web.views.views_tables import *
from django.views.generic import TemplateView
handler404 = custom_404_view
from ven911.urls import *
from seguridad_prevencion.urls import *
from junin.urls import *
from sarp.urls import *
from mecanica.urls import *
from bienes_municipales.urls import *
from maintenance.views import maintenance_view  # Si creaste la app maintenance

#Se crean las rutas que se podran visitar en la aplicacion web.
urlpatterns = [
    # includes
    path('ven911/', include('ven911.urls')),
    path('seguridad_prevencion/', include('seguridad_prevencion.urls')),
    path('junin/', include('junin.urls')),
    path('mecanica/', include('mecanica.urls')),
    path('sarp/', include('sarp.urls')),
    path('bienesMunicipales/', include('bienes_municipales.urls')),
    path('pov/', include('pov.urls')),


    # Admin
    path('alpha04/', admin.site.urls),
    path('logout/', logout, name='logout'),

    path('maintenance/', maintenance_view, name='maintenance-page'),

    # BLOG
    path('', inicio, name="inicio"),
    path('informacion/', information,name='informacion'),
    path('salasituacional/', salasituacional,name='salasituacional'),
    path('brigadajuvenil/', brigadajuvenil,name='brigadajuvenil'),
    path('glp/', glp,name='glp'),
    path('operaciones-incendios/', operaciones_incendios,name='operaciones-inceidos'),
    path('drones/', drones,name='drones'),
    path('contacto/', contacto,name='contacto'),
    path('zoedan/', zoedan_tachira,name='zoedan_tachira'),
    path('proceso_captacion/', captacion,name='captacion'),
    path('blog_psicologia/', blog_psicologia,name='psicologia_inf'),
    path('blog_capacitacion/', blog_capacitacion,name='capacitacion_inf'),
    path('blog_prevencion/', blog_prevencion,name='prevencion_inf'),
    path('blog_serviciosmedicos/', blog_serviciosmedicos,name='serviciosmedicos_inf'),
    path('noticias/', noticias,name='noticias'),

    # SISTEMA
    path('login/', Home, name="home"),
    path('dashboard/', Dashboard,name='dashboard'),
    path('api/ultimo_procedimiento/', ultimo_procedimiento),
    path("api/ultimo_personal/", ultimo_personal, name="ultimo_personal"),
    path('api/personal_comandante/', personal_primer_comandante, name='personal_comandante'),
    path('prueba/', Prueba),
    path('registros/', ver_registros, name='registros'),
    path('antecedentes/', Antecedentes, name='antecedentes'),

    # Personal
    path('personal/', View_personal, name='personal'),
    path('personal/<int:id>/', Detalles_Personal_view, name='detalles_personal'),
    path('personal/registrar/', registrar_personal_completo, name='registrar_personal'),
    path('personal/editar/<int:personal_id>/', editar_personal, name='editar_personal'),
    
    

    # Tablas
    path('tablageneral/', tabla_general, name="tabla_general"),
    path('procedimientos/', View_Procedimiento, name='view_procedimiento'),
    path('editar_procedimientos/', View_Procedimiento_Editar, name='view_procedimiento_editar'),
    path('estadisticas/', View_Estadisticas, name='view_estadisticas'),
    path('rescate/', View_Rescate, name='view_rescate'),
    path('operaciones/', View_Operaciones, name='view_operaciones'),
    path('prevencion/', View_Prevencion, name='view_prevencion'),
    path('prehospitalaria/', View_prehospitalaria, name='view_prehospitalaria'),
    path('grumae/', View_grumae, name='view_grumae'),
    path('capacitacion/', View_capacitacion, name='view_capacitacion'),
    path('enfermeria/', View_enfermeria, name='view_enfermeria'),
    path('serviciosmedicos/', View_serviciosmedicos, name='view_serviciosmedicos'),
    path('psicologia/', View_psicologia, name='view_psicologia'),

    # APIs
    path('api/procedimientos/<int:id>/', obtener_procedimiento, name='obtener_procedimiento'),
    path('api/meses/', obtener_meses, name='obtener_meses'),
    path('api/porcentajes/<str:periodo>/', obtener_porcentajes, name='api_porcentajes'),
    path('api/parroquias/', obtener_procedimientos_parroquias, name='obtener_parroquias'),
    path('api/divisiones/', obtener_divisiones, name='obtener_divisiones'),
    path('api/divisiones_estadisticas/', obtener_divisiones_estadistica, name='obtener_divisiones_estadistica'),
    path('api/generar_estadistica/', generar_resultados, name='generar_estadistica'),
    path('api/procedimientos_division/', api_procedimientos_division, name='procedimientos_division'),
    path('api/procedimientos_division_parroquia/', api_procedimientos_division_parroquias, name='procedimientos_division_parroquia'),
    path('api/procedimientos_tipo/', api_procedimientos_tipo, name='procedimientos_tipo'),
    path('api/procedimientos_tipo_horizontal/', api_procedimientos_bar_horizontales, name='procedimientos_tipo_horizontal'),
    path('api/procedimientos_tipo_parroquias/', api_procedimientos_tipo_parroquias, name='procedimientos_tipo_parroquias'),
    path('get_persona/<int:id>/', get_persona, name='get_persona'),
    path('editar_personal/', edit_personal, name='edit_personal'),
    path('api/procedimientos_tipo_detalles/', api_procedimientos_tipo_detalles, name='procedimientos_tipo_detalles'),
    path('instagram/', instagram_feed, name='instagram_feed'),
    path('api/obtener_informacion/<int:id>/', obtener_informacion_editar, name='obtener_informacion'),
    path('api/obtener_unidades/', api_unidades, name='obtener_unidades'),
    path('api/obtener_tipos_procedimientos/', api_tipos_procedimientos, name='obtener_tipos_procedimientos'),
    path('api/obtener_solicitante/', api_solicitantes, name='obtener_solicitante'),

    path('api/weather-proxy/', get_weather_data, name='weather_proxy'),

    # Descargas
    path('descargar-excel_personal/', generar_excel_personal, name='descargar_excel_personal'),
    path('descargar-base-datos/', descargar_base_datos, name='descargar_base_datos'),

    # divisiones exportacion excel
    path('descargar-excel-capacitacion/', generar_excel_capacitacion, name='descargar_excel_capacitacion'),
    path('descargar-excel-psicologia/', generar_excel_psicologia, name='descargar_excel_psicologia'),
    path('descargar-excel-operaciones/', generar_excel_operaciones, name='descargar_excel_operaciones'),
    path('descargar-excel-grumae/', generar_excel_grumae, name='descargar_excel_grumae'),
    path('descargar-excel-prehospitalaria/', generar_excel_prehospitalaria, name='descargar_excel_prehospitalaria'),
    path('descargar-excel-serviciosmedicos/', generar_excel_serviciosmedicos, name='descargar_excel_serviciosmedicos'),
    path('descargar-excel-rescate/', generar_excel_rescate, name='descargar_excel_rescate'),
    path('descargar-excel-prevencion/', generar_excel_prevencion, name='descargar_excel_prevencion'),
    path('descargar-excel-enfermeria/', generar_excel_enfermeria, name='descargar_excel_enfermeria'),
    path('descargar-excel-operacional/', generar_excel_operacional, name='descargar_excel_operacional'),
]
