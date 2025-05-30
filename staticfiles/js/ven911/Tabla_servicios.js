// Función para cargar y mostrar los datos en la tabla
function cargarTablaServicios() {
    fetch(api_table_911)
        .then(response => {
            if (!response.ok) {
                // Si la respuesta no es OK (ej. 404, 500), lanzamos un error
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json(); // Parsear la respuesta como JSON
        })
        .then(data => {
            const tbody = document.querySelector('#tablaven911 tbody');
            tbody.innerHTML = ''; // Limpiar tabla antes de cargar nuevos datos

            // Verificar si 'data' tiene la propiedad 'servicios' y si es un array
            if (data && Array.isArray(data.servicios)) {
                data.servicios.forEach((servicio, index) => {
                    const tr = document.createElement('tr');

                    // Construir cada celda de la fila
                    tr.innerHTML = `
                        <th scope="row">${index + 1}</th>
                        <td>${servicio.operador_de_guardia?.nombre_completo || 'N/A'}</td>
                        <td>${servicio.fecha}</td>
                        <td>${servicio.tipo_servicio?.nombre || 'N/A'}</td>
                        <td>${servicio.cantidad_tipo_servicio}</td>
                        <td>
                            <button class="btn btn-editar" data-id="${servicio.id}">
                                <svg width="35px" height="35px" viewBox="0 0 1024 1024" class="icon" version="1.1" xmlns="http://www.w3.org/2000/svg" fill="#000000" style="pointer-events: none;"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"><path d="M823.3 938.8H229.4c-71.6 0-129.8-58.2-129.8-129.8V215.1c0-71.6 58.2-129.8 129.8-129.8h297c23.6 0 42.7 19.1 42.7 42.7s-19.1 42.7-42.7 42.7h-297c-24.5 0-44.4 19.9-44.4 44.4V809c0 24.5 19.9 44.4 44.4 44.4h593.9c24.5 0 44.4-19.9 44.4-44.4V512c0-23.6 19.1-42.7 42.7-42.7s42.7 19.1 42.7 42.7v297c0 71.6-58.2 129.8-129.8 129.8z" fill="#3688FF"></path><path d="M483 756.5c-1.8 0-3.5-0.1-5.3-0.3l-134.5-16.8c-19.4-2.4-34.6-17.7-37-37l-16.8-134.5c-1.6-13.1 2.9-26.2 12.2-35.5l374.6-374.6c51.1-51.1 134.2-51.1 185.3 0l26.3 26.3c24.8 24.7 38.4 57.6 38.4 92.7 0 35-13.6 67.9-38.4 92.7L513.2 744c-8.1 8.1-19 12.5-30.2 12.5z m-96.3-97.7l80.8 10.1 359.8-359.8c8.6-8.6 13.4-20.1 13.4-32.3 0-12.2-4.8-23.7-13.4-32.3L801 218.2c-17.9-17.8-46.8-17.8-64.6 0L376.6 578l10.1 80.8z" fill="#5F6379"></path></g></svg>
                            </button>
                            <button class="btn btn-eliminar" data-id="${servicio.id}">
                                <svg width="35px" height="35px" viewBox="0 0 1024 1024" class="icon" version="1.1" xmlns="http://www.w3.org/2000/svg" fill="#000000" style="pointer-events: none;">
                                    <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
                                    <g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g>
                                    <g id="SVGRepo_iconCarrier">
                                        <path d="M779.5 1002.7h-535c-64.3 0-116.5-52.3-116.5-116.5V170.7h768v715.5c0 64.2-52.3 116.5-116.5 116.5zM213.3 256v630.1c0 17.2 14 31.2 31.2 31.2h534.9c17.2 0 31.2-14 31.2-31.2V256H213.3z" fill="#3688FF"></path>
                                        <path d="M917.3 256H106.7C83.1 256 64 236.9 64 213.3s19.1-42.7 42.7-42.7h810.7c23.6 0 42.7 19.1 42.7 42.7S940.9 256 917.3 256zM618.7 128H405.3c-23.6 0-42.7-19.1-42.7-42.7s19.1-42.7 42.7-42.7h213.3c23.6 0 42.7 19.1 42.7 42.7S642.2 128 618.7 128zM405.3 725.3c-23.6 0-42.7-19.1-42.7-42.7v-256c0-23.6 19.1-42.7 42.7-42.7S448 403 448 426.6v256c0 23.6-19.1 42.7-42.7 42.7zM618.7 725.3c-23.6 0-42.7-19.1-42.7-42.7v-256c0-23.6 19.1-42.7 42.7-42.7s42.7 19.1 42.7 42.7v256c-0.1 23.6-19.2 42.7-42.7 42.7z" fill="#5F6379"></path>
                                    </g>
                                </svg>
                            </button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            } else {
                tbody.innerHTML = `<tr><td colspan="7" class="text-center">No hay servicios disponibles o el formato de datos es incorrecto.</td></tr>`;
            }

            // Añadir event listeners a los botones después de crear la tabla
            añadirEventListeners();
        })
        .catch(error => {
            console.error('Error al cargar los datos de servicios:', error);
            // Mostrar mensaje de error al usuario en la tabla
            const tbody = document.querySelector('#tablaven911 tbody'); // Asegúrate de que el ID del tbody sea correcto
            tbody.innerHTML = `<tr><td colspan="7" class="text-center text-danger">Error al cargar los datos: ${error.message}</td></tr>`;
        });
}

// Función para manejar los eventos de los botones
function añadirEventListeners() {
    // Botones de editar
    document.querySelectorAll('.btn-editar').forEach(btn => {
        btn.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            window.location.href = form_services_edit + `?id=${id}`;
        });
    });

    // Botones de eliminar
    document.querySelectorAll('.btn-eliminar').forEach(btn => {
        btn.addEventListener('click', function () {
            const id = this.getAttribute('data-id');
            // Asegúrate de que 'eliminarServicio' esté definida globalmente o importada
            if (typeof eliminarServicio === 'function') {
                eliminarServicio(id); // Llama a la función externa
            } else {
                console.warn('La función eliminarServicio no está definida.');
                // Puedes agregar una alerta o un mensaje aquí si la función no existe
            }
        });
    });
}

// Cargar la tabla cuando la página esté lista
document.addEventListener('DOMContentLoaded', cargarTablaServicios);