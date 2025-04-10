let paginaActual = 1;

// Función para cargar los bienes desde la API
function cargarBienes(pagina = 1) {
  fetchWithLoader(`/api/bienes/?page=${pagina}`)
    .then((response) => response)
    .then((data) => {
      const tbody = document.querySelector("#tablaBienes tbody");
      tbody.innerHTML = ""; // Limpiar tabla

      let i = (data.current_page - 1) * 15 + 1;

      data.bienes.forEach((bien) => {
        const fila = `
          <tr data-identificador="${bien.identificador}" data-departamento="${bien.departamento}">
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
              <button class="btn" data-bien-id="${bien.identificador}" data-bs-toggle="modal" data-bs-target="#modalReasignarBien">
              <svg width="35px" height="40px" viewBox="0 0 1024 1024" class="icon" version="1.1" xmlns="http://www.w3.org/2000/svg" fill="#000000"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"><path d="M810.7 938.7H213.3c-17.3 0-34-3.4-49.9-10.1-15.2-6.4-29-15.7-40.7-27.5-11.7-11.7-21-25.4-27.4-40.7-6.7-15.8-10.1-32.6-10.1-49.8V213.3c0-17.2 3.4-34 10.1-49.8 6.4-15.2 15.7-29 27.5-40.7 11.7-11.7 25.4-20.9 40.7-27.4 15.8-6.7 32.5-10.1 49.8-10.1h597.3c17.3 0 34 3.4 49.9 10.1 15.2 6.4 29 15.7 40.7 27.5 11.7 11.7 21 25.4 27.4 40.7 6.7 15.8 10.1 32.6 10.1 49.8V320c0 23.6-19.1 42.7-42.7 42.7s-42.7-19.1-42.7-42.7V213.3c0-5.8-1.1-11.4-3.4-16.6-2.1-5.1-5.2-9.6-9.1-13.5-4-4-8.5-7-13.6-9.2-5.2-2.2-10.8-3.3-16.6-3.3H213.3c-5.8 0-11.4 1.1-16.6 3.3-5.1 2.2-9.7 5.2-13.6 9.1-4 4-7.1 8.5-9.2 13.6-2.2 5.3-3.4 10.9-3.4 16.6v597.3c0 5.8 1.1 11.4 3.4 16.6 2.1 5.1 5.2 9.6 9.1 13.5 4 4 8.5 7 13.6 9.2 5.2 2.2 10.8 3.3 16.6 3.3h597.3c5.8 0 11.4-1.1 16.6-3.3 5.1-2.2 9.7-5.2 13.6-9.1 4-4 7.1-8.5 9.2-13.6 2.2-5.3 3.4-10.9 3.4-16.6V704c0-23.6 19.1-42.7 42.7-42.7s42.7 19.1 42.7 42.7v106.7c0 17.2-3.4 34-10.1 49.8-6.4 15.2-15.7 29-27.5 40.7-11.7 11.7-25.4 20.9-40.7 27.4-15.7 6.7-32.5 10.1-49.7 10.1z" fill="#3688FF"></path><path d="M768 682.7c-10.9 0-21.8-4.2-30.2-12.5-16.7-16.7-16.7-43.7 0-60.3l97.8-97.8-97.8-97.8c-16.7-16.7-16.7-43.7 0-60.3 16.7-16.7 43.7-16.7 60.3 0l128 128c16.7 16.7 16.7 43.7 0 60.3l-128 128c-8.3 8.2-19.2 12.4-30.1 12.4z" fill="#5F6379"></path><path d="M896 554.7H512c-23.6 0-42.7-19.1-42.7-42.7s19.1-42.7 42.7-42.7h384c23.6 0 42.7 19.1 42.7 42.7s-19.1 42.7-42.7 42.7z" fill="#5F6379"></path></g></svg>
              </button>
              <button class="btn" data-bs-toggle="modal" data-bs-target="#modalHistorialBien" data-bien-id="${bien.identificador}"> <svg width="35px" height="40px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="pointer-events: none;">
              <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
              <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
              <g id="SVGRepo_iconCarrier">
                <path fill-rule="evenodd" clip-rule="evenodd"
                  d="M9 6C9 4.34315 7.65685 3 6 3H4C2.34315 3 1 4.34315 1 6V8C1 9.65685 2.34315 11 4 11H6C7.65685 11 9 9.65685 9 8V6ZM7 6C7 5.44772 6.55228 5 6 5H4C3.44772 5 3 5.44772 3 6V8C3 8.55228 3.44772 9 4 9H6C6.55228 9 7 8.55228 7 8V6Z"
                  fill="#3688FF">
                </path>
                <path fill-rule="evenodd" clip-rule="evenodd"
                  d="M9 16C9 14.3431 7.65685 13 6 13H4C2.34315 13 1 14.3431 1 16V18C1 19.6569 2.34315 21 4 21H6C7.65685 21 9 19.6569 9 18V16ZM7 16C7 15.4477 6.55228 15 6 15H4C3.44772 15 3 15.4477 3 16V18C3 18.5523 3.44772 19 4 19H6C6.55228 19 7 18.5523 7 18V16Z"
                  fill="#3688FF">
                </path>
                <path
                  d="M11 7C11 6.44772 11.4477 6 12 6H22C22.5523 6 23 6.44772 23 7C23 7.55228 22.5523 8 22 8H12C11.4477 8 11 7.55228 11 7Z"
                  fill="#5F6379">
                </path>
                <path
                  d="M11 17C11 16.4477 11.4477 16 12 16H22C22.5523 16 23 16.4477 23 17C23 17.5523 22.5523 18 22 18H12C11.4477 18 11 17.5523 11 17Z"
                  fill="#5F6379">
                </path>
              </g>
            </svg></button>
              <button class="btn" data-bs-toggle="modal" data-bs-target="#modalEliminarBien" data-id-bien="${bien.identificador}">
               <svg width="35px" height="35px" viewBox="0 0 1024 1024" class="icon" xmlns="http://www.w3.org/2000/svg" fill="#000000">
                         <g id="SVGRepo_iconCarrier">
                             <path d="M779.5 1002.7h-535c-64.3 0-116.5-52.3-116.5-116.5V170.7h768v715.5c0 64.2-52.3 116.5-116.5 116.5zM213.3 256v630.1c0 17.2 14 31.2 31.2 31.2h534.9c17.2 0 31.2-14 31.2-31.2V256H213.3z" fill="#3688FF"></path>
                             <path d="M917.3 256H106.7C83.1 256 64 236.9 64 213.3s19.1-42.7 42.7-42.7h810.7c23.6 0 42.7 19.1 42.7 42.7S940.9 256 917.3 256zM618.7 128H405.3c-23.6 0-42.7-19.1-42.7-42.7s19.1-42.7 42.7-42.7h213.3c23.6 0 42.7 19.1 42.7 42.7S642.2 128 618.7 128zM405.3 725.3c-23.6 0-42.7-19.1-42.7-42.7v-256c0-23.6 19.1-42.7 42.7-42.7S448 403 448 426.6v256c0 23.6-19.1 42.7-42.7 42.7zM618.7 725.3c-23.6 0-42.7-19.1-42.7-42.7v-256c0-23.6 19.1-42.7 42.7-42.7s42.7 19.1 42.7 42.7v256c-0.1 23.6-19.2 42.7-42.7 42.7z" fill="#5F6379"></path>
                         </g>
                     </svg>
              </button>
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

// Función para filtrar bienes
function filtrarBienes() {
  const filtroIdentificador = document.getElementById("filterid").value.trim().toLowerCase();
  const filtroDepartamento = document.getElementById("filterDepartamento").value.trim().toLowerCase();
  const filas = document.querySelectorAll("#tablaBienes tbody tr");

  filas.forEach((fila) => {
    const identificador = fila.getAttribute("data-identificador").toLowerCase();
    const departamento = fila.getAttribute("data-departamento").toLowerCase();

    // Mostrar u ocultar la fila si coinciden ambos filtros
    if (identificador.includes(filtroIdentificador) && departamento.includes(filtroDepartamento)) {
      fila.style.display = ""; // Mostrar la fila
    } else {
      fila.style.display = "none"; // Ocultar la fila
    }
  });
}

// Agregar eventos a los buscadores
document.getElementById("filterid").addEventListener("input", filtrarBienes);
document.getElementById("filterDepartamento").addEventListener("input", filtrarBienes);

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
