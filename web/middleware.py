# middleware.py
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from .models import RegistroPeticiones, Usuarios
from django.http import HttpResponseForbidden
from django.urls import resolve, NoReverseMatch # <-- Asegúrate de que estas estén aquí
from django.http import Http404, JsonResponse # Asegúrate de importar Http404


class LogoutIfAuthenticatedMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Cambia 'home' por la vista correcta si es necesario
        if request.path_info == reverse('home') and request.user.is_authenticated:
            logout(request)
            return redirect('home')  # Asegúrate de que esto sea correcto
        return self.get_response(request)

class NoCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response

class LoadingScreenMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Establece una variable en la sesión o en el contexto para indicar que el proceso ha comenzado
        request.loading = True

    def process_response(self, request, response):
        # Cuando la respuesta se envíe, quita la variable de carga
        if hasattr(request, 'loading') and request.loading:
            response['Loading'] = 'Complete'
        return response

class RegistroPeticionesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Evitar el registro de peticiones durante el proceso de login
        if request.path.startswith('/login/') or request.path.startswith('/logout/'):
            return self.get_response(request)

        # Solo registrar las peticiones POST después de la autenticación
        if request.method == 'POST':
            # Obtener el usuario de la sesión
            user_data = request.session.get('user', None)  # Obtener los datos del usuario de la sesión

            if user_data:
                # Si el usuario está en la sesión, buscarlo en la base de datos de Usuarios
                try:
                    usuario = Usuarios.objects.get(user=user_data['user'])
                except Usuarios.DoesNotExist:
                    usuario = None  # Si no existe el usuario en la base de datos personalizada, lo dejamos como None
            else:
                usuario = None  # Si no hay usuario en la sesión, lo dejamos como None

            # Si el usuario no está autenticado, redirigir o devolver una respuesta adecuada
            if not usuario:
                return HttpResponseForbidden("No estás autenticado o no se encontró el usuario.")

            # Registrar la petición
            url = request.path  # La URL a la que se hizo la petición
            datos_post = request.POST.dict()  # Los datos del formulario en formato de diccionario
            
            # Obtener la fecha y hora actual en UTC
            fecha_hora = timezone.now()

            # Convertirla a la hora local
            local = timezone.localtime(fecha_hora)

            # Crear un registro de la petición
            RegistroPeticiones.objects.create(
                usuario=usuario,
                url=url,
                datos_post=datos_post,
                fecha_hora=local  # Fecha y hora actual en zona horaria configurada
            )

        response = self.get_response(request)
        return response

# Seguridad en apis
class PrivateApiAuthMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Define los NOMBRES de tus URLs de API que DEBEN SER PÚBLICAS (NO requieren autenticación).
        # Asegúrate de que estas URLs tengan un 'name' definido en tu urls.py.
        self.public_api_url_names = {
        }
        
        self.api_url_prefixes = [
            '/api/', # Cualquier ruta que empiece con '/api/'
        ]

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            return self.get_response(request)

        is_api_request = False
        for prefix in self.api_url_prefixes:
            if request.path.startswith(prefix):
                is_api_request = True
                break
        
        if not is_api_request:
            return self.get_response(request)

        url_name = None
        try:
            resolved_url = resolve(request.path_info)
            url_name = resolved_url.url_name
        except NoReverseMatch:
            return self.get_response(request)
        except Exception:
            return self.get_response(request)

        if url_name in self.public_api_url_names:
            return self.get_response(request)

        # CAMBIO AQUÍ: Verificar 'user' en request.session en lugar de request.user.is_authenticated
        if 'user' not in request.session: # <-- Lógica de autenticación unificada
            raise Http404("No estas autenticado.")
            
        response = self.get_response(request)
        return response