import io
import instaloader
from django.shortcuts import render, redirect
from django.http import HttpResponse
from ..models import Usuarios, Divisiones, Procedimientos
from django.contrib import messages
from ..forms import *
from ..models import *
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.cache import never_cache
from django.db.models import Case, When
from datetime import timezone as dt_timezone
from django.http import JsonResponse
from datetime import datetime
from datetime import timedelta
from django.utils.timezone import make_aware
from django.db.models import Prefetch
from datetime import date
from django.shortcuts import get_object_or_404
import fitz
from django.db.models import Max
from django.db.models import Count
from django.utils.timezone import localdate
from django.forms.models import model_to_dict
from django.views.decorators.http import require_http_methods
from django.db.models import Q


# Vista Personalizada para el error 404
def custom_404_view(request, exception):
    return render(request, "404.html", status=404)


# Login required
def login_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if 'user' not in request.session:
            return redirect('/login/')  # Redirigir a la página de inicio de sesión
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# Cierrre de sesion
def logout(request):
    request.session.flush()  # Eliminar todos los datos de la sesión
    return redirect('/login/')

def get_instagram_post_date(url):
    L = instaloader.Instaloader()

    # Extraer el shortcode de la URL
    shortcode = url.split("/p/")[-1].split("/")[0]

    try:
        # Obtener la publicación usando el shortcode
        post = instaloader.Post.from_shortcode(L.context, shortcode)
        naive_datetime = post.date_utc  # Asumiendo que `post.date_utc` es el valor sin zona horaria
        # Convertir la fecha sin zona horaria a UTC
        fecha_publicacion = timezone.make_aware(naive_datetime, dt_timezone.utc)
        return fecha_publicacion
    except Exception as e:
        print(f"Error al obtener la publicación: {e}")
        return None

def instagram_feed(request):
    user = request.session.get('user')
    if not user:
        return redirect('/')

    success = False  # Variable para indicar si se ha agregado correctamente

    if request.method == 'POST':
        url = request.POST.get('url')
        if url:
            fecha_publicacion = get_instagram_post_date(url)
            if fecha_publicacion:
                InstagramPost.objects.create(url=url, fecha=fecha_publicacion)
                success = True  # Ahora success indica éxito sin redireccionar

    posts = InstagramPost.objects.all().order_by('-fecha')

    return render(request, 'instagram_feed.html', {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        'posts': posts,
        'success': success,  # Asegurarse de que success esté en el contexto
    })

# Vista de la Ventana Inicial (Login)
@never_cache
def Home(request):
    if request.method == "GET":
        return render(request, "index.html")
    else:
        usuario = request.POST["user"]
        contrasena = request.POST["password"]
        try:
            user = Usuarios.objects.get(user=usuario, password=contrasena)
            encargado = user.encargado  # Obtener el encargado relacionado
            # Guardar datos en la sesión
            request.session['user'] = {
                "user": user.user,
                "jerarquia": encargado.jerarquia,
                "nombres": encargado.nombres,
                "apellidos": encargado.apellidos,
            }
            if user.user == "Mecanica_01":
                return redirect("/mecanica/dashboard_mecanica/")
            elif user.user == "Sarp_01":
                return redirect("/sarp/dashboard_sarp/")
            elif user.user == "Bienes_00":
                return redirect("/bienes_municipales/dashboard_bienes/")
            elif user.user == "Ven_911":
                return redirect("/ven911/home/")
            elif user.user == "ComandanciaJunin":
                return redirect("/junin/DashboardJunin/")
            else:
                return redirect("/dashboard/")
        except Usuarios.DoesNotExist:
            messages.error(request, 'Usuario o contraseña incorrectos')
            return render(request, 'index.html', {'error': True})

@login_required
def View_personal(request):
    # Obtener el usuario de la sesión
    user = request.session.get('user')

    buscar_jerarquia = request.GET.get('filterJerarquia', '')
    buscar_status = request.GET.get('filterStatus', '')

    # Verificar si el usuario está en la sesión
    if not user:
        return redirect('/')

    # Base queryset
    personal_queryset = Personal.objects.exclude(id__in=[0, 4])

    # Aplicar filtros directamente al queryset
    if buscar_jerarquia:
        personal_queryset = personal_queryset.filter(jerarquia__icontains=buscar_jerarquia)
    if buscar_status:
        personal_queryset = personal_queryset.filter(status=buscar_status)

    conteo = personal_queryset.count()

    # Lista de jerarquías en el orden deseado
    jerarquias = [
        "General", "Coronel", "Teniente Coronel", "Mayor", "Capitán", "Primer Teniente", 
        "Teniente", "Sargento Mayor", "Sargento Primero", "Sargento segundo", 
        "Cabo Primero", "Cabo Segundo", "Distinguido", "Bombero"
    ]

    # Crear un mapa de jerarquía a índice para facilitar la ordenación
    jerarquia_orden = {nombre: index for index, nombre in enumerate(jerarquias)}

    # Crear la lista para los datos del personal (solo después de filtrar)
    personal_data = []
    
    # Iterar sobre las instancias de Personal para formar el diccionario de datos
    for persona in personal_queryset:

        personal_data.append({
            "id": persona.id,
            'nombres': persona.nombres,
            'apellidos': persona.apellidos,
            'jerarquia': persona.jerarquia,
            'cargo': persona.cargo,
            'cedula': persona.cedula,
            'sexo': persona.sexo,
            'rol': persona.rol,
            'status': persona.status
        })

    # Ordenar la lista personal_data por jerarquía
    personal_ordenado = sorted(
        personal_data, 
        key=lambda x: jerarquia_orden.get(x["jerarquia"], float("inf"))
    )

    return render(request, "personal.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "personal": personal_ordenado,
        "conteo": conteo,
        "filterJerarquia": buscar_jerarquia,  # Para mantener el filtro en el template
        "filterStatus": buscar_status        # Para mantener el filtro en el template
    })


def Detalles_Personal_view(request, id):
    # Obtener el usuario de la sesión
    user = request.session.get('user')
    if not user:
        return redirect('/')

    persona = get_object_or_404(Personal, pk=id)

    # Procesar el formulario de ascenso si es POST
    if request.method == 'POST':
        form = AscensoForm(request.POST)
        if form.is_valid():
            ascenso = form.save(commit=False)
            ascenso.personal = persona
            ascenso.save()
            return redirect('detalles_personal', id=id)
    else:
        form = AscensoForm()

    # Obtener el personal y sus relaciones
    try:
        persona = Personal.objects.prefetch_related(
            Prefetch('detalles_personal_set', to_attr='detalles'),
            Prefetch('ascensos_set', to_attr='lista_ascensos'),
            Prefetch('familiares_set', to_attr='lista_familiares')
        ).get(pk=id)

        # Función para calcular edad
        def calcular_edad(fecha_nacimiento):
            if fecha_nacimiento:
                today = date.today()
                return today.year - fecha_nacimiento.year - ((today.month, today.day) < (fecha_nacimiento.month, fecha_nacimiento.day))
            return None

        # Procesar familiares con edad calculada
        familiares_con_edad = []
        for familiar in persona.lista_familiares:
            familiares_con_edad.append({
                'id': familiar.id,
                'nombres': familiar.nombres,
                'apellidos': familiar.apellidos,
                'parentesco': familiar.parentesco,
                'fecha_nacimiento': familiar.fecha_nacimiento,
                'edad': calcular_edad(familiar.fecha_nacimiento),
                'cedula': familiar.cedula,
                'partida_nacimiento': familiar.partida_nacimiento
            })

        # Estructurar los datos
        detalles = {
            "personal": persona,
            "detalles": persona.detalles[0] if persona.detalles else None,
            "ascensos": persona.lista_ascensos,
            "familiares": familiares_con_edad,  # Lista de familiares con edad calculada
            "form_ascenso": form
        }

    except Personal.DoesNotExist:
        detalles = None

    return render(request, "personal/detalles_personal.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "detalles": detalles,
        "edad_personal": calcular_edad(detalles["detalles"].fecha_nacimiento) if detalles and detalles["detalles"] else None,
        "años_servicio": calcular_edad(detalles["detalles"].fecha_ingreso) if detalles and detalles["detalles"] else None,
        "nacionalidad": detalles["personal"].cedula[0] if detalles and detalles["personal"].cedula else None,
    })


def registrar_personal_completo(request):
    # Obtener el usuario de la sesión
    user = request.session.get('user')
    if not user:
        return redirect('/')
    
    FamiliaresFormSet = inlineformset_factory(
        Personal,
        Familiares,
        form=FamiliaresForm,
        extra=1,
        can_delete=False,
        fields=('nombres', 'apellidos', 'parentesco', 'fecha_nacimiento', 'cedula', 'partida_nacimiento')
    )

    if request.method == 'POST':
        personal_form = PersonalForm(request.POST)
        formset_detalles = DetallesPersonalForm(request.POST)
        formset_familiares = FamiliaresFormSet(request.POST, prefix='familiares')

        if all([
            personal_form.is_valid(),
            formset_detalles.is_valid(),
            formset_familiares.is_valid()
        ]):
            # Guardar el personal primero
            personal_instance = personal_form.save()

            # Guardar los detalles del personal
            detalles_instances = formset_detalles.save(commit=False)
            detalles_instances.personal = personal_instance
            detalles_instances.save()

            # Guardar los familiares
            familiares_instances = formset_familiares.save(commit=False)
            for familiar in familiares_instances:
                familiar.personal = personal_instance
                familiar.save()

            # Eliminar los familiares marcados para borrar
            for obj in formset_familiares.deleted_objects:
                obj.delete()

            messages.success(request, 'Personal registrado exitosamente!')
            return redirect('personal')

        else:
            # Si hay errores, mostrarlos
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        # Método GET - mostrar formularios vacíos
        personal_form = PersonalForm()
        formset_detalles = DetallesPersonalForm()
        formset_familiares = FamiliaresFormSet(prefix='familiares')

    context = {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        'personal_form': personal_form,
        'form': formset_detalles,
        'formset_familiares': formset_familiares,
    }
    return render(request, 'personal/personal_form.html', context)
    

def editar_personal(request, personal_id):
    # Obtener el usuario de la sesión
    user = request.session.get('user')
    if not user:
        return redirect('/')
    
    # Obtener la instancia de Personal a editar
    personal_instance = get_object_or_404(Personal, id=personal_id)
    
    # Obtener o crear la instancia de Detalles_Personal
    detalles_instance, created = Detalles_Personal.objects.get_or_create(personal=personal_instance)
    
    # Configurar el formset para familiares
    FamiliaresFormSet = inlineformset_factory(
        Personal,
        Familiares,
        form=FamiliaresForm,
        extra=1,
        can_delete=True,
        fields=('nombres', 'apellidos', 'parentesco', 'fecha_nacimiento', 'cedula', 'partida_nacimiento')
    )

    if request.method == 'POST':
        personal_form = PersonalForm(request.POST, instance=personal_instance)
        detalles_form = DetallesPersonalForm(request.POST, instance=detalles_instance)
        formset_familiares = FamiliaresFormSet(request.POST, instance=personal_instance, prefix='familiares')

        if all([
            personal_form.is_valid(),
            detalles_form.is_valid(),
            formset_familiares.is_valid()
        ]):
            # Guardar el personal
            personal_instance = personal_form.save()

            # Guardar los detalles del personal
            detalles = detalles_form.save(commit=False)
            detalles.personal = personal_instance
            detalles.save()

            # Guardar los familiares
            familiares_instances = formset_familiares.save(commit=False)
            for familiar in familiares_instances:
                # Solo asignar personal si es un nuevo registro (sin id)
                if not familiar.id:
                    familiar.personal = personal_instance
                familiar.save()

            # Eliminar los familiares marcados para borrar
            for obj in formset_familiares.deleted_objects:
                obj.delete()

            messages.success(request, 'Información del personal actualizada exitosamente!')
            return redirect('personal')

        else:
            # Mostrar errores detallados
            for form in formset_familiares:
                if form.errors:
                    print(f"Errores en formulario {form.prefix}: {form.errors}")
            messages.error(request, 'Por favor corrija los errores en el formulario.')
    else:
        # Método GET - mostrar formularios con datos existentes
        personal_form = PersonalForm(instance=personal_instance)
        detalles_form = DetallesPersonalForm(instance=detalles_instance)
        formset_familiares = FamiliaresFormSet(instance=personal_instance, prefix='familiares')

    context = {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        'personal_form': personal_form,
        'form': detalles_form,  # Cambiado de 'form' a 'detalles_form' para mayor claridad
        'formset_familiares': formset_familiares,
        'editing': True,
        'personal_id': personal_id,
    }
    return render(request, 'personal/personal_form.html', context)


@login_required
def Dashboard(request):
    user = request.session.get('user')

    if not user:
        return redirect('/')

    # Renderizar la página con los datos
    return render(request, "dashboard.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
    })


@login_required
# Vista de archivo para hacer pruebas de backend
def Prueba(request):

    if request.method == 'POST':
        form = Selecc_Tipo_Procedimiento(request.POST)
        if form.is_valid():
            usuarios = Usuarios.objects.all()
            divisiones = Divisiones.objects.all()
            procedimientos = Procedimientos.objects.all()

            valor_seleccionado = form.cleaned_data['tipo_procedimiento']
            # Aquí puedes hacer algo con el valor seleccionado
            return render(request, "prueba.html", {
            "usuarios": usuarios,
            "divisiones": divisiones,
            "procedimientos": procedimientos,
            "form": Formulario_Incendio(),
            })
    else:
        form = Selecc_Tipo_Procedimiento(),

        usuarios = Usuarios.objects.all()
        divisiones = Divisiones.objects.all()
        procedimientos = Procedimientos.objects.all()

        return render(request, "prueba.html", {
            "usuarios": usuarios,
            "divisiones": divisiones,
            "procedimientos": procedimientos,
            "form": Formulario_Traslado_Accidente(),
            })

