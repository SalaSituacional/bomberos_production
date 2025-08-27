from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, CreateView, FormView, View, TemplateView
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

class LotePrincipalCreateView(AuthRequiredMixin, TemplateView):
    """
    Vista que permite agregar múltiples lotes al inventario principal
    a través de una tabla dinámica.
    """
    template_name = 'components/forms/lote_principal_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Obtenemos todos los insumos para mostrarlos en la tabla
        context['insumos'] = Insumo.objects.all().order_by('nombre')
        return context

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                inventario_principal = Inventario.objects.get(is_principal=True)
                
                # Obtiene la descripción general del formulario
                descripcion = request.POST.get('descripcion', 'Entrada de nuevos lotes.')

                # Bandera para rastrear si se procesó algún lote
                lotes_procesados = False
                
                for key, value in request.POST.items():
                    # Solo procesamos las filas de la tabla
                    if key.startswith('insumo_'):
                        insumo_id = key.split('_')[1]
                        
                        try:
                            # Intenta obtener la cantidad y fecha de los campos correspondientes
                            cantidad = int(request.POST.get(f'cantidad_{insumo_id}'))
                            fecha_vencimiento = request.POST.get(f'fecha_vencimiento_{insumo_id}')
                            
                            if cantidad <= 0:
                                continue # Ignorar insumos con cantidad cero o negativa
                            
                            insumo = get_object_or_404(Insumo, id=insumo_id)
                            
                            # Crea el nuevo lote
                            lote = Lote.objects.create(
                                insumo=insumo,
                                cantidad=cantidad,
                                fecha_vencimiento=fecha_vencimiento,
                                inventario=inventario_principal
                            )
                            
                            # Registra el movimiento de entrada con la descripción general
                            Movimiento.objects.create(
                                insumo=insumo,
                                fecha_vencimiento_lote=lote.fecha_vencimiento,
                                tipo_movimiento='ENTRADA',
                                cantidad=cantidad,
                                inventario_origen=inventario_principal,
                                descripcion=descripcion # Usa la descripción general
                            )
                            
                            lotes_procesados = True

                        except (ValueError, TypeError):
                            messages.error(self.request, "La cantidad debe ser un número válido.")
                            return self.render_to_response(self.get_context_data())

                if lotes_procesados:
                    messages.success(self.request, "Lotes agregados con éxito.")
                else:
                    messages.warning(self.request, "No se seleccionó ningún insumo para agregar.")
                    
                return redirect(reverse_lazy('dashboard_insumos_medicos'))

        except Exception as e:
            messages.error(self.request, f"Ocurrió un error al guardar los lotes: {e}")
            return self.render_to_response(self.get_context_data())

# Vista para asignar insumos
class AsignarInsumoView(AuthRequiredMixin, TemplateView):
    """
    Vista que permite la asignación de múltiples insumos de la tabla del inventario principal
    a un inventario de destino.
    """
    template_name = 'components/forms/asignacion_inventarios.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            inventario_principal = Inventario.objects.get(is_principal=True)
            # Obtenemos solo los lotes del inventario principal con cantidad > 0
            context['lotes_origen'] = Lote.objects.filter(inventario=inventario_principal, cantidad__gt=0).order_by('insumo__nombre', 'fecha_vencimiento')
            # Obtenemos todos los inventarios de destino, excluyendo el principal
            context['inventarios_destino'] = Inventario.objects.exclude(is_principal=True)
        except Inventario.DoesNotExist:
            messages.error(self.request, "El inventario principal no se encuentra. No se puede continuar.")
        return context

    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                inventario_principal = Inventario.objects.get(is_principal=True)
                
                # Obtiene la descripción general y el inventario de destino del formulario
                descripcion = request.POST.get('descripcion_general', 'Asignación de insumos.')
                inventario_destino_id = request.POST.get('inventario_destino')
                inventario_destino = get_object_or_404(Inventario, id=inventario_destino_id)

                lotes_asignados = False

                for key, value in request.POST.items():
                    if key.startswith('asignar_lote_'):
                        lote_id = key.split('_')[2]
                        
                        try:
                            lote_origen = get_object_or_404(Lote, id=lote_id, inventario=inventario_principal)
                            cantidad_asignada = int(request.POST.get(f'cantidad_{lote_id}', 0))
                            
                            if cantidad_asignada <= 0:
                                messages.warning(self.request, f"Se ignoró la asignación de {lote_origen.insumo.nombre} porque la cantidad es cero.")
                                continue

                            if cantidad_asignada > lote_origen.cantidad:
                                messages.error(self.request, f"La cantidad a asignar de {lote_origen.insumo.nombre} ({cantidad_asignada}) es mayor que la disponible ({lote_origen.cantidad}).")
                                continue
                            
                            # Actualiza el lote de origen
                            lote_origen.cantidad -= cantidad_asignada
                            if lote_origen.cantidad <= 0:
                                lote_origen.delete()
                            else:
                                lote_origen.save()

                            # Asigna al inventario de destino
                            lote_destino, created = Lote.objects.get_or_create(
                                insumo=lote_origen.insumo,
                                fecha_vencimiento=lote_origen.fecha_vencimiento,
                                inventario=inventario_destino,
                                defaults={'cantidad': cantidad_asignada}
                            )
                            if not created:
                                lote_destino.cantidad += cantidad_asignada
                                lote_destino.save()

                            # Crea el movimiento para la trazabilidad
                            Movimiento.objects.create(
                                insumo=lote_origen.insumo,
                                fecha_vencimiento_lote=lote_origen.fecha_vencimiento,
                                tipo_movimiento='ASIGNACION',
                                cantidad=cantidad_asignada,
                                inventario_origen=inventario_principal,
                                inventario_destino=inventario_destino,
                                descripcion=descripcion
                            )
                            
                            lotes_asignados = True

                        except (Lote.DoesNotExist, ValueError):
                            messages.error(self.request, "Hubo un error al procesar uno de los lotes seleccionados.")
                            
                if lotes_asignados:
                    messages.success(self.request, "Lotes asignados con éxito.")
                else:
                    messages.warning(self.request, "No se seleccionó ningún lote para asignar.")
                
                return redirect(reverse_lazy('dashboard_insumos_medicos'))

        except Exception as e:
            messages.error(self.request, f"Ocurrió un error al asignar los insumos: {e}")
            return self.render_to_response(self.get_context_data())
        
