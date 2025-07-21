document.addEventListener('DOMContentLoaded', function() {

    // Initialize Bootstrap Modals
    const detalleModal = new bootstrap.Modal(document.getElementById('detalleModal'));
    const confirmarEliminarModal = new bootstrap.Modal(document.getElementById('confirmarEliminarModal'));

    // Get necessary DOM elements
    const conductoresTable = document.getElementById('conductoresTable');
    const confirmarEliminarBtn = document.getElementById('confirmarEliminarBtn');
    const detalleModalBody = document.getElementById('detalleModalBody');
    const confirmarEliminarBody = document.getElementById('confirmarEliminarBody');

    let conductorIdToDelete = null;

    if (conductoresTable) {
        conductoresTable.addEventListener('click', async function(event) {
            const targetButton = event.target.closest('button');

            if (targetButton) {
                const row = targetButton.closest('tr');
                if (!row) return;

                const conductorId = row.dataset.id;

                if (targetButton.classList.contains('btn-details-conductor')) {
                    if (detalleModalTitle && detalleModalBody) {
                        detalleModal.show();

                        try {
                            const response = await fetchWithLoader(`/mecanica/api/info_conductores/${conductorId}/`);
                            const conductor = await response;

                            if (conductor) {
                                detalleModalBody.innerHTML = `
                                    <div class="container-fluid">
                                        <div class="row mb-3">
                                            <div class="col-md-6">
                                                <p><strong>Nombre Completo:</strong> ${conductor.personal.nombres} ${conductor.personal.apellidos}</p>
                                                <p><strong>Jerarquía:</strong> ${conductor.personal.jerarquia}</p>
                                                <p><strong>Cédula:</strong> ${conductor.personal.cedula}</p>
                                                </div>
                                            <div class="col-md-6">
                                                <p><strong>Estado:</strong> <span class="badge ${conductor.activo ? 'bg-success' : 'bg-danger'}">${conductor.activo ? 'Activo' : 'Inactivo'}</span></p>
                                                <p><strong>Observaciones Generales:</strong> ${conductor.observaciones_generales || 'N/A'}</p>
                                            </div>
                                        </div>

                                        <h5>Licencias</h5>
                                        ${conductor.licencias.length > 0 ? `
                                            <div class="table-responsive">
                                                <table class="table table-bordered table-striped table-sm">
                                                    <thead class="table-light">
                                                        <tr>
                                                            <th class="fixed-width">Tipo</th>
                                                            <th class="fixed-width">Número</th>
                                                            <th class="fixed-width">Emisión</th>
                                                            <th class="fixed-width">Vencimiento</th>
                                                            <th class="fixed-width">Organismo</th>
                                                            <th class="fixed-width">Estado</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        ${conductor.licencias.map(lic => `
                                                            <tr>
                                                                <td class="fixed-width">${lic.tipo_licencia_display}</td>
                                                                <td class="fixed-width">${lic.numero_licencia}</td>
                                                                <td class="fixed-width">${lic.fecha_emision}</td>
                                                                <td class="fixed-width">${lic.fecha_vencimiento}</td>
                                                                <td class="fixed-width">${lic.organismo_emisor}</td>
                                                                <td class="fixed-width"><span class="badge ${lic.activa ? 'bg-success' : 'bg-secondary'}">${lic.activa ? 'Activa' : 'Inactiva'}</span></td>
                                                            </tr>
                                                        `).join('')}
                                                    </tbody>
                                                </table>
                                            </div>
                                        ` : '<p>No hay licencias registradas para este conductor.</p>'}

                                        <h5>Certificados Médicos</h5>
                                        ${conductor.certificados_medicos.length > 0 ? `
                                            <div class="table-responsive">
                                                <table class="table table-bordered table-striped table-sm">
                                                    <thead class="table-light">
                                                        <tr>
                                                            <th class="fixed-width">Emisión</th>
                                                            <th class="fixed-width">Vencimiento</th>
                                                            <th class="fixed-width">Centro Médico</th>
                                                            <th class="fixed-width">Médico</th>
                                                            <th class="fixed-width">Estado</th>
                                                        </tr>
                                                    </thead>
                                                    <tbody>
                                                        ${conductor.certificados_medicos.map(cert => `
                                                            <tr>
                                                                <td class="fixed-width">${cert.fecha_emision}</td>
                                                                <td class="fixed-width">${cert.fecha_vencimiento}</td>
                                                                <td class="fixed-width">${cert.centro_medico}</td>
                                                                <td class="fixed-width">${cert.medico}</td>
                                                                <td class="fixed-width"><span class="badge ${cert.activo ? 'bg-success' : 'bg-secondary'}">${cert.activo ? 'Activo' : 'Inactivo'}</span></td>
                                                            </tr>
                                                        `).join('')}
                                                    </tbody>
                                                </table>
                                            </div>
                                        ` : '<p>No hay certificados médicos registrados para este conductor.</p>'}
                                    </div>
                                `;
                            } else {
                                detalleModalTitle.textContent = 'Error';
                                detalleModalBody.innerHTML = '<p class="text-danger">No se encontraron detalles para este conductor.</p>';
                            }

                        } catch (error) {
                            console.error('Error fetching conductor details:', error);
                            detalleModalTitle.textContent = 'Error';
                            detalleModalBody.innerHTML = '<p class="text-danger">Error al cargar los detalles del conductor. Por favor, inténtalo de nuevo.</p>';
                        }
                    }
                }
                // Handle "Delete" button click (remains the same as previous logic)
                else if (targetButton.classList.contains('btn-delete-conductor')) {
                    const nombreConductorFromRow = row.cells[0].textContent.trim();
                    const cedulaConductorFromRow = row.cells[2].textContent.trim();
                    if (confirmarEliminarBody) {
                        conductorIdToDelete = conductorId; // Store the ID for the delete confirmation
                        confirmarEliminarBody.innerHTML = `¿Estás seguro de que quieres eliminar al conductor <strong>${nombreConductorFromRow}</strong> con cédula <strong>${cedulaConductorFromRow}</strong>? Esta acción no se puede deshacer.`;
                        confirmarEliminarModal.show();
                    }
                }
            }
        });
    }

    // --- Event Listener for Confirm Delete Button ---
    if (confirmarEliminarBtn) {
        confirmarEliminarBtn.addEventListener('click', function() {
            if (conductorIdToDelete) {
                // Perform the AJAX request to delete the conductor
                fetch(`/api/conductores/${conductorIdToDelete}/`, { // Ensure this URL matches your Django URL pattern
                    method: 'DELETE',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': getCookie('csrftoken') // Important for Django security
                    }
                })
                .then(response => {
                    if (response.ok) {
                        // Conductor deleted successfully from backend
                        // Remove the row from the table
                        const rowToRemove = conductoresTable.querySelector(`tr[data-id="${conductorIdToDelete}"]`);
                        if (rowToRemove) {
                            rowToRemove.remove();
                            // If the table becomes empty, you might want to show a "No data" message
                            if (conductoresTable.querySelector('#conductoresBody').children.length === 0) {
                                conductoresTable.querySelector('#conductoresBody').innerHTML = '<tr><td colspan="7" class="text-center">No se encontraron conductores.</td></tr>';
                            }
                        }
                        confirmarEliminarModal.hide(); // Hide the modal
                        alert('Conductor eliminado exitosamente.'); // Provide user feedback
                        conductorIdToDelete = null; // Reset the stored ID
                    } else {
                        // Handle server-side errors (e.g., conductor not found)
                        response.json().then(data => {
                            console.error('Error al eliminar el conductor:', data.error);
                            alert(`Error al eliminar el conductor: ${data.error || 'Mensaje desconocido'}`);
                        }).catch(() => {
                            console.error('Error al eliminar el conductor: Respuesta no JSON');
                            alert('Hubo un error inesperado al eliminar el conductor.');
                        });
                    }
                })
                .catch(error => {
                    // Handle network errors
                    console.error('Error de red al eliminar el conductor:', error);
                    alert('Hubo un error de conexión al eliminar el conductor. Por favor, inténtalo de nuevo.');
                });
            }
        });
    }

    // --- Helper function to get CSRF token from cookies (essential for Django) ---
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

});