def View_Procedimiento(request):
    user = request.session.get('user')
    if not user:
        return redirect('/')

    # Map of users to their corresponding division values
    user_divisions = {
        "Operaciones01": "2",
        "Rescate03": "1",
        "Grumae02": "4",
        "Prevencion05": "3",
        "Prehospitalaria04": "5",
        "Serviciosmedicos06": "7",
        "Capacitacion07": "9",
        "Enfermeria08": "6",
        "Psicologia09": "8"
    }

    # Get the initial value for the form
    initial_division = user_divisions.get(user.get('user')) if user else None

    result = None

    if request.method == 'POST':
        form = SelectorDivision(request.POST, prefix='form1', initial_division=initial_division)
        form2 = SeleccionarInfo(request.POST, prefix='form2')
        form3 = Datos_Ubicacion(request.POST, prefix='form3')
        form4 = Selecc_Tipo_Procedimiento(request.POST, prefix='form4')
        abast_agua = formulario_abastecimiento_agua(request.POST, prefix='abast_agua')
        apoyo_unid = Formulario_apoyo_unidades(request.POST, prefix='apoyo_unid')
        guard_prev = Formulario_guardia_prevencion(request.POST, prefix='guard_prev')
        atend_no_efec = Formulario_atendido_no_efectuado(request.POST, prefix='atend_no_efec')
        desp_seguridad = Formulario_despliegue_seguridad(request.POST, prefix='desp_seguridad')
        fals_alarm = Formulario_falsa_alarma(request.POST, prefix='fals_alarm')
        serv_especial = Formulario_Servicios_Especiales(request.POST, prefix='serv_especial')
        form_fallecido = Formulario_Fallecidos(request.POST, prefix='form_fallecido')
        rescate_form = Formulario_Rescate(request.POST, prefix='rescate_form')
        incendio_form = Formulario_Incendio(request.POST, prefix='incendio_form')
        retencion_preventiva_incendio = Formulario_Retencion_Preventiva_Incendio(request.POST, prefix='retencion_preventiva_incendio')
        atenciones_paramedicas = Formulario_Atenciones_Paramedicas(request.POST, prefix='atenciones_paramedicas')

        emergencias_medicas = Formulario_Emergencias_Medicas(request.POST, prefix='emergencias_medicas')
        traslados_emergencias = Formulario_Traslados(request.POST, prefix='traslados_emergencias')

        persona_presente_form = Formulario_Persona_Presente(request.POST, prefix='persona_presente_form')
        detalles_vehiculo_form = Formulario_Detalles_Vehiculos(request.POST, prefix='detalles_vehiculo_form')

        formulario_accidentes_transito = Formulario_Accidentes_Transito(request.POST, prefix='formulario_accidentes_transito')
        detalles_lesionados_accidentes = Formulario_Detalles_Lesionados(request.POST, prefix='detalles_lesionados_accidentes')
        detalles_lesionados_accidentes2 = Formulario_Detalles_Lesionados2(request.POST, prefix='detalles_lesionados_accidentes2')
        detalles_lesionados_accidentes3 = Formulario_Detalles_Lesionados3(request.POST, prefix='detalles_lesionados_accidentes3')
        traslados_accidentes = Formulario_Traslado_Accidente(request.POST, prefix='traslados_accidentes')
        traslados_accidentes2 = Formulario_Traslado_Accidente2(request.POST, prefix='traslados_accidentes2')
        traslados_accidentes3 = Formulario_Traslado_Accidente3(request.POST, prefix='traslados_accidentes3')
        detalles_vehiculo_accidentes = Formulario_Detalles_Vehiculos(request.POST, prefix='detalles_vehiculos_accidentes')
        detalles_vehiculo_accidentes2 = Formulario_Detalles_Vehiculos2(request.POST, prefix='detalles_vehiculos_accidentes2')
        detalles_vehiculo_accidentes3 = Formulario_Detalles_Vehiculos3(request.POST, prefix='detalles_vehiculos_accidentes3')

        rescate_form_persona = Formulario_Rescate_Persona(request.POST, prefix='rescate_form_persona')
        rescate_form_animal = Formulario_Rescate_Animal(request.POST, prefix='rescate_form_animal')

        evaluacion_riesgo_form = Forulario_Evaluacion_Riesgo(request.POST, prefix='evaluacion_riesgo_form')
        mitigacion_riesgo_form = Formulario_Mitigacion_Riesgos(request.POST, prefix='mitigacion_riesgo_form')
        vehiculo_derrame_form = Detalles_Vehiculo_Derrame_Form(request.POST, prefix='vehiculo_derrame_form')
        vehiculo_derrame_form2 = Detalles_Vehiculo_Derrame_Form2(request.POST, prefix='vehiculo_derrame_form2')
        vehiculo_derrame_form3 = Detalles_Vehiculo_Derrame_Form3(request.POST, prefix='vehiculo_derrame_form3')

        puesto_avanzada_form = Formulario_Puesto_Avanzada(request.POST, prefix='puesto_avanzada_form')
        traslados_prehospitalaria_form = Formulario_Traslados_Prehospitalaria(request.POST, prefix='traslados_prehospitalaria_form')
        asesoramiento_form = Formulario_Asesoramiento(request.POST, prefix='asesoramiento_form')
        persona_presente_eval_form = Formularia_Persona_Presente_Eval(request.POST, prefix='persona_presente_eval_form')
        reinspeccion_prevencion = Formulario_Reinspeccion_Prevencion(request.POST, prefix='reinspeccion_prevencion')
        retencion_preventiva = Formulario_Retencion_Preventiva(request.POST, prefix='retencion_preventiva')

        artificios_pirotecnico = Formulario_Artificios_Pirotecnicos(request.POST, prefix='artificios_pirotecnico')
        lesionados = Formulario_Lesionado(request.POST, prefix='lesionados')
        incendio_art = Formulario_Incendio_Art(request.POST, prefix='incendio_art')
        persona_presente_art = Formulario_Persona_Presente_Art(request.POST, prefix='persona_presente_art')
        detalles_vehiculo_art = Formulario_Detalles_Vehiculos_Incendio_Art(request.POST, prefix='detalles_vehiculo_art')
        fallecidos_art = Formulario_Fallecidos_Art(request.POST, prefix='fallecidos_art')
        inspeccion_artificios_pir = Formulario_Inspeccion_Establecimiento_Art(request.POST, prefix='inspeccion_artificios_pir')
        form_enfermeria = Formulario_Enfermeria(request.POST, prefix='form_enfermeria')
        servicios_medicos = Formulario_Servicios_medicos(request.POST, prefix='form_servicios_medicos')
        psicologia = Formulario_psicologia(request.POST,prefix='form_psicologia')
        capacitacion = Formulario_capacitacion(request.POST,prefix='form_capacitacion')
        form_valoracion_medica = Formulario_Valoracion_Medica(request.POST, prefix='form_valoracion_medica')
        form_detalles_enfermeria = Formulario_Detalles_Enfermeria(request.POST, prefix='form_detalles_enfermeria')
        form_detalles_psicologia = Formulario_Procedimientos_Psicologia(request.POST, prefix='form_detalles_psicologia')
        
        form_capacitacion = Formulario_Capacitacion_Proc(request.POST,prefix='form_capacitacion')
        form_brigada = Formulario_Brigada(request.POST,prefix='form_brigada')
        form_frente_preventivo = Formulario_Frente_Preventivo(request.POST,prefix='form_frente_preventivo')
        form_jornada_medica = Formulario_Jornada_Medica(request.POST, prefix='form_jornada_medica')

        form_inspecciones = Formulario_Inspecciones(request.POST, prefix='form_inspecciones')
        form_inspecciones_prevencion = Formulario_Inspeccion_Prevencion_Asesorias_Tecnicas(request.POST, prefix='form_inspecciones_prevencion')
        form_inspecciones_habitabilidad = Formulario_Inspeccion_Habitabilidad(request.POST, prefix='form_inspecciones_habitabilidad')
        form_inspecciones_arbol = Formulario_Inspeccion_Arbol(request.POST, prefix='form_inspecciones_arbol')
        form_inspecciones_otros = Formulario_Inspeccion_Otros(request.POST, prefix='form_inspecciones_otros')

        form_investigacion = Formulario_Investigacion(request.POST, prefix='form_investigacion')
        form_inv_vehiculo = Formulario_Investigacion_Vehiculo(request.POST, prefix='form_inv_vehiculo')
        form_inv_comercio = Formulario_Investigacion_Comercio(request.POST, prefix='form_inv_comercio')
        form_inv_estructura = Formulario_Investigacion_Estructura_Vivienda(request.POST, prefix='form_inv_estructura')
        
        form_comision = Datos_Comision(request.POST, prefix='form_comision')
        datos_comision_uno = Comision_Uno(request.POST, prefix='datos_comision_uno')
        datos_comision_dos = Comision_Dos(request.POST, prefix='datos_comision_dos')
        datos_comision_tres = Comision_Tres(request.POST, prefix='datos_comision_tres')
        
        # Imprimir request.POST para depuración
        if not form.is_valid():
            print("Errores en form1:", form.errors)
            result = True
        if not form2.is_valid():
            print("Errores en form2:", form2.errors)
            result = True
        if not form3.is_valid():
            print("Errores en form3:", form3.errors)
            result = True
        if not form4.is_valid():
            print("Errores en form4:", form4.errors)
            result = True

        if form.is_valid():
            result = False

            division = form.cleaned_data["opciones"]
            tipo_procedimiento = ""

            if (division == "1" or division == "2" or division == "3" or division == "4" or division == "5") and (form2.is_valid() and form3.is_valid() and form4.is_valid() and form_comision.is_valid() and datos_comision_uno.is_valid() and datos_comision_dos.is_valid() and datos_comision_tres.is_valid()):
                solicitante = form2.cleaned_data["solicitante"]
                solicitante_externo = form2.cleaned_data["solicitante_externo"]
                unidad = form2.cleaned_data["unidad"]
                efectivos_enviados = form2.cleaned_data["efectivos_enviados"]
                jefe_comision = form2.cleaned_data["jefe_comision"]
                municipio = form3.cleaned_data["municipio"]
                direccion = form3.cleaned_data["direccion"]
                fecha = form3.cleaned_data["fecha"]
                hora = form3.cleaned_data["hora"]
                tipo_procedimiento = form4.cleaned_data["tipo_procedimiento"]
                parroquia = form3.cleaned_data["parroquia"]

                division_instance = Divisiones.objects.get(id=division)
                jefe_comision_instance = Personal.objects.get(id=jefe_comision)
                municipio_instance = Municipios.objects.get(id=municipio)
                tipo_procedimiento_instance = Tipos_Procedimientos.objects.get(id=tipo_procedimiento)
                unidad_instance = Unidades.objects.get(id=unidad)

                if solicitante:
                    solicitante_instance = Personal.objects.get(id=solicitante)


                if solicitante_externo=="":
                    solicitante_externo = ""                    

                # # Crear una nueva instancia del modelo Procedimientos
                nuevo_procedimiento = Procedimientos(
                    id_division=division_instance,
                    id_solicitante=solicitante_instance,
                    solicitante_externo=solicitante_externo,
                    unidad=unidad_instance,
                    efectivos_enviados=efectivos_enviados,
                    id_jefe_comision=jefe_comision_instance,
                    id_municipio=municipio_instance,
                    direccion=direccion,
                    fecha=fecha,
                    hora=hora,
                    id_tipo_procedimiento=tipo_procedimiento_instance
                )

                # # Solo asignar parroquia si está presente
                if parroquia:
                    parroquia_instance = Parroquias.objects.get(id=parroquia)
                    nuevo_procedimiento.id_parroquia = parroquia_instance

                nuevo_procedimiento.save()

                if form_comision.cleaned_data["agregar"] == True:
                    cedula = datos_comision_uno.cleaned_data["cedula_oficial"] 
                    nacionalidad = datos_comision_uno.cleaned_data["nacionalidad"]


                    nueva_comsion = Comisiones(
                        procedimiento = nuevo_procedimiento,
                        comision = Tipos_Comision.objects.get(id=datos_comision_uno.cleaned_data["comision"]),
                        nombre_oficial = datos_comision_uno.cleaned_data["nombre_oficial"],
                        apellido_oficial = datos_comision_uno.cleaned_data["apellido_oficial"],
                        cedula_oficial = f"{nacionalidad}- {cedula}",
                        nro_unidad = datos_comision_uno.cleaned_data["nro_unidad"],
                        nro_cuadrante = datos_comision_uno.cleaned_data["nro_cuadrante"],
                    )

                    nueva_comsion.save()

                    if datos_comision_uno.cleaned_data["agregar"] == True:
                        cedula = datos_comision_dos.cleaned_data["cedula_oficial"] 
                        nacionalidad = datos_comision_dos.cleaned_data["nacionalidad"]

                        nueva_comsion = Comisiones(
                            procedimiento = nuevo_procedimiento,
                            comision = Tipos_Comision.objects.get(id=datos_comision_dos.cleaned_data["comision"]),
                            nombre_oficial = datos_comision_dos.cleaned_data["nombre_oficial"],
                            apellido_oficial = datos_comision_dos.cleaned_data["apellido_oficial"],
                            cedula_oficial = f"{nacionalidad}- {cedula}",
                            nro_unidad = datos_comision_dos.cleaned_data["nro_unidad"],
                            nro_cuadrante = datos_comision_dos.cleaned_data["nro_cuadrante"],
                        )
                        nueva_comsion.save()

                        if datos_comision_dos.cleaned_data["agregar"] == True:
                            cedula = datos_comision_tres.cleaned_data["cedula_oficial"] 
                            nacionalidad = datos_comision_tres.cleaned_data["nacionalidad"]

                            nueva_comsion = Comisiones(
                                procedimiento = nuevo_procedimiento,
                                comision = Tipos_Comision.objects.get(id=datos_comision_tres.cleaned_data["comision"]),
                                nombre_oficial = datos_comision_tres.cleaned_data["nombre_oficial"],
                                apellido_oficial = datos_comision_tres.cleaned_data["apellido_oficial"],
                                cedula_oficial = f"{nacionalidad}- {cedula}",
                                nro_unidad = datos_comision_tres.cleaned_data["nro_unidad"],
                                nro_cuadrante = datos_comision_tres.cleaned_data["nro_cuadrante"],
                            )
                            
                            nueva_comsion.save()

            if division == "6" and form_enfermeria.is_valid():
                dependencia = form_enfermeria.cleaned_data["dependencia"]
                encargado_area = form_enfermeria.cleaned_data["encargado_area"]
                municipio = form3.cleaned_data["municipio"]
                direccion = form3.cleaned_data["direccion"]
                fecha = form3.cleaned_data["fecha"]
                hora = form3.cleaned_data["hora"]
                tipo_procedimiento = form4.cleaned_data["tipo_procedimiento"]
                parroquia = form3.cleaned_data["parroquia"]

                division_instance = Divisiones.objects.get(id=division)
                municipio_instance = Municipios.objects.get(id=municipio)
                tipo_procedimiento_instance = Tipos_Procedimientos.objects.get(id=tipo_procedimiento)

                if encargado_area == "Otro":
                    encargado_area = form_enfermeria.cleaned_data["especifique"]

                # # Crear una nueva instancia del modelo Procedimientos
                nuevo_procedimiento = Procedimientos(
                    id_division=division_instance,
                    dependencia=dependencia,
                    solicitante_externo=encargado_area,
                    id_municipio=municipio_instance,
                    direccion=direccion,
                    fecha=fecha,
                    hora=hora,
                    id_tipo_procedimiento=tipo_procedimiento_instance
                )

                # # Solo asignar parroquia si está presente
                if parroquia:
                    parroquia_instance = Parroquias.objects.get(id=parroquia)
                    nuevo_procedimiento.id_parroquia = parroquia_instance

                nuevo_procedimiento.save()
            
            if division == "7" and servicios_medicos.is_valid():
                tipo_servicio = servicios_medicos.cleaned_data["tipo_servicio"]
                jefe_area = servicios_medicos.cleaned_data["jefe_area"]
                municipio = form3.cleaned_data["municipio"]
                direccion = form3.cleaned_data["direccion"]
                fecha = form3.cleaned_data["fecha"]
                hora = form3.cleaned_data["hora"]
                tipo_procedimiento = form4.cleaned_data["tipo_procedimiento"]
                parroquia = form3.cleaned_data["parroquia"]

                division_instance = Divisiones.objects.get(id=division)
                municipio_instance = Municipios.objects.get(id=municipio)
                tipo_procedimiento_instance = Tipos_Procedimientos.objects.get(id=tipo_procedimiento)

                # # Crear una nueva instancia del modelo Procedimientos
                nuevo_procedimiento = Procedimientos(
                    id_division=division_instance,
                    tipo_servicio=tipo_servicio,
                    solicitante_externo=jefe_area,
                    id_municipio=municipio_instance,
                    direccion=direccion,
                    fecha=fecha,
                    hora=hora,
                    id_tipo_procedimiento=tipo_procedimiento_instance
                )

                # # Solo asignar parroquia si está presente
                if parroquia:
                    parroquia_instance = Parroquias.objects.get(id=parroquia)
                    nuevo_procedimiento.id_parroquia = parroquia_instance

                nuevo_procedimiento.save()

            if division == "8" and psicologia.is_valid():
                jefe_area = psicologia.cleaned_data["jefe_area"]
                municipio = form3.cleaned_data["municipio"]
                direccion = form3.cleaned_data["direccion"]
                fecha = form3.cleaned_data["fecha"]
                hora = form3.cleaned_data["hora"]
                tipo_procedimiento = form4.cleaned_data["tipo_procedimiento"]
                parroquia = form3.cleaned_data["parroquia"]

                division_instance = Divisiones.objects.get(id=division)
                municipio_instance = Municipios.objects.get(id=municipio)
                tipo_procedimiento_instance = Tipos_Procedimientos.objects.get(id=tipo_procedimiento)

                # # Crear una nueva instancia del modelo Procedimientos
                nuevo_procedimiento = Procedimientos(
                    id_division=division_instance,
                    solicitante_externo=jefe_area,
                    id_municipio=municipio_instance,
                    direccion=direccion,
                    fecha=fecha,
                    hora=hora,
                    id_tipo_procedimiento=tipo_procedimiento_instance
                )

                # # Solo asignar parroquia si está presente
                if parroquia:
                    parroquia_instance = Parroquias.objects.get(id=parroquia)
                    nuevo_procedimiento.id_parroquia = parroquia_instance

                nuevo_procedimiento.save()

            if division == "9" and capacitacion.is_valid():
                dependencia = capacitacion.cleaned_data["dependencia"]
                instructor = capacitacion.cleaned_data["instructor"]
                solicitante = capacitacion.cleaned_data["solicitante"]
                solicitante_externo = capacitacion.cleaned_data["solicitante_externo"]
                municipio = form3.cleaned_data["municipio"]
                direccion = form3.cleaned_data["direccion"]
                fecha = form3.cleaned_data["fecha"]
                hora = form3.cleaned_data["hora"]

                parroquia = form3.cleaned_data["parroquia"]
                tipo_procedimiento = 45

                division_instance = Divisiones.objects.get(id=division)
                municipio_instance = Municipios.objects.get(id=municipio)
                tipo_procedimiento_instance = Tipos_Procedimientos.objects.get(id=tipo_procedimiento)
                jefe_comision_instance = Personal.objects.get(id=instructor)

                if solicitante:
                    solicitante_instance = Personal.objects.get(id=solicitante)

                if solicitante_externo=="":
                    solicitante_externo = ""


                # # Crear una nueva instancia del modelo Procedimientos
                nuevo_procedimiento = Procedimientos(
                    id_division=division_instance,
                    dependencia=dependencia,
                    id_jefe_comision=jefe_comision_instance,
                    id_solicitante=solicitante_instance,
                    solicitante_externo=solicitante_externo,
                    id_municipio=municipio_instance,
                    direccion=direccion,
                    fecha=fecha,
                    hora=hora,
                    id_tipo_procedimiento=tipo_procedimiento_instance
                )

                # # Solo asignar parroquia si está presente
                if parroquia:
                    parroquia_instance = Parroquias.objects.get(id=parroquia)
                    nuevo_procedimiento.id_parroquia = parroquia_instance

                nuevo_procedimiento.save()

                if dependencia == "Capacitacion" and form_capacitacion.is_valid():
                    tipo_capacitacion = form_capacitacion.cleaned_data["tipo_capacitacion"]
                    tipo_clasificacion = form_capacitacion.cleaned_data["tipo_clasificacion"]
                    personas_beneficiadas = form_capacitacion.cleaned_data["personas_beneficiadas"]
                    descripcion = form_capacitacion.cleaned_data["descripcion"]
                    material_utilizado = form_capacitacion.cleaned_data["material_utilizado"]
                    status = form_capacitacion.cleaned_data["status"]

                    new_detalles_capacitacion = Procedimientos_Capacitacion(
                        id_procedimientos = nuevo_procedimiento,
                        tipo_capacitacion = tipo_capacitacion,
                        tipo_clasificacion = tipo_clasificacion,
                        personas_beneficiadas = personas_beneficiadas,
                        descripcion = descripcion,
                        material_utilizado = material_utilizado,
                        status = status
                    )

                    new_detalles_capacitacion.save()

                if dependencia == "Brigada Juvenil" and form_brigada.is_valid():
                    tipo_capacitacion = form_brigada.cleaned_data["tipo_capacitacion"]
                    tipo_clasificacion = form_brigada.cleaned_data["tipo_clasificacion"]
                    personas_beneficiadas = form_brigada.cleaned_data["personas_beneficiadas"]
                    descripcion = form_brigada.cleaned_data["descripcion"]
                    material_utilizado = form_brigada.cleaned_data["material_utilizado"]
                    status = form_brigada.cleaned_data["status"]

                    if tipo_capacitacion == "Otros":
                        tipo_capacitacion = form_brigada.cleaned_data["otros"]

                    new_detalles_brigada = Procedimientos_Brigada(
                        id_procedimientos = nuevo_procedimiento,
                        tipo_capacitacion = tipo_capacitacion,
                        tipo_clasificacion = tipo_clasificacion,
                        personas_beneficiadas = personas_beneficiadas,
                        descripcion = descripcion,
                        material_utilizado = material_utilizado,
                        status = status
                    )

                    new_detalles_brigada.save()

                if dependencia == "Frente Preventivo" and form_frente_preventivo.is_valid():
                    nombre_actividad = form_frente_preventivo.cleaned_data["nombre_actividad"]
                    estrategia = form_frente_preventivo.cleaned_data["estrategia"]
                    personas_beneficiadas = form_frente_preventivo.cleaned_data["personas_beneficiadas"]
                    descripcion = form_frente_preventivo.cleaned_data["descripcion"]
                    material_utilizado = form_frente_preventivo.cleaned_data["material_utilizado"]
                    status = form_frente_preventivo.cleaned_data["status"]

                    new_detalles_frente_preventivo = Procedimientos_Frente_Preventivo(
                        id_procedimientos = nuevo_procedimiento,
                        nombre_actividad = nombre_actividad,
                        estrategia = estrategia,
                        personas_beneficiadas = personas_beneficiadas,
                        descripcion = descripcion,
                        material_utilizado = material_utilizado,
                        status = status
                    )

                    new_detalles_frente_preventivo.save()

            # Ahora dependiendo del tipo de procedimiento, verifica el formulario correspondiente y guarda la instancia
            if tipo_procedimiento == "1" and abast_agua.is_valid():
                # Abastecimiento de Agua
                nacionalidad=abast_agua.cleaned_data["nacionalidad"]
                cedula=abast_agua.cleaned_data["cedula"]

                nuevo_abast_agua = Abastecimiento_agua(
                    id_procedimiento=nuevo_procedimiento,
                    id_tipo_servicio=Tipo_Institucion.objects.get(id=abast_agua.cleaned_data["tipo_servicio"]),
                    nombres=abast_agua.cleaned_data["nombres"],
                    apellidos=abast_agua.cleaned_data["apellidos"],
                    cedula=f"{nacionalidad}-{cedula}",
                    ltrs_agua=abast_agua.cleaned_data["ltrs_agua"],
                    personas_atendidas=abast_agua.cleaned_data["personas_atendidas"],
                    descripcion=abast_agua.cleaned_data["descripcion"],
                    material_utilizado=abast_agua.cleaned_data["material_utilizado"],
                    status=abast_agua.cleaned_data["status"]
                )
                nuevo_abast_agua.save()

            if tipo_procedimiento == "2" and apoyo_unid.is_valid():
                tipo_apoyo = apoyo_unid.cleaned_data["tipo_apoyo"]
                unidad_apoyada = apoyo_unid.cleaned_data["unidad_apoyada"]
                descripcion = apoyo_unid.cleaned_data["descripcion"]
                material_utilizado = apoyo_unid.cleaned_data["material_utilizado"]
                status = apoyo_unid.cleaned_data["status"]

                tipo_apoyo_instance = Tipo_apoyo.objects.get(id=tipo_apoyo)

                nuevo_apoyo_unidad = Apoyo_Unidades(
                    id_procedimiento=nuevo_procedimiento,
                    id_tipo_apoyo=tipo_apoyo_instance,
                    unidad_apoyada=unidad_apoyada,
                    descripcion=descripcion,
                    material_utilizado=material_utilizado,
                    status=status
                )
                nuevo_apoyo_unidad.save()

            if tipo_procedimiento == "3" and guard_prev.is_valid():
                mot_prevencion = guard_prev.cleaned_data["motivo_prevencion"]
                descripcion = guard_prev.cleaned_data["descripcion"]
                material_utilizado = guard_prev.cleaned_data["material_utilizado"]
                status = guard_prev.cleaned_data["status"]

                Tipo_Motivo_instance = Motivo_Prevencion.objects.get(id=mot_prevencion)

                nuevo_guard_prevencion = Guardia_prevencion(
                    id_procedimiento=nuevo_procedimiento,
                    id_motivo_prevencion=Tipo_Motivo_instance,
                    descripcion=descripcion,
                    material_utilizado=material_utilizado,
                    status=status
                )
                nuevo_guard_prevencion.save()

            if tipo_procedimiento == "4" and atend_no_efec.is_valid():
                descripcion = atend_no_efec.cleaned_data["descripcion"]
                material_utilizado = atend_no_efec.cleaned_data["material_utilizado"]
                status = atend_no_efec.cleaned_data["status"]

                nuevo_atend_no_efect = Atendido_no_Efectuado(
                    id_procedimiento=nuevo_procedimiento,
                    descripcion=descripcion,
                    material_utilizado=material_utilizado,
                    status=status
                )
                nuevo_atend_no_efect.save()

            if tipo_procedimiento == "5" and desp_seguridad.is_valid():
                descripcion = desp_seguridad.cleaned_data["descripcion"]
                material_utilizado = desp_seguridad.cleaned_data["material_utilizado"]
                status =desp_seguridad.cleaned_data["status"]
                motv_despliegue = desp_seguridad.cleaned_data["motv_despliegue"]

                Tipo_Motivo_instance = Motivo_Despliegue.objects.get(id=motv_despliegue)

                desp_seguridad = Despliegue_Seguridad(
                    id_procedimiento=nuevo_procedimiento,
                    motivo_despliegue = Tipo_Motivo_instance,
                    descripcion=descripcion,
                    material_utilizado=material_utilizado,
                    status=status
                )
                desp_seguridad.save()

            if tipo_procedimiento == "6" and fals_alarm.is_valid():
                descripcion = fals_alarm.cleaned_data["descripcion"]
                material_utilizado = fals_alarm.cleaned_data["material_utilizado"]
                status = fals_alarm.cleaned_data["status"]
                motv_alarma = fals_alarm.cleaned_data["motv_alarma"]

                Tipo_Motivo_instance = Motivo_Alarma.objects.get(id=motv_alarma)

                nueva_falsa_alarma = Falsa_Alarma(
                    id_procedimiento=nuevo_procedimiento,
                    motivo_alarma = Tipo_Motivo_instance,
                    descripcion=descripcion,
                    material_utilizado=material_utilizado,
                    status=status
                )
                nueva_falsa_alarma.save()

            if tipo_procedimiento == "7" and atenciones_paramedicas.is_valid():

                tipo_atencion = atenciones_paramedicas.cleaned_data["tipo_atencion"]

                nueva_atencion_paramedica = Atenciones_Paramedicas(
                  id_procedimientos = nuevo_procedimiento,
                  tipo_atencion = tipo_atencion
                )
                nueva_atencion_paramedica.save()

                if tipo_atencion == "Emergencias Medicas" and emergencias_medicas.is_valid():
                    nombre = emergencias_medicas.cleaned_data["nombre"]
                    apellido = emergencias_medicas.cleaned_data["apellido"]
                    nacionalidad = emergencias_medicas.cleaned_data["nacionalidad"]
                    cedula = emergencias_medicas.cleaned_data["cedula"]
                    edad = emergencias_medicas.cleaned_data["edad"]
                    sexo = emergencias_medicas.cleaned_data["sexo"]
                    idx = emergencias_medicas.cleaned_data["idx"]
                    descripcion = emergencias_medicas.cleaned_data["descripcion"]
                    material_utilizado = emergencias_medicas.cleaned_data["material_utilizado"]
                    status = emergencias_medicas.cleaned_data["status"]
                    trasladado = emergencias_medicas.cleaned_data["trasladado"]

                    nueva_emergencia_medica = Emergencias_Medicas(
                       id_atencion = nueva_atencion_paramedica,
                       nombres = nombre,
                       apellidos = apellido,
                       cedula = f"{nacionalidad}-{cedula}",
                       edad = edad,
                       sexo = sexo,
                       idx = idx,
                       descripcion = descripcion,
                       material_utilizado = material_utilizado,
                       status = status,
                    )
                    nueva_emergencia_medica.save()

                    if trasladado == True and traslados_emergencias.is_valid():
                        hospital = traslados_emergencias.cleaned_data["hospital_trasladado"]
                        medico = traslados_emergencias.cleaned_data["medico_receptor"]
                        mpps_cmt = traslados_emergencias.cleaned_data["mpps_cmt"]

                        nuevo_traslado_emergencia = Traslado(
                           id_lesionado = nueva_emergencia_medica,
                           hospital_trasladado = hospital,
                           medico_receptor = medico,
                           mpps_cmt = mpps_cmt,
                        )
                        nuevo_traslado_emergencia.save()

                if tipo_atencion == "Accidentes de Transito" and formulario_accidentes_transito.is_valid():
                    tipo_accidente = formulario_accidentes_transito.cleaned_data["tipo_accidente"]
                    cantidad_lesionado = formulario_accidentes_transito.cleaned_data["cantidad_lesionado"]
                    material_utilizado = formulario_accidentes_transito.cleaned_data["material_utilizado"]
                    status = formulario_accidentes_transito.cleaned_data["status"]
                    agg_vehiculo = formulario_accidentes_transito.cleaned_data["agg_vehiculo"]
                    agg_lesionado = formulario_accidentes_transito.cleaned_data["agg_lesionado"]

                    tipo_accidente_instance = Tipo_Accidente.objects.get(id=tipo_accidente)

                    nuevo_accidente_transito = Accidentes_Transito(
                      id_atencion = nueva_atencion_paramedica,
                      tipo_de_accidente = tipo_accidente_instance,
                      cantidad_lesionados = cantidad_lesionado,
                      material_utilizado = material_utilizado,
                      status = status,
                    )
                    nuevo_accidente_transito.save()

                    if agg_vehiculo == True and detalles_vehiculo_accidentes.is_valid():
                        modelo1 = detalles_vehiculo_accidentes.cleaned_data["modelo"]
                        marca1 = detalles_vehiculo_accidentes.cleaned_data["marca"]
                        color1 = detalles_vehiculo_accidentes.cleaned_data["color"]
                        año1 = detalles_vehiculo_accidentes.cleaned_data["año"]
                        placas1 = detalles_vehiculo_accidentes.cleaned_data["placas"]
                        agg_vehiculo2 = detalles_vehiculo_accidentes.cleaned_data["agg_vehiculo"]

                        nuevo_vehiculo_accidente = Detalles_Vehiculos_Accidente(
                            id_vehiculo = nuevo_accidente_transito,
                            modelo = modelo1,
                            marca = marca1,
                            color = color1,
                            año = año1,
                            placas = placas1,
                        )
                        nuevo_vehiculo_accidente.save()

                        if agg_vehiculo2 == True and detalles_vehiculo_accidentes2.is_valid():
                            modelo2 = detalles_vehiculo_accidentes2.cleaned_data["modelo"]
                            marca2 = detalles_vehiculo_accidentes2.cleaned_data["marca"]
                            color2 = detalles_vehiculo_accidentes2.cleaned_data["color"]
                            año2 = detalles_vehiculo_accidentes2.cleaned_data["año"]
                            placas2 = detalles_vehiculo_accidentes2.cleaned_data["placas"]
                            agg_vehiculo3 = detalles_vehiculo_accidentes2.cleaned_data["agg_vehiculo"]

                            nuevo_vehiculo_accidente2 = Detalles_Vehiculos_Accidente(
                                id_vehiculo = nuevo_accidente_transito,
                                modelo = modelo2,
                                marca = marca2,
                                color = color2,
                                año = año2,
                                placas = placas2,
                            )
                            nuevo_vehiculo_accidente2.save()

                            if agg_vehiculo3 == True and detalles_vehiculo_accidentes3.is_valid():
                                modelo3 = detalles_vehiculo_accidentes3.cleaned_data["modelo"]
                                marca3 = detalles_vehiculo_accidentes3.cleaned_data["marca"]
                                color3 = detalles_vehiculo_accidentes3.cleaned_data["color"]
                                año3 = detalles_vehiculo_accidentes3.cleaned_data["año"]
                                placas3 = detalles_vehiculo_accidentes3.cleaned_data["placas"]

                                nuevo_vehiculo_accidente3 = Detalles_Vehiculos_Accidente(
                                    id_vehiculo = nuevo_accidente_transito,
                                    modelo = modelo3,
                                    marca = marca3,
                                    color = color3,
                                    año = año3,
                                    placas = placas3,
                                )
                                nuevo_vehiculo_accidente3.save()


                    if agg_lesionado == True and detalles_lesionados_accidentes.is_valid():
                        nombre = detalles_lesionados_accidentes.cleaned_data["nombre"]
                        apellido = detalles_lesionados_accidentes.cleaned_data["apellido"]
                        nacionalidad = detalles_lesionados_accidentes.cleaned_data["nacionalidad"]
                        cedula = detalles_lesionados_accidentes.cleaned_data["cedula"]
                        edad = detalles_lesionados_accidentes.cleaned_data["edad"]
                        sexo = detalles_lesionados_accidentes.cleaned_data["sexo"]
                        idx = detalles_lesionados_accidentes.cleaned_data["idx"]
                        descripcion = detalles_lesionados_accidentes.cleaned_data["descripcion"]
                        trasladado = detalles_lesionados_accidentes.cleaned_data["trasladado"]
                        otro_lesionado = detalles_lesionados_accidentes.cleaned_data["otro_lesionado"]

                        nuevo_lesionado = Lesionados(
                            id_accidente = nuevo_accidente_transito,
                            nombres = nombre,
                            apellidos = apellido,
                            cedula = f"{nacionalidad}-{cedula}",
                            edad = edad,
                            sexo = sexo,
                            idx = idx,
                            descripcion = descripcion,
                        )
                        nuevo_lesionado.save()

                        if trasladado == True and traslados_accidentes.is_valid():
                            hospital = traslados_accidentes.cleaned_data["hospital_trasladado"]
                            medico = traslados_accidentes.cleaned_data["medico_receptor"]
                            mpps_cmt = traslados_accidentes.cleaned_data["mpps_cmt"]

                            nuevo_traslado_accidente = Traslado_Accidente(
                                id_lesionado = nuevo_lesionado,
                                hospital_trasladado = hospital,
                                medico_receptor = medico,
                                mpps_cmt = mpps_cmt
                            )
                            nuevo_traslado_accidente.save()

                        if otro_lesionado == True and detalles_lesionados_accidentes2.is_valid():
                            nombre = detalles_lesionados_accidentes2.cleaned_data["nombre"]
                            apellido = detalles_lesionados_accidentes2.cleaned_data["apellido"]
                            nacionalidad = detalles_lesionados_accidentes2.cleaned_data["nacionalidad"]
                            cedula = detalles_lesionados_accidentes2.cleaned_data["cedula"]
                            edad = detalles_lesionados_accidentes2.cleaned_data["edad"]
                            sexo = detalles_lesionados_accidentes2.cleaned_data["sexo"]
                            idx = detalles_lesionados_accidentes2.cleaned_data["idx"]
                            descripcion = detalles_lesionados_accidentes2.cleaned_data["descripcion"]
                            trasladado = detalles_lesionados_accidentes2.cleaned_data["trasladado"]
                            otro_lesionado = detalles_lesionados_accidentes2.cleaned_data["otro_lesionado"]

                            nuevo_lesionado = Lesionados(
                                id_accidente = nuevo_accidente_transito,
                                nombres = nombre,
                                apellidos = apellido,
                                cedula = f"{nacionalidad}-{cedula}",
                                edad = edad,
                                sexo = sexo,
                                idx = idx,
                                descripcion = descripcion,
                            )
                            nuevo_lesionado.save()

                            if trasladado == True and traslados_accidentes2.is_valid():
                                hospital = traslados_accidentes2.cleaned_data["hospital_trasladado"]
                                medico = traslados_accidentes2.cleaned_data["medico_receptor"]
                                mpps_cmt = traslados_accidentes2.cleaned_data["mpps_cmt"]

                                nuevo_traslado_accidente = Traslado_Accidente(
                                    id_lesionado = nuevo_lesionado,
                                    hospital_trasladado = hospital,
                                    medico_receptor = medico,
                                    mpps_cmt = mpps_cmt
                                )
                                nuevo_traslado_accidente.save()

                            if otro_lesionado == True and detalles_lesionados_accidentes3.is_valid():
                                nombre = detalles_lesionados_accidentes3.cleaned_data["nombre"]
                                apellido = detalles_lesionados_accidentes3.cleaned_data["apellido"]
                                nacionalidad = detalles_lesionados_accidentes3.cleaned_data["nacionalidad"]
                                cedula = detalles_lesionados_accidentes3.cleaned_data["cedula"]
                                edad = detalles_lesionados_accidentes3.cleaned_data["edad"]
                                sexo = detalles_lesionados_accidentes3.cleaned_data["sexo"]
                                idx = detalles_lesionados_accidentes3.cleaned_data["idx"]
                                descripcion = detalles_lesionados_accidentes3.cleaned_data["descripcion"]
                                trasladado = detalles_lesionados_accidentes3.cleaned_data["trasladado"]

                                nuevo_lesionado = Lesionados(
                                    id_accidente = nuevo_accidente_transito,
                                    nombres = nombre,
                                    apellidos = apellido,
                                    cedula = f"{nacionalidad}-{cedula}",
                                    edad = edad,
                                    sexo = sexo,
                                    idx = idx,
                                    descripcion = descripcion,
                                )
                                nuevo_lesionado.save()

                                if trasladado == True and traslados_accidentes3.is_valid():
                                    hospital = traslados_accidentes3.cleaned_data["hospital_trasladado"]
                                    medico = traslados_accidentes3.cleaned_data["medico_receptor"]
                                    mpps_cmt = traslados_accidentes3.cleaned_data["mpps_cmt"]

                                    nuevo_traslado_accidente = Traslado_Accidente(
                                        id_lesionado = nuevo_lesionado,
                                        hospital_trasladado = hospital,
                                        medico_receptor = medico,
                                        mpps_cmt = mpps_cmt
                                    )
                                    nuevo_traslado_accidente.save()

            if tipo_procedimiento == "9" and serv_especial.is_valid():
                descripcion = serv_especial.cleaned_data["descripcion"]
                material_utilizado = serv_especial.cleaned_data["material_utilizado"]
                status = serv_especial.cleaned_data["status"]
                tipo_servicio = serv_especial.cleaned_data["tipo_servicio"]

                tipo_servicio_instance = Tipo_servicios.objects.get(id=tipo_servicio)

                nuevo_Servicio_especial = Servicios_Especiales(
                    id_procedimientos=nuevo_procedimiento,
                    tipo_servicio = tipo_servicio_instance,
                    descripcion=descripcion,
                    material_utilizado=material_utilizado,
                    status=status
                )
                nuevo_Servicio_especial.save()

            if tipo_procedimiento == "10" and rescate_form.is_valid():
                material_utilizado = rescate_form.cleaned_data["material_utilizado"]
                status = rescate_form.cleaned_data["status"]
                id_tipo_rescate = rescate_form.cleaned_data["tipo_rescate"]


                tipo_rescate_instance = Tipo_Rescate.objects.get(id=id_tipo_rescate)

                nuevo_proc_rescate = Rescate(
                    id_procedimientos = nuevo_procedimiento,
                    material_utilizado=material_utilizado,
                    tipo_rescate = tipo_rescate_instance,
                    status=status
                )
                nuevo_proc_rescate.save()

                if id_tipo_rescate == "1" and rescate_form_animal.is_valid():
                    especie = rescate_form_animal.cleaned_data["especie"]
                    descripcion = rescate_form_animal.cleaned_data["descripcion"]

                    new_rescate_animal = Rescate_Animal(
                        id_rescate = nuevo_proc_rescate,
                        especie = especie,
                        descripcion = descripcion,
                    )
                    new_rescate_animal.save()

                    return redirect('/dashboard/')

                else:
                    rescate_form_persona.is_valid()
                    nombre_persona = rescate_form_persona.cleaned_data["nombre_persona"]
                    apellido_persona = rescate_form_persona.cleaned_data["apellido_persona"]
                    nacionalidad = rescate_form_persona.cleaned_data["nacionalidad"]
                    cedula_persona = rescate_form_persona.cleaned_data["cedula_persona"]
                    edad_persona = rescate_form_persona.cleaned_data["edad_persona"]
                    sexo_persona = rescate_form_persona.cleaned_data["sexo_persona"]
                    descripcion = rescate_form_persona.cleaned_data["descripcion"]

                    new_rescate_persona = Rescate_Persona(
                        id_rescate = nuevo_proc_rescate,
                        nombre = nombre_persona,
                        apellidos = apellido_persona,
                        cedula = f"{nacionalidad}-{cedula_persona}",
                        edad = edad_persona,
                        sexo = sexo_persona,
                        descripcion = descripcion,
                    )
                    new_rescate_persona.save()

                    return redirect('/dashboard/')

            if tipo_procedimiento == "11" and incendio_form.is_valid():
                id_tipo_incendio = incendio_form.cleaned_data["tipo_incendio"]
                descripcion = incendio_form.cleaned_data["descripcion"]
                material_utilizado = incendio_form.cleaned_data["material_utilizado"]
                status = incendio_form.cleaned_data["status"]

                tipo_incendio_instance = Tipo_Incendio.objects.get(id=id_tipo_incendio)

                nuevo_proc_incendio = Incendios(
                    id_procedimientos = nuevo_procedimiento,
                    id_tipo_incendio = tipo_incendio_instance,
                    descripcion=descripcion,
                    material_utilizado=material_utilizado,
                    status=status
                )
                nuevo_proc_incendio.save()

                check_agregar_persona = incendio_form.cleaned_data["check_agregar_persona"]
                check_retencion = incendio_form.cleaned_data["check_retencion"]

                if check_agregar_persona == True and persona_presente_form.is_valid():
                    nombre = persona_presente_form.cleaned_data["nombre"]
                    apellido = persona_presente_form.cleaned_data["apellido"]
                    nacionalidad = persona_presente_form.cleaned_data["nacionalidad"]
                    cedula = persona_presente_form.cleaned_data["cedula"]
                    edad = persona_presente_form.cleaned_data["edad"]

                    new_persona_presente = Persona_Presente(
                        id_incendio = nuevo_proc_incendio,
                        nombre = nombre,
                        apellidos = apellido,
                        cedula = f"{nacionalidad}-{cedula}",
                        edad = edad,
                    )
                    new_persona_presente.save()

                if check_retencion == True and retencion_preventiva_incendio.is_valid():
                    tipo_cilindro = retencion_preventiva_incendio.cleaned_data["tipo_cilindro"]
                    capacidad = retencion_preventiva_incendio.cleaned_data["capacidad"]
                    serial = retencion_preventiva_incendio.cleaned_data["serial"]
                    nro_constancia_retencion = retencion_preventiva_incendio.cleaned_data["nro_constancia_retencion"]
                    nombre = retencion_preventiva_incendio.cleaned_data["nombre"]
                    apellido = retencion_preventiva_incendio.cleaned_data["apellidos"]
                    nacionalidad = retencion_preventiva_incendio.cleaned_data["nacionalidad"]
                    cedula = retencion_preventiva_incendio.cleaned_data["cedula"]

                    tipo_cilindro_instance = Tipo_Cilindro.objects.get(id=tipo_cilindro)

                    nuevo_proc_reten_incendio = Retencion_Preventiva_Incendios(
                        id_procedimiento = nuevo_proc_incendio,
                        tipo_cilindro = tipo_cilindro_instance,
                        capacidad = capacidad,
                        serial = serial,
                        nro_constancia_retencion = nro_constancia_retencion,
                        nombre = nombre,
                        apellidos = apellido,
                        cedula = f"{nacionalidad}-{cedula}",
                    )
                    nuevo_proc_reten_incendio.save()

                if id_tipo_incendio == "2" and detalles_vehiculo_form.is_valid():
                    modelo = detalles_vehiculo_form.cleaned_data["modelo"]
                    marca = detalles_vehiculo_form.cleaned_data["marca"]
                    color = detalles_vehiculo_form.cleaned_data["color"]
                    año = detalles_vehiculo_form.cleaned_data["año"]
                    placas = detalles_vehiculo_form.cleaned_data["placas"]

                    new_agregar_vehiculo = Detalles_Vehiculos(
                        id_vehiculo = nuevo_proc_incendio,
                        modelo = modelo,
                        marca = marca,
                        color = color,
                        año = año,
                        placas = placas,
                    )
                    new_agregar_vehiculo.save()

            if tipo_procedimiento == "12" and form_fallecido.is_valid():
                motivo_fallecimiento = form_fallecido.cleaned_data["motivo_fallecimiento"]
                nom_fallecido = form_fallecido.cleaned_data["nom_fallecido"]
                apellido_fallecido = form_fallecido.cleaned_data["apellido_fallecido"]
                nacionalidad = form_fallecido.cleaned_data["nacionalidad"]
                cedula_fallecido = form_fallecido.cleaned_data["cedula_fallecido"]
                edad = form_fallecido.cleaned_data["edad"]
                sexo = form_fallecido.cleaned_data["sexo"]
                descripcion = form_fallecido.cleaned_data["descripcion"]
                material_utilizado = form_fallecido.cleaned_data["material_utilizado"]
                status = form_fallecido.cleaned_data["status"]

                nuevo_proc_fallecido = Fallecidos(
                    id_procedimiento = nuevo_procedimiento,
                    motivo_fallecimiento = motivo_fallecimiento,
                    nombres = nom_fallecido,
                    apellidos = apellido_fallecido,
                    cedula = f"{nacionalidad}-{cedula_fallecido}",
                    edad = edad,
                    sexo = sexo,
                    descripcion=descripcion,
                    material_utilizado=material_utilizado,
                    status=status
                )
                nuevo_proc_fallecido.save()

            if tipo_procedimiento == "13" and mitigacion_riesgo_form.is_valid():
                tipo_riesgo = mitigacion_riesgo_form.cleaned_data["tipo_riesgo"]
                descripcion = mitigacion_riesgo_form.cleaned_data["descripcion"]
                material_utilizado = mitigacion_riesgo_form.cleaned_data["material_utilizado"]
                status = mitigacion_riesgo_form.cleaned_data["status"]

                tipo_riesgo_instance = Mitigacion_riesgo.objects.get(id=tipo_riesgo)

                nuevo_proc_mit = Mitigacion_Riesgos(
                    id_procedimientos = nuevo_procedimiento,
                    id_tipo_servicio = tipo_riesgo_instance,
                    descripcion=descripcion,
                    material_utilizado=material_utilizado,
                    status=status
                )
                nuevo_proc_mit.save()

                agg_vehiculo = mitigacion_riesgo_form.cleaned_data["agregar_vehiculo"]
                if (agg_vehiculo and vehiculo_derrame_form.is_valid()):
                    modelo = vehiculo_derrame_form.cleaned_data["modelo"]
                    marca = vehiculo_derrame_form.cleaned_data["marca"]
                    color = vehiculo_derrame_form.cleaned_data["color"]
                    año = vehiculo_derrame_form.cleaned_data["año"]
                    placas = vehiculo_derrame_form.cleaned_data["placas"]

                    nuevo_vehiculo = Detalles_Vehiculo_Derrame(
                        id_vehiculo = nuevo_proc_mit,
                        modelo = modelo,
                        marca = marca,
                        color = color,
                        año = año,
                        placas = placas,
                    )
                    nuevo_vehiculo.save()

                    agg_vehiculo2 = vehiculo_derrame_form.cleaned_data["agregar_segundo_vehiculo"]
                    if (agg_vehiculo2 and vehiculo_derrame_form2.is_valid()):
                        modelo = vehiculo_derrame_form2.cleaned_data["modelo"]
                        marca = vehiculo_derrame_form2.cleaned_data["marca"]
                        color = vehiculo_derrame_form2.cleaned_data["color"]
                        año = vehiculo_derrame_form2.cleaned_data["año"]
                        placas = vehiculo_derrame_form2.cleaned_data["placas"]

                        nuevo_vehiculo = Detalles_Vehiculo_Derrame(
                            id_vehiculo = nuevo_proc_mit,
                            modelo = modelo,
                            marca = marca,
                            color = color,
                            año = año,
                            placas = placas,
                        )
                        nuevo_vehiculo.save()
                        agg_vehiculo3 = vehiculo_derrame_form2.cleaned_data["agregar_tercer_vehiculo"]

                        if (agg_vehiculo3 and vehiculo_derrame_form3.is_valid()):
                            modelo = vehiculo_derrame_form3.cleaned_data["modelo"]
                            marca = vehiculo_derrame_form3.cleaned_data["marca"]
                            color = vehiculo_derrame_form3.cleaned_data["color"]
                            año = vehiculo_derrame_form3.cleaned_data["año"]
                            placas = vehiculo_derrame_form3.cleaned_data["placas"]

                            nuevo_vehiculo = Detalles_Vehiculo_Derrame(
                                id_vehiculo = nuevo_proc_mit,
                                modelo = modelo,
                                marca = marca,
                                color = color,
                                año = año,
                                placas = placas,
                            )
                            nuevo_vehiculo.save()

            if tipo_procedimiento == "14" and evaluacion_riesgo_form.is_valid():
                tipo_riesgo = evaluacion_riesgo_form.cleaned_data["tipo_riesgo"]
                tipo_estructura = evaluacion_riesgo_form.cleaned_data["tipo_etructura"]
                descripcion = evaluacion_riesgo_form.cleaned_data["descripcion"]
                material_utilizado = evaluacion_riesgo_form.cleaned_data["material_utilizado"]
                status = evaluacion_riesgo_form.cleaned_data["status"]

                tipo_riesgo_instance = Motivo_Riesgo.objects.get(id=tipo_riesgo)

                nuevo_proc_eval = Evaluacion_Riesgo(
                    id_procedimientos = nuevo_procedimiento,
                    id_tipo_riesgo = tipo_riesgo_instance,
                    tipo_estructura = tipo_estructura,
                    descripcion=descripcion,
                    material_utilizado=material_utilizado,
                    status=status
                )

                nuevo_proc_eval.save()

                if division == "3" and tipo_procedimiento == "14" and persona_presente_eval_form.is_valid():
                    nombre = persona_presente_eval_form.cleaned_data["nombre"]
                    apellido = persona_presente_eval_form.cleaned_data["apellidos"]
                    nacionalidad = persona_presente_eval_form.cleaned_data["nacionalidad"]
                    cedula = persona_presente_eval_form.cleaned_data["cedula"]
                    telefono = persona_presente_eval_form.cleaned_data["telefono"]

                    nuevo_per_presente = Persona_Presente_Eval(
                        id_persona = nuevo_proc_eval,
                        nombre = nombre,
                        apellidos = apellido,
                        cedula = f"{nacionalidad}-{cedula}",
                        telefono = telefono,
                    )
                    nuevo_per_presente.save()

            if tipo_procedimiento == "15" and puesto_avanzada_form.is_valid():
                tipo_avanzada = puesto_avanzada_form.cleaned_data["tipo_avanzada"]
                descripcion = puesto_avanzada_form.cleaned_data["descripcion"]
                material_utilizado = puesto_avanzada_form.cleaned_data["material_utilizado"]
                status = puesto_avanzada_form.cleaned_data["status"]

                tipo_avanzada_instance = Motivo_Avanzada.objects.get(id=tipo_avanzada)

                nuevo_proc_avan = Puesto_Avanzada(
                    id_procedimientos = nuevo_procedimiento,
                    id_tipo_servicio = tipo_avanzada_instance,
                    descripcion=descripcion,
                    material_utilizado=material_utilizado,
                    status=status
                )
                nuevo_proc_avan.save()

            if tipo_procedimiento == "16" and traslados_prehospitalaria_form.is_valid():
                tipo_traslado = traslados_prehospitalaria_form.cleaned_data["tipo_traslado"]
                nombre = traslados_prehospitalaria_form.cleaned_data["nombre"]
                apellido = traslados_prehospitalaria_form.cleaned_data["apellido"]
                nacionalidad = traslados_prehospitalaria_form.cleaned_data["nacionalidad"]
                cedula = traslados_prehospitalaria_form.cleaned_data["cedula"]
                edad = traslados_prehospitalaria_form.cleaned_data["edad"]
                sexo = traslados_prehospitalaria_form.cleaned_data["sexo"]
                idx = traslados_prehospitalaria_form.cleaned_data["idx"]
                hospital_trasladado = traslados_prehospitalaria_form.cleaned_data["hospital_trasladado"]
                medico_receptor = traslados_prehospitalaria_form.cleaned_data["medico_receptor"]
                mpps_cmt = traslados_prehospitalaria_form.cleaned_data["mpps_cmt"]
                descripcion = traslados_prehospitalaria_form.cleaned_data["descripcion"]
                material_utilizado = traslados_prehospitalaria_form.cleaned_data["material_utilizado"]
                status = traslados_prehospitalaria_form.cleaned_data["status"]

                tipo_traslado_instance = Tipos_Traslado.objects.get(id=tipo_traslado)

                nuevo_proc_tras = Traslado_Prehospitalaria(
                    id_procedimiento = nuevo_procedimiento,
                    id_tipo_traslado = tipo_traslado_instance,
                    nombre = nombre,
                    apellido = apellido,
                    cedula = f"{nacionalidad}-{cedula}",
                    edad = edad,
                    sexo = sexo,
                    idx = idx,
                    hospital_trasladado = hospital_trasladado,
                    medico_receptor = medico_receptor,
                    mpps_cmt = mpps_cmt,
                    descripcion=descripcion,
                    material_utilizado=material_utilizado,
                    status=status
                )
                nuevo_proc_tras.save()

            if tipo_procedimiento == "17" and asesoramiento_form.is_valid():
                nombre_comercio = asesoramiento_form.cleaned_data["nombre_comercio"]
                rif_comercio = asesoramiento_form.cleaned_data["rif_comercio"]
                nombre = asesoramiento_form.cleaned_data["nombres"]
                apellido = asesoramiento_form.cleaned_data["apellidos"]
                nacionalidad = asesoramiento_form.cleaned_data["nacionalidad"]
                cedula = asesoramiento_form.cleaned_data["cedula"]
                sexo = asesoramiento_form.cleaned_data["sexo"]
                telefono = asesoramiento_form.cleaned_data["telefono"]
                descripcion = asesoramiento_form.cleaned_data["descripcion"]
                material_utilizado = asesoramiento_form.cleaned_data["material_utilizado"]
                status = asesoramiento_form.cleaned_data["status"]

                nuevo_proc_ase = Asesoramiento(
                    id_procedimiento = nuevo_procedimiento,
                    nombre_comercio = nombre_comercio,
                    rif_comercio = rif_comercio,
                    nombres = nombre,
                    apellidos = apellido,
                    cedula = f"{nacionalidad}-{cedula}",
                    sexo = sexo,
                    telefono = telefono,
                    descripcion=descripcion,
                    material_utilizado=material_utilizado,
                    status=status
                )
                nuevo_proc_ase.save()
                
            if tipo_procedimiento == "18" and form_inspecciones.is_valid():
                tipo_inspeccion = form_inspecciones.cleaned_data["tipo_inspeccion"]

                if tipo_inspeccion == "Prevención" and form_inspecciones_prevencion.is_valid():
                    nombre_comercio = form_inspecciones_prevencion.cleaned_data["nombre_comercio"]
                    propietario = form_inspecciones_prevencion.cleaned_data["propietario"]
                    nacionalidad = form_inspecciones_prevencion.cleaned_data["nacionalidad"]
                    cedula_propietario = form_inspecciones_prevencion.cleaned_data["cedula_propietario"]
                    descripcion = form_inspecciones_prevencion.cleaned_data["descripcion"]
                    persona_sitio_nombre = form_inspecciones_prevencion.cleaned_data["persona_sitio_nombre"]
                    persona_sitio_apellido = form_inspecciones_prevencion.cleaned_data["persona_sitio_apellido"]
                    nacionalidad2 = form_inspecciones_prevencion.cleaned_data["nacionalidad2"]
                    persona_sitio_cedula = form_inspecciones_prevencion.cleaned_data["persona_sitio_cedula"]
                    persona_sitio_telefono = form_inspecciones_prevencion.cleaned_data["persona_sitio_telefono"]
                    material_utilizado = form_inspecciones_prevencion.cleaned_data["material_utilizado"]
                    status = form_inspecciones_prevencion.cleaned_data["status"]

                    nueva_inspeccion = Inspeccion_Prevencion_Asesorias_Tecnicas (
                        id_procedimientos = nuevo_procedimiento,
                        tipo_inspeccion = tipo_inspeccion,
                        nombre_comercio = nombre_comercio,
                        propietario = propietario,
                        cedula_propietario = f"{nacionalidad}-{cedula_propietario}",
                        descripcion = descripcion,
                        persona_sitio_nombre = persona_sitio_nombre,
                        persona_sitio_apellido = persona_sitio_apellido,
                        persona_sitio_cedula = f"{nacionalidad2}-{persona_sitio_cedula}",
                        persona_sitio_telefono = persona_sitio_telefono,
                        material_utilizado = material_utilizado,
                        status = status
                    )
                
                    nueva_inspeccion.save()

                if tipo_inspeccion == "Árbol" and form_inspecciones_arbol.is_valid():
                    especie = form_inspecciones_arbol.cleaned_data["especie"]
                    altura_aprox = form_inspecciones_arbol.cleaned_data["altura_aprox"]
                    ubicacion_arbol = form_inspecciones_arbol.cleaned_data["ubicacion_arbol"]
                    persona_sitio_nombre = form_inspecciones_arbol.cleaned_data["persona_sitio_nombre"]
                    persona_sitio_apellido = form_inspecciones_arbol.cleaned_data["persona_sitio_apellido"]
                    nacionalidad = form_inspecciones_arbol.cleaned_data["nacionalidad"]
                    persona_sitio_cedula = form_inspecciones_arbol.cleaned_data["persona_sitio_cedula"]
                    persona_sitio_telefono = form_inspecciones_arbol.cleaned_data["persona_sitio_telefono"]
                    descripcion = form_inspecciones_arbol.cleaned_data["descripcion"]
                    material_utilizado = form_inspecciones_arbol.cleaned_data["material_utilizado"]
                    status = form_inspecciones_arbol.cleaned_data["status"]

                    nueva_inspeccion = Inspeccion_Arbol (
                        id_procedimientos = nuevo_procedimiento,
                        tipo_inspeccion = tipo_inspeccion,
                        especie = especie,
                        altura_aprox = altura_aprox,
                        ubicacion_arbol = ubicacion_arbol,
                        persona_sitio_nombre = persona_sitio_nombre,
                        persona_sitio_apellido = persona_sitio_apellido,
                        persona_sitio_cedula = f"{nacionalidad}-{persona_sitio_cedula}",
                        persona_sitio_telefono = persona_sitio_telefono,
                        descripcion = descripcion,
                        material_utilizado = material_utilizado,
                        status = status
                    )
                
                    nueva_inspeccion.save()

                if tipo_inspeccion == "Asesorias Tecnicas" and form_inspecciones_prevencion.is_valid():
                    nombre_comercio = form_inspecciones_prevencion.cleaned_data["nombre_comercio"]
                    propietario = form_inspecciones_prevencion.cleaned_data["propietario"]
                    nacionalidad = form_inspecciones_prevencion.cleaned_data["nacionalidad"]
                    cedula_propietario = form_inspecciones_prevencion.cleaned_data["cedula_propietario"]
                    descripcion = form_inspecciones_prevencion.cleaned_data["descripcion"]
                    persona_sitio_nombre = form_inspecciones_prevencion.cleaned_data["persona_sitio_nombre"]
                    persona_sitio_apellido = form_inspecciones_prevencion.cleaned_data["persona_sitio_apellido"]
                    nacionalidad2 = form_inspecciones_prevencion.cleaned_data["nacionalidad2"]
                    persona_sitio_cedula = form_inspecciones_prevencion.cleaned_data["persona_sitio_cedula"]
                    persona_sitio_telefono = form_inspecciones_prevencion.cleaned_data["persona_sitio_telefono"]
                    material_utilizado = form_inspecciones_prevencion.cleaned_data["material_utilizado"]
                    status = form_inspecciones_prevencion.cleaned_data["status"]

                    nueva_inspeccion = Inspeccion_Prevencion_Asesorias_Tecnicas (
                        id_procedimientos = nuevo_procedimiento,
                        tipo_inspeccion = tipo_inspeccion,
                        nombre_comercio = nombre_comercio,
                        propietario = propietario,
                        cedula_propietario = f"{nacionalidad}-{cedula_propietario}",
                        descripcion = descripcion,
                        persona_sitio_nombre = persona_sitio_nombre,
                        persona_sitio_apellido = persona_sitio_apellido,
                        persona_sitio_cedula = f"{nacionalidad2}-{persona_sitio_cedula}",
                        persona_sitio_telefono = persona_sitio_telefono,
                        material_utilizado = material_utilizado,
                        status = status
                    )
                
                    nueva_inspeccion.save()

                if tipo_inspeccion == "Habitabilidad" and form_inspecciones_habitabilidad.is_valid():
                    descripcion = form_inspecciones_habitabilidad.cleaned_data["descripcion"]
                    persona_sitio_nombre = form_inspecciones_habitabilidad.cleaned_data["persona_sitio_nombre"]
                    persona_sitio_apellido = form_inspecciones_habitabilidad.cleaned_data["persona_sitio_apellido"]
                    nacionalidad = form_inspecciones_habitabilidad.cleaned_data["nacionalidad"]
                    persona_sitio_cedula = form_inspecciones_habitabilidad.cleaned_data["persona_sitio_cedula"]
                    persona_sitio_telefono = form_inspecciones_habitabilidad.cleaned_data["persona_sitio_telefono"]
                    material_utilizado = form_inspecciones_habitabilidad.cleaned_data["material_utilizado"]
                    status = form_inspecciones_habitabilidad.cleaned_data["status"]

                    nueva_inspeccion = Inspeccion_Habitabilidad (
                        id_procedimientos = nuevo_procedimiento,
                        tipo_inspeccion = tipo_inspeccion,
                        descripcion = descripcion,
                        persona_sitio_nombre = persona_sitio_nombre,
                        persona_sitio_apellido = persona_sitio_apellido,
                        persona_sitio_cedula = f"{nacionalidad}-{persona_sitio_cedula}",
                        persona_sitio_telefono = persona_sitio_telefono,
                        material_utilizado = material_utilizado,
                        status = status
                    )
                
                    nueva_inspeccion.save()

                if tipo_inspeccion == "Otros" and form_inspecciones_otros.is_valid():
                    especifique = form_inspecciones_otros.cleaned_data["especifique"]
                    descripcion = form_inspecciones_otros.cleaned_data["descripcion"]
                    persona_sitio_nombre = form_inspecciones_otros.cleaned_data["persona_sitio_nombre"]
                    persona_sitio_apellido = form_inspecciones_otros.cleaned_data["persona_sitio_apellido"]
                    nacionalidad = form_inspecciones_otros.cleaned_data["nacionalidad"]
                    persona_sitio_cedula = form_inspecciones_otros.cleaned_data["persona_sitio_cedula"]
                    persona_sitio_telefono = form_inspecciones_otros.cleaned_data["persona_sitio_telefono"]
                    material_utilizado = form_inspecciones_otros.cleaned_data["material_utilizado"]
                    status = form_inspecciones_otros.cleaned_data["status"]

                    nueva_inspeccion = Inspeccion_Otros (
                        id_procedimientos = nuevo_procedimiento,
                        tipo_inspeccion = tipo_inspeccion,
                        especifique = especifique,
                        descripcion = descripcion,
                        persona_sitio_nombre = persona_sitio_nombre,
                        persona_sitio_apellido = persona_sitio_apellido,
                        persona_sitio_cedula = f"{nacionalidad}-{persona_sitio_cedula}",
                        persona_sitio_telefono = persona_sitio_telefono,
                        material_utilizado = material_utilizado,
                        status = status
                    )
                
                    nueva_inspeccion.save()

            if tipo_procedimiento == "19" and form_investigacion.is_valid():
                tipo_investigacion = form_investigacion.cleaned_data["tipo_investigacion"]
                tipo_siniestro = form_investigacion.cleaned_data["tipo_siniestro"]

                tipo_investigacion_instance = Tipos_Investigacion.objects.get(id=tipo_investigacion)

                new_investigacion = Investigacion(
                    id_procedimientos = nuevo_procedimiento,
                    id_tipo_investigacion = tipo_investigacion_instance,
                    tipo_siniestro = tipo_siniestro
                )
                new_investigacion.save()

                if tipo_siniestro == "Comercio" and form_inv_comercio.is_valid():
                    nombre_comercio = form_inv_comercio.cleaned_data["nombre_comercio"]
                    rif_comercio = form_inv_comercio.cleaned_data["rif_comercio"]
                    nombre_propietario = form_inv_comercio.cleaned_data["nombre_propietario"]
                    apellido_propietario = form_inv_comercio.cleaned_data["apellido_propietario"]
                    nacionalidad = form_inv_comercio.cleaned_data["nacionalidad"]
                    cedula_propietario = form_inv_comercio.cleaned_data["cedula_propietario"]
                    descripcion = form_inv_comercio.cleaned_data["descripcion"]
                    material_utilizado = form_inv_comercio.cleaned_data["material_utilizado"]
                    status = form_inv_comercio.cleaned_data["status"]

                    new_inv_comercio = Investigacion_Comercio (
                        id_investigacion = new_investigacion,
                        nombre_comercio = nombre_comercio,
                        rif_comercio = rif_comercio,
                        nombre_propietario = nombre_propietario,
                        apellido_propietario = apellido_propietario,
                        cedula_propietario = f"{nacionalidad}-{cedula_propietario}",
                        descripcion = descripcion,
                        material_utilizado = material_utilizado,
                        status = status
                    )
                    new_inv_comercio.save()

                if (tipo_siniestro == "Estructura" or tipo_siniestro == "Vivienda") and form_inv_estructura.is_valid():
                    tipo_estructura = form_inv_estructura.cleaned_data["tipo_estructura"]
                    nombre = form_inv_estructura.cleaned_data["nombre"]
                    apellido = form_inv_estructura.cleaned_data["apellido"]
                    nacionalidad = form_inv_estructura.cleaned_data["nacionalidad"]
                    cedula = form_inv_estructura.cleaned_data["cedula"]
                    descripcion = form_inv_estructura.cleaned_data["descripcion"]
                    material_utilizado = form_inv_estructura.cleaned_data["material_utilizado"]
                    status = form_inv_estructura.cleaned_data["status"]

                    new_inv_estructura = Investigacion_Estructura_Vivienda (
                        id_investigacion = new_investigacion,
                        tipo_estructura = tipo_estructura,
                        nombre = nombre,
                        apellido = apellido,
                        cedula = f"{nacionalidad}-{cedula}",
                        descripcion = descripcion,
                        material_utilizado = material_utilizado,
                        status = status
                    )
                    new_inv_estructura.save()

                if tipo_siniestro == "Vehiculo" and form_inv_vehiculo.is_valid():
                    marca = form_inv_vehiculo.cleaned_data["marca"]
                    modelo = form_inv_vehiculo.cleaned_data["modelo"]
                    color = form_inv_vehiculo.cleaned_data["color"]
                    placas = form_inv_vehiculo.cleaned_data["placas"]
                    año = form_inv_vehiculo.cleaned_data["año"]
                    nombre_propietario = form_inv_vehiculo.cleaned_data["nombre_propietario"]
                    apellido_propietario = form_inv_vehiculo.cleaned_data["apellido_propietario"]
                    nacionalidad = form_inv_vehiculo.cleaned_data["nacionalidad"]
                    cedula_propietario = form_inv_vehiculo.cleaned_data["cedula_propietario"]
                    descripcion = form_inv_vehiculo.cleaned_data["descripcion"]
                    material_utilizado = form_inv_vehiculo.cleaned_data["material_utilizado"]
                    status = form_inv_vehiculo.cleaned_data["status"]

                    new_inv_vehiculo = Investigacion_Vehiculo(
                        id_investigacion = new_investigacion,
                        marca = marca,
                        modelo = modelo,
                        color = color,
                        placas = placas,
                        año = año,
                        nombre_propietario = nombre_propietario,
                        apellido_propietario = apellido_propietario,
                        cedula_propietario = f"{nacionalidad}-{cedula_propietario}",
                        descripcion = descripcion,
                        material_utilizado = material_utilizado,
                        status = status,
                    )
                    new_inv_vehiculo.save()

            if tipo_procedimiento == "20" and reinspeccion_prevencion.is_valid():
                nombre_comercio = reinspeccion_prevencion.cleaned_data["nombre_comercio"]
                rif_comercio = reinspeccion_prevencion.cleaned_data["rif_comercio"]
                nombre = reinspeccion_prevencion.cleaned_data["nombre"]
                apellido = reinspeccion_prevencion.cleaned_data["apellidos"]
                sexo = reinspeccion_prevencion.cleaned_data["sexo"]
                nacionalidad = reinspeccion_prevencion.cleaned_data["nacionalidad"]
                cedula = reinspeccion_prevencion.cleaned_data["cedula"]
                sexo = reinspeccion_prevencion.cleaned_data["sexo"]
                telefono = reinspeccion_prevencion.cleaned_data["telefono"]
                descripcion = reinspeccion_prevencion.cleaned_data["descripcion"]
                material_utilizado = reinspeccion_prevencion.cleaned_data["material_utilizado"]
                status = reinspeccion_prevencion.cleaned_data["status"]

                nuevo_proc_reins = Reinspeccion_Prevencion(
                    id_procedimiento = nuevo_procedimiento,
                    nombre_comercio = nombre_comercio,
                    rif_comercio = rif_comercio,
                    nombre = nombre,
                    apellidos = apellido,
                    cedula = f"{nacionalidad}-{cedula}",
                    sexo = sexo,
                    telefono = telefono,
                    descripcion=descripcion,
                    material_utilizado=material_utilizado,
                    status=status
                )
                nuevo_proc_reins.save()

            if tipo_procedimiento == "21" and retencion_preventiva.is_valid():
                tipo_cilindro = retencion_preventiva.cleaned_data["tipo_cilindro"]
                capacidad = retencion_preventiva.cleaned_data["capacidad"]
                serial = retencion_preventiva.cleaned_data["serial"]
                nro_constancia_retencion = retencion_preventiva.cleaned_data["nro_constancia_retencion"]
                nombre = retencion_preventiva.cleaned_data["nombre"]
                apellido = retencion_preventiva.cleaned_data["apellidos"]
                nacionalidad = retencion_preventiva.cleaned_data["nacionalidad"]
                cedula = retencion_preventiva.cleaned_data["cedula"]
                descripcion = retencion_preventiva.cleaned_data["descripcion"]
                material_utilizado = retencion_preventiva.cleaned_data["material_utilizado"]
                status = retencion_preventiva.cleaned_data["status"]

                tipo_cilindro_instance = Tipo_Cilindro.objects.get(id=tipo_cilindro)

                nuevo_proc_reten = Retencion_Preventiva(
                    id_procedimiento = nuevo_procedimiento,
                    tipo_cilindro = tipo_cilindro_instance,
                    capacidad = capacidad,
                    serial = serial,
                    nro_constancia_retencion = nro_constancia_retencion,
                    nombre = nombre,
                    apellidos = apellido,
                    cedula = f"{nacionalidad}-{cedula}",
                    descripcion=descripcion,
                    material_utilizado=material_utilizado,
                    status=status
                )
                nuevo_proc_reten.save()

            if tipo_procedimiento == "22" and artificios_pirotecnico.is_valid():
                nombre_comercio = artificios_pirotecnico.cleaned_data["nombre_comercio"]
                rif_comercio = artificios_pirotecnico.cleaned_data["rif_comercio"]
                tipo_procedimiento_art = artificios_pirotecnico.cleaned_data["tipo_procedimiento"]

                tipo_procedimiento_art_instance = Tipos_Artificios.objects.get(id=tipo_procedimiento_art)

                nuevo_proc_artificio_pir = Artificios_Pirotecnicos(
                    id_procedimiento = nuevo_procedimiento,
                    nombre_comercio = nombre_comercio,
                    rif_comerciante = rif_comercio,
                    tipo_procedimiento = tipo_procedimiento_art_instance
                )

                nuevo_proc_artificio_pir.save()

                if tipo_procedimiento_art == "1" and incendio_art.is_valid():
                    id_tipo_incendio = incendio_art.cleaned_data["tipo_incendio"]
                    descripcion = incendio_art.cleaned_data["descripcion"]
                    material_utilizado = incendio_art.cleaned_data["material_utilizado"]
                    status = incendio_art.cleaned_data["status"]

                    tipo_incendio_instance = Tipo_Incendio.objects.get(id=id_tipo_incendio)

                    nuevo_proc_incendio_art = Incendios_Art(
                        id_procedimientos = nuevo_proc_artificio_pir,
                        id_tipo_incendio = tipo_incendio_instance,
                        descripcion=descripcion,
                        material_utilizado=material_utilizado,
                        status=status
                    )
                    nuevo_proc_incendio_art.save()

                    check_agregar_persona = incendio_art.cleaned_data["check_agregar_persona"]

                    if check_agregar_persona == True and persona_presente_art.is_valid():
                        nombre = persona_presente_art.cleaned_data["nombre"]
                        apellido = persona_presente_art.cleaned_data["apellido"]
                        nacionalidad = persona_presente_art.cleaned_data["nacionalidad"]
                        cedula = persona_presente_art.cleaned_data["cedula"]
                        edad = persona_presente_art.cleaned_data["edad"]

                        new_persona_presente = Persona_Presente_Art(
                            id_incendio = nuevo_proc_incendio_art,
                            nombre = nombre,
                            apellidos = apellido,
                            cedula = f"{nacionalidad}-{cedula}",
                            edad = edad,
                        )
                        new_persona_presente.save()

                    if id_tipo_incendio == "2" and detalles_vehiculo_art.is_valid():
                        modelo = detalles_vehiculo_art.cleaned_data["modelo"]
                        marca = detalles_vehiculo_art.cleaned_data["marca"]
                        color = detalles_vehiculo_art.cleaned_data["color"]
                        año = detalles_vehiculo_art.cleaned_data["año"]
                        placas = detalles_vehiculo_art.cleaned_data["placas"]

                        new_agregar_vehiculo = Detalles_Vehiculos_Art(
                            id_vehiculo = nuevo_proc_incendio_art,
                            modelo = modelo,
                            marca = marca,
                            color = color,
                            año = año,
                            placas = placas,
                        )
                        new_agregar_vehiculo.save()

                if tipo_procedimiento_art == "2" and lesionados.is_valid():
                    nombre = lesionados.cleaned_data["nombre"]
                    apellido = lesionados.cleaned_data["apellido"]
                    nacionalidad = lesionados.cleaned_data["nacionalidad"]
                    cedula = lesionados.cleaned_data["cedula"]
                    edad = lesionados.cleaned_data["edad"]
                    sexo = lesionados.cleaned_data["sexo"]
                    idx = lesionados.cleaned_data["idx"]
                    descripcion = lesionados.cleaned_data["descripcion"]
                    status = lesionados.cleaned_data["status"]


                    nuevo_lesionado_art = Lesionados_Art(
                        id_accidente = nuevo_proc_artificio_pir,
                        nombres = nombre,
                        apellidos = apellido,
                        cedula = f"{nacionalidad}-{cedula}",
                        edad = edad,
                        sexo = sexo,
                        idx = idx,
                        descripcion = descripcion,
                        status = status
                    )

                    nuevo_lesionado_art.save()

                if tipo_procedimiento_art == "3" and fallecidos_art.is_valid():
                    motivo_fallecimiento = fallecidos_art.cleaned_data["motivo_fallecimiento"]
                    nom_fallecido = fallecidos_art.cleaned_data["nom_fallecido"]
                    apellido_fallecido = fallecidos_art.cleaned_data["apellido_fallecido"]
                    nacionalidad = fallecidos_art.cleaned_data["nacionalidad"]
                    cedula_fallecido = fallecidos_art.cleaned_data["cedula_fallecido"]
                    edad = fallecidos_art.cleaned_data["edad"]
                    sexo = fallecidos_art.cleaned_data["sexo"]
                    descripcion = fallecidos_art.cleaned_data["descripcion"]
                    material_utilizado = fallecidos_art.cleaned_data["material_utilizado"]
                    status = fallecidos_art.cleaned_data["status"]

                    nuevo_proc_fallecido_art = Fallecidos_Art(
                        id_procedimiento = nuevo_proc_artificio_pir,
                        motivo_fallecimiento = motivo_fallecimiento,
                        nombres = nom_fallecido,
                        apellidos = apellido_fallecido,
                        cedula = f"{nacionalidad}-{cedula_fallecido}",
                        edad = edad,
                        sexo = sexo,
                        descripcion=descripcion,
                        material_utilizado=material_utilizado,
                        status=status
                    )
                    nuevo_proc_fallecido_art.save()

            if tipo_procedimiento == "23" and inspeccion_artificios_pir.is_valid():
                nombre_comercio = inspeccion_artificios_pir.cleaned_data["nombre_comercio"]
                rif_comercio = inspeccion_artificios_pir.cleaned_data["rif_comercio"]
                nombre_encargado = inspeccion_artificios_pir.cleaned_data["nombre_encargado"]
                apellido_encargado = inspeccion_artificios_pir.cleaned_data["apellido_encargado"]
                nacionalidad = inspeccion_artificios_pir.cleaned_data["nacionalidad"]
                cedula_encargado = inspeccion_artificios_pir.cleaned_data["cedula_encargado"]
                sexo = inspeccion_artificios_pir.cleaned_data["sexo"]
                descripcion = inspeccion_artificios_pir.cleaned_data["descripcion"]
                material_utilizado = inspeccion_artificios_pir.cleaned_data["material_utilizado"]
                status = inspeccion_artificios_pir.cleaned_data["status"]

                nueva_inspeccion_art = Inspeccion_Establecimiento_Art(
                    id_proc_artificio = nuevo_procedimiento,
                    nombre_comercio = nombre_comercio,
                    rif_comercio = rif_comercio,
                    encargado_nombre = nombre_encargado,
                    encargado_apellidos = apellido_encargado,
                    encargado_cedula = f"{nacionalidad}-{cedula_encargado}",
                    encargado_sexo = sexo,
                    descripcion = descripcion,
                    material_utilizado = material_utilizado,
                    status = status
                )

                nueva_inspeccion_art.save()

            if tipo_procedimiento == "24" and form_valoracion_medica.is_valid():
                nombre = form_valoracion_medica.cleaned_data["nombre"]
                apellido = form_valoracion_medica.cleaned_data["apellido"]
                nacionalidad = form_valoracion_medica.cleaned_data["nacionalidad"]
                cedula = form_valoracion_medica.cleaned_data["cedula"]
                edad = form_valoracion_medica.cleaned_data["edad"]
                sexo = form_valoracion_medica.cleaned_data["sexo"]
                telefono = form_valoracion_medica.cleaned_data["telefono"]
                descripcion = form_valoracion_medica.cleaned_data["descripcion"]
                material_utilizado = form_valoracion_medica.cleaned_data["material_utilizado"]
                status = form_valoracion_medica.cleaned_data["status"]

                new_valoracion_medica = Valoracion_Medica(
                    id_procedimientos = nuevo_procedimiento,
                    nombre = nombre,
                    apellido = apellido,
                    cedula = f"{nacionalidad}-{cedula}",
                    edad = edad,
                    sexo = sexo,
                    telefono = telefono,
                    descripcion = descripcion,
                    material_utilizado = material_utilizado,
                    status = status
                )
                new_valoracion_medica.save()

            if tipo_procedimiento == "25" and form_jornada_medica.is_valid():
                nombre_jornada = form_jornada_medica.cleaned_data["nombre_jornada"]
                cantidad_personas_atendidas = form_jornada_medica.cleaned_data["cant_personas_aten"]
                descripcion = form_jornada_medica.cleaned_data["descripcion"]
                material_utilizado = form_jornada_medica.cleaned_data["material_utilizado"]
                status = form_jornada_medica.cleaned_data["status"]

                new_jornada_medica = Jornada_Medica(
                    id_procedimientos = nuevo_procedimiento,
                    nombre_jornada = nombre_jornada,
                    cant_personas_aten = cantidad_personas_atendidas,
                    descripcion = descripcion,
                    material_utilizado = material_utilizado,
                    status = status
                )
                new_jornada_medica.save()

            if (tipo_procedimiento == "26" or tipo_procedimiento == "27" or tipo_procedimiento == "28" or tipo_procedimiento == "29" or tipo_procedimiento == "30" or tipo_procedimiento == "31" or tipo_procedimiento == "32" or tipo_procedimiento == "33" or tipo_procedimiento == "34") and form_detalles_enfermeria.is_valid():
                nombre = form_detalles_enfermeria.cleaned_data["nombre"]
                apellido = form_detalles_enfermeria.cleaned_data["apellido"]
                nacionalidad = form_detalles_enfermeria.cleaned_data["nacionalidad"]
                cedula = form_detalles_enfermeria.cleaned_data["cedula"]
                edad = form_detalles_enfermeria.cleaned_data["edad"]
                sexo = form_detalles_enfermeria.cleaned_data["sexo"]
                telefono = form_detalles_enfermeria.cleaned_data["telefono"]
                descripcion = form_detalles_enfermeria.cleaned_data["descripcion"]
                material_utilizado = form_detalles_enfermeria.cleaned_data["material_utilizado"]
                status = form_detalles_enfermeria.cleaned_data["status"]

                new_detalles_enfermeria = Detalles_Enfermeria(
                    id_procedimientos = nuevo_procedimiento,
                    nombre = nombre,
                    apellido = apellido,
                    cedula = f"{nacionalidad}-{cedula}",
                    edad = edad,
                    sexo = sexo,
                    telefono = telefono,
                    descripcion = descripcion,
                    material_utilizado = material_utilizado,
                    status = status
                )
                new_detalles_enfermeria.save()

            if (tipo_procedimiento == "35" or tipo_procedimiento == "36" or tipo_procedimiento == "37" or tipo_procedimiento == "38" or tipo_procedimiento == "39" or tipo_procedimiento == "40" or tipo_procedimiento == "41") and form_detalles_psicologia.is_valid():
                nombre = form_detalles_psicologia.cleaned_data["nombre"]
                apellido = form_detalles_psicologia.cleaned_data["apellido"]
                nacionalidad = form_detalles_psicologia.cleaned_data["nacionalidad"]
                cedula = form_detalles_psicologia.cleaned_data["cedula"]
                edad = form_detalles_psicologia.cleaned_data["edad"]
                sexo = form_detalles_psicologia.cleaned_data["sexo"]
                descripcion = form_detalles_psicologia.cleaned_data["descripcion"]
                material_utilizado = form_detalles_psicologia.cleaned_data["material_utilizado"]
                status = form_detalles_psicologia.cleaned_data["status"]

                new_detalles_psicologia = Procedimientos_Psicologia(
                    id_procedimientos = nuevo_procedimiento,
                    nombre = nombre,
                    apellido = apellido,
                    cedula = f"{nacionalidad}-{cedula}",
                    edad = edad,
                    sexo = sexo,
                    descripcion = descripcion,
                    material_utilizado = material_utilizado,
                    status = status
                )
                new_detalles_psicologia.save()

            # Redirige a /dashboard/ después de guardar los datos
            return redirect('/dashboard/?registro_exitoso=true')
    else:
        form = SelectorDivision(prefix='form1', initial_division=initial_division)
        form2 = SeleccionarInfo(prefix='form2')
        form3 = Datos_Ubicacion(prefix='form3')
        form4 = Selecc_Tipo_Procedimiento(prefix='form4')
        abast_agua = formulario_abastecimiento_agua(prefix='abast_agua')
        apoyo_unid = Formulario_apoyo_unidades(prefix='apoyo_unid')
        guard_prev = Formulario_guardia_prevencion(prefix='guard_prev')
        atend_no_efec = Formulario_atendido_no_efectuado(prefix='atend_no_efec')
        desp_seguridad = Formulario_despliegue_seguridad(prefix='desp_seguridad')
        fals_alarm = Formulario_falsa_alarma(prefix='fals_alarm')
        serv_especial = Formulario_Servicios_Especiales(prefix='serv_especial')
        form_fallecido = Formulario_Fallecidos(prefix='form_fallecido')
        rescate_form = Formulario_Rescate(prefix='rescate_form')
        incendio_form = Formulario_Incendio(prefix='incendio_form')
        retencion_preventiva_incendio = Formulario_Retencion_Preventiva_Incendio(prefix='retencion_preventiva_incendio')
        atenciones_paramedicas = Formulario_Atenciones_Paramedicas(prefix='atenciones_paramedicas')

        emergencias_medicas = Formulario_Emergencias_Medicas(prefix='emergencias_medicas')
        traslados_emergencias = Formulario_Traslados(prefix='traslados_emergencias')

        persona_presente_form = Formulario_Persona_Presente(prefix='persona_presente_form')
        detalles_vehiculo_form = Formulario_Detalles_Vehiculos_Incendio(prefix='detalles_vehiculo_form')

        formulario_accidentes_transito = Formulario_Accidentes_Transito(prefix='formulario_accidentes_transito')
        detalles_vehiculo_accidentes = Formulario_Detalles_Vehiculos(prefix='detalles_vehiculos_accidentes')
        detalles_lesionados_accidentes = Formulario_Detalles_Lesionados(prefix='detalles_lesionados_accidentes')
        detalles_lesionados_accidentes2 = Formulario_Detalles_Lesionados2(prefix='detalles_lesionados_accidentes2')
        detalles_lesionados_accidentes3 = Formulario_Detalles_Lesionados3(prefix='detalles_lesionados_accidentes3')
        traslados_accidentes = Formulario_Traslado_Accidente(prefix='traslados_accidentes')
        traslados_accidentes2 = Formulario_Traslado_Accidente2(prefix='traslados_accidentes2')
        traslados_accidentes3 = Formulario_Traslado_Accidente3(prefix='traslados_accidentes3')
        detalles_vehiculo_accidentes2 = Formulario_Detalles_Vehiculos2(prefix='detalles_vehiculos_accidentes2')
        detalles_vehiculo_accidentes3 = Formulario_Detalles_Vehiculos3(prefix='detalles_vehiculos_accidentes3')

        rescate_form_persona = Formulario_Rescate_Persona(prefix='rescate_form_persona')
        rescate_form_animal = Formulario_Rescate_Animal(prefix='rescate_form_animal')

        evaluacion_riesgo_form = Forulario_Evaluacion_Riesgo(prefix='evaluacion_riesgo_form')
        mitigacion_riesgo_form = Formulario_Mitigacion_Riesgos(prefix='mitigacion_riesgo_form')
        vehiculo_derrame_form = Detalles_Vehiculo_Derrame_Form(prefix='vehiculo_derrame_form')
        vehiculo_derrame_form2 = Detalles_Vehiculo_Derrame_Form2(prefix='vehiculo_derrame_form2')
        vehiculo_derrame_form3 = Detalles_Vehiculo_Derrame_Form3(prefix='vehiculo_derrame_form3')

        puesto_avanzada_form = Formulario_Puesto_Avanzada(prefix='puesto_avanzada_form')
        traslados_prehospitalaria_form = Formulario_Traslados_Prehospitalaria(prefix='traslados_prehospitalaria_form')
        asesoramiento_form = Formulario_Asesoramiento(prefix='asesoramiento_form')
        persona_presente_eval_form = Formularia_Persona_Presente_Eval(prefix='persona_presente_eval_form')
        reinspeccion_prevencion = Formulario_Reinspeccion_Prevencion(prefix='reinspeccion_prevencion')
        retencion_preventiva = Formulario_Retencion_Preventiva(prefix='retencion_preventiva')

        artificios_pirotecnico = Formulario_Artificios_Pirotecnicos(prefix='artificios_pirotecnico')
        lesionados = Formulario_Lesionado(prefix='lesionados')
        incendio_art = Formulario_Incendio_Art(prefix='incendio_art')
        persona_presente_art = Formulario_Persona_Presente_Art(prefix='persona_presente_art')
        detalles_vehiculo_art = Formulario_Detalles_Vehiculos_Incendio_Art(prefix='detalles_vehiculo_art')
        fallecidos_art = Formulario_Fallecidos_Art(prefix='fallecidos_art')
        inspeccion_artificios_pir = Formulario_Inspeccion_Establecimiento_Art(prefix='inspeccion_artificios_pir')
        form_enfermeria = Formulario_Enfermeria(prefix='form_enfermeria')
        servicios_medicos = Formulario_Servicios_medicos(prefix='form_servicios_medicos')
        psicologia = Formulario_psicologia(prefix='form_psicologia')
        capacitacion = Formulario_capacitacion(prefix='form_capacitacion')
        form_valoracion_medica = Formulario_Valoracion_Medica(prefix='form_valoracion_medica')
        form_jornada_medica = Formulario_Jornada_Medica(prefix='form_jornada_medica')
        form_detalles_enfermeria = Formulario_Detalles_Enfermeria(prefix='form_detalles_enfermeria')
        form_detalles_psicologia = Formulario_Procedimientos_Psicologia(prefix='form_detalles_psicologia')

        form_capacitacion = Formulario_Capacitacion_Proc(prefix='form_capacitacion')
        form_brigada = Formulario_Brigada(prefix='form_brigada')
        form_frente_preventivo = Formulario_Frente_Preventivo(prefix='form_frente_preventivo')

        form_inspecciones = Formulario_Inspecciones(prefix='form_inspecciones')
        form_inspecciones_prevencion = Formulario_Inspeccion_Prevencion_Asesorias_Tecnicas(prefix='form_inspecciones_prevencion')
        form_inspecciones_habitabilidad = Formulario_Inspeccion_Habitabilidad(prefix='form_inspecciones_habitabilidad')
        form_inspecciones_arbol = Formulario_Inspeccion_Arbol(prefix='form_inspecciones_arbol')
        form_inspecciones_otros = Formulario_Inspeccion_Otros(prefix='form_inspecciones_otros')

        form_investigacion = Formulario_Investigacion(prefix='form_investigacion')
        form_inv_vehiculo = Formulario_Investigacion_Vehiculo(prefix='form_inv_vehiculo')
        form_inv_comercio = Formulario_Investigacion_Comercio(prefix='form_inv_comercio')
        form_inv_estructura = Formulario_Investigacion_Estructura_Vivienda(prefix='form_inv_estructura')

        form_comision = Datos_Comision(prefix='form_comision')
        datos_comision_uno = Comision_Uno(prefix='datos_comision_uno')
        datos_comision_dos = Comision_Dos(prefix='datos_comision_dos')
        datos_comision_tres = Comision_Tres(prefix='datos_comision_tres')
        

    return render(request, "procedimientos.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "initial_division": initial_division,
        "form": form,
        "form2": form2,
        "form3": form3,
        "form4": form4,
        "errors": result,
        "form_abastecimiento_agua": abast_agua,
        "form_apoyo_unidades": apoyo_unid,
        "form_guardia_prevencion": guard_prev,
        "form_atendido_no_efectuado": atend_no_efec,
        "form_despliegue_seguridad": desp_seguridad,
        "form_falsa_alarma": fals_alarm,
        "form_servicios_especiales": serv_especial,
        "form_fallecido": form_fallecido,
        "rescate_form": rescate_form,
        "rescate_form_animal": rescate_form_animal,
        "rescate_form_persona": rescate_form_persona,
        "incendio_form": incendio_form,
        "retencion_preventiva_incendio": retencion_preventiva_incendio,
        "persona_presente_form": persona_presente_form,
        "detalles_vehiculo_form": detalles_vehiculo_form,
        "atenciones_paramedicas": atenciones_paramedicas,
        "emergencias_medicas": emergencias_medicas,
        "traslados_emergencias": traslados_emergencias,
        "formulario_accidentes_transito": formulario_accidentes_transito,
        "detalles_vehiculo_accidentes":  detalles_vehiculo_accidentes,
        "detalles_vehiculo_accidentes2":  detalles_vehiculo_accidentes2,
        "detalles_vehiculo_accidentes3":  detalles_vehiculo_accidentes3,
        "detalles_lesionados_accidentes": detalles_lesionados_accidentes,
        "detalles_lesionados_accidentes2": detalles_lesionados_accidentes2,
        "detalles_lesionados_accidentes3": detalles_lesionados_accidentes3,
        "traslados_accidentes": traslados_accidentes,
        "traslados_accidentes2": traslados_accidentes2,
        "traslados_accidentes3": traslados_accidentes3,
        "evaluacion_riesgo_form": evaluacion_riesgo_form,
        "mitigacion_riesgo_form": mitigacion_riesgo_form,
        "vehiculo_derrame_form": vehiculo_derrame_form,
        "vehiculo_derrame_form2": vehiculo_derrame_form2,
        "vehiculo_derrame_form3": vehiculo_derrame_form3,
        "puesto_avanzada_form": puesto_avanzada_form,
        "traslados_prehospitalaria_form": traslados_prehospitalaria_form,
        "asesoramiento_form": asesoramiento_form,
        "persona_presente_eval_form": persona_presente_eval_form,
        "reinspeccion_prevencion": reinspeccion_prevencion,
        "retencion_preventiva": retencion_preventiva,
        "artificios_pirotecnico": artificios_pirotecnico,
        "lesionados": lesionados,
        "incendio_art": incendio_art,
        "persona_presente_art": persona_presente_art,
        "detalles_vehiculo_art": detalles_vehiculo_art,
        "fallecidos_art": fallecidos_art,
        "inspeccion_artificios_pir": inspeccion_artificios_pir,
        "form_enfermeria": form_enfermeria,
        "servicios_medicos" : servicios_medicos,
        "psicologia" : psicologia,
        "capacitacion" : capacitacion,
        "valoracion_medica": form_valoracion_medica,
        "form_detalles_enfermeria": form_detalles_enfermeria,
        "form_detalles_psicologia": form_detalles_psicologia,
        "form_capacitacion": form_capacitacion,
        "form_frente_preventivo": form_frente_preventivo,
        "jornada_medica": form_jornada_medica,
        "form_inspecciones": form_inspecciones,
        "form_inspecciones_prevencion": form_inspecciones_prevencion,
        "form_inspecciones_habitabilidad": form_inspecciones_habitabilidad,
        "form_inspecciones_arbol": form_inspecciones_arbol,
        "form_inspecciones_otros": form_inspecciones_otros,
        "form_investigacion": form_investigacion,
        "form_inv_vehiculo": form_inv_vehiculo,
        "form_inv_comercio": form_inv_comercio,
        "form_inv_estructura": form_inv_estructura,
        "form_comision": form_comision,
        "comision_uno": datos_comision_uno,
        "comision_dos": datos_comision_dos,
        "comision_tres": datos_comision_tres,
        "form_brigada": form_brigada,
        })

