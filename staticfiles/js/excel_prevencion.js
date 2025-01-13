// Archivo: generarExcel.js

async function generarExcel() {
  // Obtener los datos del servidor
  const response = await fetch("/descargar-excel-prevencion/");
  const data = await response.json();

  // Crear el libro de trabajo y la hoja
  const workbook = XLSX.utils.book_new();
  const worksheetData = [
    [
      "División",
      "Solicitante",
      "Jefe Comisión",
      "Municipio",
      "Parroquia",
      "Fecha",
      "Hora",
      "Dirección",
      "Tipo de Procedimiento",
      "Detalles",
      "Persona Presente",
      "Descripcion"
    ]
  ];

  // Agregar los datos
  data.forEach((item) => {
    worksheetData.push([
      item.division,
      item.solicitante,
      item.jefe_comision,
      item.municipio,
      item.parroquia,
      item.fecha,
      item.hora,
      item.direccion,
      item.tipo_procedimiento,
      item.detalles,
      item.personas_presentes,
      item.descripcion
    ]);
  });

  const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);

  // Ajustar el ancho de las columnas
  const columnWidths = worksheetData[0].map((header) => ({
    wch:
      Math.max(
        ...worksheetData.map(
          (row) =>
            (row[worksheetData[0].indexOf(header)] || "").toString().length
        )
      ) + 2
  }));
  worksheet["!cols"] = columnWidths;

  // Agregar hoja al libro de trabajo y exportar
  XLSX.utils.book_append_sheet(workbook, worksheet, "Prevencion");
  XLSX.writeFile(workbook, "Prevencion.xlsx");
}

// Llama a la función al hacer clic en un botón
document
  .getElementById("exportarExcel")
  .addEventListener("click", generarExcel);
