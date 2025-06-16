from django.shortcuts import render
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db.models import Case, When
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Max
from django.db.models import Count
from django.utils.timezone import localdate
from django.forms.models import model_to_dict
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Q, Sum
from datetime import time
from .urls import *
from django.db.models import Prefetch
from openpyxl import Workbook
import json
from openpyxl.styles import Font, Alignment
from datetime import timedelta # Importa timedelta para operaciones de fecha


# Vista del dashboard Ven911
@login_required
def comandancia_junin(request):
    user = request.session.get('user')
    if not user:
        return redirect('/')
    # Renderizar la página con los datos
    return render(request, "Dashboard_junin.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
    })