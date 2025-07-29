from django.http import HttpResponseRedirect
from django.conf import settings
from django.urls import reverse

class SelectiveMaintenanceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        config = getattr(settings, 'MAINTENANCE_CONFIG', {})
        maintenance_url = config.get('maintenance_url', '/maintenance/')
        response = None
        
        # Verificar si el modo mantenimiento está activado
        if config.get('enabled', False):
            path = request.path
            
            # Verificar acceso especial
            bypass_access = (
                (config.get('bypass_staff', False) and request.user.is_staff) or
                (config.get('bypass_superuser', False) and request.user.is_superuser)
            )
            
            if not bypass_access:
                # Verificar si la ruta está protegida
                is_protected = any(
                    path.startswith(protected) 
                    for protected in config.get('protected_paths', [])
                )
                
                # Verificar exclusiones
                is_excluded = any(
                    path.startswith(excluded) 
                    for excluded in config.get('excluded_paths', [])
                )
                
                # Redirigir si está protegido y no excluido
                if is_protected and not is_excluded and path != maintenance_url:
                    return HttpResponseRedirect(maintenance_url)
        
        # Obtener la respuesta
        response = self.get_response(request)
        
        # Si es la página de mantenimiento, establecer código 503
        if request.path == maintenance_url:
            response.status_code = 503
            response['Retry-After'] = 3600  # 1 hora en segundos
            
        return response