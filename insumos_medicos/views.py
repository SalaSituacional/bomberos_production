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
    model = Inventario
    template_name = 'views/dashboard_insumos.html'
    context_object_name = 'inventarios'
    paginate_by = 1  # Muestra 5 inventarios por página


    def get_queryset(self):
        lotes_queryset = Lote.objects.order_by('insumo__nombre', 'fecha_vencimiento')
        return Inventario.objects.all().prefetch_related(Prefetch('lotes', queryset=lotes_queryset))

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