# Inventario Dinamico
class InventarioConsumoView(AuthRequiredMixin, ListView):
    """
    Vista que muestra la tabla de inventario y procesa el consumo de múltiples insumos.
    """
    model = Lote
    template_name = 'views/inventario_dinamico.html'
    context_object_name = 'lotes'

    def post(self, request, *args, **kwargs):
        """
        Procesa el formulario de consumo de múltiples insumos.
        """
        # Obtenemos el inventario actual
        inventario_name = self.kwargs.get('inventario_name')
        try:
            inventario = Inventario.objects.get(nombre=inventario_name)
        except Inventario.DoesNotExist:
            messages.error(self.request, "El inventario especificado no existe.")
            return redirect('home_url')

        # Recorremos los datos del formulario para encontrar los insumos seleccionados
        for key, value in request.POST.items():
            if key.startswith('consumir_lote_'):
                lote_id = key.split('_')[2]
                try:
                    lote = get_object_or_404(Lote, id=lote_id)
                    cantidad = int(request.POST.get(f'cantidad_{lote_id}', 0))
                    descripcion = request.POST.get(f'descripcion_{lote_id}', '')

                    if cantidad <= 0:
                        messages.warning(self.request, f"Se ignoró el consumo para {lote.insumo.nombre} porque la cantidad es cero.")
                        continue # Continúa con el siguiente insumo

                    if lote.cantidad < cantidad:
                        messages.error(self.request, f"La cantidad a consumir de {lote.insumo.nombre} ({cantidad}) es mayor que la disponible ({lote.cantidad}).")
                        continue # Continúa con el siguiente insumo, no detiene el proceso

                    # Resta la cantidad del lote y guarda el cambio
                    lote.cantidad -= cantidad
                    lote.save()
                    
                    # Crea el movimiento de salida para la trazabilidad
                    Movimiento.objects.create(
                        insumo=lote.insumo,
                        fecha_vencimiento_lote=lote.fecha_vencimiento,
                        tipo_movimiento='SALIDA',
                        cantidad=cantidad,
                        inventario_origen=inventario,
                        descripcion=descripcion
                    )

                    messages.success(self.request, f"Consumo de {cantidad} unidades de {lote.insumo.nombre} registrado.")

                except (Lote.DoesNotExist, ValueError):
                    messages.error(self.request, "Hubo un error al procesar uno de los insumos seleccionados.")
        
        # Redirige a la misma página para mostrar los mensajes y la tabla actualizada
        return redirect(self.request.path_info)

    def get_queryset(self):
        inventario_name = self.kwargs.get('inventario_name')
        
        user_name = self.user.get('user')
        user_jerarquia = self.user.get('jerarquia')
        allowed_access = False
        
        if user_name in ['SeRvEr', 'Insumos_01', 'Sala_Situacional', 'Jefe de Inventario']:
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
            # Filtramos por cantidad > 0 para solo mostrar insumos consumibles
            return Lote.objects.filter(inventario=inventario, cantidad__gt=0).order_by('insumo__nombre', 'fecha_vencimiento')
        except Inventario.DoesNotExist:
            return Lote.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if hasattr(self, 'inventario'):
            context['inventario_name'] = self.inventario.nombre
            context['inventario_id'] = self.inventario.id
        return context

