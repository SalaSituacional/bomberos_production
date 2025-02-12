let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
    // Evitar que se muestre el banner de instalación por defecto
    e.preventDefault();
    // Guardar el evento para poder mostrar el banner de instalación personalizado
    deferredPrompt = e;

    // Mostrar la ventana modal solo si la PWA no está instalada
    $('#ModalPWA').modal('show');
});

$(document).ready(function() {
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

    // Si el usuario ya tiene la PWA instalada, no mostrar la ventana modal
    if (window.matchMedia('(display-mode: standalone)').matches) {
        alert('La PWA ya está instalada');
        $('#ModalPWA').modal('hide');
    }
});
