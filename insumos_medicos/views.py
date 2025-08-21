from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, FormView, View
from django.db import transaction
from django.db.models import Prefetch
from django.urls import reverse_lazy
from django.contrib import messages
from .models import *
from .forms import *

# El mixin es fundamental, lo mantenemos como está
class AuthRequiredMixin(View):
    def dispatch(self, request, *args, **kwargs):
        user = request.session.get('user')
        if not user:
            return redirect('/')
        self.user = user
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.user
        context['jerarquia'] = self.user.get('jerarquia')
        context['nombres'] = self.user.get('nombres')
        context['apellidos'] = self.user.get('apellidos')
        return context

# 1. Vista principal consolidada (Dashboard)
# Muestra todos los inventarios en una sola página. La usaremos como nuestro dashboard principal.
class DashboardInventariosView(AuthRequiredMixin, ListView):
    """
    Vista principal que muestra todos los inventarios y sus lotes.
    """
    model = Inventario
    template_name = 'views/dashboard_insumos.html'
    context_object_name = 'inventarios'
    paginate_by = 1

    def get_queryset(self):
        lotes_queryset = Lote.objects.order_by('insumo__nombre', 'fecha_vencimiento')
        # Solución a la advertencia: agrega un orden a la consulta principal
        return Inventario.objects.all().prefetch_related(Prefetch('lotes', queryset=lotes_queryset)).order_by('nombre')

    def get_context_data(self, **kwargs):
        # Solución al error: llama a super() primero para obtener el contexto completo
        context = super().get_context_data(**kwargs)
        
        # Ahora el objeto paginator ya está disponible
        paginator = context['paginator']
        
        # El resto de tu lógica es correcta
        page_names = []
        for page_number in paginator.page_range:
            page_inventories = paginator.page(page_number).object_list
            if page_inventories:
                name = page_inventories[0].nombre
            else:
                name = f"Página {page_number}"
            
            page_names.append({
                'number': page_number,
                'name': name
            })
            
        context['page_names'] = page_names
        return context
   
# 2. Vista para agregar un nuevo lote al inventario principal
# Esta vista es para la entrada de insumos al sistema.
class LotePrincipalCreateView(AuthRequiredMixin, CreateView):
    model = Lote
    form_class = LoteForm
    template_name = 'components/forms/lote_principal_form.html'
    success_url = reverse_lazy('dashboard_insumos_medicos')

    def form_valid(self, form):
        try:
            with transaction.atomic():
                inventario_principal = Inventario.objects.get(is_principal=True)
                lote = form.save(commit=False)
                lote.inventario = inventario_principal
                lote.save()
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

# 3. Vista para asignar insumos
# Esta vista es para transferir insumos del inventario principal a los subinventarios.
class AsignarInsumoView(AuthRequiredMixin, FormView):
    template_name = 'components/forms/asignacion_inventarios.html'
    form_class = AsignarInsumoForm
    success_url = reverse_lazy('dashboard_insumos_medicos')

    def form_valid(self, form):
        lote_origen = form.cleaned_data['lote']
        cantidad_asignada = form.cleaned_data['cantidad']
        inventario_destino = form.cleaned_data['inventario_destino']
        try:
            with transaction.atomic():
                if cantidad_asignada > lote_origen.cantidad:
                    messages.error(self.request, "La cantidad a asignar es mayor que la cantidad disponible.")
                    return self.form_invalid(form)
                lote_origen.cantidad -= cantidad_asignada
                if lote_origen.cantidad <= 0:
                    lote_origen.delete()
                else:
                    lote_origen.save()
                lote_destino, created = Lote.objects.get_or_create(
                    insumo=lote_origen.insumo,
                    fecha_vencimiento=lote_origen.fecha_vencimiento,
                    inventario=inventario_destino,
                    defaults={'cantidad': cantidad_asignada}
                )
                if not created:
                    lote_destino.cantidad += cantidad_asignada
                    lote_destino.save()
                Movimiento.objects.create(
                    insumo=lote_origen.insumo,
                    fecha_vencimiento_lote=lote_origen.fecha_vencimiento,
                    tipo_movimiento='ASIGNACION',
                    cantidad=cantidad_asignada,
                    inventario_origen=lote_origen.inventario,
                    inventario_destino=inventario_destino,
                    descripcion=f"Asignación de {cantidad_asignada} unidades."
                )
            messages.success(self.request, "Insumos asignados con éxito.")
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"Ocurrió un error al asignar los insumos: {e}")
            return self.form_invalid(form)

# La vista InventarioBaseListView no la usaremos, ya que el dashboard centralizado la reemplaza.
# La puedes eliminar o comentar para evitar confusiones.

# Vista dinamica para sub inventarios

class InventarioConsumoView(AuthRequiredMixin, ListView):
    """
    Vista dinámica que muestra los lotes de un inventario específico.
    Solo accesible si el usuario tiene la jerarquía o el nombre de usuario correctos.
    """
    model = Lote
    template_name = 'views/inventario_dinamico.html'
    context_object_name = 'lotes'

    def get_queryset(self):
        # Obtiene el nombre del inventario de la URL
        inventario_name = self.kwargs['inventario_name']
        
        # 1. Validación de permisos
        user_name = self.user.get('user') # ¡Acceso correcto!
        user_jerarquia = self.user.get('jerarquia') # ¡Acceso correcto!
        allowed_access = False
        
        # Lógica de permisos por jerarquía (más robusta)
        if user_jerarquia == 'Jefe de Inventario':
            allowed_access = True
            
        # Lógica de permisos por nombre de usuario
        elif user_name == 'SeRvEr' or user_name == 'Insumos_01' or user_name == 'Sala_Situacional':
            allowed_access = True

        # Lógica para otros roles por nombre de usuario y nombre de inventario
        elif user_name == 'Operaciones01' and inventario_name == 'Cuartel Central':
            allowed_access = True
        elif user_name == 'Rescate03' and inventario_name == 'Estacion 01':
            allowed_access = True
        elif user_name == 'Prehospitalaria04' and inventario_name == 'Estacion 02':
            allowed_access = True
        elif user_name == 'Grumae02' and inventario_name == 'Estacion 03':
            allowed_access = True
        elif user_name == 'Enfermeria08' and inventario_name == 'Enfermeria':
            allowed_access = True
        elif user_name == 'Serviciosmedicos06' and inventario_name == 'Servicios Medicos':
            allowed_access = True
        
        if not allowed_access:
            messages.error(self.request, f"No tiene permisos para ver el inventario '{inventario_name}'.")
            return Lote.objects.none()

        # 2. Si tiene permisos, busca el inventario y retorna los lotes
        try:
            inventario = Inventario.objects.get(nombre=inventario_name)
            self.inventario = inventario
            return Lote.objects.filter(inventario=inventario).order_by('insumo__nombre', 'fecha_vencimiento')
        except Inventario.DoesNotExist:
            return Lote.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'inventario'):
            context['inventario'] = self.inventario
        return context
