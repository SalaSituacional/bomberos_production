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
    const response = fetchWithLoader('/api/conductores/');
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
    let licenciaBadge = '<span class="badge bg-secondary">Sin licencia</span>';
    if (licencia) {
      const vencida = licencia.fecha_vencimiento < hoy;
      const activa = licencia.activa;
      licenciaBadge = `
        <span class="badge ${activa ? (vencida ? 'bg-danger' : 'bg-success') : 'bg-warning'}">
          ${licencia.tipo_licencia_display} ${vencida ? '(Vencida)' : ''}
        </span>
        ${conductor.licencias.length > 1 ? `<span class="badge bg-info">+${conductor.licencias.length - 1}</span>` : ''}
      `;
    }
    
    // Estado certificado
    let certificadoBadge = '<span class="badge bg-secondary">Sin certificado</span>';
    if (certificado) {
      const vencido = certificado.fecha_vencimiento < hoy;
      const activo = certificado.activo;
      certificadoBadge = `
        <span class="badge ${activo ? (vencido ? 'bg-danger' : 'bg-success') : 'bg-warning'}">
          ${vencido ? 'Vencido' : 'Vigente'}
        </span>
      `;
    }
    
    // Estado conductor
    const estadoBadge = `
      <span class="badge ${conductor.activo ? 'bg-success' : 'bg-danger'}">
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
        <td class="text-end">
          <button class="btn btn-sm btn-outline-primary me-1" onclick="mostrarDetalles(${conductor.id})">
            <i class="bi bi-eye"></i>
          </button>
          <a href="/conductores/${conductor.id}/editar/" class="btn btn-sm btn-outline-warning me-1">
            <i class="bi bi-pencil"></i>
          </a>
          <button class="btn btn-sm btn-outline-danger" onclick="confirmarEliminar(${conductor.id})">
            <i class="bi bi-trash"></i>
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
  
  detalleModalTitle.textContent = `${conductor.personal.nombres} ${conductor.personal.apellidos}`;
  detalleModalBody.innerHTML = `
    <div class="row mb-3">
      <div class="col-md-6">
        <div class="card h-100">
          <div class="card-header bg-light">
            <h6 class="mb-0"><i class="bi bi-person-badge"></i> Datos Personales</h6>
          </div>
          <div class="card-body">
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
            <h6 class="mb-0"><i class="bi bi-file-medical"></i> Certificado Médico</h6>
          </div>
          <div class="card-body">
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
    
    <div class="card mt-3">
      <div class="card-header bg-light">
        <h6 class="mb-0"><i class="bi bi-id-card"></i> Licencias</h6>
      </div>
      <div class="card-body">
        ${conductor.licencias.length > 0 ? `
          <div class="table-responsive">
            <table class="table table-sm">
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
      ¿Está seguro que desea eliminar al conductor <strong>${conductor.personal.nombres} ${conductor.personal.apellidos}</strong>?
    `;
  }
  confirmarEliminarModal.show();
};

// Eliminar conductor
confirmarEliminarBtn.addEventListener('click', async () => {
  if (!conductorAEliminar) return;
  
  try {
    const response = await fetchWithLoader(`/api/conductores/${conductorAEliminar}/`, {
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
