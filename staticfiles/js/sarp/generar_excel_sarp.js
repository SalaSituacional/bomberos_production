let mesExcel = "";

// Función para descargar el archivo Excel con los datos de vuelo
function descargarExcelVuelos(mes) {
  fetchWithLoader2(`/generar-excel-reportes-sarp/?mes=${mes}`)
    .then((response) => {
      return response;
    })
    .then((data) => {
      const wb = XLSX.utils.book_new();
      const sheetData = [];
      const encabezados = [
        "Fecha",
        "Hora",
        "Encargado",
        "Descripción",
        "Tipo de Misión",
      ];

      // Agregar encabezados al arreglo de datos de la hoja
      sheetData.push(encabezados);

      // Procesar los datos recibidos para agregar cada fila a la hoja
      data.forEach((vuelo) => {
        sheetData.push([
          vuelo["fecha"],
          vuelo["hora"],
          vuelo["encargado"],
          vuelo["descripcion"],
          vuelo["tipo_mision"],
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
      XLSX.utils.book_append_sheet(wb, ws, "Vuelos");

      // Descargar el archivo Excel
      XLSX.writeFile(wb, "Vuelos.xlsx");
    })
    .catch((error) => {
      console.error("Error al obtener los datos:", error);
      alert(
        "Ocurrió un error al obtener los datos. Por favor, inténtalo de nuevo."
      );
    });
}

document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("mes_excel").addEventListener("change", function () {
    mesExcel = document.getElementById("mes_excel").value;

    if (this.value) {
      const boton = document.getElementById("exportarExcel");
      boton.removeAttribute("disabled");

      boton.addEventListener("click", function () {
        descargarExcelVuelos(mesExcel);
      });
    } else {
      document.getElementById("exportarExcel").setAttribute("disabled", true);
    }
  });
});

async function fetchWithLoader2(url, options = {}) {
  activeRequests++;
  showLoader();

  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(
        `Error en la solicitud: ${response.status} ${response.statusText}`
      );
    }

    return await response.blob(); // ⬅️ Convertir la respuesta en un Blob
  } catch (error) {
    console.error("Error al consumir la API:", error);
    throw error;
  } finally {
    activeRequests--;
    hideLoader();
  }
}
