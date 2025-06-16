// Estado global
let conductoresData = [];
let conductorAEliminar = null;

// 1. Obtener el token CSRF primero (si usas cookies)
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
const csrftoken = getCookie('csrftoken');

// Elementos del DOM
const conductoresBody = document.getElementById('conductoresBody');
const detalleModal = new bootstrap.Modal(document.getElementById('detalleModal'));
const detalleModalTitle = document.getElementById('detalleModalTitle');
const detalleModalBody = document.getElementById('detalleModalBody');
const confirmarEliminarModal = new bootstrap.Modal(document.getElementById('confirmarEliminarModal'));
const confirmarEliminarBtn = document.getElementById('confirmarEliminarBtn');

// Formatear fecha
const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A';
  const date = new Date(dateStr);
  return date.toLocaleDateString('es-ES');
};

// Obtener conductores desde la API
const fetchConductores = async () => {
  try {
    const response = fetchWithLoader('/mecanica/api/conductores/');
    conductoresData = await response;
    renderConductores();
  } catch (error) {
    console.error('Error:', error);
    conductoresBody.innerHTML = `
      <tr>
        <td colspan="7" class="text-center text-danger">
          Error al cargar los datos. Intente recargar la página.
        </td>
      </tr>`;
  }
};

// Renderizar lista de conductores
const renderConductores = () => {
  const hoy = new Date().toISOString().split('T')[0];

  conductoresBody.innerHTML = conductoresData.map(conductor => {
    const licencia = conductor.licencias.length > 0 ? conductor.licencias[0] : null;
    const certificado = conductor.certificados_medicos.length > 0 ? conductor.certificados_medicos[0] : null;

    // Estado licencia
    let licenciaBadge = '<span class="">Sin licencia</span>';
    if (licencia) {
      const vencida = licencia.fecha_vencimiento < hoy;
      const activa = licencia.activa;
      licenciaBadge = `
        <span class="badge size-font ${activa ? (vencida ? 'bg-danger' : 'bg-success') : 'bg-warning'}">
          ${licencia.tipo_licencia_display} ${vencida ? '(Vencida)' : ''}
        </span>
        ${conductor.licencias.length > 1 ? `<span>+${conductor.licencias.length - 1}</span>` : ''}
      `;
    }

    // Estado certificado
    let certificadoBadge = '<span class="badge bg-secondary">Sin certificado</span>';
    if (certificado) {
      const vencido = certificado.fecha_vencimiento < hoy;
      const activo = certificado.activo;
      certificadoBadge = `
        <span class="badge size-font ${activo ? (vencido ? 'bg-danger' : 'bg-success') : 'bg-warning'}">
          ${vencido ? 'Vencido' : 'Vigente'}
        </span>
      `;
    }

    // Estado conductor
    const estadoBadge = `
      <span class="badge size-font ${conductor.activo ? 'bg-success' : 'bg-danger'}">
        ${conductor.activo ? 'Activo' : 'Inactivo'}
      </span>
    `;

    return `
      <tr>
        <td>${conductor.personal.nombres} ${conductor.personal.apellidos}</td>
        <td>${conductor.personal.jerarquia}</td>
        <td>${conductor.personal.cedula}</td>
        <td>${licenciaBadge}</td>
        <td>${certificadoBadge}</td>
        <td>${estadoBadge}</td>
        <td>
          <button class="btn" onclick="mostrarDetalles(${conductor.id})">
            <svg
                  width="35px"
                  height="35px"
                  viewBox="0 0 1024 1024"
                  class="icon"
                  version="1.1"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="#000000"
                  style="pointer-events: none;"
                >
                  <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                  <g
                    id="SVGRepo_tracerCarrier"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  ></g>
                  <g id="SVGRepo_iconCarrier">
                    <path
                      d="M892.1 938.7H131.9c-17.8 0-35.1-3.5-51.4-10.4-15.6-6.6-29.7-16.1-41.9-28.2C26.5 888 17 873.9 10.3 858.2 3.5 841.8 0 824.5 0 806.8V217.2c0-17.8 3.5-35 10.4-51.3 6.6-15.7 16.1-29.8 28.2-41.9 12.2-12.2 26.3-21.7 42-28.3 16.2-6.9 33.5-10.4 51.3-10.4h83.4c23.6 0 42.7 19.1 42.7 42.7s-19.1 42.7-42.7 42.7h-83.4c-6.3 0-12.4 1.2-18.1 3.6-5.6 2.4-10.6 5.7-14.9 10-4.3 4.3-7.6 9.2-10 14.8-2.4 5.7-3.6 11.8-3.6 18.1v589.6c0 6.3 1.2 12.4 3.7 18.1 2.3 5.5 5.7 10.5 10 14.8 4.3 4.2 9.2 7.6 14.8 9.9 5.8 2.4 11.9 3.7 18.1 3.7h760.2c6.3 0 12.4-1.2 18.1-3.6 5.6-2.4 10.6-5.7 14.9-10 4.3-4.3 7.6-9.2 10-14.8 2.4-5.7 3.6-11.8 3.6-18.1V217.2c0-6.3-1.2-12.4-3.7-18.1-2.3-5.5-5.7-10.5-10-14.8-4.3-4.2-9.2-7.6-14.8-9.9-5.8-2.4-11.9-3.7-18.1-3.7h-83.4c-23.6 0-42.7-19.1-42.7-42.7s19.1-42.7 42.7-42.7h83.4c17.8 0 35.1 3.5 51.4 10.4 15.6 6.6 29.7 16.1 41.9 28.2 12.1 12.1 21.6 26.2 28.3 41.9 6.9 16.3 10.4 33.6 10.4 51.4v589.6c0 17.8-3.5 35-10.4 51.3-6.6 15.7-16.1 29.8-28.2 41.9-12.2 12.2-26.3 21.7-42 28.3-16.3 6.9-33.6 10.4-51.4 10.4z"
                      fill="#3688FF"
                    ></path>
                    <path
                      d="M229.8 714.8c-6.1 0-12.3-1.3-18.1-4.1-21.3-10-30.5-35.5-20.4-56.8L467.5 67.1c10-21.3 35.5-30.5 56.8-20.4 21.3 10 30.5 35.5 20.4 56.8L268.5 690.3c-7.3 15.4-22.7 24.5-38.7 24.5zM810.7 448H640c-23.6 0-42.7-19.1-42.7-42.7s19.1-42.7 42.7-42.7h170.7c23.6 0 42.7 19.1 42.7 42.7S834.2 448 810.7 448zM810.7 704h-384c-23.6 0-42.7-19.1-42.7-42.7s19.1-42.7 42.7-42.7h384c23.6 0 42.7 19.1 42.7 42.7S834.2 704 810.7 704z"
                      fill="#5F6379"
                    ></path>
                  </g>
                </svg>
          </button>
          <a href="/conductores/${conductor.id}/editar/" class="btn">
            <svg width="35px" height="35px" viewBox="0 0 1024 1024" class="icon" version="1.1" xmlns="http://www.w3.org/2000/svg" fill="#000000" style="pointer-events: none;"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"><path d="M823.3 938.8H229.4c-71.6 0-129.8-58.2-129.8-129.8V215.1c0-71.6 58.2-129.8 129.8-129.8h297c23.6 0 42.7 19.1 42.7 42.7s-19.1 42.7-42.7 42.7h-297c-24.5 0-44.4 19.9-44.4 44.4V809c0 24.5 19.9 44.4 44.4 44.4h593.9c24.5 0 44.4-19.9 44.4-44.4V512c0-23.6 19.1-42.7 42.7-42.7s42.7 19.1 42.7 42.7v297c0 71.6-58.2 129.8-129.8 129.8z" fill="#3688FF"></path><path d="M483 756.5c-1.8 0-3.5-0.1-5.3-0.3l-134.5-16.8c-19.4-2.4-34.6-17.7-37-37l-16.8-134.5c-1.6-13.1 2.9-26.2 12.2-35.5l374.6-374.6c51.1-51.1 134.2-51.1 185.3 0l26.3 26.3c24.8 24.7 38.4 57.6 38.4 92.7 0 35-13.6 67.9-38.4 92.7L513.2 744c-8.1 8.1-19 12.5-30.2 12.5z m-96.3-97.7l80.8 10.1 359.8-359.8c8.6-8.6 13.4-20.1 13.4-32.3 0-12.2-4.8-23.7-13.4-32.3L801 218.2c-17.9-17.8-46.8-17.8-64.6 0L376.6 578l10.1 80.8z" fill="#5F6379"></path></g></svg>
          </a>
          <button class="btn" onclick="confirmarEliminar(${conductor.id})">
         <svg width="35px" height="35px" viewBox="0 0 1024 1024" class="icon" version="1.1"
                  xmlns="http://www.w3.org/2000/svg" fill="#000000" style="pointer-events: none;">
                  <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                  <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                  <g id="SVGRepo_iconCarrier">
                    <path
                      d="M779.5 1002.7h-535c-64.3 0-116.5-52.3-116.5-116.5V170.7h768v715.5c0 64.2-52.3 116.5-116.5 116.5zM213.3 256v630.1c0 17.2 14 31.2 31.2 31.2h534.9c17.2 0 31.2-14 31.2-31.2V256H213.3z"
                      fill="#3688FF"></path>
                    <path
                      d="M917.3 256H106.7C83.1 256 64 236.9 64 213.3s19.1-42.7 42.7-42.7h810.7c23.6 0 42.7 19.1 42.7 42.7S940.9 256 917.3 256zM618.7 128H405.3c-23.6 0-42.7-19.1-42.7-42.7s19.1-42.7 42.7-42.7h213.3c23.6 0 42.7 19.1 42.7 42.7S642.2 128 618.7 128zM405.3 725.3c-23.6 0-42.7-19.1-42.7-42.7v-256c0-23.6 19.1-42.7 42.7-42.7S448 403 448 426.6v256c0 23.6-19.1 42.7-42.7 42.7zM618.7 725.3c-23.6 0-42.7-19.1-42.7-42.7v-256c0-23.6 19.1-42.7 42.7-42.7s42.7 19.1 42.7 42.7v256c-0.1 23.6-19.2 42.7-42.7 42.7z"
                      fill="#5F6379"></path>
                  </g>
                </svg>
          </button>
        </td>
      </tr>
    `;
  }).join('');
};

