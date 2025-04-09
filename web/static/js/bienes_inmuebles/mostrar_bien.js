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
        <p><strong>Identificador:</strong> ${bien.identificador}</p>
        <p><strong>Descripción:</strong> ${bien.descripcion}</p>
        <p><strong>Cantidad:</strong> ${bien.cantidad}</p>
        <p><strong>Dependencia:</strong> ${bien.dependencia}</p>
        <p><strong>Departamento:</strong> ${bien.departamento}</p>
        <p><strong>Responsable:</strong> ${bien.responsable}</p>
        <p><strong>Estado:</strong> ${bien.estado_actual}</p>
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
