document.addEventListener('DOMContentLoaded', function() {
    // Seleccionar todas las filas de la tabla
    const filasReportes = document.querySelectorAll('#tabla-reportes tbody tr');
    
    // Obtener referencia al modal
    const modalReporte = new bootstrap.Modal(document.getElementById('detalleReporteModal'));
    
    // Agregar evento click a cada fila
    filasReportes.forEach(fila => {
        fila.addEventListener('click', async function(e) {
            // Prevenir que se active si se hizo clic en un botón de acción
            if (e.target.tagName === 'A' || e.target.closest('a') || 
                e.target.classList.contains('button-delete-reporte') || 
                e.target.closest('.button-delete-reporte')) {
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
    
    // Manejar eliminación de reportes
    const botonesEliminar = document.querySelectorAll('.button-delete-reporte');
    botonesEliminar.forEach(boton => {
        boton.addEventListener('click', function(e) {
            e.stopPropagation();
            const reporteId = this.getAttribute('data-id');
            const unidad = this.getAttribute('data-unidad');
            const fecha = this.getAttribute('data-fecha');
            
            if (confirm(`¿Está seguro de que desea eliminar el reporte de la unidad ${unidad} del ${fecha}?`)) {
                // Aquí iría la lógica para eliminar el reporte
                fetch(`/mecanica/api/reportes-unidades/${reporteId}/eliminar/`, {
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
    });
    
    // Función para obtener el token CSRF
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
});