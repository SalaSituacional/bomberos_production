let paginaActual = 1;
const vuelosPorPagina = 15; // Número de registros por página

async function cargarVuelos(pagina = 1) {
  let response = await fetchWithLoader(`${ApiVuelos}?page=${pagina}&limit=5`); // Establecer limit=5
  let data = await response;

  let tabla = document.getElementById("tabla-vuelos");
  tabla.innerHTML = ""; // Limpiar la tabla antes de agregar nuevos registros

  data.vuelos.forEach((vuelo) => {
    let detalles = vuelo.detalles || {};
    let fila = `<tr>
          <td>${vuelo.id_vuelo}</td>
          <td>${vuelo.fecha}</td>
          <td>${vuelo.sitio}</td>
          <td>${vuelo.id_dron__nombre_dron}</td>
          <td>${vuelo.id_operador__jerarquia} ${vuelo.id_operador__nombres} ${vuelo.id_operador__apellidos
      }</td>
          <td>
              ${vuelo.observador_externo
        ? vuelo.observador_externo
        : `${vuelo.id_observador__jerarquia} ${vuelo.id_observador__nombres} ${vuelo.id_observador__apellidos}`
      }
          </td>
          <td>${detalles.duracion_vuelo || "N/A"}</td>
          <td>
              <button class="btn editar_unidad" data-unidad="${vuelo.id_vuelo}">
                   <svg fill="#3688FF" height="35px" width="40px" version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg"
                     xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 217.855 217.855" xml:space="preserve" style="pointer-events: none;">
                     <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                       <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                       <g id="SVGRepo_iconCarrier">
                           <path
                             d="M215.658,53.55L164.305,2.196C162.899,0.79,160.991,0,159.002,0c-1.989,0-3.897,0.79-5.303,2.196L3.809,152.086 c-1.35,1.352-2.135,3.166-2.193,5.075l-1.611,52.966c-0.063,2.067,0.731,4.069,2.193,5.532c1.409,1.408,3.317,2.196,5.303,2.196 c0.076,0,0.152-0.001,0.229-0.004l52.964-1.613c1.909-0.058,3.724-0.842,5.075-2.192l149.89-149.889 C218.587,61.228,218.587,56.479,215.658,53.55z M57.264,201.336l-42.024,1.28l1.279-42.026l91.124-91.125l40.75,40.743 L57.264,201.336z M159,99.602l-40.751-40.742l40.752-40.753l40.746,40.747L159,99.602z">
                           </path>
                       </g>
                   </svg>
              </button>

              <button class="btn generar-excel" data-unidad="${vuelo.id_vuelo}">
                   <svg width="35px" height="40px" viewBox="0 0 1024 1024" class="icon" version="1.1" xmlns="http://www.w3.org/2000/svg" fill="#000000"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"><path d="M809.3 1024H214.7c-71.3 0-129.4-58-129.4-129.4V129.4C85.3 58 143.4 0 214.7 0h594.6c71.3 0 129.4 58 129.4 129.4v765.3c0 71.3-58.1 129.3-129.4 129.3zM214.7 85.3c-24.3 0-44 19.8-44 44v765.3c0 24.3 19.8 44 44 44h594.6c24.3 0 44-19.8 44-44V129.4c0-24.3-19.8-44-44-44H214.7z" fill="#3688FF"></path><path d="M426.7 1024H213.3c-70.6 0-128-57.4-128-128V682.7h213.4c70.6 0 128 57.4 128 128V1024z m-256-256v128c0 23.5 19.1 42.6 42.6 42.6h128v-128c0-23.5-19.1-42.6-42.6-42.6h-128zM810.7 1024H597.3V810.6c0-70.6 57.4-128 128-128h213.4V896c0 70.6-57.4 128-128 128z m-128-85.3h128c23.5 0 42.6-19.1 42.6-42.6V768h-128c-23.5 0-42.6 19.1-42.6 42.6v128.1zM448 355.6H277.3c-23.6 0-42.7-19.1-42.7-42.7s19.1-42.7 42.7-42.7H448c23.6 0 42.7 19.1 42.7 42.7s-19.1 42.7-42.7 42.7zM661.3 533.3h-384c-23.6 0-42.7-19.1-42.7-42.7s19.1-42.7 42.7-42.7h384c23.6 0 42.7 19.1 42.7 42.7s-19.1 42.7-42.7 42.7z" fill="#5F6379"></path></g></svg>
                </button>

              <button onclick="eliminarVuelo('${vuelo.id_vuelo
      }')" style="border: none; background: none; cursor: pointer;">
                     <svg width="35px" height="35px" viewBox="0 0 1024 1024" class="icon" xmlns="http://www.w3.org/2000/svg" fill="#000000">
                         <g id="SVGRepo_iconCarrier">
                             <path d="M779.5 1002.7h-535c-64.3 0-116.5-52.3-116.5-116.5V170.7h768v715.5c0 64.2-52.3 116.5-116.5 116.5zM213.3 256v630.1c0 17.2 14 31.2 31.2 31.2h534.9c17.2 0 31.2-14 31.2-31.2V256H213.3z" fill="#3688FF"></path>
                             <path d="M917.3 256H106.7C83.1 256 64 236.9 64 213.3s19.1-42.7 42.7-42.7h810.7c23.6 0 42.7 19.1 42.7 42.7S940.9 256 917.3 256zM618.7 128H405.3c-23.6 0-42.7-19.1-42.7-42.7s19.1-42.7 42.7-42.7h213.3c23.6 0 42.7 19.1 42.7 42.7S642.2 128 618.7 128zM405.3 725.3c-23.6 0-42.7-19.1-42.7-42.7v-256c0-23.6 19.1-42.7 42.7-42.7S448 403 448 426.6v256c0 23.6-19.1 42.7-42.7 42.7zM618.7 725.3c-23.6 0-42.7-19.1-42.7-42.7v-256c0-23.6 19.1-42.7 42.7-42.7s42.7 19.1 42.7 42.7v256c-0.1 23.6-19.2 42.7-42.7 42.7z" fill="#5F6379"></path>
                         </g>
                     </svg>
              </button>
          </td>
      </tr>`;
    tabla.innerHTML += fila;
  });

  // Actualizar botones de paginación
  document.getElementById("pagina-actual").textContent = pagina;
  document.getElementById("anterior").disabled = !data.tiene_anterior;
  document.getElementById("siguiente").disabled = !data.tiene_siguiente;
}

// Eventos para paginación
document.getElementById("anterior").addEventListener("click", () => {
  if (paginaActual > 1) {
    paginaActual--;
    cargarVuelos(paginaActual);
  }
});

document.getElementById("siguiente").addEventListener("click", () => {
  paginaActual++;
  cargarVuelos(paginaActual);
});

// Cargar la primera página al iniciar
window.onload = () => cargarVuelos(1);
