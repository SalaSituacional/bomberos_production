let paginaActual = 1;
const vuelosPorPagina = 15; // Número de registros por página

async function cargarVuelos(pagina = 1) {
  let response = await fetchWithLoader(`/api/vuelos/?page=${pagina}&limit=5`);  // Establecer limit=5
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
          <td>${vuelo.id_operador__jerarquia} ${vuelo.id_operador__nombres} ${vuelo.id_operador__apellidos}</td>
          <td>
              ${vuelo.observador_externo ? vuelo.observador_externo : `${vuelo.id_observador__jerarquia} ${vuelo.id_observador__nombres} ${vuelo.id_observador__apellidos}`}
          </td>
          <td>${detalles.duracion_vuelo || "N/A"}</td>
          <td>
              <button class="btn editar_unidad" data-unidad="${vuelo.id_vuelo}">
                              <svg width="35px" height="35px" viewBox="0 0 1024 1024" class="icon" version="1.1" xmlns="http://www.w3.org/2000/svg" fill="#000000" style="pointer-events: none;"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"><path d="M823.3 938.8H229.4c-71.6 0-129.8-58.2-129.8-129.8V215.1c0-71.6 58.2-129.8 129.8-129.8h297c23.6 0 42.7 19.1 42.7 42.7s-19.1 42.7-42.7 42.7h-297c-24.5 0-44.4 19.9-44.4 44.4V809c0 24.5 19.9 44.4 44.4 44.4h593.9c24.5 0 44.4-19.9 44.4-44.4V512c0-23.6 19.1-42.7 42.7-42.7s42.7 19.1 42.7 42.7v297c0 71.6-58.2 129.8-129.8 129.8z" fill="#3688FF"></path><path d="M483 756.5c-1.8 0-3.5-0.1-5.3-0.3l-134.5-16.8c-19.4-2.4-34.6-17.7-37-37l-16.8-134.5c-1.6-13.1 2.9-26.2 12.2-35.5l374.6-374.6c51.1-51.1 134.2-51.1 185.3 0l26.3 26.3c24.8 24.7 38.4 57.6 38.4 92.7 0 35-13.6 67.9-38.4 92.7L513.2 744c-8.1 8.1-19 12.5-30.2 12.5z m-96.3-97.7l80.8 10.1 359.8-359.8c8.6-8.6 13.4-20.1 13.4-32.3 0-12.2-4.8-23.7-13.4-32.3L801 218.2c-17.9-17.8-46.8-17.8-64.6 0L376.6 578l10.1 80.8z" fill="#5F6379"></path></g></svg>
</button>
              <button class="btn generar-excel" data-unidad="${vuelo.id_vuelo}">
                    <svg
                  width="35px"
                  height="35px"
                  viewBox="0 0 1024 1024"
                  class="icon"
                  version="1.1"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="#000000"
                  style="pointer-events: none;"
                >
                  <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                  <g
                    id="SVGRepo_tracerCarrier"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  ></g>
                  <g id="SVGRepo_iconCarrier">
                    <path
                      d="M892.1 938.7H131.9c-17.8 0-35.1-3.5-51.4-10.4-15.6-6.6-29.7-16.1-41.9-28.2C26.5 888 17 873.9 10.3 858.2 3.5 841.8 0 824.5 0 806.8V217.2c0-17.8 3.5-35 10.4-51.3 6.6-15.7 16.1-29.8 28.2-41.9 12.2-12.2 26.3-21.7 42-28.3 16.2-6.9 33.5-10.4 51.3-10.4h83.4c23.6 0 42.7 19.1 42.7 42.7s-19.1 42.7-42.7 42.7h-83.4c-6.3 0-12.4 1.2-18.1 3.6-5.6 2.4-10.6 5.7-14.9 10-4.3 4.3-7.6 9.2-10 14.8-2.4 5.7-3.6 11.8-3.6 18.1v589.6c0 6.3 1.2 12.4 3.7 18.1 2.3 5.5 5.7 10.5 10 14.8 4.3 4.2 9.2 7.6 14.8 9.9 5.8 2.4 11.9 3.7 18.1 3.7h760.2c6.3 0 12.4-1.2 18.1-3.6 5.6-2.4 10.6-5.7 14.9-10 4.3-4.3 7.6-9.2 10-14.8 2.4-5.7 3.6-11.8 3.6-18.1V217.2c0-6.3-1.2-12.4-3.7-18.1-2.3-5.5-5.7-10.5-10-14.8-4.3-4.2-9.2-7.6-14.8-9.9-5.8-2.4-11.9-3.7-18.1-3.7h-83.4c-23.6 0-42.7-19.1-42.7-42.7s19.1-42.7 42.7-42.7h83.4c17.8 0 35.1 3.5 51.4 10.4 15.6 6.6 29.7 16.1 41.9 28.2 12.1 12.1 21.6 26.2 28.3 41.9 6.9 16.3 10.4 33.6 10.4 51.4v589.6c0 17.8-3.5 35-10.4 51.3-6.6 15.7-16.1 29.8-28.2 41.9-12.2 12.2-26.3 21.7-42 28.3-16.3 6.9-33.6 10.4-51.4 10.4z"
                      fill="#3688FF"
                    ></path>
                    <path
                      d="M229.8 714.8c-6.1 0-12.3-1.3-18.1-4.1-21.3-10-30.5-35.5-20.4-56.8L467.5 67.1c10-21.3 35.5-30.5 56.8-20.4 21.3 10 30.5 35.5 20.4 56.8L268.5 690.3c-7.3 15.4-22.7 24.5-38.7 24.5zM810.7 448H640c-23.6 0-42.7-19.1-42.7-42.7s19.1-42.7 42.7-42.7h170.7c23.6 0 42.7 19.1 42.7 42.7S834.2 448 810.7 448zM810.7 704h-384c-23.6 0-42.7-19.1-42.7-42.7s19.1-42.7 42.7-42.7h384c23.6 0 42.7 19.1 42.7 42.7S834.2 704 810.7 704z"
                      fill="#5F6379"
                    ></path>
                  </g>
                </svg>
              </button>
              <button onclick="eliminarVuelo('${vuelo.id_vuelo}')" class="btn eliminar_unidad">
                 <svg
                  width="35px"
                  height="35px"
                  viewBox="0 0 1024 1024"
                  class="icon"
                  version="1.1"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="#000000"
                  style="pointer-events: none;"
                >
                  <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                  <g
                    id="SVGRepo_tracerCarrier"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  ></g>
                  <g id="SVGRepo_iconCarrier">
                    <path
                      d="M779.5 1002.7h-535c-64.3 0-116.5-52.3-116.5-116.5V170.7h768v715.5c0 64.2-52.3 116.5-116.5 116.5zM213.3 256v630.1c0 17.2 14 31.2 31.2 31.2h534.9c17.2 0 31.2-14 31.2-31.2V256H213.3z"
                      fill="#3688FF"
                    ></path>
                    <path
                      d="M917.3 256H106.7C83.1 256 64 236.9 64 213.3s19.1-42.7 42.7-42.7h810.7c23.6 0 42.7 19.1 42.7 42.7S940.9 256 917.3 256zM618.7 128H405.3c-23.6 0-42.7-19.1-42.7-42.7s19.1-42.7 42.7-42.7h213.3c23.6 0 42.7 19.1 42.7 42.7S642.2 128 618.7 128zM405.3 725.3c-23.6 0-42.7-19.1-42.7-42.7v-256c0-23.6 19.1-42.7 42.7-42.7S448 403 448 426.6v256c0 23.6-19.1 42.7-42.7 42.7zM618.7 725.3c-23.6 0-42.7-19.1-42.7-42.7v-256c0-23.6 19.1-42.7 42.7-42.7s42.7 19.1 42.7 42.7v256c-0.1 23.6-19.2 42.7-42.7 42.7z"
                      fill="#5F6379"
                    ></path>
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


// async function cargarVuelos() {
//   let response = await fetchWithLoader("/api/vuelos/");
//   let data = await response;
//   let tabla = document.getElementById("tabla-vuelos");

//   data.forEach((vuelo) => {
//     let detalles = vuelo.detalles || {}; // Evita errores si no hay detalles
//     let fila = `<tr>
//               <td>${vuelo.id_vuelo}</td>
//               <td>${vuelo.fecha}</td>
//               <td>${vuelo.sitio}</td>
//               <td>${vuelo.id_dron__nombre_dron}</td>
//               <td>${vuelo.id_operador__jerarquia} ${vuelo.id_operador__nombres} ${vuelo.id_operador__apellidos}</td>
//               <td>
//                 ${vuelo.observador_externo ? vuelo.observador_externo : `${vuelo.id_observador__jerarquia} ${vuelo.id_observador__nombres} ${vuelo.id_observador__apellidos}`}
//               </td>
//               <td>${detalles.duracion_vuelo || "N/A"}</td>
//               <td>

//                 <button class="btn editar_unidad" data-unidad="${vuelo.id_vuelo}">
//                   <svg fill="#3688FF" height="35px" width="40px" version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg"
//                     xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 217.855 217.855" xml:space="preserve" style="pointer-events: none;">
//                     <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
//                       <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
//                       <g id="SVGRepo_iconCarrier">
//                           <path
//                             d="M215.658,53.55L164.305,2.196C162.899,0.79,160.991,0,159.002,0c-1.989,0-3.897,0.79-5.303,2.196L3.809,152.086 c-1.35,1.352-2.135,3.166-2.193,5.075l-1.611,52.966c-0.063,2.067,0.731,4.069,2.193,5.532c1.409,1.408,3.317,2.196,5.303,2.196 c0.076,0,0.152-0.001,0.229-0.004l52.964-1.613c1.909-0.058,3.724-0.842,5.075-2.192l149.89-149.889 C218.587,61.228,218.587,56.479,215.658,53.55z M57.264,201.336l-42.024,1.28l1.279-42.026l91.124-91.125l40.75,40.743 L57.264,201.336z M159,99.602l-40.751-40.742l40.752-40.753l40.746,40.747L159,99.602z">
//                           </path>
//                       </g>
//                   </svg>
//                 </button>

//                 <button class="btn generar-excel" data-unidad="${vuelo.id_vuelo}">
//                   <svg width="35px" height="40px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="pointer-events: none;">
//                     <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
//                     <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
//                     <g id="SVGRepo_iconCarrier">
//                       <path fill-rule="evenodd" clip-rule="evenodd"
//                         d="M9 6C9 4.34315 7.65685 3 6 3H4C2.34315 3 1 4.34315 1 6V8C1 9.65685 2.34315 11 4 11H6C7.65685 11 9 9.65685 9 8V6ZM7 6C7 5.44772 6.55228 5 6 5H4C3.44772 5 3 5.44772 3 6V8C3 8.55228 3.44772 9 4 9H6C6.55228 9 7 8.55228 7 8V6Z"
//                         fill="#3688FF">
//                       </path>
//                       <path fill-rule="evenodd" clip-rule="evenodd"
//                         d="M9 16C9 14.3431 7.65685 13 6 13H4C2.34315 13 1 14.3431 1 16V18C1 19.6569 2.34315 21 4 21H6C7.65685 21 9 19.6569 9 18V16ZM7 16C7 15.4477 6.55228 15 6 15H4C3.44772 15 3 15.4477 3 16V18C3 18.5523 3.44772 19 4 19H6C6.55228 19 7 18.5523 7 18V16Z"
//                         fill="#3688FF">
//                       </path>
//                       <path
//                         d="M11 7C11 6.44772 11.4477 6 12 6H22C22.5523 6 23 6.44772 23 7C23 7.55228 22.5523 8 22 8H12C11.4477 8 11 7.55228 11 7Z"
//                         fill="#5F6379">
//                       </path>
//                       <path
//                         d="M11 17C11 16.4477 11.4477 16 12 16H22C22.5523 16 23 16.4477 23 17C23 17.5523 22.5523 18 22 18H12C11.4477 18 11 17.5523 11 17Z"
//                         fill="#5F6379">
//                       </path>
//                     </g>
//                   </svg>
//                 </button>

//                 <button onclick="eliminarVuelo('${vuelo.id_vuelo}')" style="border: none; background: none; cursor: pointer;">
//                     <svg width="35px" height="35px" viewBox="0 0 1024 1024" class="icon" xmlns="http://www.w3.org/2000/svg" fill="#000000">
//                         <g id="SVGRepo_iconCarrier">
//                             <path d="M779.5 1002.7h-535c-64.3 0-116.5-52.3-116.5-116.5V170.7h768v715.5c0 64.2-52.3 116.5-116.5 116.5zM213.3 256v630.1c0 17.2 14 31.2 31.2 31.2h534.9c17.2 0 31.2-14 31.2-31.2V256H213.3z" fill="#3688FF"></path>
//                             <path d="M917.3 256H106.7C83.1 256 64 236.9 64 213.3s19.1-42.7 42.7-42.7h810.7c23.6 0 42.7 19.1 42.7 42.7S940.9 256 917.3 256zM618.7 128H405.3c-23.6 0-42.7-19.1-42.7-42.7s19.1-42.7 42.7-42.7h213.3c23.6 0 42.7 19.1 42.7 42.7S642.2 128 618.7 128zM405.3 725.3c-23.6 0-42.7-19.1-42.7-42.7v-256c0-23.6 19.1-42.7 42.7-42.7S448 403 448 426.6v256c0 23.6-19.1 42.7-42.7 42.7zM618.7 725.3c-23.6 0-42.7-19.1-42.7-42.7v-256c0-23.6 19.1-42.7 42.7-42.7s42.7 19.1 42.7 42.7v256c-0.1 23.6-19.2 42.7-42.7 42.7z" fill="#5F6379"></path>
//                         </g>
//                     </svg>
//                 </button>

//               </td>
//             </tr>`;
//     tabla.innerHTML += fila;
//   });
// }
// window.onload = cargarVuelos;
