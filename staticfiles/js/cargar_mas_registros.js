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
    const url = `/registros?fecha=${fecha}`; // URL con la fecha como parámetro
  
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
            const fields = [
                { content: proc.usuario__user },
                { content: proc.url },
                { content: formatDate(proc.fecha_hora) },  // Aplicar formato legible a la fecha
            ];
        
            const row = document.createElement('tr');
        
            const th = document.createElement('th');
            th.setAttribute('scope', 'row');
            th.textContent = rowCount;
            row.appendChild(th);
            rowCount++;
        
            fields.forEach(field => {
                const cell = document.createElement('td');
                cell.innerHTML = field.content;
                row.appendChild(cell);
            });
        
            tableBody.appendChild(row);
        });

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

// Función para formatear la fecha al estilo DD/MM/YYYY HH:mm
function formatDate(fechaISO) {
    const date = new Date(fechaISO);
    const options = { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: false };
    return date.toLocaleString('es-ES', options);  // Formato para español
}


// Al hacer clic en "Cargar más", se cargan los procedimientos del día anterior
cargarMasBtn.addEventListener('click', () => {
    let fechaActual = fechaActualInput.value;  // Obtener la fecha actual desde el campo oculto
    
    cargarProcedimientos(fechaActual);  // Llamamos a la función para cargar procedimientos
    
});