// Mostrar detalles del conductor
window.mostrarDetalles = (id) => {
  const conductor = conductoresData.find(c => c.id === id);
  if (!conductor) return;

  const licenciasRows = conductor.licencias.map(licencia => `
    <tr>
      <td>${licencia.tipo_licencia_display}</td>
      <td>${licencia.numero_licencia}</td>
      <td>${formatDate(licencia.fecha_emision)}</td>
      <td class="${licencia.fecha_vencimiento < new Date().toISOString().split('T')[0] ? 'text-danger' : ''}">
        ${formatDate(licencia.fecha_vencimiento)} ${licencia.fecha_vencimiento < new Date().toISOString().split('T')[0] ? '(Vencida)' : ''}
      </td>
      <td>
        <span class="badge ${licencia.activa ? 'bg-success' : 'bg-secondary'}">
          ${licencia.activa ? 'Activa' : 'Inactiva'}
        </span>
      </td>
    </tr>
  `).join('');

  const certificado = conductor.certificados_medicos.length > 0 ? conductor.certificados_medicos[0] : null;

  detalleModalTitle.textContent = `Informacion Detallada: ${conductor.personal.nombres} ${conductor.personal.apellidos}`;
  detalleModalBody.innerHTML = `
    <div class="row mb-3 expand-card">
      <div class="col-md-6">
        <div class="card h-100">
          <div class="card-header card-header-modify bg-light">
            <h5><i class="bi bi-person-badge"></i> Datos Personales</h5>
          </div>
          <div class="card-body card-body-modify">
            <p><strong>Jerarquía:</strong> ${conductor.personal.jerarquia}</p>
            <p><strong>Cédula:</strong> ${conductor.personal.cedula}</p>
            <p><strong>Estado:</strong> 
              <span class="badge ${conductor.activo ? 'bg-success' : 'bg-danger'}">
                ${conductor.activo ? 'Activo' : 'Inactivo'}
              </span>
            </p>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <div class="card h-100">
          <div class="card-header bg-light">
            <h5><i class="bi bi-file-medical"></i> Certificado Médico</h5>
          </div>
          <div class="card-body card-body-modify">
            ${certificado ? `
              <p><strong>Centro Médico:</strong> ${certificado.centro_medico}</p>
              <p><strong>Vencimiento:</strong> 
                <span class="${certificado.fecha_vencimiento < new Date().toISOString().split('T')[0] ? 'text-danger' : ''}">
                  ${formatDate(certificado.fecha_vencimiento)}
                  ${certificado.fecha_vencimiento < new Date().toISOString().split('T')[0] ? '(Vencido)' : ''}
                </span>
              </p>
              <p><strong>Estado:</strong> 
                <span class="badge ${certificado.activo ? 'bg-success' : 'bg-secondary'}">
                  ${certificado.activo ? 'Activo' : 'Inactivo'}
                </span>
              </p>
            ` : '<p class="text-muted">No hay certificado registrado</p>'}
          </div>
        </div>
      </div>
    </div>
    
    <div class="card mt-3 card-conductores-modify">
      <div class="card-header bg-light">
        <h5><i class="bi bi-id-card"></i> Licencias</h5>
      </div>
      <div class="card-body">
        ${conductor.licencias.length > 0 ? `
          <div class="table-responsive dsp-flex">
            <table class="table table-hover">
              <thead>
                <tr>
                  <th>Tipo</th>
                  <th>Número</th>
                  <th>Emisión</th>
                  <th>Vencimiento</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                ${licenciasRows}
              </tbody>
            </table>
          </div>
        ` : '<p class="text-muted">No hay licencias registradas</p>'}
      </div>
    </div>
  `;

  detalleModal.show();
};

// Confirmar eliminación
window.confirmarEliminar = (id) => {
  conductorAEliminar = id;
  const conductor = conductoresData.find(c => c.id === id);
  if (conductor) {
    document.getElementById('confirmarEliminarBody').innerHTML = `
      Nombre Del Conductor: <strong>${conductor.personal.nombres} ${conductor.personal.apellidos}</strong>
    `;
  }
  confirmarEliminarModal.show();
};

// Eliminar conductor
confirmarEliminarBtn.addEventListener('click', async () => {
  if (!conductorAEliminar) return;

  try {
    const response = await fetchWithLoader(`/mecanica/api/conductores/${conductorAEliminar}/`, {
      method: 'DELETE',
      headers: {
        'X-CSRFToken': csrftoken,
        'Content-Type': 'application/json'
      }
    });

    if (response) {
      fetchConductores(); // Recargar la lista
      confirmarEliminarModal.hide();
    } else {
      alert('Error al eliminar el conductor');
    }
  } catch (error) {
    console.error('Error:', error);
    alert('Error al conectar con el servidor');
  }
});

// Inicializar
document.addEventListener('DOMContentLoaded', fetchConductores);
