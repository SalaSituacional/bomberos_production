# middleware.py
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

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
