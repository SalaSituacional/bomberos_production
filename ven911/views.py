from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db.models import Case, When
from django.http import JsonResponse
from datetime import datetime
from datetime import timedelta
from django.db.models import Max
from django.db.models import Count
from django.utils.timezone import localdate
from django.forms.models import model_to_dict
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from .urls import *
from .forms import *


# Create your views here.


@login_required
def ven911(request):
    user = request.session.get('user')
    if not user:
        return redirect('/')
    # Renderizar la página con los datos
    return render(request, "Dashboard_ven911.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
    })
@login_required
def form_services(request):
    form_services = ServicioForm()
    user = request.session.get('user')
    if not user:
        return redirect('/')
    # Renderizar la página con los datos
    return render(request, "formulario_servicios.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "formulario_servicios": form_services,
    })
