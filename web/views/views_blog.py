from django.shortcuts import render, redirect
from ..models import *

def inicio(request):
    return render(request, 'Blog/inicio.html')

def zoedan_tachira(request):
    return render(request, 'Blog/zoedan.html')

def captacion(request):
    return render(request, 'Blog/proceso_captacion.html')

def contacto(request):
    return render(request, 'Blog/contacto.html')

def information(request):
    return render(request, 'Blog/informacion.html') 

def blog_psicologia(request):
    return render(request, 'Blog/sections/blog_psicologia.html') 

def blog_capacitacion(request):
    return render(request, 'Blog/sections/blog_capacitacion.html') 

def blog_prevencion(request):
    return render(request, 'Blog/sections/blog_seguridadprevencion.html') 

def blog_serviciosmedicos(request):
    return render(request, 'Blog/sections/blog_serviciosmedicos.html') 

def salasituacional(request):
    return render(request, 'Blog/area/salasituacional.html') 

def drones(request):
    return render(request, 'Blog/area/drones.html') 

def glp(request):
    return render(request, 'Blog/area/glp.html') 

def operaciones_incendios(request):
    return render(request, 'Blog/area/operaciones-incendios.html') 

def brigadajuvenil(request):
    return render(request, 'Blog/area/brigada.html') 

def noticias(request):
    # Obtener todas las publicaciones, ordenadas por fecha (más recientes primero)
    posts = InstagramPost.objects.all().order_by('-fecha')

    return render(request, 'Blog/noticias.html', {'posts': posts,}) 
