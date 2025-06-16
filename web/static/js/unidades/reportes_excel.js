let mesExcel = "";

// Función para descargar el archivo Excel con los datos de capacitación
function descargarExcelUnidades(mes) {
  fetch(`/mecanica/generar-excel-reportes-unidades/?mes=${mes}`)
    .then((response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return response.json();
    })
    .then((data) => {
      const wb = XLSX.utils.book_new();
      const sheetData = [];
      const encabezados = [
        'Nombre Unidad',
        'Servicio',
        'Fecha',
        'Hora',
        'Descripción',
        'Persona Responsable'
      ];

      // Agregar encabezados al arreglo de datos de la hoja
      sheetData.push(encabezados);

      // Procesar los datos recibidos para agregar cada fila a la hoja
      data.forEach((reporte) => {
        sheetData.push([
          reporte['nombre unidad'],
          reporte['servicio'],
          reporte['fecha'],
          reporte['hora'],
          reporte['descripcion'],
          reporte['persona responsable'],
        ]);
      });

      // Crear la hoja de trabajo y agregarla al libro
      const ws = XLSX.utils.aoa_to_sheet(sheetData);

      // Calcular el ancho máximo de cada columna
      const colWidths = sheetData[0].map((col, index) => {
        let maxLength = col ? col.toString().length : 0;
        sheetData.forEach((row) => {
          maxLength = Math.max(
            maxLength,
            row[index] ? row[index].toString().length : 0
          );
        });
        return { wch: maxLength + 2 }; // Agregamos un margen de 2 caracteres
      });

      // Asignar los anchos de columna calculados a la hoja
      ws["!cols"] = colWidths;

      // Agregar la hoja al libro
      XLSX.utils.book_append_sheet(wb, ws, "Reportes");

      // Descargar el archivo Excel
      XLSX.writeFile(wb, "Reportes.xlsx");
    })
    .catch((error) => {
      console.error("Error al obtener los datos:", error);
      alert("Ocurrió un error al obtener los datos. Por favor, inténtalo de nuevo.");
    });
}

document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("mes_excel").addEventListener("change", function () {
    mesExcel = document.getElementById("mes_excel").value;

    if (this.value) {
      const boton = document.getElementById("exportarExcel");
      boton.removeAttribute("disabled");

      boton.addEventListener("click", function () {
        descargarExcelUnidades(mesExcel);
      });
    } else {
      document.getElementById("exportarExcel").setAttribute("disabled", true);
    }
  });
});