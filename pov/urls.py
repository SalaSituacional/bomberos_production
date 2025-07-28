from django.urls import path, include
from Web_App.urls import *
from .views import *

urlpatterns = [
    # POV
    path('dashboard_pov/', Dashboard_pov, name='dashboard_pov'),
]
