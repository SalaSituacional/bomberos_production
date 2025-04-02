async function cargarVuelos() {
  let response = await fetchWithLoader("/api/vuelos/");
  let data = await response;
  let tabla = document.getElementById("tabla-vuelos");

  data.forEach((vuelo) => {
    let detalles = vuelo.detalles || {}; // Evita errores si no hay detalles
    let fila = `<tr>
              <td>${vuelo.id_vuelo}</td>
              <td>${vuelo.fecha}</td>
              <td>${vuelo.sitio}</td>
              <td>${vuelo.id_dron__nombre_dron}</td>
              <td>${vuelo.id_operador__jerarquia} ${vuelo.id_operador__nombres} ${vuelo.id_operador__apellidos}</td>
              <td>${vuelo.id_observador__jerarquia} ${vuelo.id_observador__nombres} ${vuelo.id_observador__apellidos}</td>
              <td>${detalles.duracion_vuelo || "N/A"}</td>
              <td>
              
                <button class="btn editar_unidad" data-unidad="${ vuelo.id_vuelo }">
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
                  
                <button class="btn generar-excel" data-unidad="${ vuelo.id_vuelo }">
                  <svg width="35px" height="40px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" style="pointer-events: none;">
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
                  </svg>
                </button>

                <button class="btn eliminar-unidad" data-unidad="${ vuelo.id_vuelo }">
                  <svg width="35px" height="35px" viewBox="0 0 1024 1024" class="icon" version="1.1" xmlns="http://www.w3.org/2000/svg" fill="#000000"
                   style="pointer-events: none;">
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
}
window.onload = cargarVuelos;
