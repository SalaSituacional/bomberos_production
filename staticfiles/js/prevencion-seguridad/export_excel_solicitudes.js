async function generarExcel() {
    try {
        // Deshabilitar botón y mostrar mensaje de carga
        const boton = document.getElementById("exportarExcel");
        boton.disabled = true;
        boton.textContent = "Generando...";

        // Obtener los datos del backend
        const response = await fetch('/generar-excel-solicitudes/');
        const data = await response.json();

        // Crear libro y hoja de trabajo
        const workbook = XLSX.utils.book_new();
        const worksheetData = [
            [
                "ID Comercio",
                "Nombre Comercio",
                "RIF Comercio",
                "Número de Teléfono",
                "Nombre y Apellido del Solicitante",
                "Fecha de Solicitud",
                "Dirección"
            ]
        ];

        // Agregar datos
        data.forEach(item => {
            worksheetData.push([
                item["ID Comercio"] || "N/A",
                item["Nombre Comercio"] || "N/A",
                item["RIF Comercio"] || "N/A",
                item["Número de Teléfono"] || "N/A",
                item["Nombre y Apellido del Solicitante"] || "N/A",
                item["Fecha de Solicitud"] || "N/A",
                item["Dirección"] || "N/A"
            ]);
        });

        const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);

        // Ajustar ancho de columnas
        const columnWidths = worksheetData[0].map(header => ({
            wch: Math.max(
                ...worksheetData.map(row => (row[worksheetData[0].indexOf(header)] || "").toString().length)
            ) + 2
        }));
        worksheet["!cols"] = columnWidths;

        // Agregar hoja y exportar
        XLSX.utils.book_append_sheet(workbook, worksheet, "Solicitudes");
        XLSX.writeFile(workbook, "solicitudes-Seguridad-prevencion.xlsx");
    } catch (error) {
        console.error("Hubo un problema al generar el Excel:", error);
        alert("No se pudo generar el archivo Excel. Por favor, inténtalo de nuevo.");
    } finally {
        // Restaurar botón
        const boton = document.getElementById("exportarExcel");
        boton.disabled = false;
        boton.textContent = "Exportar .xls";
    }
}

// Evento para botón
document.addEventListener("DOMContentLoaded", function () {
    const boton = document.getElementById("exportarExcel");
    boton.addEventListener("click", generarExcel);
});
