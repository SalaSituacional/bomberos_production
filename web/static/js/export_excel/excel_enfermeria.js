let mesExcel = ""

async function generarExcelEnfermeria(mes) {
    try {
      // Deshabilitar el botón mientras se genera el archivo
      const boton = document.getElementById("exportarExcel");
      boton.disabled = true;
      boton.textContent = "Generando...";

      // Obtener los datos del servidor
      const response = await fetch(`/descargar-excel-enfermeria?mes=${mes}`);
      if (!response.ok) {
        throw new Error("Error al obtener los datos del servidor.");
      }
      const data = await response.json();

      // Crear el libro de trabajo y la hoja
      const workbook = XLSX.utils.book_new();
      const worksheetData = [
        [
          "División",
          "Dependencia",
          "Encargado del Area",
          "Municipio",
          "Parroquia",
          "Fecha",
          "Hora",
          "Dirección",
          "Tipo de Procedimiento",
          "Descripcion",
          "Material Utilizado",
          "Status",
          "Personas Presentes",
          "Traslados"
        ]
      ];

      // Agregar los datos con validación
      data.forEach((item) => {
        worksheetData.push([
          item.division || "N/A",
          item.dependencia || "N/A",
          item.encargado || "N/A",
          item.municipio || "N/A",
          item.parroquia || "N/A",
          item.fecha || "N/A",
          item.hora || "N/A",
          item.direccion || "N/A",
          item.tipo_procedimiento || "N/A",
          item.descripcion || "N/A",
          item.material_utilizado || "N/A",
          item.status || "N/A",
          item.personas_presentes || "N/A",
          item.traslados || "N/A"
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
      XLSX.utils.book_append_sheet(workbook, worksheet, "Enfermería");
      XLSX.writeFile(workbook, "Enfermería.xlsx");
    } catch (error) {
      console.error("Hubo un problema al generar el Excel:", error);
      alert("No se pudo generar el archivo Excel. Por favor, inténtalo de nuevo.");
    } finally {
      // Habilitar el botón y restaurar su texto
      const boton = document.getElementById("exportarExcel");
      boton.disabled = false;
      boton.textContent = "Exportar a Excel";
    }
  }


document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("mes_excel").addEventListener("change", function () {
    mesExcel = document.getElementById("mes_excel").value;

    if (this.value) {
      const boton = document.getElementById("exportarExcel");
      boton.removeAttribute("disabled");
      
      boton.addEventListener("click", function () {
        generarExcelEnfermeria(mesExcel);
      });
    } else {
      document.getElementById("exportarExcel").setAttribute("disabled", true);
    }
  });
});
  