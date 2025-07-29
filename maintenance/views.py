from django.shortcuts import render
from django.conf import settings
from datetime import datetime


def maintenance_view(request):
    config = getattr(settings, 'MAINTENANCE_CONFIG', {})
    
    # Función para convertir fechas a timestamp y formato legible
    def process_date(date_str):
        try:
            dt = datetime.strptime(date_str, '%d/%m/%Y %H:%M')
            return {
                'timestamp': int(dt.timestamp()),
                'formatted': dt.strftime('%d/%m/%Y %H:%M')
            }
        except Exception as e:
            print(f"Error procesando fecha: {e}")
            return None
    
    end_date = process_date(config.get('end_time', ''))
    
    context = {
        'end_timestamp': end_date['timestamp'] if end_date else None,
        'end_time_formatted': end_date['formatted'] if end_date else config.get('end_time', ''),
        'start_time_formatted': config.get('start_time', ''),
        'estimated_time': config.get('estimated_time', '')
    }
    return render(request, 'maintenance.html', context, status=503)