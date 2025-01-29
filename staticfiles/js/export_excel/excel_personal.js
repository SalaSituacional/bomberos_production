async function generarExcel() {
    try {
      // Deshabilitar el botón y mostrar un mensaje de carga
      const boton = document.getElementById("exportarExcel");
      boton.disabled = true;
      boton.textContent = "Generando...";
  
      // Obtener los datos del servidor
      const response = await fetch('/descargar-excel_personal/');
      if (!response.ok) {
        throw new Error("Error al obtener los datos del servidor.");
      }
      const data = await response.json();
  
      // Crear el libro de trabajo y la hoja
      const workbook = XLSX.utils.book_new();
      const worksheetData = [
        [
          "Nombres",
          "Apellidos",
          "Jerarquia",
          "Cargo",
          "Cedula",
          "Edad",
          "Fecha de ingreso",
          "Grupo Sanguineo",
          "Sexo",
          "Talla de Camisa",
          "Talla de Pantalon",
          "Talla de Zapatos",
          "Contrato",
          "Estado",
        ]
      ];
  
      // Agregar los datos con validación
      data.forEach((item) => {
        worksheetData.push([
          item.nombres || "N/A",
          item.apellidos || "N/A",
          item.jerarquia || "N/A",
          item.cargo || "N/A",
          item.cedula || "N/A",
          item.edad || "N/A",
          item.fecha_ingreso || "N/A",
          item.grupo_sanguineo || "N/A",
          item.sexo || "N/A",
          item.talla_camisa || "N/A",
          item.talla_pantalon || "N/A",
          item.talla_zapatos || "N/A",
          item.rol || "N/A",
          item.status || "N/A"
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
      XLSX.utils.book_append_sheet(workbook, worksheet, "Personal");
      XLSX.writeFile(workbook, "personal.xlsx");
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
    const boton = document.getElementById("exportarExcel");
    boton.addEventListener("click", generarExcel);
  });