# Vista de la seccion de Estadisticas
def View_Estadisticas(request):
    user = request.session.get('user')
    if not user:
            return redirect('/')

    return render(request, "estadisticas.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
    })

def ver_registros(request):
    user = request.session.get('user')

    if not user:
        return redirect('/')

        # Obtener la fecha enviada desde el frontend
    fecha_carga = request.GET.get('fecha', None)
        # Convierte la fecha cargada a un objeto datetime "aware"
    if fecha_carga:
        fecha_inicio = make_aware(datetime.strptime(fecha_carga, "%Y-%m-%d"))
        fecha_fin = fecha_inicio + timedelta(days=1)
    else:
        # Si no se pasa la fecha, por defecto cargar los procedimientos del día actual
        fecha_inicio = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        fecha_fin = fecha_inicio + timedelta(days=1)


    # Filtrar procedimientos según la fecha
    registros = RegistroPeticiones.objects.filter(
        fecha_hora__gte=fecha_inicio,
        fecha_hora__lt=fecha_fin
    ).order_by('-fecha_hora')

    # Convertir el QuerySet en una lista de diccionarios
    procedimientos = list(
        registros.values(
            "usuario__user",  # Nombre del usuario relacionado
            "url",
            "fecha_hora"
        )
    )

    # Formatear las fechas en el backend
    for procedimiento in procedimientos:
        procedimiento['fecha_hora'] = procedimiento['fecha_hora'].strftime("%d/%m/%Y, %H:%M")


    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # Verificar si es una solicitud AJAX
        # Serializa los datos en un formato compatible con JSON
        procedimientos = list(registros.values(
            "usuario__user",
            "url",
            "fecha_hora",
        ))

        # Responder con los datos en formato JSON y la fecha para la siguiente carga
        return JsonResponse({'procedimientos': procedimientos, 'fecha': fecha_inicio.strftime("%Y-%m-%d")})

    return render(request, 'ver_registros.html', {'registros': procedimientos,
                                                  "user": user,
                                                  "jerarquia": user["jerarquia"],
                                                  "nombres": user["nombres"],
                                                  "apellidos": user["apellidos"],
                                                  })

