const modalHistorial = document.getElementById("modalHistorialBien");

// Function to safely get attribute, preventing null errors
function getAttributeSafe(element, attribute) {
    return element ? element.getAttribute(attribute) : null;
}

// Cargar datos al mostrar el modal
modalHistorial.addEventListener("show.bs.modal", function (event) {
    const button = event.relatedTarget;
    const bienId = getAttributeSafe(button, "data-bien-id");

    // Clear previous content and show loader
    document.getElementById("bienDetalle").innerHTML = '<p class="text-center text-muted">Cargando detalles del bien...</p>';
    document.getElementById("listaMovimientos").innerHTML = '<p class="text-center text-muted">Cargando movimientos...</p>';

    fetchWithLoader(`/bienesMunicipales/api/historial-bien/${bienId}/`)
        .then((response) => {
          return response; // Parse the JSON from the response
        })
        .then((data) => {
            const bien = data.bien;
            const movimientos = data.movimientos;

            console.log(data)

            let bienDetalleHtml = `
                <div class="card bg-light shadow-sm rounded p-3 mb-4">
                    <div class="card-body">
                        <div class="row g-3">
                            <div class="col-md-6 col-12">
                                <p class="mb-1"><span class="fw-bold text-danger">Identificador:</span><br> <span class="text-dark">${bien.identificador}</span></p>
                            </div>
                            <div class="col-md-6 col-12">
                                <p class="mb-1"><span class="fw-bold text-danger">Descripción:</span><br> <span class="text-dark">${bien.descripcion}</span></p>
                            </div>
                            <div class="col-md-6 col-12">
                                <p class="mb-1"><span class="fw-bold text-danger">Cantidad:</span><br> <span class="text-dark">${bien.cantidad}</span></p>
                            </div>
                            <div class="col-md-6 col-12">
                                <p class="mb-1"><span class="fw-bold text-danger">Dependencia:</span><br> <span class="text-dark">${bien.dependencia}</span></p>
                            </div>
                            <div class="col-md-6 col-12">
                                <p class="mb-1"><span class="fw-bold text-danger">Departamento:</span><br> <span class="text-dark">${bien.departamento}</span></p>
                            </div>
                            <div class="col-md-6 col-12">
                                <p class="mb-1"><span class="fw-bold text-danger">Responsable:</span><br> <span class="text-dark">${bien.responsable}</span></p>
                            </div>
                            <div class="col-md-6 col-12">
                                <p class="mb-1"><span class="fw-bold text-danger">Estado:</span><br> <span class="text-dark">${bien.estado_actual}</span></p>
                            </div>
                            <div class="col-md-6 col-12">
                                <p class="mb-1"><span class="fw-bold text-danger">Fecha Registro:</span><br> <span class="text-dark">${bien.fecha_registro}</span></p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.getElementById("bienDetalle").innerHTML = bienDetalleHtml;

            // --- Restructure Movimientos List with enhanced styling ---
            const listaMovimientos = document.getElementById("listaMovimientos");
            listaMovimientos.innerHTML = ""; // Clear previous content

            if (movimientos.length === 0) {
                listaMovimientos.innerHTML =
                    '<div class="alert alert-info text-center shadow-sm" role="alert"><i class="bi bi-info-circle me-2"></i>No hay movimientos registrados para este bien.</div>';
            } else {
                movimientos.forEach((mov) => {
                    const movementDateString = mov.fecha_orden; // This should be "21-07-2025"
                    const parts = movementDateString.split('-');
                    const movementDate = new Date(parts[2], parts[1] - 1, parts[0]);

                    const formattedDate = movementDate.toLocaleDateString('es-ES', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                    });

                    listaMovimientos.innerHTML += `
                        <div class="card mb-3 shadow-sm border-start border-danger border-5 rounded">
                            <div class="card-body py-2">
                                <h6 class="card-title fw-bold text-danger mb-1 mt-0">Movimiento del ${formattedDate}</h6>
                                <p class="card-text mb-0">
                                    <small class="text-muted">A:</small> <span class="fw-bold">${mov.nueva_dependencia}</span> / <span>${mov.nuevo_departamento}</span>
                                </p>
                                <p class="card-text mb-0"><small class="text-secondary font-italic">Ordenado por: ${mov.ordenado_por}</small></p>
                                ${mov.observaciones ? `<p class="card-text mb-0"><small class="text-secondary">Observaciones: ${mov.observaciones}</small></p>` : ''}
                            </div>
                        </div>
                    `;
                });
            }
        })
        .catch((error) => {
            console.error("Error al cargar historial del bien:", error);
            document.getElementById("bienDetalle").innerHTML = '<div class="alert alert-danger" role="alert"><i class="bi bi-exclamation-triangle me-2"></i>Error al cargar los detalles del bien. Por favor, intente de nuevo.</div>';
            document.getElementById("listaMovimientos").innerHTML = '<div class="alert alert-danger" role="alert"><i class="bi bi-exclamation-triangle me-2"></i>Error al cargar el historial de movimientos. Por favor, intente de nuevo.</div>';
        });
});
// Limpiar datos al cerrar el modal
modalHistorial.addEventListener("hidden.bs.modal", function () {
  document.getElementById("bienDetalle").innerHTML = "<p>Cargando...</p>";
  document.getElementById("listaMovimientos").innerHTML = "";
});
