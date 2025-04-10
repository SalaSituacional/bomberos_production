const modalHistorial = document.getElementById("modalHistorialBien");

// Cargar datos al mostrar el modal
modalHistorial.addEventListener("show.bs.modal", function (event) {
  const button = event.relatedTarget;
  const bienId = button.getAttribute("data-bien-id");

  fetchWithLoader(`/api/historial-bien/${bienId}/`)
    .then((res) => res)
    .then((data) => {
      const bien = data.bien;
      const movimientos = data.movimientos;

      document.getElementById("bienDetalle").innerHTML = `
        <div class="mb-3">
          <label for="bienIdentificador" class="form-label"><strong>Identificador:</strong></label>
          <input type="text" id="bienIdentificador" class="form-control" value="${bien.identificador}" readonly>
        </div>
        <div class="mb-3">
          <label for="bienDescripcion" class="form-label"><strong>Descripción:</strong></label>
          <input type="text" id="bienDescripcion" class="form-control" value="${bien.descripcion}" readonly>
        </div>
        <div class="mb-3">
          <label for="bienCantidad" class="form-label"><strong>Cantidad:</strong></label>
          <input type="text" id="bienCantidad" class="form-control" value="${bien.cantidad}" readonly>
        </div>
        <div class="mb-3">
          <label for="bienDependencia" class="form-label"><strong>Dependencia:</strong></label>
          <input type="text" id="bienDependencia" class="form-control" value="${bien.dependencia}" readonly>
        </div>
        <div class="mb-3">
          <label for="bienDepartamento" class="form-label"><strong>Departamento:</strong></label>
          <input type="text" id="bienDepartamento" class="form-control" value="${bien.departamento}" readonly>
        </div>
        <div class="mb-3">
          <label for="bienResponsable" class="form-label"><strong>Responsable:</strong></label>
          <input type="text" id="bienResponsable" class="form-control" value="${bien.responsable}" readonly>
        </div>
        <div class="mb-3">
          <label for="bienEstado" class="form-label"><strong>Estado:</strong></label>
          <input type="text" id="bienEstado" class="form-control" value="${bien.estado_actual}" readonly>
        </div>
      `;

      const lista = document.getElementById("listaMovimientos");
      lista.innerHTML = "";

      if (movimientos.length === 0) {
        lista.innerHTML =
          '<li class="list-group-item text-muted">No hay movimientos recientes.</li>';
      } else {
        movimientos.forEach((mov) => {
          lista.innerHTML += `
            <li class="list-group-item">
              <strong>${mov.fecha_orden}</strong> - ${mov.nueva_dependencia} / ${mov.nuevo_departamento} <br>
              Ordenado por: ${mov.ordenado_por}
            </li>
          `;
        });
      }
    });
});

// Limpiar datos al cerrar el modal
modalHistorial.addEventListener("hidden.bs.modal", function () {
  document.getElementById("bienDetalle").innerHTML = "<p>Cargando...</p>";
  document.getElementById("listaMovimientos").innerHTML = "";
});
