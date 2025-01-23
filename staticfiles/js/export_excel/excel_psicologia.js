let mesExcel = ""

async function generarExcel(mes) {
    try {
      // Deshabilitar el botón y mostrar un mensaje de carga
      const boton = document.getElementById("exportarExcel");
      boton.disabled = true;
      boton.textContent = "Generando...";
  
      // Obtener los datos del servidor
      const response = await fetch(`/descargar-excel-psicologia?mes=${mes}`);
      if (!response.ok) {
        throw new Error("Error al obtener los datos del servidor.");
      }
      const data = await response.json();
  
      // Crear el libro de trabajo y la hoja
      const workbook = XLSX.utils.book_new();
      const worksheetData = [
        [
          "División",
          "Jefa del Area",
          "Municipio",
          "Parroquia",
          "Fecha",
          "Hora",
          "Dirección",
          "Tipo de Procedimiento",
          "Descripción",
          "Material Utilizado",
          "Status",
          "Persona Presente",
        ]
      ];
  
      // Agregar los datos con validación
      data.data.forEach((item) => {
        worksheetData.push([
          item.division || "N/A", // División
          item.jefe_area || "N/A", // Solicitante
          item.municipio || "N/A", // Municipio
          item.parroquia || "N/A", // Parroquia
          item.fecha || "N/A", // Fecha
          item.hora || "N/A", // Hora
          item.direccion || "N/A", // Dirección
          item.tipo_procedimiento || "N/A", // Tipo de Procedimiento
          item.descripcion || "N/A", // Descripción
          item.material_utilizado || "N/A", // Descripción
          item.status || "N/A", // Descripción
          item.personas_presentes || "N/A", // Personas presentes
        ]);
      });
  
      const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);
  
      // Ajustar el ancho de las columnas
      const columnWidths = worksheetData[0].map((header) => ({
        wch: Math.max(
          ...worksheetData.map(
            (row) =>
              (row[worksheetData[0].indexOf(header)] || "").toString().length
          )
        ) + 2
      }));
      worksheet["!cols"] = columnWidths;
  
      // Agregar hoja al libro de trabajo y exportar
      XLSX.utils.book_append_sheet(workbook, worksheet, "Psicología");
      XLSX.writeFile(workbook, "Psicologia.xlsx");
    } catch (error) {
      console.error("Hubo un problema al generar el Excel:", error);
      alert("No se pudo generar el archivo Excel. Por favor, inténtalo de nuevo.");
    } finally {
      // Habilitar el botón y restaurar su texto
      const boton = document.getElementById("exportarExcel");
      boton.disabled = false;
      boton.textContent = "Exportar .xls";
    }
  }
  
document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("mes_excel").addEventListener("change", function () {
    mesExcel = document.getElementById("mes_excel").value;

    if (this.value) {
      const boton = document.getElementById("exportarExcel");
      boton.removeAttribute("disabled");
      
      boton.addEventListener("click", function () {
        generarExcel(mesExcel);
      });
    } else {
      document.getElementById("exportarExcel").setAttribute("disabled", true);
    }
  });
});
  
  