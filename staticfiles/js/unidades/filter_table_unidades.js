// Obtener referencias a los elementos del DOM
const inputNombreUnidad = document.getElementById("filterJerarquia");
const tabla = document.querySelector(".tabla-unidades tbody");

// Función para filtrar la tabla
function filtrarTabla() {
  const filtroNombre = inputNombreUnidad.value.toLowerCase();

  // Iterar por cada fila de la tabla
  Array.from(tabla.rows).forEach((fila) => {
    const columnaUnidad = fila.cells[1].textContent.toLowerCase(); // Columna de Unidad

    const coincideNombre = columnaUnidad.includes(filtroNombre);

    // Mostrar u ocultar la fila según el filtro
    if (coincideNombre) {
      fila.style.display = ""; // Mostrar
    } else {
      fila.style.display = "none"; // Ocultar
    }
  });
}

// Agregar eventos al filtro
inputNombreUnidad.addEventListener("input", filtrarTabla);
