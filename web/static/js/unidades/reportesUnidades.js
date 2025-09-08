document.addEventListener('DOMContentLoaded', function() {
    // Seleccionar todas las filas de la tabla
    const filasReportes = document.querySelectorAll('#tabla-reportes tbody tr');
    const modalReporte = new bootstrap.Modal(document.getElementById('detalleReporteModal'));
    
    // Agregar evento click a cada fila
    filasReportes.forEach(fila => {
        fila.addEventListener('click', async function(e) {
            // Prevenir que se active si se hizo clic en un botón de acción
            if (e.target.tagName === 'A' || e.target.closest('button') || e.target.classList.contains('button-delete-reporte') || e.target.classList.contains('button-edit-reporte') || e.target.closest('.button-delete-reporte')) {
                return;
            }
            
            const reporteId = this.getAttribute('data-reporte-id');
            
            // Mostrar el modal
            modalReporte.show();
            document.getElementById('modal-reporte-content').innerHTML = `<div class="text-center">
                        <div class="spinner-border text-danger" role="status">
                            <span class="visually-hidden">Cargando...</span>
                        </div>
                        <p class="mt-2">Cargando información del reporte...</p>
                    </div>`;
            
            // Cargar los detalles del reporte via AJAX
            try {
                const response = await fetch(`/mecanica/api/reportes-unidades/${reporteId}/`);
                const data = await response.json();
                
                document.getElementById('modal-reporte-content').innerHTML = `
                    <div class="row">
                        <div class="col-md-6">
                            <div class="detail-item">
                                <div class="detail-icon bg-primary">
                                    <i class="bi bi-truck"></i>
                                </div>
                                <div class="detail-content">
                                    <span class="fw-bold text-secondary">Unidad:</span>
                                    <span class="text-dark">${data.unidad || 'N/A'}</span>
                                </div>
                            </div>
                            
                            <div class="detail-item">
                                <div class="detail-icon bg-info">
                                    <i class="bi bi-building"></i>
                                </div>
                                <div class="detail-content">
                                    <span class="fw-bold text-secondary">División:</span>
                                    <span class="text-dark">${data.division || 'N/A'}</span>
                                </div>
                            </div>
                            
                            <div class="detail-item">
                                <div class="detail-icon bg-warning">
                                    <i class="bi bi-clipboard-check"></i>
                                </div>
                                <div class="detail-content">
                                    <span class="fw-bold text-secondary">Tipo de Reporte:</span>
                                    <span class="text-dark">${data.tipo_reporte || 'N/A'}</span>
                                </div>
                            </div>
                            
                            <div class="detail-item">
                                <div class="detail-icon bg-success">
                                    <i class="bi bi-calendar-event"></i>
                                </div>
                                <div class="detail-content">
                                    <span class="fw-bold text-secondary">Fecha y Hora:</span>
                                    <span class="text-dark">${data.fecha_reporte || 'N/A'} - ${data.hora_reporte || 'N/A'}</span>
                                </div>
                            </div>
                        </div>
                        
                        <div class="col-md-6">
                            <div class="detail-item">
                                <div class="detail-icon bg-danger">
                                    <i class="bi bi-person"></i>
                                </div>
                                <div class="detail-content">
                                    <span class="fw-bold text-secondary">Reportado por:</span>
                                    <span class="text-dark">${data.personal_responsable || 'N/A'}</span>
                                </div>
                            </div>
                            <div class="detail-item">
                                <div class="detail-icon bg-secondary">
                                    <i class="bi bi-card-text"></i>
                                </div>
                                <div class="detail-content">
                                    <span class="fw-bold text-secondary">Descripción:</span>
                                    <p class="text-dark">${data.descripcion || 'Sin descripción'}</p>
                                </div>
                            </div>
                        </div>
                    </div>`;
                
            } catch (error) {
                console.error('Error al cargar los detalles:', error);
                document.getElementById('modal-reporte-content').innerHTML = `
                    <div class="alert alert-danger" role="alert">
                        <i class="bi bi-exclamation-triangle-fill me-2"></i>
                        Error al cargar los detalles del reporte. Por favor, intente nuevamente.
                    </div>
                `;
            }
        });
    });
    
    // Manejar eliminación de reportes// Manejar la eliminación de reportes con un modal de confirmación
    const botonesEliminar = document.querySelectorAll('.button-delete-reporte');
    const confirmationModal = new bootstrap.Modal(document.getElementById('confirmationModal'));
    const confirmDeleteBtn = document.getElementById('confirm-delete-btn');
    const modalDeleteText = document.getElementById('modal-delete-text');

    let reporteAEliminar = null;
    botonesEliminar.forEach(boton => {
        boton.addEventListener('click', function(e) {
            e.stopPropagation();
            const reporteId = this.getAttribute('data-id');
            const unidad = this.getAttribute('data-unidad');
            const fecha = this.getAttribute('data-fecha');
            
            // Almacenar el ID del reporte en una variable temporal
            reporteAEliminar = reporteId;

            // Actualizar el texto del modal con los datos del reporte
            modalDeleteText.innerHTML = `Reporte de la unidad <strong>${unidad}</strong> del ${fecha}.`;
            
            // Mostrar el modal
            confirmationModal.show();
        });
    });

    // Manejar el clic en el botón de "Eliminar" dentro del modal
    confirmDeleteBtn.addEventListener('click', function() {
        if (reporteAEliminar) {
            // Cerrar el modal
            confirmationModal.hide();

            // Lógica para eliminar el reporte
            fetch(`/mecanica/api/reportes-unidades/${reporteAEliminar}/eliminar/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                }
            })
            .then(response => {
                if (response.ok) {
                    location.reload();
                } else {
                    alert('Error al eliminar el reporte');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Error al eliminar el reporte');
            });
        }
    });

    // Función para obtener el token CSRF (esta parte no cambia)
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






    // Manejar la edición de reportes
    const editReporteModal = new bootstrap.Modal(document.getElementById('editReporteModal'));
    const botonesEditar = document.querySelectorAll('.button-edit-reporte');
    const editForm = document.getElementById('editReporteForm');
    const saveEditBtn = document.getElementById('save-edit-btn');
    const editServicioSelect = document.getElementById('id_servicio');

    botonesEditar.forEach(boton => {
        boton.addEventListener('click', function(e) {
            // Prevenir el comportamiento por defecto del enlace si fuera un <a>
            e.preventDefault(); 
            
            // Obtener los datos del reporte desde los atributos data-*
            const reporteId = this.getAttribute('data-id');
            const unidad = this.getAttribute('data-unidad');
            const servicioId = this.getAttribute('data-servicio-id');
            const fecha = this.getAttribute('data-fecha');
            const hora = this.getAttribute('data-hora');
            const responsable = this.getAttribute('data-responsable');
            const descripcion = this.getAttribute('data-descripcion');
            
            // Llenar el formulario del modal con los datos
            document.getElementById('edit-reporte-id').value = reporteId;
            document.getElementById('id_id_unidad').setAttribute('readonly', true); // Hacer el campo de unidad solo lectura
            document.getElementById('id_id_unidad').value = unidad;
            document.getElementById('id_fecha').value = fecha;
            document.getElementById('id_hora').value = hora;
            document.getElementById('id_responsable').value = responsable;
            document.getElementById('id_descripcion').value = descripcion;
            
            editServicioSelect.value = servicioId;

            // Mostrar el modal
            editReporteModal.show();
        });
    });

    // Manejar el envío del formulario del modal
    saveEditBtn.addEventListener('click', function() {
        const reporteId = document.getElementById('edit-reporte-id').value;
        const formData = {
            servicio: document.getElementById('id_servicio').value,
            fecha: document.getElementById('id_fecha').value,
            hora: document.getElementById('id_hora').value,
            responsable: document.getElementById('id_responsable').value,
            descripcion: document.getElementById('id_descripcion').value,
        };

        fetchWithLoader(`/mecanica/api/reportes-unidades/${reporteId}/editar/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(formData),
        })
        .then(data => {
            editReporteModal.hide();
            location.reload(); // Recargar la página para ver los cambios
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al actualizar el reporte.');
        });
    });
});