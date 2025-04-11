let mesExcel = "";

// Función para descargar el archivo Excel con todos los bienes municipales
function descargarExcelBienes() {
  fetch(`/generar-excel-bienesmunicipales/`) // Eliminamos el parámetro mes
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Error en la solicitud: ${response.status} ${response.statusText}`);
      }
      return response.json(); // Procesar los datos como JSON
    })
    .then((data) => {
      const wb = XLSX.utils.book_new(); // Crear un nuevo libro de Excel
      const sheetData = [];
      const encabezados = [
        "Identificador",
        "Descripción",
        "Cantidad",
        "Dependencia",
        "Departamento",
        "Responsable",
        "Fecha de Registro",
        "Estado Actual",
        "Movimientos", // Nueva columna para los movimientos
      ];

      // Agregar encabezados al arreglo de datos de la hoja
      sheetData.push(encabezados);

      // Procesar los datos recibidos para agregar cada fila a la hoja
      data.forEach((bien) => {
        // Procesar movimientos relacionados
        const movimientos = bien.movimientos.map((movimiento) => {
          return `Dependencia: ${movimiento.nueva_dependencia}, Departamento: ${movimiento.nuevo_departamento}, Ordenado Por: ${movimiento.ordenado_por}, Fecha: ${movimiento.fecha_orden}`;
        }).join("\n"); // Convertir cada movimiento en texto separado por saltos de línea

        sheetData.push([
          bien["identificador"],
          bien["descripcion"],
          bien["cantidad"],
          bien["dependencia"],
          bien["departamento"],
          bien["responsable"],
          bien["fecha_registro"],
          bien["estado_actual"],
          movimientos, // Incluir los movimientos como una cadena de texto
        ]);
      });

      // Crear la hoja de trabajo y agregarla al libro
      const ws = XLSX.utils.aoa_to_sheet(sheetData);

      // Calcular el ancho máximo de cada columna
      const colWidths = sheetData[0].map((col, index) => {
        let maxLength = col ? col.toString().length : 0;
        sheetData.forEach((row) => {
          maxLength = Math.max(maxLength, row[index] ? row[index].toString().length : 0);
        });
        return { wch: maxLength + 2 }; // Agregamos un margen de 2 caracteres
      });

      // Asignar los anchos de columna calculados a la hoja
      ws["!cols"] = colWidths;

      // Agregar la hoja al libro
      XLSX.utils.book_append_sheet(wb, ws, "Bienes Inmuebles");

      // Descargar el archivo Excel
      XLSX.writeFile(wb, "Bienes_inmuebles.xlsx");
    })
    .catch((error) => {
      console.error("Error al obtener los datos:", error);
      alert("Ocurrió un error al obtener los datos. Por favor, inténtalo de nuevo.");
    });
}

document.addEventListener("DOMContentLoaded", function () {
  const boton = document.getElementById("exportarExcel");
  boton.addEventListener("click", function () {
    descargarExcelBienes(); // Llama a la función sin filtro de mes
  });
});