def Antecedentes(request):
    datos_combinados = []
    form = FormularioBusquedaCedula(request.GET or None)

    user = request.session.get('user')

    if not user:                                                                                                                                                                                                                                                                                                                                              
        return redirect('/')
    
    procedimientos_ids = set()

    if form.is_valid():
        nacionalidad = form.cleaned_data['nacionalidad']
        numero_cedula = form.cleaned_data['numero_cedula']

        busqueda = f"{nacionalidad}-{numero_cedula}"

        procedimientos_ids = set()  # Para almacenar los IDs de procedimientos
        datos_detallados = []  # Para almacenar los datos adicionales como nombre, apellido, cédula

        # Buscar en cada tabla hija
        ids_abastecimiento = Abastecimiento_agua.objects.filter(cedula=busqueda).values('id_procedimiento', 'nombres', 'apellidos')
        ids_fallecidos = Fallecidos.objects.filter(cedula=busqueda).values('id_procedimiento', 'nombres', 'apellidos')
        # Buscar rescates asociados al número de cédula
        ids_rescate_personas = Rescate_Persona.objects.filter(cedula=busqueda).values(
            'id_rescate__id_procedimientos',
            'nombre', 'apellidos', 'cedula'
        )
        ids_incendio = Persona_Presente.objects.filter(cedula=busqueda).values(
            'id_incendio__id_procedimientos',
            'nombre', 'apellidos', 'cedula'
        )
        ids_emergencias_medicas = Emergencias_Medicas.objects.filter(cedula=busqueda).values(
            'id_atencion__id_procedimientos',
            'nombres', 'apellidos', 'cedula'
        )
        ids_traslados = Traslado_Prehospitalaria.objects.filter(cedula=busqueda).values(
            'id_procedimiento',
            'nombre', 'apellido', 'cedula'
        )
        ids_accidentes = Lesionados.objects.filter(cedula=busqueda).values(
            'id_accidente__id_atencion__id_procedimientos',
            'nombres', 'apellidos', 'cedula'
        )
        ids_evaluacion = Persona_Presente_Eval.objects.filter(cedula=busqueda).values(
            'id_persona__id_procedimientos',
            'nombre', 'apellidos', 'cedula'
        )
        ids_asesoramiento = Asesoramiento.objects.filter(cedula=busqueda).values(
            'id_procedimiento',
            'nombres', 'apellidos', 'cedula'
        )
        ids_reispeccion = Reinspeccion_Prevencion.objects.filter(cedula=busqueda).values(
            'id_procedimiento',
            'nombre', 'apellidos', 'cedula'
        )
        ids_retencion = Retencion_Preventiva.objects.filter(cedula=busqueda).values(
            'id_procedimiento',
            'nombre', 'apellidos', 'cedula'
        )
        ids_incendio_art = Persona_Presente_Art.objects.filter(cedula=busqueda).values(
            'id_incendio__id_procedimientos__id_procedimiento',
            'nombre', 'apellidos', 'cedula'
        )
        ids_lesionados_art = Lesionados_Art.objects.filter(cedula=busqueda).values(
            'id_accidente__id_procedimiento',
            'nombres', 'apellidos', 'cedula'
        )
        ids_fallecidos_art = Fallecidos_Art.objects.filter(cedula=busqueda).values(
            'id_procedimiento__id_procedimiento',
            'nombres', 'apellidos', 'cedula'
        )
        ids_inspeccion_art = Inspeccion_Establecimiento_Art.objects.filter(encargado_cedula=busqueda).values(
            'id_proc_artificio',
            'encargado_nombre', 'encargado_apellidos', 'encargado_cedula'
        )
        ids_valoracion_medica = Valoracion_Medica.objects.filter(cedula=busqueda).values(
            'id_procedimientos',
            'nombre', 'apellido', 'cedula'
        )
        ids_enfermeria = Detalles_Enfermeria.objects.filter(cedula=busqueda).values(
            'id_procedimientos',
            'nombre', 'apellido', 'cedula'
        )
        ids_psicologia = Procedimientos_Psicologia.objects.filter(cedula=busqueda).values(
            'id_procedimientos',
            'nombre', 'apellido', 'cedula'
        )
        ids_inspeccion_prevencion_i = Inspeccion_Prevencion_Asesorias_Tecnicas.objects.filter(cedula_propietario=busqueda).values(
            'id_procedimientos',
            'propietario', 'cedula_propietario'
        )
        ids_inspeccion_prevencion_ii = Inspeccion_Prevencion_Asesorias_Tecnicas.objects.filter(persona_sitio_cedula=busqueda).values(
            'id_procedimientos',
            'persona_sitio_nombre', 'persona_sitio_apellido', 'persona_sitio_cedula'
        )
        ids_habitabilidad = Inspeccion_Habitabilidad.objects.filter(persona_sitio_cedula=busqueda).values(
            'id_procedimientos',
            'persona_sitio_nombre', 'persona_sitio_apellido', 'persona_sitio_cedula'
        )
        ids_inspeccion_otros = Inspeccion_Otros.objects.filter(persona_sitio_cedula=busqueda).values(
            'id_procedimientos',
            'persona_sitio_nombre', 'persona_sitio_apellido', 'persona_sitio_cedula'
        )
        ids_inspeccion_arbol = Inspeccion_Arbol.objects.filter(persona_sitio_cedula=busqueda).values(
            'id_procedimientos',
            'persona_sitio_nombre', 'persona_sitio_apellido', 'persona_sitio_cedula'
        )
        ids_investigacion_vehiculo = Investigacion_Vehiculo.objects.filter(cedula_propietario=busqueda).values(
            'id_investigacion__id_procedimientos',
            'nombre_propietario', 'apellido_propietario', 'cedula_propietario'
        )
        ids_investigacion_comercio = Investigacion_Comercio.objects.filter(cedula_propietario=busqueda).values(
            'id_investigacion__id_procedimientos',
            'nombre_propietario', 'apellido_propietario', 'cedula_propietario'
        )
        ids_investigacion_estructura = Investigacion_Estructura_Vivienda.objects.filter(cedula=busqueda).values(
            'id_investigacion__id_procedimientos',
            'nombre', 'apellido', 'cedula'
        )

        # Procesar los resultados de cada tabla
        for item in ids_abastecimiento:
            procedimientos_ids.add(item['id_procedimiento'])
            datos_detallados.append({
                'id_procedimiento': item['id_procedimiento'],
                'nombres': item['nombres'],
                'apellidos': item['apellidos'],
                'cedula': busqueda
            })

        for item in ids_fallecidos:
            procedimientos_ids.add(item['id_procedimiento'])
            datos_detallados.append({
                'id_procedimiento': item['id_procedimiento'],
                'nombres': item['nombres'],
                'apellidos': item['apellidos'],
                'cedula': busqueda
            })

        for item in ids_rescate_personas:
            procedimientos_ids.add(item['id_rescate__id_procedimientos'])
            datos_detallados.append({
                'id_procedimiento': item['id_rescate__id_procedimientos'],
                'nombres': item['nombre'],
                'apellidos': item['apellidos'],
                'cedula': busqueda
            })

        for item in ids_incendio:
            procedimientos_ids.add(item['id_incendio__id_procedimientos'])
            datos_detallados.append({
                'id_procedimiento': item['id_incendio__id_procedimientos'],
                'nombres': item['nombre'],
                'apellidos': item['apellidos'],
                'cedula': busqueda
            })

        for item in ids_emergencias_medicas:
            procedimientos_ids.add(item['id_atencion__id_procedimientos'])
            datos_detallados.append({
                'id_procedimiento': item['id_atencion__id_procedimientos'],
                'nombres': item['nombres'],
                'apellidos': item['apellidos'],
                'cedula': busqueda
            })

        for item in ids_traslados:
            procedimientos_ids.add(item['id_procedimiento'])
            datos_detallados.append({
                'id_procedimiento': item['id_procedimiento'],
                'nombres': item['nombre'],
                'apellidos': item['apellido'],
                'cedula': busqueda
            })

        for item in ids_accidentes:
            procedimientos_ids.add(item['id_accidente__id_atencion__id_procedimientos'])
            datos_detallados.append({
                'id_procedimiento': item['id_accidente__id_atencion__id_procedimientos'],
                'nombres': item['nombres'],
                'apellidos': item['apellidos'],
                'cedula': busqueda
            })

        for item in ids_evaluacion:
            procedimientos_ids.add(item['id_persona__id_procedimientos'])
            datos_detallados.append({
                'id_procedimiento': item['id_persona__id_procedimientos'],
                'nombres': item['nombre'],
                'apellidos': item['apellidos'],
                'cedula': busqueda
            })

        for item in ids_asesoramiento:
            procedimientos_ids.add(item['id_procedimiento'])
            datos_detallados.append({
                'id_procedimiento': item['id_procedimiento'],
                'nombres': item['nombres'],
                'apellidos': item['apellidos'],
                'cedula': busqueda
            })

        for item in ids_reispeccion:
            procedimientos_ids.add(item['id_procedimiento'])
            datos_detallados.append({
                'id_procedimiento': item['id_procedimiento'],
                'nombres': item['nombre'],
                'apellidos': item['apellidos'],
                'cedula': busqueda
            })

        for item in ids_retencion:
            procedimientos_ids.add(item['id_procedimiento'])
            datos_detallados.append({
                'id_procedimiento': item['id_procedimiento'],
                'nombres': item['nombre'],
                'apellidos': item['apellidos'],
                'cedula': busqueda
            })

        for item in ids_incendio_art:
            procedimientos_ids.add(item['id_incendio__id_procedimientos__id_procedimiento'])
            datos_detallados.append({
                'id_procedimiento': item['id_incendio__id_procedimientos__id_procedimiento'],
                'nombres': item['nombre'],
                'apellidos': item['apellidos'],
                'cedula': busqueda
            })
        
        for item in ids_lesionados_art:
            procedimientos_ids.add(item['id_accidente__id_procedimiento'])
            datos_detallados.append({
                'id_procedimiento': item['id_accidente__id_procedimiento'],
                'nombres': item['nombres'],
                'apellidos': item['apellidos'],
                'cedula': busqueda
            })
        
        for item in ids_fallecidos_art:
            procedimientos_ids.add(item['id_procedimiento__id_procedimiento'])
            datos_detallados.append({
                'id_procedimiento': item['id_procedimiento__id_procedimiento'],
                'nombres': item['nombres'],
                'apellidos': item['apellidos'],
                'cedula': busqueda
            })

        for item in ids_inspeccion_art:
            procedimientos_ids.add(item['id_proc_artificio'])
            datos_detallados.append({
                'id_procedimiento': item['id_proc_artificio'],
                'nombres': item['encargado_nombre'],
                'apellidos': item['encargado_apellidos'],
                'cedula': busqueda
            })

        for item in ids_valoracion_medica:
            procedimientos_ids.add(item['id_procedimientos'])
            datos_detallados.append({
                'id_procedimiento': item['id_procedimientos'],
                'nombres': item['nombre'],
                'apellidos': item['apellido'],
                'cedula': busqueda
            })

        for item in ids_enfermeria:
            procedimientos_ids.add(item['id_procedimientos'])
            datos_detallados.append({
                'id_procedimiento': item['id_procedimientos'],
                'nombres': item['nombre'],
                'apellidos': item['apellido'],
                'cedula': busqueda
            })

        for item in ids_psicologia:
            procedimientos_ids.add(item['id_procedimientos'])
            datos_detallados.append({
                'id_procedimiento': item['id_procedimientos'],
                'nombres': item['nombre'],
                'apellidos': item['apellido'],
                'cedula': busqueda
            })

        for item in ids_inspeccion_prevencion_i:
            procedimientos_ids.add(item['id_procedimientos'])
            datos_detallados.append({
                'id_procedimiento': item['id_procedimientos'],
                'nombres': item['propietario'],
                'cedula': busqueda
            })

        for item in ids_inspeccion_prevencion_ii:
            procedimientos_ids.add(item['id_procedimientos'])
            datos_detallados.append({
                'id_procedimiento': item['id_procedimientos'],
                'nombres': item['persona_sitio_nombre'],
                'apellidos': item['persona_sitio_apellido'],
                'cedula': busqueda
            })

        for item in ids_habitabilidad:
            procedimientos_ids.add(item['id_procedimientos'])
            datos_detallados.append({
                'id_procedimiento': item['id_procedimientos'],
                'nombres': item['persona_sitio_nombre'],
                'apellidos': item['persona_sitio_apellido'],
                'cedula': busqueda
            })

        for item in ids_inspeccion_otros:
            procedimientos_ids.add(item['id_procedimientos'])
            datos_detallados.append({
                'id_procedimiento': item['id_procedimientos'],
                'nombres': item['persona_sitio_nombre'],
                'apellidos': item['persona_sitio_apellido'],
                'cedula': busqueda
            })

        for item in ids_inspeccion_arbol:
            procedimientos_ids.add(item['id_procedimientos'])
            datos_detallados.append({
                'id_procedimiento': item['id_procedimientos'],
                'nombres': item['persona_sitio_nombre'],
                'apellidos': item['persona_sitio_apellido'],
                'cedula': busqueda
            })

        for item in ids_investigacion_vehiculo:
            procedimientos_ids.add(item['id_investigacion__id_procedimientos'])
            datos_detallados.append({
                'id_procedimiento': item['id_investigacion__id_procedimientos'],
                'nombres': item['nombre_propietario'],
                'apellidos': item['apellido_propietario'],
                'cedula': busqueda
            })

        for item in ids_investigacion_comercio:
            procedimientos_ids.add(item['id_investigacion__id_procedimientos'])
            datos_detallados.append({
                'id_procedimiento': item['id_investigacion__id_procedimientos'],
                'nombres': item['nombre_propietario'],
                'apellidos': item['apellido_propietario'],
                'cedula': busqueda
            })

        for item in ids_investigacion_estructura:
            procedimientos_ids.add(item['id_investigacion__id_procedimientos'])
            datos_detallados.append({
                'id_procedimiento': item['id_investigacion__id_procedimientos'],
                'nombres': item['nombre'],
                'apellidos': item['apellido'],
                'cedula': busqueda
            })

        # Agrega más tablas si es necesario

        # Filtrar procedimientos principales
        procedimientos = Procedimientos.objects.filter(id__in=procedimientos_ids)

        # Convertir datos_detallados a un diccionario para un acceso rápido
        datos_detallados_dict = {dato['id_procedimiento']: dato for dato in datos_detallados}

        # Asegurarte de que solo emparejas procedimientos con datos detallados válidos
        datos_combinados = []
        for procedimiento in procedimientos:
            id_procedimiento = procedimiento.id
            if id_procedimiento in datos_detallados_dict:
                datos_combinados.append({
                    'procedimiento': procedimiento,
                    'detalles': datos_detallados_dict[id_procedimiento]
                })

    # Renderizar la vista con los datos combinados correctamente
    return render(request, 'antecedentes.html', 
                {
                    "user": user,
                    "jerarquia": user["jerarquia"],
                    "nombres": user["nombres"],
                    "apellidos": user["apellidos"],
                    "form": form,
                    'datos': datos_combinados,  # Lista de diccionarios con 'procedimiento' y 'detalles'
                })

