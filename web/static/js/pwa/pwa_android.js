let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
    // Permitir que se muestre el banner de instalación por defecto
    e.preventDefault();
    // Guardar el evento para poder mostrar el banner de instalación personalizado
    deferredPrompt = e;
});

$(document).ready(function() {
    // Añadir un evento de clic para asegurar la interacción del usuario
    $(document).on('click', function() {
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
