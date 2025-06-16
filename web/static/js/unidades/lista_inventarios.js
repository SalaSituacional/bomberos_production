    document.addEventListener('DOMContentLoaded', function () {
        const botonesDetalle = document.querySelectorAll('.ver-detalle');
    const detalleModal = new bootstrap.Modal(document.getElementById('detalleModal'));
    const modalContent = document.getElementById('modal-body-content');

    // Función para mostrar el loader
    function showLoader() {
        modalContent.innerHTML = `
                <div class="text-center py-4">
                    <div class="text-primary" role="status">
                        <span class="visually-hidden">Cargando...</span>
                    </div>
                    <p class="mt-2">Cargando detalles del inventario...</p>
                </div>
            `;
        }

        botonesDetalle.forEach(boton => {
        boton.addEventListener('click', async function () {
            const id = this.dataset.id;

            // Mostrar el loader inmediatamente
            showLoader();

            // Mostrar el modal
            detalleModal.show();

            try {
                const response = await fetchWithLoader(`/mecanica/inventarios/ajax/${id}/`);
                const data = await response;

                // Construir HTML con los datos
                let html = `
                        <div class="container-fluid container-info-tools">
                            <div>
                                <div class="">
                                    <p><strong>Unidad:</strong> ${data.inventario.unidad}</p>
                                    <p><strong>Fecha:</strong> ${data.inventario.fecha}</p>
                                </div>
                                <div class="">
                                    <p><strong>Realizado por:</strong> ${data.inventario.realizado_por.nombre_completo || data.inventario.realizado_por}</p>
                                    ${data.inventario.observaciones ? `<p><strong>Observaciones:</strong> ${data.inventario.observaciones}</p>` : ''}
                                </div>
                            </div>
                            <div class="table-responsive edit-table-tools">
                                <table class="table table-hover align-middle table-modify">
                                    <thead>
                                        <tr>
                                            <th>Herramienta</th>
                                            <th>Presente</th>
                                            <th>Estado</th>
                                            <th>Observaciones</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${data.detalles.map(detalle => `
                                            <tr class="${detalle.presente ? '' : 'table-danger'}">
                                                <td>${detalle.herramienta}</td>
                                                <td class="text-center">
                                                    ${detalle.presente ?
                        '<span class="text-success">Presente</span>' :
                        '<span class="text-danger">No Presente</span>'}
                                                </td>
                                                <td>
                                                    <span class="badge ${getEstadoBadgeClass(detalle.estado)}">
                                                        ${detalle.estado}
                                                    </span>
                                                </td>
                                                <td>${detalle.observaciones}</td>
                                            </tr>
                                        `).join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    `;

                modalContent.innerHTML = html;

            } catch (error) {
                console.error('Error al cargar el detalle:', error);
                modalContent.innerHTML = `
                        <div class="alert alert-danger">
                            <i class="fas fa-exclamation-triangle mr-2"></i>
                            Error al cargar los detalles: ${error.message}
                        </div>
                    `;
            }
        });
        });

    // Función auxiliar para clases de badges según estado
    function getEstadoBadgeClass(estado) {
        const estadosClasses = {
            'Bueno': 'bg-success',
            'Regular': 'bg-warning',
            'Malo': 'bg-danger',
            'En reparación': 'bg-secondary'
        };
        return estadosClasses[estado] || 'bg-primary';
    }

    // Resetear el modal cuando se cierre
    detalleModal._element.addEventListener('hidden.bs.modal', function () {
        showLoader();
        });
    });
