// Variable para mantener la fecha que se está mostrando actualmente en la tabla
// Se inicializa en null, y se establecerá cuando se carguen los datos
let fechaActualEnDisplay = null; 

// Función principal para cargar la tabla
// Acepta una fecha opcional. Si no se proporciona, usa la fecha actual por defecto.
async function cargarTablaServicios(fecha = null) {
    let url = api_table_911; // Usa la URL de tu API definida en el HTML

    if (fecha) {
        // Si se proporciona una fecha, la añadimos como parámetro de consulta
        url += `?fecha=${fecha}`;
        console.log(`Cargando servicios para la fecha: ${fecha}`); // Depuración
    } else {
        console.log('Cargando servicios para la fecha actual (por defecto)'); // Depuración
    }

    const tbody = document.querySelector('#tablaven911 tbody');
    // Mostrar un spinner de carga mientras se obtienen los datos
    tbody.innerHTML = `
        <tr>
            <td colspan="6" class="text-center py-4">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="mt-2 mb-0">Cargando servicios...</p>
            </td>
        </tr>
    `;
    
    try {
        const response = await fetch(url);
        
        if (!response.ok) {
            // Si la respuesta no es OK (ej. 404, 500), lanzamos un error
            throw new Error(`Error HTTP: ${response.status} - ${response.statusText}`);
        }

        const data = await response.json();
        tbody.innerHTML = ''; // Limpiar tabla antes de cargar nuevos datos

        console.debug('Datos recibidos:', data); // Para depuración
        console.debug('Fecha consultada del backend:', data.fecha_consultada); // Depuración crucial

        // Actualizar la fecha mostrada en el elemento <h4> en el frontend
        // data.fecha_consultada viene del backend, si no está, usa la fecha actual formateada
        fechaActualEnDisplay = data.fecha_consultada || obtenerFechaActualFormateada();
        const dateDisplayElement = document.getElementById('current-date-display');
        if (dateDisplayElement) {
            dateDisplayElement.textContent = `Servicios para: ${fechaActualEnDisplay}`;
        } else {
            console.warn('Elemento #current-date-display no encontrado.');
        }

        // Verificar si 'data' tiene la propiedad 'servicios' y si es un array
        if (data.servicios && Array.isArray(data.servicios) && data.servicios.length > 0) {
            data.servicios.forEach((servicio, index) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <th scope="row">${index + 1}</th>
                    <td>${servicio.operador_de_guardia?.nombre_completo || 'No asignado'}</td>
                    <td>${servicio.fecha || 'N/A'}</td>
                    <td>${servicio.tipo_servicio?.nombre || 'Sin tipo'}</td>
                    <td>${servicio.cantidad_tipo_servicio || 0}</td>
                    <td class="text-center">
                        <button class="btn btn-editar btn-sm" data-id="${servicio.id}" title="Editar">
                            <svg width="25" height="25" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M11 2H9C4 2 2 4 2 9V15C2 20 4 22 9 22H15C20 22 22 20 22 15V13" stroke="#292D32" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M16.04 3.02001L8.16 10.9C7.86 11.2 7.56 11.79 7.5 12.22L7.07 15.23C6.91 16.32 7.68 17.08 8.77 16.93L11.78 16.5C12.2 16.44 12.79 16.14 13.1 15.84L20.98 7.96001C22.34 6.60001 22.98 5.02001 20.98 3.02001C18.98 1.02001 17.4 1.66001 16.04 3.02001Z" stroke="#292D32" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M14.91 4.1499C15.58 6.5399 17.45 8.4099 19.85 9.0899" stroke="#292D32" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </button>
                        <button class="btn btn-eliminar btn-sm ms-2" data-id="${servicio.id}" title="Eliminar">
                            <svg width="25" height="25" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M21 5.97998C17.67 5.64998 14.32 5.47998 10.98 5.47998C9 5.47998 7.02 5.57998 5.04 5.77998L3 5.97998" stroke="#292D32" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M8.5 4.97L8.72 3.66C8.88 2.71 9 2 10.69 2H13.31C15 2 15.13 2.75 15.28 3.67L15.5 4.97" stroke="#292D32" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M18.85 9.14001L18.2 19.21C18.09 20.78 18 22 15.21 22H8.79002C6.00002 22 5.91002 20.78 5.80002 19.21L5.15002 9.14001" stroke="#292D32" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M10.33 16.5H13.66" stroke="#292D32" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M9.5 12.5H14.5" stroke="#292D32" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </button>
                    </td>
                `;
                tbody.appendChild(tr);
            });
        } else {
            tbody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-muted py-4">
                        <i class="bi bi-calendar-x fs-4"></i>
                        <p class="mt-2 mb-0">No hay servicios registrados para esta fecha.</p>
                    </td>
                </tr>
            `;
        }

        añadirEventListeners(); // Vuelve a añadir los event listeners a los nuevos botones

    } catch (error) {
        console.error('Error al cargar servicios:', error);
        mostrarErrorEnTabla(error.message);
    }
}

// **Función para obtener la fecha formateada a YYYY-MM-DD**
// Ahora toma un objeto Date y lo formatea.
function obtenerFechaActualFormateada(date = new Date()) {
    const year = date.getFullYear();
    // getMonth() es 0-index, así que sumamos 1. padStart(2, '0') asegura dos dígitos.
    const month = String(date.getMonth() + 1).padStart(2, '0'); 
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}


// --- INICIALIZACIÓN Y EVENT LISTENERS ---
document.addEventListener('DOMContentLoaded', () => {
    // Cargar la tabla con la fecha actual al inicio
    // Usamos obtenerFechaActualFormateada sin parámetros para el día de hoy
    cargarTablaServicios(obtenerFechaActualFormateada());
    
    // Configurar la recarga automática cada 60 segundos
    // Usa `fechaActualEnDisplay` para mantener la fecha actualmente visible
    setInterval(() => {
        if (fechaActualEnDisplay) { // Solo recargar si ya hay una fecha mostrada
            cargarTablaServicios(fechaActualEnDisplay);
        }
    }, 60000);
    
    // Event listener para el botón manual de recarga (si existe)
    // También usa `fechaActualEnDisplay`
    document.getElementById('btn-recargar')?.addEventListener('click', () => {
        if (fechaActualEnDisplay) {
            cargarTablaServicios(fechaActualEnDisplay);
        } else {
            cargarTablaServicios(obtenerFechaActualFormateada()); // Si no hay fecha, carga la de hoy
        }
    });

    // Event Listener para el botón "Día Siguiente"
    const btnDiaSiguiente = document.getElementById('btn-dia-siguiente');
    if (btnDiaSiguiente) {
        btnDiaSiguiente.addEventListener('click', () => {
            console.log('Botón "Día Siguiente" clickeado.'); // Depuración
            if (fechaActualEnDisplay) {
                const currentDisplayedDate = new Date(fechaActualEnDisplay + 'T00:00:00'); // IMPORTANTE: Añadir 'T00:00:00' para evitar problemas de zona horaria
                currentDisplayedDate.setDate(currentDisplayedDate.getDate() + 1); // Suma un día
                const nextDayFormatted = obtenerFechaActualFormateada(currentDisplayedDate); // Formatea la nueva fecha
                console.log(`Calculado día siguiente: ${nextDayFormatted}`); // Depuración
                cargarTablaServicios(nextDayFormatted); // Carga la tabla con la fecha del día siguiente
            } else {
                console.warn('fechaActualEnDisplay es nula. No se puede calcular el día siguiente.');
                // Opcional: cargar servicios del día actual si no hay fecha definida
                cargarTablaServicios(obtenerFechaActualFormateada(new Date())); 
            }
        });
    }

    // Event Listener para el botón "Día Anterior"
    const btnDiaAnterior = document.getElementById('btn-dia-anterior');
    if (btnDiaAnterior) {
        btnDiaAnterior.addEventListener('click', () => {
            console.log('Botón "Día Anterior" clickeado.'); // Depuración
            if (fechaActualEnDisplay) {
                const currentDisplayedDate = new Date(fechaActualEnDisplay + 'T00:00:00'); // IMPORTANTE: Añadir 'T00:00:00' para evitar problemas de zona horaria
                currentDisplayedDate.setDate(currentDisplayedDate.getDate() - 1); // Resta un día
                const prevDayFormatted = obtenerFechaActualFormateada(currentDisplayedDate); // Formatea la nueva fecha
                console.log(`Calculado día anterior: ${prevDayFormatted}`); // Depuración
                cargarTablaServicios(prevDayFormatted); // Carga la tabla con la fecha del día anterior
            } else {
                console.warn('fechaActualEnDisplay es nula. No se puede calcular el día anterior.');
                // Opcional: cargar servicios del día actual si no hay fecha definida
                cargarTablaServicios(obtenerFechaActualFormateada(new Date()));
            }
        });
    }
});


// --- FUNCIONES HELPER (Mantienen su lógica original) ---

// Función para manejar los eventos de los botones (editar y eliminar)
function añadirEventListeners() {
    document.querySelectorAll('.btn-editar').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.getAttribute('data-id');
            window.location.href = `${form_services_edit}?id=${id}`;
        });
    });

    document.querySelectorAll('.btn-eliminar').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = btn.getAttribute('data-id');
            if (typeof eliminarServicio === 'function') {
                eliminarServicio(id);
            } else {
                console.error('La función eliminarServicio no está definida. Asegúrate de que eliminar_servicio.js se carga correctamente y define esta función globalmente.');
            }
        });
    });
}

