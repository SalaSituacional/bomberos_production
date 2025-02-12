let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
    // Evitar que se muestre el banner de instalación por defecto
    e.preventDefault();
    // Guardar el evento para poder mostrar el banner de instalación personalizado
    deferredPrompt = e;

    // Habilitar el botón de descarga
    $('#downloadPWA').show();
});

$(document).ready(function() {
    // Verificar si la PWA está instalada
    if (window.matchMedia('(display-mode: standalone)').matches) {
        console.log('La PWA ya está instalada');
        $('#downloadPWA').hide(); // Ocultar el botón si la PWA ya está instalada
    }

    // Habilitar el botón de descarga de la PWA
    $('#downloadPWA').on('click', function() {
        if (deferredPrompt) {
            // Mostrar el prompt de instalación
            deferredPrompt.prompt();
            // Manejar la respuesta del usuario
            deferredPrompt.userChoice.then((choiceResult) => {
                if (choiceResult.outcome === 'accepted') {
                    console.log('User accepted the A2HS prompt');
                } else {
                    console.log('User dismissed the A2HS prompt');
                }
                // Limpiar el deferredPrompt
                deferredPrompt = null;
            });
        }
    });
});
