let paginaActual = 1;

function cargarBienes(pagina = 1) {
  fetchWithLoader(`/api/bienes/?page=${pagina}`)
    .then((response) => response)
    .then((data) => {
      const tbody = document.querySelector("#tablaBienes tbody");
      tbody.innerHTML = ""; // Limpiar tabla

      let i = (data.current_page - 1) * 15 + 1;

      data.bienes.forEach((bien) => {
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
              <button class="btn btn-primary btn-editar-bien" data-bien-id="${bien.identificador}" data-bs-toggle="modal" data-bs-target="#modalReasignarBien">⇆</button>
              <button class="btn btn-danger" data-bs-toggle="modal" data-bs-target="#modalEliminarBien" data-id-bien="${bien.identificador}">🗑️</button>
              <button class="btn btn-info" data-bs-toggle="modal" data-bs-target="#modalHistorialBien" data-bien-id="${bien.identificador}">📄</button>
            </td>
          </tr>`;
        tbody.insertAdjacentHTML("beforeend", fila);
        i++;
      });

      paginaActual = data.current_page;
      document.getElementById("pagina-actual").textContent = paginaActual;

      document.getElementById("anterior").disabled = paginaActual === 1;
      document.getElementById("siguiente").disabled = paginaActual === data.total_pages;
    })
    .catch((error) => {
      console.error("Error cargando bienes:", error);
    });
}

// Eventos para botones de paginación
document.getElementById("anterior").addEventListener("click", function () {
  if (paginaActual > 1) {
    cargarBienes(paginaActual - 1);
  }
});

document.getElementById("siguiente").addEventListener("click", function () {
  cargarBienes(paginaActual + 1);
});

// Cargar al cargar la página
window.addEventListener("DOMContentLoaded", () => cargarBienes());