// Muestra un mensaje de error dentro de la tabla
function mostrarErrorEnTabla(mensaje) {
    const tbody = document.querySelector('#tablaven911 tbody');
    tbody.innerHTML = `
        <tr>
            <td colspan="6" class="text-center text-danger py-4">
                <i class="bi bi-exclamation-triangle fs-4"></i>
                <p class="mt-2 mb-0">${mensaje}</p>
                <button class="btn btn-sm btn-primary mt-2" onclick="cargarTablaServicios()">
                    Reintentar
                </button>
            </td>
        </tr>
    `;
}

// Muestra mensajes flotantes (toasts)
function mostrarMensaje(texto, tipo = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${tipo} border-0 show`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${texto}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Cerrar"></button>
        </div>
    `;
    
    const contenedor = document.getElementById('toast-container');
    if (contenedor) {
        contenedor.appendChild(toast);
        // Desaparecer el toast después de 5 segundos
        setTimeout(() => {
            // Usa Bootstrap's native dismiss if available, otherwise just remove
            // Necesitarás tener el JS de Bootstrap cargado para esto
            const bsToast = bootstrap.Toast.getInstance(toast) || new bootstrap.Toast(toast, { delay: 500 });
            bsToast.hide();
            toast.addEventListener('hidden.bs.toast', () => toast.remove());
        }, 5000);
    } else {
        console.warn('Contenedor de toasts no encontrado. Mensaje:', texto);
        alert(texto); // Fallback si el contenedor no está presente
    }
}

// Obtiene el valor de una cookie (CSRF token, etc.)
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}