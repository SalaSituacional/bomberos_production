from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, FormView, View
from django.db import transaction
from django.db.models import Prefetch
from django.urls import reverse_lazy
from django.contrib import messages
from .models import *
from .forms import *
from django.http import JsonResponse

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

class InventarioConsumoView(AuthRequiredMixin, ListView, FormView):
    """
    Vista que muestra los lotes de un inventario específico y permite
    registrar el consumo de insumos.
    """
    model = Lote
    template_name = 'views/inventario_dinamico.html'
    context_object_name = 'lotes'
    form_class = RegistroConsumoForm

    # Método para manejar solicitudes POST
    def post(self, request, *args, **kwargs):
        """
        Maneja la lógica del formulario cuando se envía una solicitud POST.
        """
        # Se asegura de definir el objeto de inventario y la lista de objetos
        self.inventario = get_object_or_404(Inventario, nombre=self.kwargs['inventario_name'])
        self.object_list = self.get_queryset() # Esto es crucial para que ListView funcione
        
        # Crear una instancia del formulario con los datos POST y pasar el inventario_id
        form = self.form_class(request.POST, inventario_id=self.inventario.id)
        
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    # El resto de los métodos de la clase...
    
    def get_queryset(self):
        inventario_name = self.kwargs['inventario_name']
        
        user_name = self.user.get('user')
        user_jerarquia = self.user.get('jerarquia')
        allowed_access = False
        
        if user_jerarquia == 'Jefe de Inventario':
            allowed_access = True
        elif user_name in ['SeRvEr', 'Insumos_01', 'Sala_Situacional']:
            allowed_access = True
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

        try:
            inventario = Inventario.objects.get(nombre=inventario_name)
            self.inventario = inventario
            return Lote.objects.filter(inventario=inventario, cantidad__gt=0).order_by('insumo__nombre', 'fecha_vencimiento')
        except Inventario.DoesNotExist:
            return Lote.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # La vista ya tiene una instancia de 'inventario', usamos eso para pasar el ID
        if hasattr(self, 'inventario'):
            context['form'] = self.form_class(inventario_id=self.inventario.id)
            context['inventario_name'] = self.inventario.nombre
            context['inventario_id'] = self.inventario.id
        else:
            context['form'] = self.form_class()
        return context
    
    def form_valid(self, form):
        lote = form.cleaned_data['lote']
        cantidad = form.cleaned_data['cantidad']
        descripcion = form.cleaned_data['descripcion']

        if lote.cantidad < cantidad:
            messages.error(self.request, f"La cantidad a consumir ({cantidad}) es mayor que la disponible en el lote ({lote.cantidad}).")
            return self.form_invalid(form)
        
        lote.cantidad -= cantidad
        lote.save()

        Movimiento.objects.create(
            insumo=lote.insumo,
            fecha_vencimiento_lote=lote.fecha_vencimiento,
            tipo_movimiento='SALIDA',
            cantidad=cantidad,
            inventario_origen=self.inventario,
            descripcion=descripcion
        )

        messages.success(self.request, f"Se han registrado {cantidad} unidades de {lote.insumo.nombre} como consumidas.")
        return redirect(self.request.path_info)

    def form_invalid(self, form):
        messages.error(self.request, "Hubo un error en el formulario. Por favor, revisa los datos ingresados.")
        print(form.errors)
        return self.render_to_response(self.get_context_data(form=form))

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if hasattr(self, 'inventario'):
            kwargs['inventario_id'] = self.inventario.id
        return kwargs

    def get_success_url(self):
        return reverse_lazy('inventario_dinamico', kwargs={'inventario_name': self.inventario.nombre})

# Funciones auxiliares para AJAX

def obtener_lotes_ajax(request):
    insumo_id = request.GET.get('insumo_id')
    inventario_id_str = request.GET.get('inventario_id')
    lotes = []

    # Validamos que los IDs no estén vacíos y sean números válidos
    if insumo_id and inventario_id_str:
        try:
            inventario_id = int(inventario_id_str)
            insumo_id = int(insumo_id)
            
            # Filtra los lotes del insumo y el inventario, con cantidad > 0
            lotes_qs = Lote.objects.filter(
                insumo_id=insumo_id, 
                inventario_id=inventario_id, 
                cantidad__gt=0
            ).order_by('fecha_vencimiento')
            
            lotes = [{'id': lote.id, 'text': str(lote)} for lote in lotes_qs]
        except (ValueError, TypeError):
            # En caso de que los valores no sean válidos, no hacemos nada y regresamos una lista vacía
            pass 
            
    return JsonResponse({'lotes': lotes})