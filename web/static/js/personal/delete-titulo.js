document.addEventListener('DOMContentLoaded', function() {
  // Configuración de CSRF para AJAX
  const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
  // Manejar clic en botones de eliminar
  document.querySelectorAll('.eliminar-titulo').forEach(button => {
    button.addEventListener('click', function() {
      const tituloId = this.getAttribute('data-id');
      fetchWithLoader(`/eliminar_titulo/${tituloId}/`, {
          method: 'DELETE',
          headers: {
              'X-CSRFToken': csrftoken,
              'Content-Type': 'application/json'
          }
      })
      .then(response => {
        // Eliminar la fila de la tabla
        location.reload()
      })
    });
  });
});