# vista formulario para registrar los insumos (medicamentos)
class InsumoCreateView(AuthRequiredMixin, CreateView):
    model = Insumo
    form_class = InsumoForm
    template_name = 'components/forms/registro_insumo.html'
    success_url = reverse_lazy('dashboard_insumos_medicos') # Cambia esto a la URL a la que quieres redirigir
    
    def form_valid(self, form):
        # Opcional: Lógica adicional antes de guardar el insumo
        # Por ejemplo, form.instance.usuario = self.request.user
        messages.success(self.request, "El insumo se ha registrado correctamente.")
        return super().form_valid(form)

# Vista Para los movimientos de los insumos

class MovimientoListView(AuthRequiredMixin, ListView):
    """
    Vista para listar todos los movimientos de insumos.
    """
    model = Movimiento
    template_name = 'views/historial_movimientos.html'
    context_object_name = 'movimientos'
    paginate_by = 25 # Muestra 25 movimientos por página, si es necesario

    def get_queryset(self):
        """
        Ordena los movimientos de forma descendente por fecha.
        """
        return Movimiento.objects.all().order_by('-fecha_movimiento')

# vista para la devolucion de insumos

class DevolucionView(AuthRequiredMixin, View):
    """
    Vista para manejar la devolución de un insumo a su inventario principal.
    """
    def post(self, request, *args, **kwargs):
        lote_id = request.POST.get('lote_id')
        cantidad = request.POST.get('cantidad')
        descripcion = request.POST.get('descripcion')
        
        try:
            # Lote original del que provienen los insumos devueltos
            lote_original = get_object_or_404(Lote, pk=lote_id)
            cantidad = int(cantidad)

            if cantidad <= 0:
                messages.error(self.request, "La cantidad a devolver debe ser mayor que cero.")
                return redirect(request.META.get('HTTP_REFERER', '/'))
            
            # 1. Validar que la cantidad a devolver no supere la cantidad consumida
            # Nota: Esto es una suposición. La cantidad consumida no está en el lote.
            # Podrías verificarlo contra el último movimiento de SALIDA si es necesario.
            # Por ahora, nos aseguramos que no sea un número negativo al restar.
            # if lote_original.cantidad < cantidad:
            #     messages.error(self.request, "La cantidad a devolver no puede ser mayor que la cantidad consumida de este lote.")
            #     return redirect(request.META.get('HTTP_REFERER', '/'))

            # 2. Restar la cantidad del lote de origen (el que se usó para el consumo)
            lote_original.cantidad -= cantidad
            lote_original.save()

            # 3. Encontrar el inventario principal usando el campo `is_principal`
            inventario_principal = get_object_or_404(Inventario, is_principal=True)

            # 4. Buscar o crear el lote para el insumo en el inventario principal
            try:
                lote_principal = Lote.objects.get(
                    insumo=lote_original.insumo,
                    inventario=inventario_principal,
                    fecha_vencimiento=lote_original.fecha_vencimiento
                )
                # Si el lote existe, le sumamos la cantidad devuelta
                lote_principal.cantidad += cantidad
                lote_principal.save()
            except Lote.DoesNotExist:
                # Si el lote no existe en el inventario principal, se crea uno nuevo
                lote_principal = Lote.objects.create(
                    insumo=lote_original.insumo,
                    inventario=inventario_principal,
                    cantidad=cantidad,
                    fecha_vencimiento=lote_original.fecha_vencimiento
                )

            # 5. Registrar el movimiento de devolución
            Movimiento.objects.create(
                insumo=lote_original.insumo,
                fecha_vencimiento_lote=lote_original.fecha_vencimiento,
                tipo_movimiento='DEVOLUCION',
                cantidad=cantidad,
                inventario_origen=lote_original.inventario, # Origen: el inventario del lote original
                inventario_destino=inventario_principal, # Destino: el inventario principal
                descripcion=descripcion
            )

            messages.success(self.request, f"Se han devuelto {cantidad} unidades de {lote_original.insumo.nombre} al '{inventario_principal.nombre}'.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        except (ValueError, TypeError):
            messages.error(self.request, "Error: La cantidad no es un número válido.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        except Lote.DoesNotExist:
            messages.error(self.request, "Error: El lote original no existe.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
        except Inventario.DoesNotExist:
            messages.error(self.request, "Error: No se encontró un inventario principal.")
            return redirect(request.META.get('HTTP_REFERER', '/'))
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
            pass 
            
    return JsonResponse({'lotes': lotes})