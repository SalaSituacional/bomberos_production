const cargarMasBtn = document.getElementById('cargar_mas_btn');
const fechaActualInput = document.getElementById('fecha_actual');  // El campo donde se guarda la fecha actual
const procedimientosContainer = document.getElementById('procedimientos-container');
let rowCount = document.querySelectorAll('#data-table tbody tr').length + 1;

// Establecer la fecha de la primera carga como el día anterior
const fechaInicial = new Date();
fechaInicial.setDate(fechaInicial.getDate() - 1);  // Restar un día
const fechaInicialString = fechaInicial.toISOString().split('T')[0];  // Formato YYYY-MM-DD
// Establecer la fecha inicial en el campo oculto
fechaActualInput.value = fechaInicialString;

// Al cargar la página por primera vez, cargamos los procedimientos del día anterior
// cargarProcedimientos(fechaInicialString);

async function cargarProcedimientos(fecha) {
    const url = `/enfermeria?fecha=${fecha}`; // URL con la fecha como parámetro
  
    try {
      const data = await fetchWithLoader(url, {
        method: 'GET',
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
          'Content-Type': 'application/json',
        },
      });
        const procedimientos = data.procedimientos;
        const tableBody = document.querySelector('#data-table tbody');

        // Limpiar el cuerpo de la tabla antes de agregar nuevas filas
        // tableBody.innerHTML = '';

        procedimientos.forEach(proc => {
            // Para cada procedimiento, mapear los campos que quieres mostrar
            const fields = [
                // { content: `<th scope="row">${rowCount++}</th>` },
                { content: proc.dependencia},
                { content: proc.solicitante_externo},
                { content: proc.id_parroquia__parroquia !== "Sin Registro" ? proc.id_parroquia__parroquia : "Otros Municipios" },  // Parroquia
                { content: proc.id_municipio__municipio },  // Municipio
                { content: proc.direccion, className: 'fixed-width' },  // Dirección
                { content: formatDate(proc.fecha) },  // Fecha (formateada)
                { content: formatTime(proc.hora) },  // Hora (formateada)
                { content: proc.id_tipo_procedimiento__tipo_procedimiento },  // Tipo de procedimiento
                { content: `<td>
              <!-- NO TOCAR BOTON ELIMINAR-->
              <button
                type="button"
                class="button_delete"
                data-id="${proc.id}"
                data-id_mostrar="${rowCount}"
                data-solicitante="${proc.solicitante_externo}"
                data-jefeComision="${proc.id_jefe_comision__jerarquia + " " + proc.id_jefe_comision__nombres + " " + proc.id_jefe_comision__apellidos}"
                data-fecha="${formatDate(proc.fecha)}"
                data-tipoProcedimiento="${ proc.id_tipo_procedimiento__tipo_procedimiento}"
                data-bs-toggle="modal"
                data-bs-target="#staticBackdrop"
              >
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

              <!-- NO TOCAR Boton informacion-->
              <button
                type="button"
                class="button-info"
                data-id="${proc.id}"
                data-id_procedimiento="${proc.id_tipo_procedimiento__tipo_procedimiento}"
                id="view-info"
                data-bs-toggle="modal"
                data-bs-target="#modal-info"
                
              >
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

              <!-- Boton de Editar -->
              <button 
                class="button_delete btn-editar" 
                data-id="${proc.id}"
                data-bs-toggle="modal" 
                data-bs-target="#editarModal">
                <svg width="35px" height="35px" viewBox="0 0 1024 1024" class="icon" version="1.1" xmlns="http://www.w3.org/2000/svg" fill="#000000" style="pointer-events: none;"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"><path d="M823.3 938.8H229.4c-71.6 0-129.8-58.2-129.8-129.8V215.1c0-71.6 58.2-129.8 129.8-129.8h297c23.6 0 42.7 19.1 42.7 42.7s-19.1 42.7-42.7 42.7h-297c-24.5 0-44.4 19.9-44.4 44.4V809c0 24.5 19.9 44.4 44.4 44.4h593.9c24.5 0 44.4-19.9 44.4-44.4V512c0-23.6 19.1-42.7 42.7-42.7s42.7 19.1 42.7 42.7v297c0 71.6-58.2 129.8-129.8 129.8z" fill="#3688FF"></path><path d="M483 756.5c-1.8 0-3.5-0.1-5.3-0.3l-134.5-16.8c-19.4-2.4-34.6-17.7-37-37l-16.8-134.5c-1.6-13.1 2.9-26.2 12.2-35.5l374.6-374.6c51.1-51.1 134.2-51.1 185.3 0l26.3 26.3c24.8 24.7 38.4 57.6 38.4 92.7 0 35-13.6 67.9-38.4 92.7L513.2 744c-8.1 8.1-19 12.5-30.2 12.5z m-96.3-97.7l80.8 10.1 359.8-359.8c8.6-8.6 13.4-20.1 13.4-32.3 0-12.2-4.8-23.7-13.4-32.3L801 218.2c-17.9-17.8-46.8-17.8-64.6 0L376.6 578l10.1 80.8z" fill="#5F6379"></path></g></svg>
              </button>
            </td>`, className: 'icons-accion' }
            ];

            // Crear una fila para cada procedimiento
            const row = document.createElement('tr');

            // Crear la celda de contador como un <th>
            const th = document.createElement('th');
            th.setAttribute('scope', 'row');  // Asegurarse de que sea una celda de encabezado (th)
            th.textContent = rowCount;  // Restamos 1 para que el contador comience correctamente
            row.appendChild(th);
            rowCount++

            fields.forEach(field => {
                const cell = document.createElement('td');
                if (field.className) {
                    cell.classList.add(field.className);
                }
                cell.innerHTML = field.content;
                row.appendChild(cell);
            });

            // Agregar la fila al cuerpo de la tabla
            tableBody.appendChild(row);
        });
        
        // Función para formatear la fecha
        function formatDate(dateString) {
            // Crear la fecha sin ajuste de zona horaria, asegurando que sea exactamente la fecha proporcionada
            const date = new Date(dateString + 'T00:00:00'); // Se asegura que la hora esté en 00:00:00 para evitar problemas de zona horaria

            // Extraer el día, mes y año
            const day = String(date.getDate()).padStart(2, '0');  // Asegurarse de que el día tenga 2 dígitos
            const month = String(date.getMonth() + 1).padStart(2, '0');  // Mes (el mes en JavaScript comienza desde 0, así que sumamos 1)
            const year = date.getFullYear();  // Año

            // Devuelve la fecha en formato dd-mm-yyyy
            return `${day}-${month}-${year}`;
        }

        // Función para formatear la hora en formato 12 horas con a.m. / p.m.
        function formatTime(time) {
            const [hours, minutes, seconds] = time.split(':');  // Separar horas, minutos y segundos

            // Convertir horas y minutos a enteros
            let hour = parseInt(hours, 10);
            let minute = parseInt(minutes, 10);

            // Determinar si es AM o PM
            const period = hour >= 12 ? 'p.m.' : 'a.m.';

            // Convertir las horas al formato de 12 horas
            if (hour > 12) {
                hour -= 12;  // Convertir horas mayores a 12 en formato de 12 horas
            } else if (hour === 0) {
                hour = 12;  // 12 a.m. es representado como 12, no como 0
            }

            // Añadir ceros a la izquierda a los minutos si es necesario
            minute = minute < 10 ? '0' + minute : minute;

            // Devolver la hora en formato de 12 horas con a.m. / p.m.
            return `${hour}:${minute} ${period}`;
        }


        // Actualizar la fecha con la fecha del día anterior para la siguiente solicitud
        const fechaAnterior = new Date(data.fecha);  // Convertir la fecha recibida a un objeto Date
        fechaAnterior.setDate(fechaAnterior.getDate() - 1);  // Restar un día

        // Actualizar el campo oculto con la nueva fecha
        const nuevaFecha = fechaAnterior.toISOString().split('T')[0];  // Formato YYYY-MM-DD
        fechaActualInput.value = nuevaFecha;  // Actualizar el valor del campo oculto

        // Actualizar la URL para cargar más procedimientos de la fecha anterior
        // No es estrictamente necesario, ya que `fecha_actual` lo maneja el input oculto
    }
    catch (error) {
        console.error("Error al cargar procedimientos:", error);
    }
}

// Al hacer clic en "Cargar más", se cargan los procedimientos del día anterior
cargarMasBtn.addEventListener('click', () => {
    let fechaActual = fechaActualInput.value;  // Obtener la fecha actual desde el campo oculto
    
    cargarProcedimientos(fechaActual);  // Llamamos a la función para cargar procedimientos
    
});
