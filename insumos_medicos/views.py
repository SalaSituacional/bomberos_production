from django.shortcuts import render
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView
from django.db import transaction
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.db.models import Sum
from django.views import View
from .models import *
from .forms import *

# mixin de usuario
class AuthRequiredMixin(View):
    """
    Mixin para asegurar que un usuario esté autenticado.
    Redirige al login si la sesión no contiene un 'user'.
    """
    def dispatch(self, request, *args, **kwargs):
        user = request.session.get('user')
        if not user:
            return redirect('/')  # Redirige a la página de login si no hay usuario en sesión
        
        # Pasa la información del usuario a la vista
        self.user = user
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añade los datos del usuario al contexto de la plantilla
        context['user'] = self.user
        context['jerarquia'] = self.user.get('jerarquia')
        context['nombres'] = self.user.get('nombres')
        context['apellidos'] = self.user.get('apellidos')
        return context


# Renderizacion de Vistas (Paginas)
    
def cuartel_central(request):
    user = request.session.get('user')
    if not user:
            return redirect('/')

    return render(request, "views/insumos_cuartel.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
    })

def estacion_1(request):
    user = request.session.get('user')
    if not user:
            return redirect('/')

    return render(request, "views/insumos_estacion_1.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
    })

def estacion_2(request):
    user = request.session.get('user')
    if not user:
            return redirect('/')

    return render(request, "views/insumos_estacion_2.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
    })

def estacion_3(request):
    user = request.session.get('user')
    if not user:
            return redirect('/')

    return render(request, "views/insumos_estacion_3.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
    })

def enfermeria(request):
    user = request.session.get('user')
    if not user:
            return redirect('/')

    return render(request, "views/insumos_enfermeria.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
    })
    
def servicios_medicos(request):
    user = request.session.get('user')
    if not user:
            return redirect('/')

    return render(request, "views/insumos_serviciosmedicos.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
    })
    
# CBVs (Componentes)
class InventarioPrincipalListView(AuthRequiredMixin,ListView):
    model = Lote
    template_name = 'views/dashboard.html'
    context_object_name = 'lotes'

    def get_queryset(self):
        # Usamos .filter() en lugar de .get() y .first() para evitar el error
        inventario_principal = Inventario.objects.filter(is_principal=True).first()
        
        if inventario_principal:
            return Lote.objects.filter(
                inventario=inventario_principal
            ).order_by('insumo__nombre', 'fecha_vencimiento')
        
        # Si no se encuentra un inventario principal, devolvemos un queryset vacío
        return Lote.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Aquí también usamos .filter().first() para ser más robustos
        context['inventario_principal'] = Inventario.objects.filter(is_principal=True).first()
        return context

class LotePrincipalCreateView(AuthRequiredMixin,CreateView):
    """
    Vista para agregar un nuevo lote de insumos al inventario principal.
    """
    model = Lote
    form_class = LoteForm  # Usa el formulario que definimos en forms.py
    template_name = 'components/forms/lote_principal_form.html'
    success_url = reverse_lazy('dashboard_insumos_medicos')

    def form_valid(self, form):
        try:
            with transaction.atomic():
                inventario_principal = Inventario.objects.get(is_principal=True)
                
                # Guarda el lote normalmente
                lote = form.save(commit=False)
                lote.inventario = inventario_principal
                lote.save()
                
                # Crea el registro de movimiento usando los datos del lote
                Movimiento.objects.create(
                    insumo=lote.insumo,
                    fecha_vencimiento_lote=lote.fecha_vencimiento,
                    tipo_movimiento='ENTRADA',
                    cantidad=lote.cantidad,
                    inventario_origen=inventario_principal,
                    descripcion="Entrada de nuevo lote al inventario principal."
                )
                
                messages.success(self.request, "Lote agregado con éxito.")
                return super().form_valid(form)

        except Exception as e:
            messages.error(self.request, f"Ocurrió un error al guardar el lote: {e}")
            return self.form_invalid(form)