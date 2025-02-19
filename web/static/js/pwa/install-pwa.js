let deferredPrompt;
const installButton = document.getElementById('installpwa');

window.addEventListener('beforeinstallprompt', (event) => {
  // Previene la aparición del cuadro de diálogo de instalación automática
  event.preventDefault();
  deferredPrompt = event;
  installButton.style.display = 'block';

  installButton.addEventListener('click', () => {
    installButton.style.display = 'none';
    deferredPrompt.prompt();
    deferredPrompt.userChoice.then((choiceResult) => {
      if (choiceResult.outcome === 'accepted') {
        alert('El usuario aceptó instalar la PWA');
      }
      deferredPrompt = null;
    });
  });
});

window.addEventListener('appinstalled', () => {
  console.log('PWA instalada con éxito');
  deferredPrompt = null;
});
