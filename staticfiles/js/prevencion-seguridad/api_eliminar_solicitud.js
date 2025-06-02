// Definir DocumentConfig si no está definido
const DocumentConfig = window.DocumentConfig || {
  types: {
    Eliminar: {
      endpoint: '/seguridad_prevencion/api/eliminar_solicitudes/'
    }
  }
};

const handleDeleteDocument = async (boton) => {
  const solicitudId = boton.dataset.solicitud;
  const url = `${DocumentConfig.types.Eliminar.endpoint}${solicitudId}/`;
  
  try {
    // Mostrar modal de confirmación
    const confirmModal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
    const confirmBtn = document.getElementById('confirmDeleteBtn');
    
    const userConfirmed = await new Promise((resolve) => {
      confirmBtn.onclick = () => {
        confirmModal.hide();
        resolve(true);
      };
      
      confirmModal._element.addEventListener('hidden.bs.modal', () => {
        if (!confirmBtn.onclick) resolve(false);
      });
      
      confirmModal.show();
    });
    
    if (!userConfirmed) return;

    const response = await fetchWithLoader(url, {  // Cambiado de fetchWithLoader a fetch
      headers: {
        'X-CSRFToken': getCookie('csrftoken'),
        'Content-Type': 'application/json'
      }
    });
    
    const data = await response;  // Parsear la respuesta JSON
    
    showSuccess(data.message || 'Solicitud eliminada correctamente');
    setTimeout(() => location.reload(), 1500);
    
    
  } catch (error) {
    console.error('Error al eliminar solicitud:', error);
    showError(error.message || 'Error al eliminar la solicitud. Por favor intente nuevamente.');
  }
};


// Función auxiliar para obtener cookies (necesaria para el CSRF token)
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Solo ejecutar si estamos en un contexto donde se necesita
if (document.querySelector('.eliminar-documento')) {
  document.addEventListener('click', (e) => {
    if (e.target.closest('.eliminar-documento')) {
      handleDeleteDocument(e.target.closest('.eliminar-documento'));
    }
  });
}

// Función para mostrar éxito
const showSuccess = (message) => {
  const successToast = document.createElement('div');
  successToast.className = 'alert alert-success position-fixed top-0 end-0 m-3';
  successToast.style.zIndex = '9999';
  successToast.textContent = message;
  document.body.appendChild(successToast);
  
  setTimeout(() => successToast.remove(), 5000);
};

// Función para mostrar errores
const showError = (message) => {
  const errorToast = document.createElement('div');
  errorToast.className = 'alert alert-danger position-fixed top-0 end-0 m-3';
  errorToast.style.zIndex = '9999';
  errorToast.textContent = message;
  document.body.appendChild(errorToast);
  
  setTimeout(() => errorToast.remove(), 5000);
};