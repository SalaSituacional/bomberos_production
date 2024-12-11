  // Verificar si el parámetro "registro_exitoso" está presente en la URL
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.has('registro_exitoso') && urlParams.get('registro_exitoso') === 'true') {
      // Mostrar el modal
      const modal = new bootstrap.Modal(document.getElementById('registroExitosoModal'));
      modal.show();

      // Opcional: Eliminar el parámetro de la URL para evitar mostrar el modal al recargar
      const newUrl = window.location.href.split('?')[0];
      window.history.replaceState({}, document.title, newUrl);
    }