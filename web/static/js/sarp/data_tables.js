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
            <td>${vuelo.tipo_mision}</td>
            <td>${vuelo.id_operador__jerarquia} ${vuelo.id_operador__nombres} ${vuelo.id_operador__apellidos}</td>
            <td>${vuelo.id_observador__jerarquia} ${vuelo.id_observador__nombres} ${vuelo.id_observador__apellidos}</td>
            <td>${detalles.distancia_recorrida || 'N/A'}</td>
            <td>${detalles.duracion_vuelo || 'N/A'}</td>
            <td>
              <button class="btn reasignar-unidad" data-unidad="{{ row.id_unidad }}"
                data-unidad-nombre="{{ row.nombre_unidad }}" data-division-actual="{{ row.divisiones|join:', ' }}"
                data-bs-toggle="modal" data-bs-target="#modal-division">
                <svg fill="blue" xmlns="http://www.w3.org/2000/svg" width="35px" height="40px" viewBox="0 0 52 52"
                  enable-background="new 0 0 52 52" xml:space="preserve">
                  <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                  <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                  <g id="SVGRepo_iconCarrier">
                    <path
                      d="M23.2,10.2C18.1,5.1,10,3.5,2.9,5.7C2.6,5.7,2.2,6.2,2.2,7s0,3,0,3.9c0,0.8,0.7,1,1.1,0.9 c5.4-2.2,12-1.2,16.3,3.3l1.1,1.1c0.6,0.6,0.1,1.7-0.7,1.7h-7.8c-0.8,0-1.5,0.6-1.5,1.5v3c0,0.8,0.6,1.5,1.5,1.5l19.2,0.2 c0.8,0,1.5-0.6,1.5-1.5L33,3.5C33,2.7,32.4,2,31.5,2h-3c-0.8,0-1.6,0.6-1.6,1.4l-0.1,7.9c0,0.8-1.1,1.3-1.7,0.7 C25.2,12.1,23.2,10.2,23.2,10.2z">
                    </path>
                    <path
                      d="M3.5,27.8h3c0.8,0,1.5,0.7,1.5,1.5v13.2C8,43.3,8.7,44,9.5,44h33c0.8,0,1.5-0.7,1.5-1.5V16.9 c0-0.8-0.7-1.5-1.5-1.5h-4c-0.8,0-1.5-0.7-1.5-1.5v-3c0-0.8,0.7-1.5,1.5-1.5H46c2.2,0,4,1.8,4,4V46c0,2.2-1.8,4-4,4H6 c-2.2,0-4-1.8-4-4V29.3C2,28.5,2.7,27.8,3.5,27.8z">
                    </path>
                  </g>
                </svg>
              </button>
            </td>
            <td>
              <button class="btn editar_unidad" data-unidad="{{ row.id_unidad }}">
                <svg fill="blue" height="35px" width="40px" version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg"
                  xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 217.855 217.855" xml:space="preserve">
                  <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                  <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                  <g id="SVGRepo_iconCarrier">
                    <path
                      d="M215.658,53.55L164.305,2.196C162.899,0.79,160.991,0,159.002,0c-1.989,0-3.897,0.79-5.303,2.196L3.809,152.086 c-1.35,1.352-2.135,3.166-2.193,5.075l-1.611,52.966c-0.063,2.067,0.731,4.069,2.193,5.532c1.409,1.408,3.317,2.196,5.303,2.196 c0.076,0,0.152-0.001,0.229-0.004l52.964-1.613c1.909-0.058,3.724-0.842,5.075-2.192l149.89-149.889 C218.587,61.228,218.587,56.479,215.658,53.55z M57.264,201.336l-42.024,1.28l1.279-42.026l91.124-91.125l40.75,40.743 L57.264,201.336z M159,99.602l-40.751-40.742l40.752-40.753l40.746,40.747L159,99.602z">
                    </path>
                  </g>
                </svg>
              </button>
            </td>
            <td>
              <button class="btn ver-informacion" data-unidad="{{ row.id_unidad }}">
                <svg width="35px" height="40px" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                  <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                  <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                  <g id="SVGRepo_iconCarrier">
                    <path fill-rule="evenodd" clip-rule="evenodd"
                      d="M9 6C9 4.34315 7.65685 3 6 3H4C2.34315 3 1 4.34315 1 6V8C1 9.65685 2.34315 11 4 11H6C7.65685 11 9 9.65685 9 8V6ZM7 6C7 5.44772 6.55228 5 6 5H4C3.44772 5 3 5.44772 3 6V8C3 8.55228 3.44772 9 4 9H6C6.55228 9 7 8.55228 7 8V6Z"
                      fill="blue"></path>
                    <path fill-rule="evenodd" clip-rule="evenodd"
                      d="M9 16C9 14.3431 7.65685 13 6 13H4C2.34315 13 1 14.3431 1 16V18C1 19.6569 2.34315 21 4 21H6C7.65685 21 9 19.6569 9 18V16ZM7 16C7 15.4477 6.55228 15 6 15H4C3.44772 15 3 15.4477 3 16V18C3 18.5523 3.44772 19 4 19H6C6.55228 19 7 18.5523 7 18V16Z"
                      fill="blue"></path>
                    <path
                      d="M11 7C11 6.44772 11.4477 6 12 6H22C22.5523 6 23 6.44772 23 7C23 7.55228 22.5523 8 22 8H12C11.4477 8 11 7.55228 11 7Z"
                      fill="#0F0F0F"></path>
                    <path
                      d="M11 17C11 16.4477 11.4477 16 12 16H22C22.5523 16 23 16.4477 23 17C23 17.5523 22.5523 18 22 18H12C11.4477 18 11 17.5523 11 17Z"
                      fill="#0F0F0F"></path>
                  </g>
                </svg>
              </button>
            </td>
            </tr>`;
    tabla.innerHTML += fila;
  });
}
window.onload = cargarVuelos;