def View_Procedimiento_Editar(request):
    user = request.session.get('user')
    if not user:
        return redirect('/')

    result = None

    if request.method == 'POST':
        id = request.POST["id_editar"]
        form = SelectorDivision(request.POST, prefix='form1')
        form2 = SeleccionarInfo(request.POST, prefix='form2')
        form3 = Datos_Ubicacion(request.POST, prefix='form3')
        form4 = Selecc_Tipo_Procedimiento(request.POST, prefix='form4')
        abast_agua = formulario_abastecimiento_agua(request.POST, prefix='abast_agua')
        apoyo_unid = Formulario_apoyo_unidades(request.POST, prefix='apoyo_unid')
        guard_prev = Formulario_guardia_prevencion(request.POST, prefix='guard_prev')
        atend_no_efec = Formulario_atendido_no_efectuado(request.POST, prefix='atend_no_efec')
        desp_seguridad = Formulario_despliegue_seguridad(request.POST, prefix='desp_seguridad')
        fals_alarm = Formulario_falsa_alarma(request.POST, prefix='fals_alarm')
        serv_especial = Formulario_Servicios_Especiales(request.POST, prefix='serv_especial')
        form_fallecido = Formulario_Fallecidos(request.POST, prefix='form_fallecido')
        rescate_form = Formulario_Rescate(request.POST, prefix='rescate_form')
        incendio_form = Formulario_Incendio(request.POST, prefix='incendio_form')
        retencion_preventiva_incendio = Formulario_Retencion_Preventiva_Incendio(request.POST, prefix='retencion_preventiva_incendio')
        atenciones_paramedicas = Formulario_Atenciones_Paramedicas(request.POST, prefix='atenciones_paramedicas')

        emergencias_medicas = Formulario_Emergencias_Medicas(request.POST, prefix='emergencias_medicas')
        traslados_emergencias = Formulario_Traslados(request.POST, prefix='traslados_emergencias')

        persona_presente_form = Formulario_Persona_Presente(request.POST, prefix='persona_presente_form')
        detalles_vehiculo_form = Formulario_Detalles_Vehiculos(request.POST, prefix='detalles_vehiculo_form')

        formulario_accidentes_transito = Formulario_Accidentes_Transito(request.POST, prefix='formulario_accidentes_transito')
        detalles_lesionados_accidentes = Formulario_Detalles_Lesionados(request.POST, prefix='detalles_lesionados_accidentes')
        detalles_lesionados_accidentes2 = Formulario_Detalles_Lesionados2(request.POST, prefix='detalles_lesionados_accidentes2')
        detalles_lesionados_accidentes3 = Formulario_Detalles_Lesionados3(request.POST, prefix='detalles_lesionados_accidentes3')
        traslados_accidentes = Formulario_Traslado_Accidente(request.POST, prefix='traslados_accidentes')
        traslados_accidentes2 = Formulario_Traslado_Accidente2(request.POST, prefix='traslados_accidentes2')
        traslados_accidentes3 = Formulario_Traslado_Accidente3(request.POST, prefix='traslados_accidentes3')
        detalles_vehiculo_accidentes = Formulario_Detalles_Vehiculos(request.POST, prefix='detalles_vehiculos_accidentes')
        detalles_vehiculo_accidentes2 = Formulario_Detalles_Vehiculos2(request.POST, prefix='detalles_vehiculos_accidentes2')
        detalles_vehiculo_accidentes3 = Formulario_Detalles_Vehiculos3(request.POST, prefix='detalles_vehiculos_accidentes3')

        rescate_form_persona = Formulario_Rescate_Persona(request.POST, prefix='rescate_form_persona')
        rescate_form_animal = Formulario_Rescate_Animal(request.POST, prefix='rescate_form_animal')

        evaluacion_riesgo_form = Forulario_Evaluacion_Riesgo(request.POST, prefix='evaluacion_riesgo_form')
        mitigacion_riesgo_form = Formulario_Mitigacion_Riesgos(request.POST, prefix='mitigacion_riesgo_form')
        vehiculo_derrame_form = Detalles_Vehiculo_Derrame_Form(request.POST, prefix='vehiculo_derrame_form')
        vehiculo_derrame_form2 = Detalles_Vehiculo_Derrame_Form2(request.POST, prefix='vehiculo_derrame_form2')
        vehiculo_derrame_form3 = Detalles_Vehiculo_Derrame_Form3(request.POST, prefix='vehiculo_derrame_form3')

        puesto_avanzada_form = Formulario_Puesto_Avanzada(request.POST, prefix='puesto_avanzada_form')
        traslados_prehospitalaria_form = Formulario_Traslados_Prehospitalaria(request.POST, prefix='traslados_prehospitalaria_form')
        asesoramiento_form = Formulario_Asesoramiento(request.POST, prefix='asesoramiento_form')
        persona_presente_eval_form = Formularia_Persona_Presente_Eval(request.POST, prefix='persona_presente_eval_form')
        reinspeccion_prevencion = Formulario_Reinspeccion_Prevencion(request.POST, prefix='reinspeccion_prevencion')
        retencion_preventiva = Formulario_Retencion_Preventiva(request.POST, prefix='retencion_preventiva')

        artificios_pirotecnico = Formulario_Artificios_Pirotecnicos(request.POST, prefix='artificios_pirotecnico')
        lesionados = Formulario_Lesionado(request.POST, prefix='lesionados')
        incendio_art = Formulario_Incendio_Art(request.POST, prefix='incendio_art')
        persona_presente_art = Formulario_Persona_Presente_Art(request.POST, prefix='persona_presente_art')
        detalles_vehiculo_art = Formulario_Detalles_Vehiculos_Incendio_Art(request.POST, prefix='detalles_vehiculo_art')
        fallecidos_art = Formulario_Fallecidos_Art(request.POST, prefix='fallecidos_art')
        inspeccion_artificios_pir = Formulario_Inspeccion_Establecimiento_Art(request.POST, prefix='inspeccion_artificios_pir')
        form_enfermeria = Formulario_Enfermeria(request.POST, prefix='form_enfermeria')
        servicios_medicos = Formulario_Servicios_medicos(request.POST, prefix='form_servicios_medicos')
        psicologia = Formulario_psicologia(request.POST,prefix='form_psicologia')
        capacitacion = Formulario_capacitacion(request.POST,prefix='form_capacitacion')
        form_valoracion_medica = Formulario_Valoracion_Medica(request.POST, prefix='form_valoracion_medica')
        form_detalles_enfermeria = Formulario_Detalles_Enfermeria(request.POST, prefix='form_detalles_enfermeria')
        form_detalles_psicologia = Formulario_Procedimientos_Psicologia(request.POST, prefix='form_detalles_psicologia')
        
        form_capacitacion = Formulario_Capacitacion_Proc(request.POST,prefix='form_capacitacion')
        form_brigada = Formulario_Brigada(request.POST,prefix='form_brigada')
        form_frente_preventivo = Formulario_Frente_Preventivo(request.POST,prefix='form_frente_preventivo')
        form_jornada_medica = Formulario_Jornada_Medica(request.POST, prefix='form_jornada_medica')

        form_inspecciones = Formulario_Inspecciones(request.POST, prefix='form_inspecciones')
        form_inspecciones_prevencion = Formulario_Inspeccion_Prevencion_Asesorias_Tecnicas(request.POST, prefix='form_inspecciones_prevencion')
        form_inspecciones_habitabilidad = Formulario_Inspeccion_Habitabilidad(request.POST, prefix='form_inspecciones_habitabilidad')
        form_inspecciones_arbol = Formulario_Inspeccion_Arbol(request.POST, prefix='form_inspecciones_arbol')
        form_inspecciones_otros = Formulario_Inspeccion_Otros(request.POST, prefix='form_inspecciones_otros')

        form_investigacion = Formulario_Investigacion(request.POST, prefix='form_investigacion')
        form_inv_vehiculo = Formulario_Investigacion_Vehiculo(request.POST, prefix='form_inv_vehiculo')
        form_inv_comercio = Formulario_Investigacion_Comercio(request.POST, prefix='form_inv_comercio')
        form_inv_estructura = Formulario_Investigacion_Estructura_Vivienda(request.POST, prefix='form_inv_estructura')
        
        form_comision = Datos_Comision(request.POST, prefix='form_comision')
        datos_comision_uno = Comision_Uno(request.POST, prefix='datos_comision_uno')
        datos_comision_dos = Comision_Dos(request.POST, prefix='datos_comision_dos')
        datos_comision_tres = Comision_Tres(request.POST, prefix='datos_comision_tres')
        
        # Imprimir request.POST para depuración
        if not form.is_valid():
            print("Errores en form1:", form.errors)
            result = True
        if not form2.is_valid():
            print("Errores en form2:", form2.errors)
            result = True
        if not form3.is_valid():
            print("Errores en form3:", form3.errors)
            result = True
        if not form4.is_valid():
            print("Errores en form4:", form4.errors)
            result = True

        if form.is_valid():
            result = False

            procedimiento = Procedimientos.objects.get(id=id) 
            division = form.cleaned_data["opciones"]
            tipo_procedimiento = ""

            if (division == "1" or division == "2" or division == "3" or division == "4" or division == "5") and (
            form2.is_valid() and form3.is_valid() and form4.is_valid() and 
            form_comision.is_valid() and datos_comision_uno.is_valid() and 
            datos_comision_dos.is_valid() and datos_comision_tres.is_valid()
                ):
                # Obtener los datos del formulario
                solicitante = form2.cleaned_data["solicitante"]
                solicitante_externo = form2.cleaned_data["solicitante_externo"]
                jefe_comision = form2.cleaned_data["jefe_comision"]
                municipio = form3.cleaned_data["municipio"]
                tipo_procedimiento = form4.cleaned_data["tipo_procedimiento"]
                parroquia = form3.cleaned_data["parroquia"]

                # Obtener las instancias relacionadas
                division_instance = Divisiones.objects.get(id=division)
                jefe_comision_instance = Personal.objects.get(id=jefe_comision)
                municipio_instance = Municipios.objects.get(id=municipio)
                tipo_procedimiento_instance = Tipos_Procedimientos.objects.get(id=tipo_procedimiento)

                if solicitante:
                    solicitante_instance = Personal.objects.get(id=solicitante)
                else:
                    solicitante_instance = None

                if solicitante_externo == "":
                    solicitante_externo = ""

                # Actualizar los campos del procedimiento
                procedimiento.id_division = division_instance
                procedimiento.id_solicitante = solicitante_instance
                procedimiento.solicitante_externo = solicitante_externo
                procedimiento.efectivos_enviados = form2.cleaned_data["efectivos_enviados"]
                procedimiento.id_jefe_comision = jefe_comision_instance
                procedimiento.id_municipio = municipio_instance
                procedimiento.direccion = form3.cleaned_data["direccion"]
                procedimiento.fecha = form3.cleaned_data["fecha"]
                procedimiento.hora = form3.cleaned_data["hora"]
                procedimiento.id_tipo_procedimiento = tipo_procedimiento_instance

                # Asignar parroquia si está presente
                if parroquia:
                    parroquia_instance = Parroquias.objects.get(id=parroquia)
                    procedimiento.id_parroquia = parroquia_instance
                else:
                    procedimiento_instance = Parroquias.objects.get(id=0)
                    procedimiento.id_parroquia = procedimiento_instance

                # Manejar el campo "unidad" si aplica
                if division != "3":
                    unidad = form2.cleaned_data["unidad"]
                    unidad_instance = Unidades.objects.get(id=unidad)
                    procedimiento.unidad = unidad_instance

                # Guardar los cambios en la base de datos
                procedimiento.save()


                if form_comision.cleaned_data["agregar"] == True:
                    # Obtén todas las comisiones relacionadas con el procedimiento
                    detalles_comisiones = list(Comisiones.objects.filter(procedimiento=procedimiento))

                    # Listado de formularios de comisiones y sus datos
                    formularios_comisiones = [
                        datos_comision_uno,
                        datos_comision_dos,
                        datos_comision_tres,
                    ]

                    for idx, formulario in enumerate(formularios_comisiones):
                        if formulario.is_valid():
                            # Validar que el campo 'comision' no esté vacío antes de proceder
                            comision = formulario.cleaned_data.get("comision")
                            if not comision:
                                continue  # Saltar este formulario si no tiene un valor válido para 'comision'

                            cedula = formulario.cleaned_data["cedula_oficial"]
                            nacionalidad = formulario.cleaned_data["nacionalidad"]
                            tipo_comision_instance = Tipos_Comision.objects.get(id=comision)

                            # Determinar si modificar o crear la comisión
                            if idx < len(detalles_comisiones):
                                # Modificar una comisión existente
                                comision_instance = detalles_comisiones[idx]
                            else:
                                # Crear una nueva comisión
                                comision_instance = Comisiones(procedimiento=procedimiento)

                            # Asignar datos al objeto de comisión
                            comision_instance.comision = tipo_comision_instance
                            comision_instance.nombre_oficial = formulario.cleaned_data["nombre_oficial"]
                            comision_instance.apellido_oficial = formulario.cleaned_data["apellido_oficial"]
                            comision_instance.cedula_oficial = f"{nacionalidad}-{cedula}"
                            comision_instance.nro_unidad = formulario.cleaned_data["nro_unidad"]
                            comision_instance.nro_cuadrante = formulario.cleaned_data["nro_cuadrante"]
                            comision_instance.save()



                    # Si necesitas manejar más comisiones, puedes seguir el patrón anterior

            if division == "6" and form_enfermeria.is_valid():
                
                municipio = form3.cleaned_data["municipio"]
                tipo_procedimiento = form4.cleaned_data["tipo_procedimiento"]
                parroquia = form3.cleaned_data["parroquia"]

                division_instance = Divisiones.objects.get(id=division)
                municipio_instance = Municipios.objects.get(id=municipio)
                tipo_procedimiento_instance = Tipos_Procedimientos.objects.get(id=tipo_procedimiento)

                encargado_area = form_enfermeria.cleaned_data["encargado_area"]

                if encargado_area == "Otro":
                    encargado_area = form_enfermeria.cleaned_data["especifique"]

                procedimiento.id_division = division_instance
                procedimiento.dependencia = form_enfermeria.cleaned_data["dependencia"]
                procedimiento.solicitante_externo = encargado_area
                procedimiento.id_municipio = municipio_instance
                procedimiento.direccion = form3.cleaned_data["direccion"]
                procedimiento.fecha = form3.cleaned_data["fecha"]
                procedimiento.hora = form3.cleaned_data["hora"]
                procedimiento.id_tipo_procedimiento = tipo_procedimiento_instance

                # # Solo asignar parroquia si está presente
                if parroquia:
                    parroquia_instance = Parroquias.objects.get(id=parroquia)
                    procedimiento.id_parroquia = parroquia_instance
                else:
                    procedimiento_instance = Parroquias.objects.get(id=0)
                    procedimiento.id_parroquia = procedimiento_instance

                procedimiento.save()
            
            if division == "7" and servicios_medicos.is_valid():
                municipio = form3.cleaned_data["municipio"]
                tipo_procedimiento = form4.cleaned_data["tipo_procedimiento"]
                parroquia = form3.cleaned_data["parroquia"]

                division_instance = Divisiones.objects.get(id=division)
                municipio_instance = Municipios.objects.get(id=municipio)
                tipo_procedimiento_instance = Tipos_Procedimientos.objects.get(id=tipo_procedimiento)

                procedimiento.id_division = division_instance
                procedimiento.tipo_servicio = servicios_medicos.cleaned_data["tipo_servicio"]
                procedimiento.solicitante_externo = servicios_medicos.cleaned_data["jefe_area"]
                procedimiento.id_municipio = municipio_instance
                procedimiento.direccion = form3.cleaned_data["direccion"]
                procedimiento.fecha = form3.cleaned_data["fecha"]
                procedimiento.hora = form3.cleaned_data["hora"]
                procedimiento.id_tipo_procedimiento = tipo_procedimiento_instance

                # # Solo asignar parroquia si está presente
                if parroquia:
                    parroquia_instance = Parroquias.objects.get(id=parroquia)
                    procedimiento.id_parroquia = parroquia_instance
                else:
                    procedimiento_instance = Parroquias.objects.get(id=0)
                    procedimiento.id_parroquia = procedimiento_instance

                procedimiento.save()

            if division == "8" and psicologia.is_valid():
                municipio = form3.cleaned_data["municipio"]
                tipo_procedimiento = form4.cleaned_data["tipo_procedimiento"]
                parroquia = form3.cleaned_data["parroquia"]

                division_instance = Divisiones.objects.get(id=division)
                municipio_instance = Municipios.objects.get(id=municipio)
                tipo_procedimiento_instance = Tipos_Procedimientos.objects.get(id=tipo_procedimiento)

                procedimiento.id_division = division_instance
                procedimiento.solicitante_externo = psicologia.cleaned_data["jefe_area"]
                procedimiento.id_municipio = municipio_instance
                procedimiento.direccion =  form3.cleaned_data["direccion"]
                procedimiento.fecha = form3.cleaned_data["fecha"]
                procedimiento.hora = form3.cleaned_data["hora"]
                procedimiento.id_tipo_procedimiento = tipo_procedimiento_instance

                # # Solo asignar parroquia si está presente
                if parroquia:
                    parroquia_instance = Parroquias.objects.get(id=parroquia)
                    procedimiento.id_parroquia = parroquia_instance
                else:
                    procedimiento_instance = Parroquias.objects.get(id=0)
                    procedimiento.id_parroquia = procedimiento_instance

                procedimiento.save()

            if division == "9" and capacitacion.is_valid():
                dependencia = capacitacion.cleaned_data["dependencia"]
                instructor = capacitacion.cleaned_data["instructor"]
                solicitante = capacitacion.cleaned_data["solicitante"]
                solicitante_externo = capacitacion.cleaned_data["solicitante_externo"]
                municipio = form3.cleaned_data["municipio"]

                parroquia = form3.cleaned_data["parroquia"]
                tipo_procedimiento = 45

                division_instance = Divisiones.objects.get(id=division)
                municipio_instance = Municipios.objects.get(id=municipio)
                tipo_procedimiento_instance = Tipos_Procedimientos.objects.get(id=tipo_procedimiento)
                jefe_comision_instance = Personal.objects.get(id=instructor)

                if solicitante:
                    solicitante_instance = Personal.objects.get(id=solicitante)

                if solicitante_externo=="":
                    solicitante_externo = ""

                procedimiento.id_division = division_instance
                procedimiento.dependencia = dependencia
                procedimiento.id_jefe_comision = jefe_comision_instance
                procedimiento.solicitante_externo = solicitante_externo
                procedimiento.id_solicitante = solicitante_instance
                procedimiento.id_municipio = municipio_instance
                procedimiento.direccion = form3.cleaned_data["direccion"]
                procedimiento.fecha = form3.cleaned_data["fecha"]
                procedimiento.hora = form3.cleaned_data["hora"]
                procedimiento.id_tipo_procedimiento = tipo_procedimiento_instance
                
                # # Solo asignar parroquia si está presente
                if parroquia:
                    parroquia_instance = Parroquias.objects.get(id=parroquia)
                    procedimiento.id_parroquia = parroquia_instance
                else:
                    procedimiento_instance = Parroquias.objects.get(id=0)
                    procedimiento.id_parroquia = procedimiento_instance

                procedimiento.save()

                # Terminar de aqui para abajo

                if dependencia == "Capacitacion" and form_capacitacion.is_valid():

                    detalles_capacitacion = Procedimientos_Capacitacion.objects.get(id_procedimientos=procedimiento.id);

                    detalles_capacitacion.tipo_capacitacion = form_capacitacion.cleaned_data["tipo_capacitacion"]
                    detalles_capacitacion.tipo_clasificacion = form_capacitacion.cleaned_data["tipo_clasificacion"]
                    detalles_capacitacion.personas_beneficiadas = form_capacitacion.cleaned_data["personas_beneficiadas"]
                    detalles_capacitacion.descripcion = form_capacitacion.cleaned_data["descripcion"]
                    detalles_capacitacion.material_utilizado = form_capacitacion.cleaned_data["material_utilizado"]
                    detalles_capacitacion.status = form_capacitacion.cleaned_data["status"]

                    detalles_capacitacion.save()

                if dependencia == "Brigada Juvenil" and form_brigada.is_valid():

                    detalles_brigada = Procedimientos_Brigada.objects.get(id_procedimientos=procedimiento.id);

                    tipo_capacitacion = form_brigada.cleaned_data["tipo_capacitacion"]

                    if tipo_capacitacion == "Otros":
                        tipo_capacitacion = form_brigada.cleaned_data["otros"]

                    detalles_brigada.tipo_capacitacion = tipo_capacitacion
                    detalles_brigada.tipo_clasificacion = form_brigada.cleaned_data["tipo_clasificacion"]
                    detalles_brigada.personas_beneficiadas = form_brigada.cleaned_data["personas_beneficiadas"]
                    detalles_brigada.descripcion = form_brigada.cleaned_data["descripcion"]
                    detalles_brigada.material_utilizado = form_brigada.cleaned_data["material_utilizado"]
                    detalles_brigada.status = form_brigada.cleaned_data["status"]

                    detalles_brigada.save()

                if dependencia == "Frente Preventivo" and form_frente_preventivo.is_valid():

                    detalles_frente = Procedimientos_Frente_Preventivo.objects.get(id_procedimientos=procedimiento.id);

                    detalles_frente.nombre_actividad = form_frente_preventivo.cleaned_data["nombre_actividad"]
                    detalles_frente.estrategia = form_frente_preventivo.cleaned_data["estrategia"]
                    detalles_frente.personas_beneficiadas = form_frente_preventivo.cleaned_data["personas_beneficiadas"]
                    detalles_frente.descripcion = form_frente_preventivo.cleaned_data["descripcion"]
                    detalles_frente.material_utilizado = form_frente_preventivo.cleaned_data["material_utilizado"]
                    detalles_frente.status = form_frente_preventivo.cleaned_data["status"]

                    detalles_frente.save()

            # # Ahora dependiendo del tipo de procedimiento, verifica el formulario correspondiente y guarda la instancia
            # Terminado
            if tipo_procedimiento == "1" and abast_agua.is_valid():

                detalles_procedimiento = Abastecimiento_agua.objects.get(id_procedimiento = procedimiento)

                # Abastecimiento de Agua
                nacionalidad=abast_agua.cleaned_data["nacionalidad"]
                cedula=abast_agua.cleaned_data["cedula"]

                detalles_procedimiento.id_tipo_servicio = Tipo_Institucion.objects.get(id=abast_agua.cleaned_data["tipo_servicio"])
                detalles_procedimiento.nombres = abast_agua.cleaned_data["nombres"]
                detalles_procedimiento.apellidos = abast_agua.cleaned_data["apellidos"]
                detalles_procedimiento.cedula = f"{nacionalidad}-{cedula}"
                detalles_procedimiento.ltrs_agua = abast_agua.cleaned_data["ltrs_agua"]
                detalles_procedimiento.personas_atendidas = abast_agua.cleaned_data["personas_atendidas"]
                detalles_procedimiento.descripcion = abast_agua.cleaned_data["descripcion"]
                detalles_procedimiento.material_utilizado = abast_agua.cleaned_data["material_utilizado"]
                detalles_procedimiento.status = abast_agua.cleaned_data["status"]

                detalles_procedimiento.save()

            # Terminado
            if tipo_procedimiento == "2" and apoyo_unid.is_valid():

                detalles_procedimiento = Apoyo_Unidades.objects.get(id_procedimiento = procedimiento)

                tipo_apoyo_instance = Tipo_apoyo.objects.get(id=apoyo_unid.cleaned_data["tipo_apoyo"])

                detalles_procedimiento.id_tipo_apoyo = tipo_apoyo_instance
                detalles_procedimiento.unidad_apoyada = apoyo_unid.cleaned_data["unidad_apoyada"]
                detalles_procedimiento.descripcion = apoyo_unid.cleaned_data["descripcion"]
                detalles_procedimiento.material_utilizado = apoyo_unid.cleaned_data["material_utilizado"]
                detalles_procedimiento.status = apoyo_unid.cleaned_data["status"]

                detalles_procedimiento.save()

            # Terminado
            if tipo_procedimiento == "3" and guard_prev.is_valid():

                detalles_procedimiento = Guardia_prevencion.objects.get(id_procedimiento = procedimiento)
                Tipo_Motivo_instance = Motivo_Prevencion.objects.get(id=guard_prev.cleaned_data["motivo_prevencion"])

                detalles_procedimiento.id_motivo_prevencion = Tipo_Motivo_instance 
                detalles_procedimiento.descripcion = guard_prev.cleaned_data["descripcion"]
                detalles_procedimiento.material_utilizado = guard_prev.cleaned_data["material_utilizado"]
                detalles_procedimiento.status = guard_prev.cleaned_data["status"]

                detalles_procedimiento.save()

            # Terminado
            if tipo_procedimiento == "4" and atend_no_efec.is_valid():
                
                detalles_procedimiento = Atendido_no_Efectuado.objects.get(id_procedimiento = procedimiento)

                detalles_procedimiento.descripcion = atend_no_efec.cleaned_data["descripcion"]
                detalles_procedimiento.material_utilizado = atend_no_efec.cleaned_data["material_utilizado"]
                detalles_procedimiento.status = atend_no_efec.cleaned_data["status"]

                detalles_procedimiento.save()

            # Terminado
            if tipo_procedimiento == "5" and desp_seguridad.is_valid():

                detalles_procedimiento = Despliegue_Seguridad.objects.get(id_procedimiento = procedimiento) 
                Tipo_Motivo_instance = Motivo_Despliegue.objects.get(id=desp_seguridad.cleaned_data["motv_despliegue"])

                detalles_procedimiento.descripcion = desp_seguridad.cleaned_data["descripcion"]
                detalles_procedimiento.material_utilizado = desp_seguridad.cleaned_data["material_utilizado"]
                detalles_procedimiento.status = desp_seguridad.cleaned_data["status"]
                detalles_procedimiento.motivo_despliegue = Tipo_Motivo_instance

                detalles_procedimiento.save()

            # Terminado
            if tipo_procedimiento == "6" and fals_alarm.is_valid():
                
                detalles_procedimiento = Falsa_Alarma.objects.get(id_procedimiento = procedimiento) 
                Tipo_Motivo_instance = Motivo_Alarma.objects.get(id=fals_alarm.cleaned_data["motv_alarma"])

                detalles_procedimiento.motivo_alarma = Tipo_Motivo_instance
                detalles_procedimiento.descripcion = fals_alarm.cleaned_data["descripcion"]
                detalles_procedimiento.material_utilizado = fals_alarm.cleaned_data["material_utilizado"]
                detalles_procedimiento.status = fals_alarm.cleaned_data["status"]

                detalles_procedimiento.save()

            # Terminado 
            if tipo_procedimiento == "7" and atenciones_paramedicas.is_valid():

                detalles_procedimiento = Atenciones_Paramedicas.objects.get(id_procedimientos = procedimiento) 

                detalles_procedimiento.tipo_atencion = atenciones_paramedicas.cleaned_data["tipo_atencion"]

                detalles_procedimiento.save()

                if detalles_procedimiento.tipo_atencion == "Emergencias Medicas" and emergencias_medicas.is_valid():

                    detalles_emergencias = Emergencias_Medicas.objects.get(id_atencion = detalles_procedimiento)
                    nacionalidad = emergencias_medicas.cleaned_data["nacionalidad"]
                    cedula = emergencias_medicas.cleaned_data["cedula"]

                    detalles_emergencias.nombres = emergencias_medicas.cleaned_data["nombre"]
                    detalles_emergencias.apellidos = emergencias_medicas.cleaned_data["apellido"]
                    detalles_emergencias.cedula = f"{nacionalidad}-{cedula}"
                    detalles_emergencias.edad = emergencias_medicas.cleaned_data["edad"]
                    detalles_emergencias.sexo = emergencias_medicas.cleaned_data["sexo"]
                    detalles_emergencias.idx = emergencias_medicas.cleaned_data["idx"]
                    detalles_emergencias.descripcion = emergencias_medicas.cleaned_data["descripcion"]
                    detalles_emergencias.material_utilizado = emergencias_medicas.cleaned_data["material_utilizado"]
                    detalles_emergencias.status = emergencias_medicas.cleaned_data["status"]
                    
                    trasladado = emergencias_medicas.cleaned_data["trasladado"]

                    detalles_emergencias.save()

                    if trasladado == True and traslados_emergencias.is_valid():
                        # Intenta obtener el traslado relacionado con el lesionado
                        detalles_traslado = Traslado.objects.filter(id_lesionado=detalles_emergencias).first()

                        if detalles_traslado:
                            # Modifica el traslado existente
                            detalles_traslado.hospital_trasladado = traslados_emergencias.cleaned_data["hospital_trasladado"]
                            detalles_traslado.medico_receptor = traslados_emergencias.cleaned_data["medico_receptor"]
                            detalles_traslado.mpps_cmt = traslados_emergencias.cleaned_data["mpps_cmt"]
                        else:
                            # Crea un nuevo traslado si no existe
                            detalles_traslado = Traslado(
                                id_lesionado=detalles_emergencias,
                                hospital_trasladado=traslados_emergencias.cleaned_data["hospital_trasladado"],
                                medico_receptor=traslados_emergencias.cleaned_data["medico_receptor"],
                                mpps_cmt=traslados_emergencias.cleaned_data["mpps_cmt"],
                            )

                        detalles_traslado.save()

                if detalles_procedimiento.tipo_atencion == "Accidentes de Transito" and formulario_accidentes_transito.is_valid():
                    detalles_accidente = Accidentes_Transito.objects.get(id_atencion=detalles_procedimiento)
                    tipo_accidente_instance = Tipo_Accidente.objects.get(id=formulario_accidentes_transito.cleaned_data["tipo_accidente"])

                    # Actualizar detalles del accidente
                    detalles_accidente.tipo_de_accidente = tipo_accidente_instance
                    detalles_accidente.cantidad_lesionados = formulario_accidentes_transito.cleaned_data["cantidad_lesionado"]
                    detalles_accidente.material_utilizado = formulario_accidentes_transito.cleaned_data["material_utilizado"]
                    detalles_accidente.status = formulario_accidentes_transito.cleaned_data["status"]
                    
                    detalles_accidente.save()

                    agg_vehiculo = formulario_accidentes_transito.cleaned_data["agg_vehiculo"]
                    agg_lesionado = formulario_accidentes_transito.cleaned_data["agg_lesionado"]

                    # Editar vehículos existentes
                    if agg_vehiculo == True and detalles_vehiculo_accidentes.is_valid():
                        placas1 = detalles_vehiculo_accidentes.cleaned_data["placas"]
                        agg_vehiculo2 = detalles_vehiculo_accidentes.cleaned_data["agg_vehiculo"]

                        # Buscar o crear el vehículo con la placa
                        vehiculo, created = Detalles_Vehiculos_Accidente.objects.get_or_create(
                            id_vehiculo=detalles_accidente,
                            placas=placas1,
                            defaults={
                                "modelo": detalles_vehiculo_accidentes.cleaned_data["modelo"],
                                "marca": detalles_vehiculo_accidentes.cleaned_data["marca"],
                                "color": detalles_vehiculo_accidentes.cleaned_data["color"],
                                "año": detalles_vehiculo_accidentes.cleaned_data["año"],
                            }
                        )
                        if not created:  # Si ya existe, actualizar los datos
                            vehiculo.modelo = detalles_vehiculo_accidentes.cleaned_data["modelo"]
                            vehiculo.marca = detalles_vehiculo_accidentes.cleaned_data["marca"]
                            vehiculo.color = detalles_vehiculo_accidentes.cleaned_data["color"]
                            vehiculo.año = detalles_vehiculo_accidentes.cleaned_data["año"]
                            vehiculo.save()

                        # Verificar y manejar vehículos adicionales
                        if detalles_vehiculo_accidentes2.is_valid() and agg_vehiculo2:
                            placas2 = detalles_vehiculo_accidentes2.cleaned_data["placas"]
                            agg_vehiculo3 = detalles_vehiculo_accidentes2.cleaned_data["agg_vehiculo"]

                            vehiculo2, created = Detalles_Vehiculos_Accidente.objects.get_or_create(
                                id_vehiculo=detalles_accidente,
                                placas=placas2,
                                defaults={
                                    "modelo": detalles_vehiculo_accidentes2.cleaned_data["modelo"],
                                    "marca": detalles_vehiculo_accidentes2.cleaned_data["marca"],
                                    "color": detalles_vehiculo_accidentes2.cleaned_data["color"],
                                    "año": detalles_vehiculo_accidentes2.cleaned_data["año"],
                                }
                            )
                            if not created:
                                vehiculo2.modelo = detalles_vehiculo_accidentes2.cleaned_data["modelo"]
                                vehiculo2.marca = detalles_vehiculo_accidentes2.cleaned_data["marca"]
                                vehiculo2.color = detalles_vehiculo_accidentes2.cleaned_data["color"]
                                vehiculo2.año = detalles_vehiculo_accidentes2.cleaned_data["año"]
                                vehiculo2.save()

                            if detalles_vehiculo_accidentes3.is_valid() and agg_vehiculo3:
                                placas3 = detalles_vehiculo_accidentes3.cleaned_data["placas"]

                                vehiculo3, created = Detalles_Vehiculos_Accidente.objects.get_or_create(
                                    id_vehiculo=detalles_accidente,
                                    placas=placas3,
                                    defaults={
                                        "modelo": detalles_vehiculo_accidentes3.cleaned_data["modelo"],
                                        "marca": detalles_vehiculo_accidentes3.cleaned_data["marca"],
                                        "color": detalles_vehiculo_accidentes3.cleaned_data["color"],
                                        "año": detalles_vehiculo_accidentes3.cleaned_data["año"],
                                    }
                                )
                                if not created:
                                    vehiculo3.modelo = detalles_vehiculo_accidentes3.cleaned_data["modelo"]
                                    vehiculo3.marca = detalles_vehiculo_accidentes3.cleaned_data["marca"]
                                    vehiculo3.color = detalles_vehiculo_accidentes3.cleaned_data["color"]
                                    vehiculo3.año = detalles_vehiculo_accidentes3.cleaned_data["año"]
                                    vehiculo3.save()

                    # Editar o agregar lesionados existentes
                    if agg_lesionado == True and detalles_lesionados_accidentes.is_valid():
                        cedula1 = f"{detalles_lesionados_accidentes.cleaned_data['nacionalidad']}-{detalles_lesionados_accidentes.cleaned_data['cedula']}"
                        agg_lesionado2 = detalles_lesionados_accidentes.cleaned_data["otro_lesionado"]

                        # Buscar o crear el lesionado
                        lesionado, created = Lesionados.objects.get_or_create(
                            id_accidente=detalles_accidente,
                            cedula=cedula1,
                            defaults={
                                "nombres": detalles_lesionados_accidentes.cleaned_data["nombre"],
                                "apellidos": detalles_lesionados_accidentes.cleaned_data["apellido"],
                                "edad": detalles_lesionados_accidentes.cleaned_data["edad"],
                                "sexo": detalles_lesionados_accidentes.cleaned_data["sexo"],
                                "idx": detalles_lesionados_accidentes.cleaned_data["idx"],
                                "descripcion": detalles_lesionados_accidentes.cleaned_data["descripcion"],
                            }
                        )
                        if not created:
                            lesionado.nombres = detalles_lesionados_accidentes.cleaned_data["nombre"]
                            lesionado.apellidos = detalles_lesionados_accidentes.cleaned_data["apellido"]
                            lesionado.cedula = f"{detalles_lesionados_accidentes.cleaned_data['nacionalidad']}-{detalles_lesionados_accidentes.cleaned_data['cedula']}"
                            lesionado.edad = detalles_lesionados_accidentes.cleaned_data["edad"]
                            lesionado.sexo = detalles_lesionados_accidentes.cleaned_data["sexo"]
                            lesionado.idx = detalles_lesionados_accidentes.cleaned_data["idx"]
                            lesionado.descripcion = detalles_lesionados_accidentes.cleaned_data["descripcion"]
                            lesionado.save()

                        # Si el lesionado fue trasladado, manejar traslado
                        if traslados_accidentes.is_valid() and detalles_lesionados_accidentes.cleaned_data["trasladado"]:
                            traslado, created = Traslado_Accidente.objects.get_or_create(
                                id_lesionado=lesionado,
                                defaults={
                                    "hospital_trasladado": traslados_accidentes.cleaned_data["hospital_trasladado"],
                                    "medico_receptor": traslados_accidentes.cleaned_data["medico_receptor"],
                                    "mpps_cmt": traslados_accidentes.cleaned_data["mpps_cmt"],
                                }
                            )
                            if not created:
                                traslado.hospital_trasladado = traslados_accidentes.cleaned_data["hospital_trasladado"]
                                traslado.medico_receptor = traslados_accidentes.cleaned_data["medico_receptor"]
                                traslado.mpps_cmt = traslados_accidentes.cleaned_data["mpps_cmt"]
                                traslado.save()

                        # Verificar y manejar otros lesionados
                        if detalles_lesionados_accidentes2.is_valid() and agg_lesionado2:
                            cedula2 = f"{detalles_lesionados_accidentes2.cleaned_data['nacionalidad']}-{detalles_lesionados_accidentes2.cleaned_data['cedula']}"
                            agg_lesionado3 = detalles_lesionados_accidentes2.cleaned_data["otro_lesionado"]

                            lesionado2, created = Lesionados.objects.get_or_create(
                                id_accidente=detalles_accidente,
                                cedula=cedula2,
                                defaults={
                                    "nombres": detalles_lesionados_accidentes2.cleaned_data["nombre"],
                                    "apellidos": detalles_lesionados_accidentes2.cleaned_data["apellido"],
                                    "edad": detalles_lesionados_accidentes2.cleaned_data["edad"],
                                    "sexo": detalles_lesionados_accidentes2.cleaned_data["sexo"],
                                    "idx": detalles_lesionados_accidentes2.cleaned_data["idx"],
                                    "descripcion": detalles_lesionados_accidentes2.cleaned_data["descripcion"],
                                }
                            )
                            if not created:
                                lesionado2.cedula = f"{detalles_lesionados_accidentes2.cleaned_data['nacionalidad']}-{detalles_lesionados_accidentes2.cleaned_data['cedula']}"
                                lesionado2.nombres = detalles_lesionados_accidentes2.cleaned_data["nombre"]
                                lesionado2.apellidos = detalles_lesionados_accidentes2.cleaned_data["apellido"]
                                lesionado2.edad = detalles_lesionados_accidentes2.cleaned_data["edad"]
                                lesionado2.sexo = detalles_lesionados_accidentes2.cleaned_data["sexo"]
                                lesionado2.idx = detalles_lesionados_accidentes2.cleaned_data["idx"]
                                lesionado2.descripcion = detalles_lesionados_accidentes2.cleaned_data["descripcion"]
                                lesionado2.save()

                            if traslados_accidentes2.is_valid() and detalles_lesionados_accidentes2.cleaned_data["trasladado"]:
                                traslado, created = Traslado_Accidente.objects.get_or_create(
                                    id_lesionado=lesionado2,
                                    defaults={
                                        "hospital_trasladado": traslados_accidentes2.cleaned_data["hospital_trasladado"],
                                        "medico_receptor": traslados_accidentes2.cleaned_data["medico_receptor"],
                                        "mpps_cmt": traslados_accidentes2.cleaned_data["mpps_cmt"],
                                    }
                                )
                                if not created:
                                    traslado.hospital_trasladado = traslados_accidentes2.cleaned_data["hospital_trasladado"]
                                    traslado.medico_receptor = traslados_accidentes2.cleaned_data["medico_receptor"]
                                    traslado.mpps_cmt = traslados_accidentes2.cleaned_data["mpps_cmt"]
                                    traslado.save()

                        if detalles_lesionados_accidentes3.is_valid() and agg_lesionado3:
                            cedula3 = f"{detalles_lesionados_accidentes3.cleaned_data['nacionalidad']}-{detalles_lesionados_accidentes3.cleaned_data['cedula']}"

                            lesionado3, created = Lesionados.objects.get_or_create(
                                id_accidente=detalles_accidente,
                               cedula=cedula3,
                                defaults={
                                    "nombres": detalles_lesionados_accidentes3.cleaned_data["nombre"],
                                    "apellidos": detalles_lesionados_accidentes3.cleaned_data["apellido"],
                                    "edad": detalles_lesionados_accidentes3.cleaned_data["edad"],
                                    "sexo": detalles_lesionados_accidentes3.cleaned_data["sexo"],
                                    "idx": detalles_lesionados_accidentes3.cleaned_data["idx"],
                                    "descripcion": detalles_lesionados_accidentes3.cleaned_data["descripcion"],
                                }
                            )
                            if not created:
                                lesionado3.nombres = detalles_lesionados_accidentes3.cleaned_data["nombre"]
                                lesionado3.apellidos = detalles_lesionados_accidentes3.cleaned_data["apellido"]
                                lesionado3.cedula = f"{detalles_lesionados_accidentes3.cleaned_data['nacionalidad']}-{detalles_lesionados_accidentes3.cleaned_data['cedula']}"
                                lesionado3.edad = detalles_lesionados_accidentes3.cleaned_data["edad"]
                                lesionado3.sexo = detalles_lesionados_accidentes3.cleaned_data["sexo"]
                                lesionado3.idx = detalles_lesionados_accidentes3.cleaned_data["idx"]
                                lesionado3.descripcion = detalles_lesionados_accidentes3.cleaned_data["descripcion"]
                                lesionado3.save()

                            if traslados_accidentes3.is_valid() and detalles_lesionados_accidentes3.cleaned_data["trasladado"]:
                                traslado, created = Traslado_Accidente.objects.get_or_create(
                                    id_lesionado=lesionado3,
                                    defaults={
                                        "hospital_trasladado": traslados_accidentes3.cleaned_data["hospital_trasladado"],
                                        "medico_receptor": traslados_accidentes3.cleaned_data["medico_receptor"],
                                        "mpps_cmt": traslados_accidentes3.cleaned_data["mpps_cmt"],
                                    }
                                )
                                if not created:
                                    traslado.hospital_trasladado = traslados_accidentes3.cleaned_data["hospital_trasladado"]
                                    traslado.medico_receptor = traslados_accidentes3.cleaned_data["medico_receptor"]
                                    traslado.mpps_cmt = traslados_accidentes3.cleaned_data["mpps_cmt"]
                                    traslado.save()

            # Terminado
            if tipo_procedimiento == "9" and serv_especial.is_valid():
                
                detalles_procedimiento = Servicios_Especiales.objects.get(id_procedimientos = procedimiento)
                tipo_servicio = serv_especial.cleaned_data["tipo_servicio"]
                tipo_servicio_instance = Tipo_servicios.objects.get(id=tipo_servicio)
                
                detalles_procedimiento.descripcion = serv_especial.cleaned_data["descripcion"]
                detalles_procedimiento.material_utilizado = serv_especial.cleaned_data["material_utilizado"]
                detalles_procedimiento.status = serv_especial.cleaned_data["status"]
                detalles_procedimiento.tipo_servicio = tipo_servicio_instance

                detalles_procedimiento.save()

            # Terminado
            if tipo_procedimiento == "10" and rescate_form.is_valid():

                detalles_procedimiento = Rescate.objects.get(id_procedimientos = procedimiento)
                id_tipo_rescate = rescate_form.cleaned_data["tipo_rescate"]
                tipo_rescate_instance = Tipo_Rescate.objects.get(id=id_tipo_rescate)

                detalles_procedimiento.material_utilizado = rescate_form.cleaned_data["material_utilizado"]
                detalles_procedimiento.status = rescate_form.cleaned_data["status"]
                detalles_procedimiento.tipo_rescate = tipo_rescate_instance

                detalles_procedimiento.save()

                if id_tipo_rescate == "1" and rescate_form_animal.is_valid():

                    detalles_rescate = Rescate_Animal.objects.get(id_rescate = detalles_procedimiento)

                    detalles_rescate.especie = rescate_form_animal.cleaned_data["especie"]
                    detalles_rescate.descripcion = rescate_form_animal.cleaned_data["descripcion"]

                    detalles_rescate.save()

                else:
                    rescate_form_persona.is_valid()

                    detalles_rescate = Rescate_Persona.objects.get(id_rescate = detalles_procedimiento)
                    nacionalidad = rescate_form_persona.cleaned_data["nacionalidad"]
                    cedula_persona = rescate_form_persona.cleaned_data["cedula_persona"]

                    detalles_rescate.nombre = rescate_form_persona.cleaned_data["nombre_persona"]
                    detalles_rescate.apellidos = rescate_form_persona.cleaned_data["apellido_persona"]
                    detalles_rescate.cedula = f"{nacionalidad}-{cedula_persona}"
                    detalles_rescate.edad = rescate_form_persona.cleaned_data["edad_persona"]
                    detalles_rescate.sexo = rescate_form_persona.cleaned_data["sexo_persona"]
                    detalles_rescate.descripcion = rescate_form_persona.cleaned_data["descripcion"]

                    detalles_rescate.save()

            # Terminado
            if tipo_procedimiento == "11" and incendio_form.is_valid():

                detalles_procedimiento = Incendios.objects.get(id_procedimientos = procedimiento)
                id_tipo_incendio = incendio_form.cleaned_data["tipo_incendio"]
                tipo_incendio_instance = Tipo_Incendio.objects.get(id=id_tipo_incendio)

                detalles_procedimiento.id_tipo_incendio = tipo_incendio_instance
                detalles_procedimiento.descripcion = incendio_form.cleaned_data["descripcion"]
                detalles_procedimiento.material_utilizado = incendio_form.cleaned_data["material_utilizado"]
                detalles_procedimiento.status = incendio_form.cleaned_data["status"]

                detalles_procedimiento.save()

                check_agregar_persona = incendio_form.cleaned_data["check_agregar_persona"]
                check_retencion = incendio_form.cleaned_data["check_retencion"]
                
                if check_agregar_persona == True and persona_presente_form.is_valid():
                    nacionalidad = persona_presente_form.cleaned_data["nacionalidad"]
                    cedula = persona_presente_form.cleaned_data["cedula"]

                    try:
                        # Intentar obtener el registro existente
                        detalles_persona = Persona_Presente.objects.get(id_incendio=detalles_procedimiento)
                        # Actualizar campos si el registro existe
                        detalles_persona.nombre = persona_presente_form.cleaned_data["nombre"]
                        detalles_persona.apellidos = persona_presente_form.cleaned_data["apellido"]
                        detalles_persona.cedula = f"{nacionalidad}-{cedula}"
                        detalles_persona.edad = persona_presente_form.cleaned_data["edad"]
                        detalles_persona.save()
                    except Persona_Presente.DoesNotExist:
                        # Crear un nuevo registro si no existe
                        detalles_persona = Persona_Presente.objects.create(
                            id_incendio=detalles_procedimiento,
                            nombre=persona_presente_form.cleaned_data["nombre"],
                            apellidos=persona_presente_form.cleaned_data["apellido"],
                            cedula=f"{nacionalidad}-{cedula}",
                            edad=persona_presente_form.cleaned_data["edad"],
                        )

                if check_retencion == True and retencion_preventiva_incendio.is_valid():
                    nacionalidad = retencion_preventiva_incendio.cleaned_data["nacionalidad"]
                    cedula = retencion_preventiva_incendio.cleaned_data["cedula"]
                    tipo_cilindro = retencion_preventiva_incendio.cleaned_data["tipo_cilindro"]
                    tipo_cilindro_instance = Tipo_Cilindro.objects.get(id=tipo_cilindro)

                    try:
                        # Intentar obtener el registro existente
                        detalles_retencion = Retencion_Preventiva_Incendios.objects.get(id_procedimiento=detalles_procedimiento)
                        # Actualizar campos si el registro existe
                        detalles_retencion.tipo_cilindro = tipo_cilindro_instance
                        detalles_retencion.capacidad = retencion_preventiva_incendio.cleaned_data["capacidad"]
                        detalles_retencion.serial = retencion_preventiva_incendio.cleaned_data["serial"]
                        detalles_retencion.nro_constancia_retencion = retencion_preventiva_incendio.cleaned_data["nro_constancia_retencion"]
                        detalles_retencion.nombre = retencion_preventiva_incendio.cleaned_data["nombre"]
                        detalles_retencion.apellidos = retencion_preventiva_incendio.cleaned_data["apellidos"]
                        detalles_retencion.cedula = f"{nacionalidad}-{cedula}"
                        detalles_retencion.save()
                    except Retencion_Preventiva_Incendios.DoesNotExist:
                        # Crear un nuevo registro si no existe
                        detalles_retencion = Retencion_Preventiva_Incendios.objects.create(
                            id_procedimiento=detalles_procedimiento,
                            tipo_cilindro=tipo_cilindro_instance,
                            capacidad=retencion_preventiva_incendio.cleaned_data["capacidad"],
                            serial=retencion_preventiva_incendio.cleaned_data["serial"],
                            nro_constancia_retencion=retencion_preventiva_incendio.cleaned_data["nro_constancia_retencion"],
                            nombre=retencion_preventiva_incendio.cleaned_data["nombre"],
                            apellidos=retencion_preventiva_incendio.cleaned_data["apellidos"],
                            cedula=f"{nacionalidad}-{cedula}",
                        )

                if id_tipo_incendio == "2" and detalles_vehiculo_form.is_valid():
                    modelo = detalles_vehiculo_form.cleaned_data["modelo"]
                    marca = detalles_vehiculo_form.cleaned_data["marca"]
                    color = detalles_vehiculo_form.cleaned_data["color"]
                    año = detalles_vehiculo_form.cleaned_data["año"]
                    placas = detalles_vehiculo_form.cleaned_data["placas"]

                    # Buscar registro existente por placas
                    try:
                        vehiculo = Detalles_Vehiculos.objects.get(placas=placas)
                        # Actualizar campos del vehículo existente
                        vehiculo.modelo = modelo
                        vehiculo.marca = marca
                        vehiculo.color = color
                        vehiculo.año = año
                        vehiculo.id_vehiculo = detalles_procedimiento  # Actualizar referencia si aplica
                        vehiculo.save()

                    except Detalles_Vehiculos.DoesNotExist:
                        pass

            # Terminado
            if tipo_procedimiento == "12" and form_fallecido.is_valid():

                detalles_procedimiento = Fallecidos.objects.get(id_procedimiento = procedimiento)
                nacionalidad = form_fallecido.cleaned_data["nacionalidad"]
                cedula_fallecido = form_fallecido.cleaned_data["cedula_fallecido"]

                detalles_procedimiento.motivo_fallecimiento = form_fallecido.cleaned_data["motivo_fallecimiento"]
                detalles_procedimiento.nombres = form_fallecido.cleaned_data["nom_fallecido"]
                detalles_procedimiento.apellidos = form_fallecido.cleaned_data["apellido_fallecido"]
                detalles_procedimiento.cedula =  f"{nacionalidad}-{cedula_fallecido}"
                detalles_procedimiento.edad = form_fallecido.cleaned_data["edad"]
                detalles_procedimiento.sexo = form_fallecido.cleaned_data["sexo"]
                detalles_procedimiento.descripcion = form_fallecido.cleaned_data["descripcion"]
                detalles_procedimiento.material_utilizado = form_fallecido.cleaned_data["material_utilizado"]
                detalles_procedimiento.status = form_fallecido.cleaned_data["status"]

                detalles_procedimiento.save()

            # Terminado
            if tipo_procedimiento == "13" and mitigacion_riesgo_form.is_valid():

                detalles_procedimiento = Mitigacion_Riesgos.objects.get(id_procedimientos = procedimiento)
                tipo_riesgo = mitigacion_riesgo_form.cleaned_data["tipo_riesgo"]
                tipo_riesgo_instance = Mitigacion_riesgo.objects.get(id=tipo_riesgo)

                detalles_procedimiento.id_tipo_servicio = tipo_riesgo_instance
                detalles_procedimiento.descripcion = mitigacion_riesgo_form.cleaned_data["descripcion"]
                detalles_procedimiento.material_utilizado = mitigacion_riesgo_form.cleaned_data["material_utilizado"]
                detalles_procedimiento.status = mitigacion_riesgo_form.cleaned_data["status"]

                detalles_procedimiento.save()

                agg_vehiculo = mitigacion_riesgo_form.cleaned_data["agregar_vehiculo"]

                # Editar vehículos existentes
                if agg_vehiculo == True and vehiculo_derrame_form.is_valid():
                    placas1 = vehiculo_derrame_form.cleaned_data["placas"]
                    agg_vehiculo2 = vehiculo_derrame_form.cleaned_data["agregar_segundo_vehiculo"]

                    # Buscar o crear el vehículo con la placa
                    vehiculo, created = Detalles_Vehiculo_Derrame.objects.get_or_create(
                        id_vehiculo=detalles_procedimiento,
                        placas=placas1,
                        defaults={
                            "modelo": vehiculo_derrame_form.cleaned_data["modelo"],
                            "marca": vehiculo_derrame_form.cleaned_data["marca"],
                            "color": vehiculo_derrame_form.cleaned_data["color"],
                            "año": vehiculo_derrame_form.cleaned_data["año"],
                        }
                    )
                    if not created:  # Si ya existe, actualizar los datos
                        vehiculo.modelo = vehiculo_derrame_form.cleaned_data["modelo"]
                        vehiculo.marca = vehiculo_derrame_form.cleaned_data["marca"]
                        vehiculo.color = vehiculo_derrame_form.cleaned_data["color"]
                        vehiculo.año = vehiculo_derrame_form.cleaned_data["año"]
                        vehiculo.save()

                    # Verificar y manejar vehículos adicionales
                    if vehiculo_derrame_form2.is_valid() and agg_vehiculo2:
                        placas2 = vehiculo_derrame_form2.cleaned_data["placas"]
                        agg_vehiculo3 = vehiculo_derrame_form2.cleaned_data["agregar_tercer_vehiculo"]

                        vehiculo2, created = Detalles_Vehiculo_Derrame.objects.get_or_create(
                            id_vehiculo=detalles_procedimiento,
                            placas=placas2,
                            defaults={
                                "modelo": vehiculo_derrame_form2.cleaned_data["modelo"],
                                "marca": vehiculo_derrame_form2.cleaned_data["marca"],
                                "color": vehiculo_derrame_form2.cleaned_data["color"],
                                "año": vehiculo_derrame_form2.cleaned_data["año"],
                            }
                        )
                        if not created:
                            vehiculo2.modelo = vehiculo_derrame_form2.cleaned_data["modelo"]
                            vehiculo2.marca = vehiculo_derrame_form2.cleaned_data["marca"]
                            vehiculo2.color = vehiculo_derrame_form2.cleaned_data["color"]
                            vehiculo2.año = vehiculo_derrame_form2.cleaned_data["año"]
                            vehiculo2.save()

                        if vehiculo_derrame_form3.is_valid() and agg_vehiculo3:
                            placas3 = vehiculo_derrame_form3.cleaned_data["placas"]

                            vehiculo3, created = Detalles_Vehiculo_Derrame.objects.get_or_create(
                                id_vehiculo=detalles_procedimiento,
                                placas=placas3,
                                defaults={
                                    "modelo": vehiculo_derrame_form3.cleaned_data["modelo"],
                                    "marca": vehiculo_derrame_form3.cleaned_data["marca"],
                                    "color": vehiculo_derrame_form3.cleaned_data["color"],
                                    "año": vehiculo_derrame_form3.cleaned_data["año"],
                                }
                            )
                            if not created:
                                vehiculo3.modelo = vehiculo_derrame_form3.cleaned_data["modelo"]
                                vehiculo3.marca = vehiculo_derrame_form3.cleaned_data["marca"]
                                vehiculo3.color = vehiculo_derrame_form3.cleaned_data["color"]
                                vehiculo3.año = vehiculo_derrame_form3.cleaned_data["año"]
                                vehiculo3.save()

            # Terminado
            if tipo_procedimiento == "14" and evaluacion_riesgo_form.is_valid():
                # Obtener datos del formulario de evaluación de riesgo
                tipo_riesgo = evaluacion_riesgo_form.cleaned_data.get("tipo_riesgo")
                tipo_estructura = evaluacion_riesgo_form.cleaned_data.get("tipo_etructura")
                descripcion = evaluacion_riesgo_form.cleaned_data.get("descripcion")
                material_utilizado = evaluacion_riesgo_form.cleaned_data.get("material_utilizado")
                status = evaluacion_riesgo_form.cleaned_data.get("status")

                try:
                    tipo_riesgo_instance = Motivo_Riesgo.objects.get(id=tipo_riesgo)
                except Motivo_Riesgo.DoesNotExist:
                    tipo_riesgo_instance = None

                if tipo_riesgo_instance:
                    try:
                        # Intentar obtener la evaluación de riesgo existente
                        nuevo_proc_eval = Evaluacion_Riesgo.objects.get(id_procedimientos=procedimiento)
                        
                        # Actualizar los campos existentes
                        nuevo_proc_eval.id_tipo_riesgo = tipo_riesgo_instance
                        nuevo_proc_eval.tipo_estructura = tipo_estructura
                        nuevo_proc_eval.descripcion = descripcion
                        nuevo_proc_eval.material_utilizado = material_utilizado
                        nuevo_proc_eval.status = status
                        nuevo_proc_eval.save()
                    except Evaluacion_Riesgo.DoesNotExist:
                        pass
                    # Editar persona presente, si aplica
                    if division == "3" and persona_presente_eval_form.is_valid():
                        # Obtener los datos del formulario de persona presente
                        nombre = persona_presente_eval_form.cleaned_data.get("nombre")
                        apellido = persona_presente_eval_form.cleaned_data.get("apellidos")
                        nacionalidad = persona_presente_eval_form.cleaned_data.get("nacionalidad")
                        cedula = persona_presente_eval_form.cleaned_data.get("cedula")
                        telefono = persona_presente_eval_form.cleaned_data.get("telefono")

                        try:
                            # Intentar obtener la persona presente existente
                            nuevo_per_presente = Persona_Presente_Eval.objects.get(id_persona=nuevo_proc_eval)
                            
                            # Actualizar los campos existentes
                            nuevo_per_presente.nombre = nombre
                            nuevo_per_presente.apellidos = apellido
                            nuevo_per_presente.cedula = f"{nacionalidad}-{cedula}"
                            nuevo_per_presente.telefono = telefono
                            nuevo_per_presente.save()
                        except Persona_Presente_Eval.DoesNotExist:
                           pass

            # Terminado
            if tipo_procedimiento == "15" and puesto_avanzada_form.is_valid():
                # Obtener los datos del formulario
                tipo_avanzada = puesto_avanzada_form.cleaned_data["tipo_avanzada"]
                descripcion = puesto_avanzada_form.cleaned_data["descripcion"]
                material_utilizado = puesto_avanzada_form.cleaned_data["material_utilizado"]
                status = puesto_avanzada_form.cleaned_data["status"]

                try:
                    # Buscar la instancia de `Motivo_Avanzada` correspondiente
                    tipo_avanzada_instance = Motivo_Avanzada.objects.get(id=tipo_avanzada)
                except Motivo_Avanzada.DoesNotExist:
                    tipo_avanzada_instance = None

                if tipo_avanzada_instance:
                    try:
                        # Intentar obtener la instancia existente de `Puesto_Avanzada`
                        nuevo_proc_avan = Puesto_Avanzada.objects.get(id_procedimientos=procedimiento)

                        # Actualizar los campos de la instancia
                        nuevo_proc_avan.id_tipo_servicio = tipo_avanzada_instance
                        nuevo_proc_avan.descripcion = descripcion
                        nuevo_proc_avan.material_utilizado = material_utilizado
                        nuevo_proc_avan.status = status
                        nuevo_proc_avan.save()
                    except Puesto_Avanzada.DoesNotExist:
                        pass

            # Terminado
            if tipo_procedimiento == "16" and traslados_prehospitalaria_form.is_valid():
                # Obtener los datos del formulario
                tipo_traslado = traslados_prehospitalaria_form.cleaned_data["tipo_traslado"]
                nombre = traslados_prehospitalaria_form.cleaned_data["nombre"]
                apellido = traslados_prehospitalaria_form.cleaned_data["apellido"]
                nacionalidad = traslados_prehospitalaria_form.cleaned_data["nacionalidad"]
                cedula = traslados_prehospitalaria_form.cleaned_data["cedula"]
                edad = traslados_prehospitalaria_form.cleaned_data["edad"]
                sexo = traslados_prehospitalaria_form.cleaned_data["sexo"]
                idx = traslados_prehospitalaria_form.cleaned_data["idx"]
                hospital_trasladado = traslados_prehospitalaria_form.cleaned_data["hospital_trasladado"]
                medico_receptor = traslados_prehospitalaria_form.cleaned_data["medico_receptor"]
                mpps_cmt = traslados_prehospitalaria_form.cleaned_data["mpps_cmt"]
                descripcion = traslados_prehospitalaria_form.cleaned_data["descripcion"]
                material_utilizado = traslados_prehospitalaria_form.cleaned_data["material_utilizado"]
                status = traslados_prehospitalaria_form.cleaned_data["status"]

                try:
                    # Obtener la instancia del tipo de traslado
                    tipo_traslado_instance = Tipos_Traslado.objects.get(id=tipo_traslado)
                except Tipos_Traslado.DoesNotExist:
                    tipo_traslado_instance = None

                if tipo_traslado_instance:
                    try:
                        # Intentar obtener el registro existente de `Traslado_Prehospitalaria` para este procedimiento
                        traslado_proc = Traslado_Prehospitalaria.objects.get(id_procedimiento=procedimiento)

                        # Actualizar los datos del registro existente
                        traslado_proc.id_tipo_traslado = tipo_traslado_instance
                        traslado_proc.nombre = nombre
                        traslado_proc.apellido = apellido
                        traslado_proc.cedula = f"{nacionalidad}-{cedula}"
                        traslado_proc.edad = edad
                        traslado_proc.sexo = sexo
                        traslado_proc.idx = idx
                        traslado_proc.hospital_trasladado = hospital_trasladado
                        traslado_proc.medico_receptor = medico_receptor
                        traslado_proc.mpps_cmt = mpps_cmt
                        traslado_proc.descripcion = descripcion
                        traslado_proc.material_utilizado = material_utilizado
                        traslado_proc.status = status
                        traslado_proc.save()

                    except Traslado_Prehospitalaria.DoesNotExist:
                        pass

            # Terminado
            if tipo_procedimiento == "17" and asesoramiento_form.is_valid():
                # Obtener los datos del formulario
                nombre_comercio = asesoramiento_form.cleaned_data["nombre_comercio"]
                rif_comercio = asesoramiento_form.cleaned_data["rif_comercio"]
                nombre = asesoramiento_form.cleaned_data["nombres"]
                apellido = asesoramiento_form.cleaned_data["apellidos"]
                nacionalidad = asesoramiento_form.cleaned_data["nacionalidad"]
                cedula = asesoramiento_form.cleaned_data["cedula"]
                sexo = asesoramiento_form.cleaned_data["sexo"]
                telefono = asesoramiento_form.cleaned_data["telefono"]
                descripcion = asesoramiento_form.cleaned_data["descripcion"]
                material_utilizado = asesoramiento_form.cleaned_data["material_utilizado"]
                status = asesoramiento_form.cleaned_data["status"]

                try:
                    # Intentar obtener el registro existente de `Asesoramiento` para este procedimiento
                    asesoramiento_proc = Asesoramiento.objects.get(id_procedimiento=procedimiento)

                    # Actualizar los datos del registro existente
                    asesoramiento_proc.nombre_comercio = nombre_comercio
                    asesoramiento_proc.rif_comercio = rif_comercio
                    asesoramiento_proc.nombres = nombre
                    asesoramiento_proc.apellidos = apellido
                    asesoramiento_proc.cedula = f"{nacionalidad}-{cedula}"
                    asesoramiento_proc.sexo = sexo
                    asesoramiento_proc.telefono = telefono
                    asesoramiento_proc.descripcion = descripcion
                    asesoramiento_proc.material_utilizado = material_utilizado
                    asesoramiento_proc.status = status
                    asesoramiento_proc.save()

                except Asesoramiento.DoesNotExist:
                    pass

            # Terminado
            if tipo_procedimiento == "18" and form_inspecciones.is_valid():
                tipo_inspeccion = form_inspecciones.cleaned_data["tipo_inspeccion"]

                # Prevención
                if tipo_inspeccion == "Prevención" and form_inspecciones_prevencion.is_valid():
                    nombre_comercio = form_inspecciones_prevencion.cleaned_data["nombre_comercio"]
                    propietario = form_inspecciones_prevencion.cleaned_data["propietario"]
                    nacionalidad = form_inspecciones_prevencion.cleaned_data["nacionalidad"]
                    cedula_propietario = form_inspecciones_prevencion.cleaned_data["cedula_propietario"]
                    descripcion = form_inspecciones_prevencion.cleaned_data["descripcion"]
                    persona_sitio_nombre = form_inspecciones_prevencion.cleaned_data["persona_sitio_nombre"]
                    persona_sitio_apellido = form_inspecciones_prevencion.cleaned_data["persona_sitio_apellido"]
                    nacionalidad2 = form_inspecciones_prevencion.cleaned_data["nacionalidad2"]
                    persona_sitio_cedula = form_inspecciones_prevencion.cleaned_data["persona_sitio_cedula"]
                    persona_sitio_telefono = form_inspecciones_prevencion.cleaned_data["persona_sitio_telefono"]
                    material_utilizado = form_inspecciones_prevencion.cleaned_data["material_utilizado"]
                    status = form_inspecciones_prevencion.cleaned_data["status"]

                    inspeccion = Inspeccion_Prevencion_Asesorias_Tecnicas.objects.get(id_procedimientos=procedimiento)
                    inspeccion.tipo_inspeccion = tipo_inspeccion
                    inspeccion.nombre_comercio = nombre_comercio
                    inspeccion.propietario = propietario
                    inspeccion.cedula_propietario = f"{nacionalidad}-{cedula_propietario}"
                    inspeccion.descripcion = descripcion
                    inspeccion.persona_sitio_nombre = persona_sitio_nombre
                    inspeccion.persona_sitio_apellido = persona_sitio_apellido
                    inspeccion.persona_sitio_cedula = f"{nacionalidad2}-{persona_sitio_cedula}"
                    inspeccion.persona_sitio_telefono = persona_sitio_telefono
                    inspeccion.material_utilizado = material_utilizado
                    inspeccion.status = status
                    inspeccion.save()

                # Árbol
                if tipo_inspeccion == "Árbol" and form_inspecciones_arbol.is_valid():
                    especie = form_inspecciones_arbol.cleaned_data["especie"]
                    altura_aprox = form_inspecciones_arbol.cleaned_data["altura_aprox"]
                    ubicacion_arbol = form_inspecciones_arbol.cleaned_data["ubicacion_arbol"]
                    persona_sitio_nombre = form_inspecciones_arbol.cleaned_data["persona_sitio_nombre"]
                    persona_sitio_apellido = form_inspecciones_arbol.cleaned_data["persona_sitio_apellido"]
                    nacionalidad = form_inspecciones_arbol.cleaned_data["nacionalidad"]
                    persona_sitio_cedula = form_inspecciones_arbol.cleaned_data["persona_sitio_cedula"]
                    persona_sitio_telefono = form_inspecciones_arbol.cleaned_data["persona_sitio_telefono"]
                    descripcion = form_inspecciones_arbol.cleaned_data["descripcion"]
                    material_utilizado = form_inspecciones_arbol.cleaned_data["material_utilizado"]
                    status = form_inspecciones_arbol.cleaned_data["status"]

                    inspeccion = Inspeccion_Arbol.objects.get(id_procedimientos=procedimiento)
                    inspeccion.tipo_inspeccion = tipo_inspeccion
                    inspeccion.especie = especie
                    inspeccion.altura_aprox = altura_aprox
                    inspeccion.ubicacion_arbol = ubicacion_arbol
                    inspeccion.persona_sitio_nombre = persona_sitio_nombre
                    inspeccion.persona_sitio_apellido = persona_sitio_apellido
                    inspeccion.persona_sitio_cedula = f"{nacionalidad}-{persona_sitio_cedula}"
                    inspeccion.persona_sitio_telefono = persona_sitio_telefono
                    inspeccion.descripcion = descripcion
                    inspeccion.material_utilizado = material_utilizado
                    inspeccion.status = status
                    inspeccion.save()

                # Asesorías Técnicas
                if tipo_inspeccion == "Asesorias Tecnicas" and form_inspecciones_prevencion.is_valid():
                    nombre_comercio = form_inspecciones_prevencion.cleaned_data["nombre_comercio"]
                    propietario = form_inspecciones_prevencion.cleaned_data["propietario"]
                    nacionalidad = form_inspecciones_prevencion.cleaned_data["nacionalidad"]
                    cedula_propietario = form_inspecciones_prevencion.cleaned_data["cedula_propietario"]
                    descripcion = form_inspecciones_prevencion.cleaned_data["descripcion"]
                    persona_sitio_nombre = form_inspecciones_prevencion.cleaned_data["persona_sitio_nombre"]
                    persona_sitio_apellido = form_inspecciones_prevencion.cleaned_data["persona_sitio_apellido"]
                    nacionalidad2 = form_inspecciones_prevencion.cleaned_data["nacionalidad2"]
                    persona_sitio_cedula = form_inspecciones_prevencion.cleaned_data["persona_sitio_cedula"]
                    persona_sitio_telefono = form_inspecciones_prevencion.cleaned_data["persona_sitio_telefono"]
                    material_utilizado = form_inspecciones_prevencion.cleaned_data["material_utilizado"]
                    status = form_inspecciones_prevencion.cleaned_data["status"]

                    inspeccion = Inspeccion_Prevencion_Asesorias_Tecnicas.objects.get(id_procedimientos=procedimiento)
                    inspeccion.tipo_inspeccion = tipo_inspeccion
                    inspeccion.nombre_comercio = nombre_comercio
                    inspeccion.propietario = propietario
                    inspeccion.cedula_propietario = f"{nacionalidad}-{cedula_propietario}"
                    inspeccion.descripcion = descripcion
                    inspeccion.persona_sitio_nombre = persona_sitio_nombre
                    inspeccion.persona_sitio_apellido = persona_sitio_apellido
                    inspeccion.persona_sitio_cedula = f"{nacionalidad2}-{persona_sitio_cedula}"
                    inspeccion.persona_sitio_telefono = persona_sitio_telefono
                    inspeccion.material_utilizado = material_utilizado
                    inspeccion.status = status
                    inspeccion.save()

                # Habitabilidad
                if tipo_inspeccion == "Habitabilidad" and form_inspecciones_habitabilidad.is_valid():
                    descripcion = form_inspecciones_habitabilidad.cleaned_data["descripcion"]
                    persona_sitio_nombre = form_inspecciones_habitabilidad.cleaned_data["persona_sitio_nombre"]
                    persona_sitio_apellido = form_inspecciones_habitabilidad.cleaned_data["persona_sitio_apellido"]
                    nacionalidad = form_inspecciones_habitabilidad.cleaned_data["nacionalidad"]
                    persona_sitio_cedula = form_inspecciones_habitabilidad.cleaned_data["persona_sitio_cedula"]
                    persona_sitio_telefono = form_inspecciones_habitabilidad.cleaned_data["persona_sitio_telefono"]
                    material_utilizado = form_inspecciones_habitabilidad.cleaned_data["material_utilizado"]
                    status = form_inspecciones_habitabilidad.cleaned_data["status"]

                    inspeccion = Inspeccion_Habitabilidad.objects.get(id_procedimientos=procedimiento)
                    inspeccion.tipo_inspeccion = tipo_inspeccion
                    inspeccion.descripcion = descripcion
                    inspeccion.persona_sitio_nombre = persona_sitio_nombre
                    inspeccion.persona_sitio_apellido = persona_sitio_apellido
                    inspeccion.persona_sitio_cedula = f"{nacionalidad}-{persona_sitio_cedula}"
                    inspeccion.persona_sitio_telefono = persona_sitio_telefono
                    inspeccion.material_utilizado = material_utilizado
                    inspeccion.status = status
                    inspeccion.save()

                # Otros
                if tipo_inspeccion == "Otros" and form_inspecciones_otros.is_valid():
                    especifique = form_inspecciones_otros.cleaned_data["especifique"]
                    descripcion = form_inspecciones_otros.cleaned_data["descripcion"]
                    persona_sitio_nombre = form_inspecciones_otros.cleaned_data["persona_sitio_nombre"]
                    persona_sitio_apellido = form_inspecciones_otros.cleaned_data["persona_sitio_apellido"]
                    nacionalidad = form_inspecciones_otros.cleaned_data["nacionalidad"]
                    persona_sitio_cedula = form_inspecciones_otros.cleaned_data["persona_sitio_cedula"]
                    persona_sitio_telefono = form_inspecciones_otros.cleaned_data["persona_sitio_telefono"]
                    material_utilizado = form_inspecciones_otros.cleaned_data["material_utilizado"]
                    status = form_inspecciones_otros.cleaned_data["status"]

                    inspeccion = Inspeccion_Otros.objects.get(id_procedimientos=procedimiento)
                    inspeccion.tipo_inspeccion = tipo_inspeccion
                    inspeccion.especifique = especifique
                    inspeccion.descripcion = descripcion
                    inspeccion.persona_sitio_nombre = persona_sitio_nombre
                    inspeccion.persona_sitio_apellido = persona_sitio_apellido
                    inspeccion.persona_sitio_cedula = f"{nacionalidad}-{persona_sitio_cedula}"
                    inspeccion.persona_sitio_telefono = persona_sitio_telefono
                    inspeccion.material_utilizado = material_utilizado
                    inspeccion.status = status
                    inspeccion.save()

            # Terminado
            if tipo_procedimiento == "19" and form_investigacion.is_valid():
                tipo_investigacion = form_investigacion.cleaned_data["tipo_investigacion"]
                tipo_siniestro = form_investigacion.cleaned_data["tipo_siniestro"]

                tipo_investigacion_instance = Tipos_Investigacion.objects.get(id=tipo_investigacion)
                investigacion = Investigacion.objects.get(id_procedimientos=procedimiento)

                investigacion.id_tipo_investigacion = tipo_investigacion_instance
                investigacion.tipo_siniestro = tipo_siniestro
                investigacion.save()

                if tipo_siniestro == "Comercio" and form_inv_comercio.is_valid():
                    nombre_comercio = form_inv_comercio.cleaned_data["nombre_comercio"]
                    rif_comercio = form_inv_comercio.cleaned_data["rif_comercio"]
                    nombre_propietario = form_inv_comercio.cleaned_data["nombre_propietario"]
                    apellido_propietario = form_inv_comercio.cleaned_data["apellido_propietario"]
                    nacionalidad = form_inv_comercio.cleaned_data["nacionalidad"]
                    cedula_propietario = form_inv_comercio.cleaned_data["cedula_propietario"]
                    descripcion = form_inv_comercio.cleaned_data["descripcion"]
                    material_utilizado = form_inv_comercio.cleaned_data["material_utilizado"]
                    status = form_inv_comercio.cleaned_data["status"]

                    inv_comercio = Investigacion_Comercio.objects.get(id_investigacion=investigacion)
                    inv_comercio.nombre_comercio = nombre_comercio
                    inv_comercio.rif_comercio = rif_comercio
                    inv_comercio.nombre_propietario = nombre_propietario
                    inv_comercio.apellido_propietario = apellido_propietario
                    inv_comercio.cedula_propietario = f"{nacionalidad}-{cedula_propietario}"
                    inv_comercio.descripcion = descripcion
                    inv_comercio.material_utilizado = material_utilizado
                    inv_comercio.status = status
                    inv_comercio.save()

                if (tipo_siniestro == "Estructura" or tipo_siniestro == "Vivienda") and form_inv_estructura.is_valid():
                    tipo_estructura = form_inv_estructura.cleaned_data["tipo_estructura"]
                    nombre = form_inv_estructura.cleaned_data["nombre"]
                    apellido = form_inv_estructura.cleaned_data["apellido"]
                    nacionalidad = form_inv_estructura.cleaned_data["nacionalidad"]
                    cedula = form_inv_estructura.cleaned_data["cedula"]
                    descripcion = form_inv_estructura.cleaned_data["descripcion"]
                    material_utilizado = form_inv_estructura.cleaned_data["material_utilizado"]
                    status = form_inv_estructura.cleaned_data["status"]

                    inv_estructura = Investigacion_Estructura_Vivienda.objects.get(id_investigacion=investigacion)
                    inv_estructura.tipo_estructura = tipo_estructura
                    inv_estructura.nombre = nombre
                    inv_estructura.apellido = apellido
                    inv_estructura.cedula = f"{nacionalidad}-{cedula}"
                    inv_estructura.descripcion = descripcion
                    inv_estructura.material_utilizado = material_utilizado
                    inv_estructura.status = status
                    inv_estructura.save()

                if tipo_siniestro == "Vehiculo" and form_inv_vehiculo.is_valid():
                    marca = form_inv_vehiculo.cleaned_data["marca"]
                    modelo = form_inv_vehiculo.cleaned_data["modelo"]
                    color = form_inv_vehiculo.cleaned_data["color"]
                    placas = form_inv_vehiculo.cleaned_data["placas"]
                    año = form_inv_vehiculo.cleaned_data["año"]
                    nombre_propietario = form_inv_vehiculo.cleaned_data["nombre_propietario"]
                    apellido_propietario = form_inv_vehiculo.cleaned_data["apellido_propietario"]
                    nacionalidad = form_inv_vehiculo.cleaned_data["nacionalidad"]
                    cedula_propietario = form_inv_vehiculo.cleaned_data["cedula_propietario"]
                    descripcion = form_inv_vehiculo.cleaned_data["descripcion"]
                    material_utilizado = form_inv_vehiculo.cleaned_data["material_utilizado"]
                    status = form_inv_vehiculo.cleaned_data["status"]

                    inv_vehiculo = Investigacion_Vehiculo.objects.get(id_investigacion=investigacion)
                    inv_vehiculo.marca = marca
                    inv_vehiculo.modelo = modelo
                    inv_vehiculo.color = color
                    inv_vehiculo.placas = placas
                    inv_vehiculo.año = año
                    inv_vehiculo.nombre_propietario = nombre_propietario
                    inv_vehiculo.apellido_propietario = apellido_propietario
                    inv_vehiculo.cedula_propietario = f"{nacionalidad}-{cedula_propietario}"
                    inv_vehiculo.descripcion = descripcion
                    inv_vehiculo.material_utilizado = material_utilizado
                    inv_vehiculo.status = status
                    inv_vehiculo.save()

            # Terminado
            if tipo_procedimiento == "20" and reinspeccion_prevencion.is_valid():
                nombre_comercio = reinspeccion_prevencion.cleaned_data["nombre_comercio"]
                rif_comercio = reinspeccion_prevencion.cleaned_data["rif_comercio"]
                nombre = reinspeccion_prevencion.cleaned_data["nombre"]
                apellido = reinspeccion_prevencion.cleaned_data["apellidos"]
                sexo = reinspeccion_prevencion.cleaned_data["sexo"]
                nacionalidad = reinspeccion_prevencion.cleaned_data["nacionalidad"]
                cedula = reinspeccion_prevencion.cleaned_data["cedula"]
                telefono = reinspeccion_prevencion.cleaned_data["telefono"]
                descripcion = reinspeccion_prevencion.cleaned_data["descripcion"]
                material_utilizado = reinspeccion_prevencion.cleaned_data["material_utilizado"]
                status = reinspeccion_prevencion.cleaned_data["status"]

                try:
                    # Intentar obtener el registro existente
                    proc_reins = Reinspeccion_Prevencion.objects.get(id_procedimiento=procedimiento)

                    # Actualizar los campos existentes
                    proc_reins.nombre_comercio = nombre_comercio
                    proc_reins.rif_comercio = rif_comercio
                    proc_reins.nombre = nombre
                    proc_reins.apellidos = apellido
                    proc_reins.cedula = f"{nacionalidad}-{cedula}"
                    proc_reins.sexo = sexo
                    proc_reins.telefono = telefono
                    proc_reins.descripcion = descripcion
                    proc_reins.material_utilizado = material_utilizado
                    proc_reins.status = status
                    proc_reins.save()

                except Reinspeccion_Prevencion.DoesNotExist:
                    pass

            # Terminado
            if tipo_procedimiento == "21" and retencion_preventiva.is_valid():
                tipo_cilindro = retencion_preventiva.cleaned_data["tipo_cilindro"]
                capacidad = retencion_preventiva.cleaned_data["capacidad"]
                serial = retencion_preventiva.cleaned_data["serial"]
                nro_constancia_retencion = retencion_preventiva.cleaned_data["nro_constancia_retencion"]
                nombre = retencion_preventiva.cleaned_data["nombre"]
                apellido = retencion_preventiva.cleaned_data["apellidos"]
                nacionalidad = retencion_preventiva.cleaned_data["nacionalidad"]
                cedula = retencion_preventiva.cleaned_data["cedula"]
                descripcion = retencion_preventiva.cleaned_data["descripcion"]
                material_utilizado = retencion_preventiva.cleaned_data["material_utilizado"]
                status = retencion_preventiva.cleaned_data["status"]

                tipo_cilindro_instance = Tipo_Cilindro.objects.get(id=tipo_cilindro)

                try:
                    # Intentar obtener el registro existente
                    proc_reten = Retencion_Preventiva.objects.get(id_procedimiento=procedimiento)

                    # Actualizar los campos existentes
                    proc_reten.tipo_cilindro = tipo_cilindro_instance
                    proc_reten.capacidad = capacidad
                    proc_reten.serial = serial
                    proc_reten.nro_constancia_retencion = nro_constancia_retencion
                    proc_reten.nombre = nombre
                    proc_reten.apellidos = apellido
                    proc_reten.cedula = f"{nacionalidad}-{cedula}"
                    proc_reten.descripcion = descripcion
                    proc_reten.material_utilizado = material_utilizado
                    proc_reten.status = status
                    proc_reten.save()

                except Retencion_Preventiva.DoesNotExist:
                    pass

            # Terminado
            if tipo_procedimiento == "22" and artificios_pirotecnico.is_valid():
                nombre_comercio = artificios_pirotecnico.cleaned_data["nombre_comercio"]
                rif_comercio = artificios_pirotecnico.cleaned_data["rif_comercio"]
                tipo_procedimiento_art = artificios_pirotecnico.cleaned_data["tipo_procedimiento"]

                tipo_procedimiento_art_instance = Tipos_Artificios.objects.get(id=tipo_procedimiento_art)

                try:
                    # Intentar obtener el registro existente
                    proc_artificio_pir = Artificios_Pirotecnicos.objects.get(id_procedimiento=procedimiento)

                    # Actualizar los campos existentes
                    proc_artificio_pir.nombre_comercio = nombre_comercio
                    proc_artificio_pir.rif_comerciante = rif_comercio
                    proc_artificio_pir.tipo_procedimiento = tipo_procedimiento_art_instance
                    proc_artificio_pir.save()

                except Artificios_Pirotecnicos.DoesNotExist:
                    pass

                if tipo_procedimiento_art == "1" and incendio_art.is_valid():
                    id_tipo_incendio = incendio_art.cleaned_data["tipo_incendio"]
                    descripcion = incendio_art.cleaned_data["descripcion"]
                    material_utilizado = incendio_art.cleaned_data["material_utilizado"]
                    status = incendio_art.cleaned_data["status"]

                    tipo_incendio_instance = Tipo_Incendio.objects.get(id=id_tipo_incendio)

                    try:
                        # Intentar obtener el registro de incendio
                        proc_incendio_art = Incendios_Art.objects.get(id_procedimientos=proc_artificio_pir)

                        # Actualizar los campos del incendio
                        proc_incendio_art.id_tipo_incendio = tipo_incendio_instance
                        proc_incendio_art.descripcion = descripcion
                        proc_incendio_art.material_utilizado = material_utilizado
                        proc_incendio_art.status = status
                        proc_incendio_art.save()

                    except Incendios_Art.DoesNotExist:
                        pass

                    check_agregar_persona = incendio_art.cleaned_data["check_agregar_persona"]

                    if check_agregar_persona == True and persona_presente_art.is_valid():
                        nombre = persona_presente_art.cleaned_data["nombre"]
                        apellido = persona_presente_art.cleaned_data["apellido"]
                        nacionalidad = persona_presente_art.cleaned_data["nacionalidad"]
                        cedula = persona_presente_art.cleaned_data["cedula"]
                        edad = persona_presente_art.cleaned_data["edad"]

                        try:
                            # Intentar obtener la persona presente
                            persona_presente = Persona_Presente_Art.objects.get(id_incendio=proc_incendio_art)

                            # Actualizar los campos de la persona presente
                            persona_presente.nombre = nombre
                            persona_presente.apellidos = apellido
                            persona_presente.cedula = f"{nacionalidad}-{cedula}"
                            persona_presente.edad = edad
                            persona_presente.save()

                        except Persona_Presente_Art.DoesNotExist:
                            # Si no existe, crear uno nuevo
                            new_persona_presente = Persona_Presente_Art(
                                id_incendio=proc_incendio_art,
                                nombre=nombre,
                                apellidos=apellido,
                                cedula=f"{nacionalidad}-{cedula}",
                                edad=edad,
                            )
                            new_persona_presente.save()

                    if id_tipo_incendio == "2" and detalles_vehiculo_art.is_valid():
                        modelo = detalles_vehiculo_art.cleaned_data["modelo"]
                        marca = detalles_vehiculo_art.cleaned_data["marca"]
                        color = detalles_vehiculo_art.cleaned_data["color"]
                        año = detalles_vehiculo_art.cleaned_data["año"]
                        placas = detalles_vehiculo_art.cleaned_data["placas"]

                        try:
                            # Intentar obtener el vehículo relacionado
                            detalles_vehiculo = Detalles_Vehiculos_Art.objects.get(id_vehiculo=proc_incendio_art)

                            # Actualizar los campos del vehículo
                            detalles_vehiculo.modelo = modelo
                            detalles_vehiculo.marca = marca
                            detalles_vehiculo.color = color
                            detalles_vehiculo.año = año
                            detalles_vehiculo.placas = placas
                            detalles_vehiculo.save()

                        except Detalles_Vehiculos_Art.DoesNotExist:
                            # Si no existe, crear uno nuevo
                            new_agregar_vehiculo = Detalles_Vehiculos_Art(
                                id_vehiculo=proc_incendio_art,
                                modelo=modelo,
                                marca=marca,
                                color=color,
                                año=año,
                                placas=placas,
                            )
                            new_agregar_vehiculo.save()

                if tipo_procedimiento_art == "2" and lesionados.is_valid():
                    nombre = lesionados.cleaned_data["nombre"]
                    apellido = lesionados.cleaned_data["apellido"]
                    nacionalidad = lesionados.cleaned_data["nacionalidad"]
                    cedula = lesionados.cleaned_data["cedula"]
                    edad = lesionados.cleaned_data["edad"]
                    sexo = lesionados.cleaned_data["sexo"]
                    idx = lesionados.cleaned_data["idx"]
                    descripcion = lesionados.cleaned_data["descripcion"]
                    status = lesionados.cleaned_data["status"]

                    try:
                        # Intentar obtener el lesionado
                        lesionado_art = Lesionados_Art.objects.get(id_accidente=proc_artificio_pir)

                        # Actualizar los campos del lesionado
                        lesionado_art.nombres = nombre
                        lesionado_art.apellidos = apellido
                        lesionado_art.cedula = f"{nacionalidad}-{cedula}"
                        lesionado_art.edad = edad
                        lesionado_art.sexo = sexo
                        lesionado_art.idx = idx
                        lesionado_art.descripcion = descripcion
                        lesionado_art.status = status
                        lesionado_art.save()

                    except Lesionados_Art.DoesNotExist:
                        pass

                if tipo_procedimiento_art == "3" and fallecidos_art.is_valid():
                    motivo_fallecimiento = fallecidos_art.cleaned_data["motivo_fallecimiento"]
                    nom_fallecido = fallecidos_art.cleaned_data["nom_fallecido"]
                    apellido_fallecido = fallecidos_art.cleaned_data["apellido_fallecido"]
                    nacionalidad = fallecidos_art.cleaned_data["nacionalidad"]
                    cedula_fallecido = fallecidos_art.cleaned_data["cedula_fallecido"]
                    edad = fallecidos_art.cleaned_data["edad"]
                    sexo = fallecidos_art.cleaned_data["sexo"]
                    descripcion = fallecidos_art.cleaned_data["descripcion"]
                    material_utilizado = fallecidos_art.cleaned_data["material_utilizado"]
                    status = fallecidos_art.cleaned_data["status"]

                    try:
                        # Intentar obtener el fallecido
                        fallecido_art = Fallecidos_Art.objects.get(id_procedimiento=proc_artificio_pir)

                        # Actualizar los campos del fallecido
                        fallecido_art.motivo_fallecimiento = motivo_fallecimiento
                        fallecido_art.nombres = nom_fallecido
                        fallecido_art.apellidos = apellido_fallecido
                        fallecido_art.cedula = f"{nacionalidad}-{cedula_fallecido}"
                        fallecido_art.edad = edad
                        fallecido_art.sexo = sexo
                        fallecido_art.descripcion = descripcion
                        fallecido_art.material_utilizado = material_utilizado
                        fallecido_art.status = status
                        fallecido_art.save()

                    except Fallecidos_Art.DoesNotExist:
                        pass

            # Terminado
            if tipo_procedimiento == "23" and inspeccion_artificios_pir.is_valid():
                nombre_comercio = inspeccion_artificios_pir.cleaned_data["nombre_comercio"]
                rif_comercio = inspeccion_artificios_pir.cleaned_data["rif_comercio"]
                nombre_encargado = inspeccion_artificios_pir.cleaned_data["nombre_encargado"]
                apellido_encargado = inspeccion_artificios_pir.cleaned_data["apellido_encargado"]
                nacionalidad = inspeccion_artificios_pir.cleaned_data["nacionalidad"]
                cedula_encargado = inspeccion_artificios_pir.cleaned_data["cedula_encargado"]
                sexo = inspeccion_artificios_pir.cleaned_data["sexo"]
                descripcion = inspeccion_artificios_pir.cleaned_data["descripcion"]
                material_utilizado = inspeccion_artificios_pir.cleaned_data["material_utilizado"]
                status = inspeccion_artificios_pir.cleaned_data["status"]

                try:
                    # Intentar obtener el registro existente
                    inspeccion_art = Inspeccion_Establecimiento_Art.objects.get(id_proc_artificio=procedimiento)

                    # Actualizar los campos existentes
                    inspeccion_art.nombre_comercio = nombre_comercio
                    inspeccion_art.rif_comercio = rif_comercio
                    inspeccion_art.encargado_nombre = nombre_encargado
                    inspeccion_art.encargado_apellidos = apellido_encargado
                    inspeccion_art.encargado_cedula = f"{nacionalidad}-{cedula_encargado}"
                    inspeccion_art.encargado_sexo = sexo
                    inspeccion_art.descripcion = descripcion
                    inspeccion_art.material_utilizado = material_utilizado
                    inspeccion_art.status = status
                    inspeccion_art.save()

                except Inspeccion_Establecimiento_Art.DoesNotExist:
                    pass

            # Terminado
            if tipo_procedimiento == "24" and form_valoracion_medica.is_valid():
                nombre = form_valoracion_medica.cleaned_data["nombre"]
                apellido = form_valoracion_medica.cleaned_data["apellido"]
                nacionalidad = form_valoracion_medica.cleaned_data["nacionalidad"]
                cedula = form_valoracion_medica.cleaned_data["cedula"]
                edad = form_valoracion_medica.cleaned_data["edad"]
                sexo = form_valoracion_medica.cleaned_data["sexo"]
                telefono = form_valoracion_medica.cleaned_data["telefono"]
                descripcion = form_valoracion_medica.cleaned_data["descripcion"]
                material_utilizado = form_valoracion_medica.cleaned_data["material_utilizado"]
                status = form_valoracion_medica.cleaned_data["status"]

                try:
                    # Intentar obtener el registro existente de Valoración Médica
                    valoracion_medica = Valoracion_Medica.objects.get(id_procedimientos=procedimiento)

                    # Actualizar los campos con los nuevos valores
                    valoracion_medica.nombre = nombre
                    valoracion_medica.apellido = apellido
                    valoracion_medica.cedula = f"{nacionalidad}-{cedula}"
                    valoracion_medica.edad = edad
                    valoracion_medica.sexo = sexo
                    valoracion_medica.telefono = telefono
                    valoracion_medica.descripcion = descripcion
                    valoracion_medica.material_utilizado = material_utilizado
                    valoracion_medica.status = status

                    # Guardar los cambios
                    valoracion_medica.save()

                except Valoracion_Medica.DoesNotExist:
                    pass

            # Terminado
            if tipo_procedimiento == "25" and form_jornada_medica.is_valid():
                nombre_jornada = form_jornada_medica.cleaned_data["nombre_jornada"]
                cantidad_personas_atendidas = form_jornada_medica.cleaned_data["cant_personas_aten"]
                descripcion = form_jornada_medica.cleaned_data["descripcion"]
                material_utilizado = form_jornada_medica.cleaned_data["material_utilizado"]
                status = form_jornada_medica.cleaned_data["status"]

                try:
                    # Intentar obtener el registro existente de Jornada Médica
                    jornada_medica = Jornada_Medica.objects.get(id_procedimientos=procedimiento)

                    # Actualizar los campos con los nuevos valores
                    jornada_medica.nombre_jornada = nombre_jornada
                    jornada_medica.cant_personas_aten = cantidad_personas_atendidas
                    jornada_medica.descripcion = descripcion
                    jornada_medica.material_utilizado = material_utilizado
                    jornada_medica.status = status

                    # Guardar los cambios
                    jornada_medica.save()

                except Jornada_Medica.DoesNotExist:
                     pass

            # Terminado
            if (tipo_procedimiento == "26" or tipo_procedimiento == "27" or tipo_procedimiento == "28" or tipo_procedimiento == "29" or tipo_procedimiento == "30" or tipo_procedimiento == "31" or tipo_procedimiento == "32" or tipo_procedimiento == "33" or tipo_procedimiento == "34") and form_detalles_enfermeria.is_valid():
                nombre = form_detalles_enfermeria.cleaned_data["nombre"]
                apellido = form_detalles_enfermeria.cleaned_data["apellido"]
                nacionalidad = form_detalles_enfermeria.cleaned_data["nacionalidad"]
                cedula = form_detalles_enfermeria.cleaned_data["cedula"]
                edad = form_detalles_enfermeria.cleaned_data["edad"]
                sexo = form_detalles_enfermeria.cleaned_data["sexo"]
                telefono = form_detalles_enfermeria.cleaned_data["telefono"]
                descripcion = form_detalles_enfermeria.cleaned_data["descripcion"]
                material_utilizado = form_detalles_enfermeria.cleaned_data["material_utilizado"]
                status = form_detalles_enfermeria.cleaned_data["status"]

                try:
                    # Intentar obtener el registro existente de Detalles Enfermería
                    detalles_enfermeria = Detalles_Enfermeria.objects.get(id_procedimientos=procedimiento)

                    # Actualizar los campos con los nuevos valores
                    detalles_enfermeria.nombre = nombre
                    detalles_enfermeria.apellido = apellido
                    detalles_enfermeria.cedula = f"{nacionalidad}-{cedula}"
                    detalles_enfermeria.edad = edad
                    detalles_enfermeria.sexo = sexo
                    detalles_enfermeria.telefono = telefono
                    detalles_enfermeria.descripcion = descripcion
                    detalles_enfermeria.material_utilizado = material_utilizado
                    detalles_enfermeria.status = status

                    # Guardar los cambios
                    detalles_enfermeria.save()

                except Detalles_Enfermeria.DoesNotExist:
                    pass

            # Terminado
            if (tipo_procedimiento == "35" or tipo_procedimiento == "36" or tipo_procedimiento == "37" or tipo_procedimiento == "38" or tipo_procedimiento == "39" or tipo_procedimiento == "40" or tipo_procedimiento == "41") and form_detalles_psicologia.is_valid():
                nombre = form_detalles_psicologia.cleaned_data["nombre"]
                apellido = form_detalles_psicologia.cleaned_data["apellido"]
                nacionalidad = form_detalles_psicologia.cleaned_data["nacionalidad"]
                cedula = form_detalles_psicologia.cleaned_data["cedula"]
                edad = form_detalles_psicologia.cleaned_data["edad"]
                sexo = form_detalles_psicologia.cleaned_data["sexo"]
                descripcion = form_detalles_psicologia.cleaned_data["descripcion"]
                material_utilizado = form_detalles_psicologia.cleaned_data["material_utilizado"]
                status = form_detalles_psicologia.cleaned_data["status"]

                try:
                    # Intentar obtener el registro existente de Procedimientos_Psicologia
                    detalles_psicologia = Procedimientos_Psicologia.objects.get(id_procedimientos=procedimiento)

                    # Actualizar los campos con los nuevos valores
                    detalles_psicologia.nombre = nombre
                    detalles_psicologia.apellido = apellido
                    detalles_psicologia.cedula = f"{nacionalidad}-{cedula}"
                    detalles_psicologia.edad = edad
                    detalles_psicologia.sexo = sexo
                    detalles_psicologia.descripcion = descripcion
                    detalles_psicologia.material_utilizado = material_utilizado
                    detalles_psicologia.status = status

                    # Guardar los cambios
                    detalles_psicologia.save()

                except Procedimientos_Psicologia.DoesNotExist:
                    pass


            # Redirige a /dashboard/ después de guardar los datos
            return redirect('/dashboard/?registro_exitoso=true')
    else:
        form = SelectorDivision(prefix='form1')
        form2 = SeleccionarInfo(prefix='form2')
        form3 = Datos_Ubicacion(prefix='form3')
        form4 = Selecc_Tipo_Procedimiento(prefix='form4')
        abast_agua = formulario_abastecimiento_agua(prefix='abast_agua')
        apoyo_unid = Formulario_apoyo_unidades(prefix='apoyo_unid')
        guard_prev = Formulario_guardia_prevencion(prefix='guard_prev')
        atend_no_efec = Formulario_atendido_no_efectuado(prefix='atend_no_efec')
        desp_seguridad = Formulario_despliegue_seguridad(prefix='desp_seguridad')
        fals_alarm = Formulario_falsa_alarma(prefix='fals_alarm')
        serv_especial = Formulario_Servicios_Especiales(prefix='serv_especial')
        form_fallecido = Formulario_Fallecidos(prefix='form_fallecido')
        rescate_form = Formulario_Rescate(prefix='rescate_form')
        incendio_form = Formulario_Incendio(prefix='incendio_form')
        retencion_preventiva_incendio = Formulario_Retencion_Preventiva_Incendio(prefix='retencion_preventiva_incendio')
        atenciones_paramedicas = Formulario_Atenciones_Paramedicas(prefix='atenciones_paramedicas')

        emergencias_medicas = Formulario_Emergencias_Medicas(prefix='emergencias_medicas')
        traslados_emergencias = Formulario_Traslados(prefix='traslados_emergencias')

        persona_presente_form = Formulario_Persona_Presente(prefix='persona_presente_form')
        detalles_vehiculo_form = Formulario_Detalles_Vehiculos_Incendio(prefix='detalles_vehiculo_form')

        formulario_accidentes_transito = Formulario_Accidentes_Transito(prefix='formulario_accidentes_transito')
        detalles_vehiculo_accidentes = Formulario_Detalles_Vehiculos(prefix='detalles_vehiculos_accidentes')
        detalles_lesionados_accidentes = Formulario_Detalles_Lesionados(prefix='detalles_lesionados_accidentes')
        detalles_lesionados_accidentes2 = Formulario_Detalles_Lesionados2(prefix='detalles_lesionados_accidentes2')
        detalles_lesionados_accidentes3 = Formulario_Detalles_Lesionados3(prefix='detalles_lesionados_accidentes3')
        traslados_accidentes = Formulario_Traslado_Accidente(prefix='traslados_accidentes')
        traslados_accidentes2 = Formulario_Traslado_Accidente2(prefix='traslados_accidentes2')
        traslados_accidentes3 = Formulario_Traslado_Accidente3(prefix='traslados_accidentes3')
        detalles_vehiculo_accidentes2 = Formulario_Detalles_Vehiculos2(prefix='detalles_vehiculos_accidentes2')
        detalles_vehiculo_accidentes3 = Formulario_Detalles_Vehiculos3(prefix='detalles_vehiculos_accidentes3')

        rescate_form_persona = Formulario_Rescate_Persona(prefix='rescate_form_persona')
        rescate_form_animal = Formulario_Rescate_Animal(prefix='rescate_form_animal')

        evaluacion_riesgo_form = Forulario_Evaluacion_Riesgo(prefix='evaluacion_riesgo_form')
        mitigacion_riesgo_form = Formulario_Mitigacion_Riesgos(prefix='mitigacion_riesgo_form')
        vehiculo_derrame_form = Detalles_Vehiculo_Derrame_Form(request.POST, prefix='vehiculo_derrame_form')
        vehiculo_derrame_form2 = Detalles_Vehiculo_Derrame_Form2(request.POST, prefix='vehiculo_derrame_form2')
        vehiculo_derrame_form3 = Detalles_Vehiculo_Derrame_Form3(request.POST, prefix='vehiculo_derrame_form3')

        puesto_avanzada_form = Formulario_Puesto_Avanzada(prefix='puesto_avanzada_form')
        traslados_prehospitalaria_form = Formulario_Traslados_Prehospitalaria(prefix='traslados_prehospitalaria_form')
        asesoramiento_form = Formulario_Asesoramiento(prefix='asesoramiento_form')
        persona_presente_eval_form = Formularia_Persona_Presente_Eval(prefix='persona_presente_eval_form')
        reinspeccion_prevencion = Formulario_Reinspeccion_Prevencion(prefix='reinspeccion_prevencion')
        retencion_preventiva = Formulario_Retencion_Preventiva(prefix='retencion_preventiva')

        artificios_pirotecnico = Formulario_Artificios_Pirotecnicos(prefix='artificios_pirotecnico')
        lesionados = Formulario_Lesionado(prefix='lesionados')
        incendio_art = Formulario_Incendio_Art(prefix='incendio_art')
        persona_presente_art = Formulario_Persona_Presente_Art(prefix='persona_presente_art')
        detalles_vehiculo_art = Formulario_Detalles_Vehiculos_Incendio_Art(prefix='detalles_vehiculo_art')
        fallecidos_art = Formulario_Fallecidos_Art(prefix='fallecidos_art')
        inspeccion_artificios_pir = Formulario_Inspeccion_Establecimiento_Art(prefix='inspeccion_artificios_pir')
        form_enfermeria = Formulario_Enfermeria(prefix='form_enfermeria')
        servicios_medicos = Formulario_Servicios_medicos(prefix='form_servicios_medicos')
        psicologia = Formulario_psicologia(prefix='form_psicologia')
        capacitacion = Formulario_capacitacion(prefix='form_capacitacion')
        form_valoracion_medica = Formulario_Valoracion_Medica(prefix='form_valoracion_medica')
        form_jornada_medica = Formulario_Jornada_Medica(prefix='form_jornada_medica')
        form_detalles_enfermeria = Formulario_Detalles_Enfermeria(prefix='form_detalles_enfermeria')
        form_detalles_psicologia = Formulario_Procedimientos_Psicologia(prefix='form_detalles_psicologia')

        form_capacitacion = Formulario_Capacitacion_Proc(prefix='form_capacitacion')
        form_brigada = Formulario_Brigada(prefix='form_brigada')
        form_frente_preventivo = Formulario_Frente_Preventivo(prefix='form_frente_preventivo')

        form_inspecciones = Formulario_Inspecciones(prefix='form_inspecciones')
        form_inspecciones_prevencion = Formulario_Inspeccion_Prevencion_Asesorias_Tecnicas(prefix='form_inspecciones_prevencion')
        form_inspecciones_habitabilidad = Formulario_Inspeccion_Habitabilidad(prefix='form_inspecciones_habitabilidad')
        form_inspecciones_arbol = Formulario_Inspeccion_Arbol(prefix='form_inspecciones_arbol')
        form_inspecciones_otros = Formulario_Inspeccion_Otros(prefix='form_inspecciones_otros')

        form_investigacion = Formulario_Investigacion(prefix='form_investigacion')
        form_inv_vehiculo = Formulario_Investigacion_Vehiculo(prefix='form_inv_vehiculo')
        form_inv_comercio = Formulario_Investigacion_Comercio(prefix='form_inv_comercio')
        form_inv_estructura = Formulario_Investigacion_Estructura_Vivienda(prefix='form_inv_estructura')

        form_comision = Datos_Comision(prefix='form_comision')
        datos_comision_uno = Comision_Uno(prefix='datos_comision_uno')
        datos_comision_dos = Comision_Dos(prefix='datos_comision_dos')
        datos_comision_tres = Comision_Tres(prefix='datos_comision_tres')
        

    return render(request, "editar_procedimientos.html", {
        "user": user,
        "jerarquia": user["jerarquia"],
        "nombres": user["nombres"],
        "apellidos": user["apellidos"],
        "form": form,
        "form2": form2,
        "form3": form3,
        "form4": form4,
        "errors": result,
        "form_abastecimiento_agua": abast_agua,
        "form_apoyo_unidades": apoyo_unid,
        "form_guardia_prevencion": guard_prev,
        "form_atendido_no_efectuado": atend_no_efec,
        "form_despliegue_seguridad": desp_seguridad,
        "form_falsa_alarma": fals_alarm,
        "form_servicios_especiales": serv_especial,
        "form_fallecido": form_fallecido,
        "rescate_form": rescate_form,
        "rescate_form_animal": rescate_form_animal,
        "rescate_form_persona": rescate_form_persona,
        "incendio_form": incendio_form,
        "retencion_preventiva_incendio": retencion_preventiva_incendio,
        "persona_presente_form": persona_presente_form,
        "detalles_vehiculo_form": detalles_vehiculo_form,
        "atenciones_paramedicas": atenciones_paramedicas,
        "emergencias_medicas": emergencias_medicas,
        "traslados_emergencias": traslados_emergencias,
        "formulario_accidentes_transito": formulario_accidentes_transito,
        "detalles_vehiculo_accidentes":  detalles_vehiculo_accidentes,
        "detalles_vehiculo_accidentes2":  detalles_vehiculo_accidentes2,
        "detalles_vehiculo_accidentes3":  detalles_vehiculo_accidentes3,
        "detalles_lesionados_accidentes": detalles_lesionados_accidentes,
        "detalles_lesionados_accidentes2": detalles_lesionados_accidentes2,
        "detalles_lesionados_accidentes3": detalles_lesionados_accidentes3,
        "traslados_accidentes": traslados_accidentes,
        "traslados_accidentes2": traslados_accidentes2,
        "traslados_accidentes3": traslados_accidentes3,
        "evaluacion_riesgo_form": evaluacion_riesgo_form,
        "mitigacion_riesgo_form": mitigacion_riesgo_form,
        "vehiculo_derrame_form": vehiculo_derrame_form,
        "vehiculo_derrame_form2": vehiculo_derrame_form2,
        "vehiculo_derrame_form3": vehiculo_derrame_form3,
        "puesto_avanzada_form": puesto_avanzada_form,
        "traslados_prehospitalaria_form": traslados_prehospitalaria_form,
        "asesoramiento_form": asesoramiento_form,
        "persona_presente_eval_form": persona_presente_eval_form,
        "reinspeccion_prevencion": reinspeccion_prevencion,
        "retencion_preventiva": retencion_preventiva,
        "artificios_pirotecnico": artificios_pirotecnico,
        "lesionados": lesionados,
        "incendio_art": incendio_art,
        "persona_presente_art": persona_presente_art,
        "detalles_vehiculo_art": detalles_vehiculo_art,
        "fallecidos_art": fallecidos_art,
        "inspeccion_artificios_pir": inspeccion_artificios_pir,
        "form_enfermeria": form_enfermeria,
        "servicios_medicos" : servicios_medicos,
        "psicologia" : psicologia,
        "capacitacion" : capacitacion,
        "valoracion_medica": form_valoracion_medica,
        "form_detalles_enfermeria": form_detalles_enfermeria,
        "form_detalles_psicologia": form_detalles_psicologia,
        "form_capacitacion": form_capacitacion,
        "form_frente_preventivo": form_frente_preventivo,
        "jornada_medica": form_jornada_medica,
        "form_inspecciones": form_inspecciones,
        "form_inspecciones_prevencion": form_inspecciones_prevencion,
        "form_inspecciones_habitabilidad": form_inspecciones_habitabilidad,
        "form_inspecciones_arbol": form_inspecciones_arbol,
        "form_inspecciones_otros": form_inspecciones_otros,
        "form_investigacion": form_investigacion,
        "form_inv_vehiculo": form_inv_vehiculo,
        "form_inv_comercio": form_inv_comercio,
        "form_inv_estructura": form_inv_estructura,
        "form_comision": form_comision,
        "comision_uno": datos_comision_uno,
        "comision_dos": datos_comision_dos,
        "comision_tres": datos_comision_tres,
        "form_brigada": form_brigada,
        })

# ========================================================================================= Vistas Para el Area de Inventario de Unidades =====================================================