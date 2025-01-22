async function generarExcelPrevencion() {
  try {
    // Deshabilitar el botón y mostrar un mensaje de carga
    const boton = document.getElementById("exportarBtn");
    boton.disabled = true;
    boton.textContent = "Generando...";

    // Obtener los datos del servidor
    const response = await fetch("/descargar-excel-prevencion/");
    if (!response.ok) {
      throw new Error("Error al obtener los datos del servidor.");
    }
    const data = await response.json();

    // Crear el libro de trabajo y la hoja
    const workbook = XLSX.utils.book_new();
    const worksheetData = [
      [
        "División",
        "Solicitante",
        "Jefe de Comisión",
        "Municipio",
        "Parroquia",
        "Fecha",
        "Hora",
        "Dirección",
        "Tipo de Procedimiento",
        "Detalles",
        "Descripcion",
        "Material Utilizado",
        "Status",
        "Persona Presente",
        "Vehiculos",
        "Comisiones",
        "Retención Preventiva"
      ]
    ];

    // Agregar los datos con validación
    data.forEach((item) => {
      worksheetData.push([
        item.division || "N/A",
        item.solicitante || "N/A",
        item.jefe_comision || "N/A",
        item.municipio || "N/A",
        item.parroquia || "N/A",
        item.fecha || "N/A",
        item.hora || "N/A",
        item.direccion || "N/A",
        item.tipo_procedimiento || "N/A",
        item.detalles || "[SIN DATOS]",
        item.descripcion || "[SIN DATOS]",
        item.material_utilizado || "[SIN DATOS]",
        item.status || "[SIN DATOS]",
        item.personas_presentes || "[SIN DATOS]",
        item.vehiculos || "[SIN DATOS]",
        item.comisiones || "[SIN DATOS]",
        item.retencion_preventiva || "[SIN DATOS]",
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
    XLSX.utils.book_append_sheet(workbook, worksheet, "Prevención");
    XLSX.writeFile(workbook, "Prevencion.xlsx");
  } catch (error) {
    console.error("Hubo un problema al generar el Excel:", error);
    alert("No se pudo generar el archivo Excel. Por favor, inténtalo de nuevo.");
  } finally {
    // Habilitar el botón y restaurar su texto
    const boton = document.getElementById("exportarBtn");
    boton.disabled = false;
    boton.textContent = "Exportar .xls";
  }
}

// Asignar el evento al botón
document
  .getElementById("exportarBtn")
  .addEventListener("click", generarExcelPrevencion);
