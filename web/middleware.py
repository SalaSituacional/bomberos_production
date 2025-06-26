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
        self.public_api_url_names = {
            # 'nombre_de_mi_api_publica', # Ejemplo
        }
        
        # Prefijos de URL que DEBEN ser protegidos por tu sistema de autenticación.
        self.protected_prefixes = [
            '/api/',        # Cualquier ruta que empiece con '/api/'
            '/alpha04/',    # ¡Ahora tu panel de administración está protegido!
        ]

    def __call__(self, request):

        is_protected_request = False
        for prefix in self.protected_prefixes:
            if request.path.startswith(prefix):
                is_protected_request = True
                break
        
        # Si la ruta no está entre los prefijos protegidos, no hacemos nada y pasamos la petición.
        if not is_protected_request:
            return self.get_response(request)

        # Intenta resolver el nombre de la URL para ver si es una URL pública por nombre.
        url_name = None
        try:
            resolved_url = resolve(request.path_info)
            url_name = resolved_url.url_name
        except NoReverseMatch:
            # Si no se puede resolver el nombre, no es una URL pública por nombre.
            pass 
        except Exception:
            # Captura otras excepciones durante la resolución.
            pass

        # Si la URL es pública por nombre, permite el acceso.
        if url_name in self.public_api_url_names:
            return self.get_response(request)

        # Aquí viene tu lógica de autenticación principal:
        # Si 'user' NO está en la sesión, el usuario no está autenticado.
        if 'user' not in request.session:
            # Es mejor usar HttpResponseForbidden (403) para "acceso denegado"
            # o HttpResponseUnauthorized (401) si es específicamente por falta de credenciales de autenticación.
            # Http404 es para recursos no encontrados.
            return HttpResponseForbidden("Acceso denegado. No estás autenticado.")
            
        # Si el usuario está autenticado y la ruta es protegida, permite el acceso.
        response = self.get_response(request)
        return response 