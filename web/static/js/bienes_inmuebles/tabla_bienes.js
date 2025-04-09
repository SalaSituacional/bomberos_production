function cargarBienes() {
  fetchWithLoader("/api/bienes/")
    .then((response) => response)
    .then((data) => {
      const tbody = document.querySelector("#tablaBienes tbody");
      tbody.innerHTML = ""; // Limpiar tabla
      i = 1;

      data.forEach((bien) => {
        const fila = `
            <tr>
              <td>${i}</td>
              <td>${bien.identificador}</td>
              <td>${bien.descripcion}</td>
              <td>${bien.cantidad}</td>
              <td>${bien.dependencia}</td>
              <td>${bien.departamento}</td>
              <td>${bien.responsable}</td>
              <td>${bien.fecha_registro}</td>
              <td>${bien.estado_actual}</td>
              <td>
                <button class="btn btn-primary btn-editar-bien" data-bien-id="${ bien.identificador }" data-bs-toggle="modal" data-bs-target="#modalReasignarBien"> ⇆ </button>
                <button class="btn btn-danger" onclick="eliminarBien(${bien.identificador})">🗑️</button>
                <button class="btn btn-info" onclick="verHistorial(${bien.identificador})">📄</button>
              </td>
            </tr>
          `;
        tbody.insertAdjacentHTML("beforeend", fila);
        i++;
      });
    })
    .catch((error) => {
      console.error("Error cargando bienes:", error);
    });
}

// Cargar al cargar la página
window.addEventListener("DOMContentLoaded", cargarBienes);
