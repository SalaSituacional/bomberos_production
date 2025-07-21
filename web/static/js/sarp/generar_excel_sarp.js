let mesSeleccionadoParaExcel = "";

/**
 * Descarga un archivo Excel con datos de vuelos para el mes especificado.
 * @param {string} mes - El mes seleccionado del input (formato YYYY-MM o MM-YYYY).
 */
async function descargarExcelVuelos(mes) {
  // Aseguramos que el formato del mes sea YYYY-MM para el backend de Django.
  let mesParaBackend = mes;
  if (mes.includes('-')) {
    const partes = mes.split('-');
    // Si detectamos formato MM-YYYY (ej. "07-2025"), lo convertimos a YYYY-MM
    if (partes[0].length === 2 && partes[1].length === 4) {
      mesParaBackend = `${partes[1]}-${partes[0]}`;
    }
  }

  const urlCompleta = `${GenerarExcelReportesSarpUrl}?mes=${mesParaBackend}`;
  // console.log("Solicitando datos Excel desde:", urlCompleta); // <- Este log es clave para verificar la URL

  try {
    const response = await fetch(urlCompleta);

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Error en la solicitud: ${response.status} ${response.statusText} - ${errorText}`);
    }

    const data = await response.json(); // Parsea la respuesta JSON

    if (!data || data.length === 0) {
      alert("No se encontraron datos para el mes seleccionado.");
      return; // Salir si no hay datos
    }

    // --- Generación del archivo Excel usando SheetJS (XLSX.js) ---
    const wb = XLSX.utils.book_new(); // Nuevo libro de trabajo
    const sheetData = [];
    const encabezados = ["Fecha", "Hora", "Encargado", "Descripción", "Tipo de Misión"];
    sheetData.push(encabezados); // Añadir encabezados

    // Llenar datos de la hoja
    data.forEach((vuelo) => {
      sheetData.push([
        vuelo["fecha"],
        vuelo["hora"],
        vuelo["encargado"],
        vuelo["descripcion"],
        vuelo["tipo_mision"],
      ]);
    });

    const ws = XLSX.utils.aoa_to_sheet(sheetData); // Convertir array a hoja de trabajo

    // Calcular y aplicar anchos de columna automáticamente
    const colWidths = sheetData[0].map((col, index) => {
      let maxLength = col ? String(col).length : 0;
      sheetData.forEach((row) => {
        maxLength = Math.max(maxLength, row[index] ? String(row[index]).length : 0);
      });
      return { wch: maxLength + 2 }; // Añadir un poco de padding
    });
    ws["!cols"] = colWidths;

    XLSX.utils.book_append_sheet(wb, ws, "Vuelos"); // Añadir hoja al libro
    XLSX.writeFile(wb, `Reporte_Vuelos_Mes_${mesParaBackend}.xlsx`); // Descargar el archivo

  } catch (error) {
    console.error("Error al obtener o procesar los datos para Excel:", error);
    alert("Ocurrió un error al obtener los datos para el Excel. Por favor, inténtalo de nuevo.");
  }
}

// --- Manejo de Eventos del DOM ---
document.addEventListener("DOMContentLoaded", function () {
  const selectMesInput = document.getElementById("mes_excel");
  const exportarBoton = document.getElementById("exportarExcel");

  // Verificar que los elementos existen en el HTML
  if (selectMesInput && exportarBoton) {
    exportarBoton.setAttribute("disabled", true); // Deshabilita el botón por defecto

    // Listener para cuando el valor del input de mes cambia
    selectMesInput.addEventListener("change", function () {
      mesSeleccionadoParaExcel = this.value; // Obtiene el valor del input

      if (mesSeleccionadoParaExcel) {
        exportarBoton.removeAttribute("disabled"); // Habilita el botón
        // Asigna el manejador de clic, limpiando cualquier asignación anterior
        exportarBoton.onclick = () => descargarExcelVuelos(mesSeleccionadoParaExcel);
      } else {
        exportarBoton.setAttribute("disabled", true); // Deshabilita si no hay mes seleccionado
        exportarBoton.onclick = null; // Elimina el manejador de clic
      }
    });
  } else {
    console.warn("No se encontraron los elementos 'mes_excel' o 'exportarExcel' en el DOM.");
  }
});