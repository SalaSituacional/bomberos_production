let mesExcel = "";

async function obtenerDatosPaginados(mes) {
  let page = 1;
  const pageSize = 120; // Ajusta según sea necesario
  let todosLosDatos = [];

  try {
    while (true) {
      const response = await fetch(`/descargar-excel-operacional/?mes=${mes}&page=${page}&page_size=${pageSize}`);

      if (!response.ok) {
        throw new Error(`Error en la página ${page}`);
      }

      const data = await response.json();

      if (!data.data || data.data.length === 0) {
        break; // No hay más datos, salir del bucle
      }

      todosLosDatos = todosLosDatos.concat(data.data);
      if (page >= data.total_pages) {
        break; // Si ya estamos en la última página, terminamos
      }

      page++; // Pasamos a la siguiente página
    }
  } catch (error) {
    console.error("Error al obtener los datos paginados:", error);
    alert("No se pudo obtener los datos para generar el Excel.");
    return [];
  }

  return todosLosDatos;
}

async function generarExcel(mes) {
  try {
    const boton = document.getElementById("exportarExcel");
    boton.disabled = true;
    boton.textContent = "Generando...";

    const data = await obtenerDatosPaginados(mes);
    if (data.length === 0) {
      throw new Error("No se encontraron datos.");
    }

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
        "Descripcion",
        "Material Utilizado",
        "Status",
        "Persona Presente",
        "Traslados",
        "Vehiculos",
        "Comisiones",
        "Retención Preventiva"
      ]
    ];

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
        item.detalles || "N/A",
        item.descripcion || "[SIN DATOS]",
        item.material_utilizado || "[SIN DATOS]",
        item.status || "[SIN DATOS]",
        item.personas_presentes || "[SIN DATOS]",
        item.traslados || "[SIN DATOS]",
        item.vehiculos || "[SIN DATOS]",
        item.comisiones || "[SIN DATOS]",
        item.retencion_preventiva || "[SIN DATOS]",
      ]);
    });

    const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);

    const columnWidths = worksheetData[0].map((header) => ({
      wch: Math.max(...worksheetData.map((row) => (row[worksheetData[0].indexOf(header)] || "").toString().length)) + 2
    }));
    worksheet["!cols"] = columnWidths;

    XLSX.utils.book_append_sheet(workbook, worksheet, "TablaOperacional");
    XLSX.writeFile(workbook, "TablaOperacional.xlsx");

  } catch (error) {
    console.error("Hubo un problema al generar el Excel:", error);
    alert("No se pudo generar el archivo Excel. Inténtalo de nuevo.");
  } finally {
    const boton = document.getElementById("exportarExcel");
    boton.disabled = false;
    boton.textContent = "Exportar .xls";
  }
}

// Asegurar que solo haya un evento de click en el botón
document.addEventListener("DOMContentLoaded", function () {
  const boton = document.getElementById("exportarExcel");
  const selectMes = document.getElementById("mes_excel");

  selectMes.addEventListener("change", function () {
    mesExcel = this.value;
    boton.disabled = !mesExcel;
  });

  boton.addEventListener("click", function () {
    if (mesExcel) {
      generarExcel(mesExcel);
    }
  });
});
