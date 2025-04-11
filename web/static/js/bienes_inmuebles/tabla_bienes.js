let paginaActual = 1;

// Función para cargar los bienes desde la API
function cargarBienes(pagina = 1) {
  const filtro = document.getElementById("filterJerarquia").value.trim();
  const url = filtro
    ? `/api/bienes/?identificador=${encodeURIComponent(filtro)}`
    : `/api/bienes/?page=${pagina}`;

  fetchWithLoader(url)
    .then((response) => response)
    .then((data) => {
      const tbody = document.querySelector("#tablaBienes tbody");
      tbody.innerHTML = ""; // Limpiar tabla

      // let i = 1;
      // if (!filtro) {
      //   i = (data.current_page - 1) * 15 + 1;
      // }


      data.bienes.forEach((bien) => {
        const fila = `
          <tr data-identificador="${bien.identificador}">
            <td>${bien.numero}</td>  <!-- Número enviado por el backend -->
            <td>${bien.identificador}</td>
            <td>${bien.descripcion}</td>
            <td>${bien.cantidad}</td>
            <td>${bien.dependencia}</td>
            <td>${bien.departamento}</td>
            <td>${bien.responsable}</td>
            <td>${bien.fecha_registro}</td>
            <td>${bien.estado_actual}</td>
            <td> ... </td>
          </tr>`;
        tbody.insertAdjacentHTML("beforeend", fila);
        // i++;
      });

      paginaActual = data.current_page;
      document.getElementById("pagina-actual").textContent = paginaActual;

      document.getElementById("anterior").disabled = paginaActual === 1 || filtro !== "";
      document.getElementById("siguiente").disabled = paginaActual === data.total_pages || filtro !== "";
    })
    .catch((error) => {
      console.error("Error cargando bienes:", error);
    });
}


// // Función para filtrar bienes por identificador
// function filtrarPorIdentificador() {
//   const filtro = document.getElementById("filterJerarquia").value.trim().toLowerCase();
//   const filas = document.querySelectorAll("#tablaBienes tbody tr");

//   filas.forEach((fila) => {
//     const identificador = fila.getAttribute("data-identificador").toLowerCase();
//     if (identificador.includes(filtro)) {
//       fila.style.display = ""; // Mostrar la fila si coincide
//     } else {
//       fila.style.display = "none"; // Ocultar la fila si no coincide
//     }
//   });
// }

// document.getElementById("filterJerarquia").addEventListener("blur", function () {
//   const filtro = this.value.trim();
//   if (filtro === "") {
//     cargarBienes(); // volver a paginación normal
//   } else {
//     cargarBienes(1, filtro);
//   }
// });

// Eventos para botones de paginación
document.getElementById("anterior").addEventListener("click", function () {
  if (paginaActual > 1) {
    cargarBienes(paginaActual - 1);
  }
});

document.getElementById("siguiente").addEventListener("click", function () {
  cargarBienes(paginaActual + 1);
});

// Cargar bienes al iniciar la página
window.addEventListener("DOMContentLoaded", () => cargarBienes());

document.getElementById("filterJerarquia").addEventListener("blur", function () {
  cargarBienes(); // ya no necesitamos `filtrarPorIdentificador`
});


