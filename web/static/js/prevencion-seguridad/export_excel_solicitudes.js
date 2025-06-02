// Configurar fechas por defecto (último mes)
function setDefaultDates() {
    const today = new Date();
    const lastMonth = new Date(today.getFullYear(), today.getMonth() - 1, today.getDate());
    
    const formatDate = (date) => date.toISOString().split('T')[0];
    
    document.getElementById('fechaInicio').value = formatDate(lastMonth);
    document.getElementById('fechaFin').value = formatDate(today);
}

// Función principal para generar Excel
async function generarExcel() {
    try {
        const boton = document.getElementById("exportarExcel");
        const progressBar = document.getElementById("exportProgress");
        const progressBarInner = progressBar.querySelector(".progress-bar");
        
        // Configurar UI durante la exportación
        boton.disabled = true;
        boton.innerHTML = '<i class="bi bi-hourglass-split me-2"></i> Generando...';
        progressBar.classList.remove("d-none");
        progressBarInner.style.width = "0%";
        
        // Obtener parámetros de filtro
        const fechaInicio = document.getElementById("fechaInicio").value;
        const fechaFin = document.getElementById("fechaFin").value;
        const soloUltimos = document.getElementById("soloUltimos").checked;
        
        // Obtener dependencia correctamente - VERSIÓN CORREGIDA
        let dependencia = "";
        const dependenciaUsuario = document.getElementById("dependenciaUsuario");
        const dependenciaSelect = document.getElementById("dependenciaSelect"); // Usando ID directo

        if (dependenciaUsuario) {
            dependencia = dependenciaUsuario.value;
            console.log("Usando dependencia de usuario:", dependencia);
        } else if (dependenciaSelect) {
            dependencia = dependenciaSelect.value;
            console.log("Usando select de dependencia:", dependencia);
        } else {
            console.warn("No se encontró elemento para obtener dependencia");
        }

        // Asegúrate de que el valor se está enviando
        console.log("Valor de dependencia a enviar:", dependencia);
        
        // Validar fechas
        if (fechaInicio && fechaFin && new Date(fechaInicio) > new Date(fechaFin)) {
            alert("La fecha de inicio no puede ser mayor que la fecha final");
            throw new Error("Rango de fechas inválido");
        }
        
        // Configurar parámetros de la solicitud
        const params = new URLSearchParams();
        if (fechaInicio) params.append("fecha_inicio", fechaInicio);
        if (fechaFin) params.append("fecha_fin", fechaFin);
        params.append("solo_ultimos", soloUltimos);
        if (dependencia) params.append("departamento", dependencia);
        
        console.log("Parámetros enviados:", params.toString());
        
        // Obtener datos con paginación
        let allData = [];
        let page = 1;
        let hasMore = true;
        const pageSize = 500;
        
        while (hasMore) {
            params.set("page", page);
            params.set("page_size", pageSize);
            
            const response = await fetch(`/seguridad_prevencion/generar-excel-solicitudes/?${params.toString()}`);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || "Error al obtener datos");
            }
            
            const data = await response.json();
            allData = allData.concat(data);
            
            // Actualizar progreso
            const progress = Math.min((page * pageSize) / (page * pageSize + pageSize) * 100);
            progressBarInner.style.width = `${progress}%`;
            
            // Verificar si hay más datos
            hasMore = data.length === pageSize;
            page++;
            
            // Pequeña pausa para evitar bloquear el UI
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        if (allData.length === 0) {
            alert("No hay datos para exportar con los filtros seleccionados");
            throw new Error("No hay datos");
        }
        
        console.log("Datos recibidos:", allData);
        
        // Crear libro Excel
        progressBarInner.style.width = "95%";
        progressBarInner.textContent = "Preparando archivo...";
        
        const workbook = XLSX.utils.book_new();
        const headers = [
            "ID Comercio", "Nombre Comercio", "RIF Comercio", 
            "Número de Teléfono", "Nombre y Apellido del Solicitante",
            "Fecha de Solicitud", "Dirección", "Estado", "Municipio", "Parroquia",
            "Departamento"
        ];
        
        const worksheetData = [headers];
        
        // Procesar datos
        allData.forEach(item => {
            worksheetData.push([
                item["ID Comercio"] || "N/A",
                item["Nombre Comercio"] || "N/A",
                item["RIF Comercio"] || "N/A",
                item["Número de Teléfono"] || "N/A",
                item["Nombre y Apellido del Solicitante"] || "N/A",
                item["Fecha de Solicitud"] || "N/A",
                item["Dirección"] || "N/A",
                item["Estado"] || "N/A",
                item["Municipio"] || "N/A",
                item["Parroquia"] || "N/A",
                item["Departamento"] || "N/A"
            ]);
        });
        
        const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);
        
        // Aplicar estilos
        worksheet["!cols"] = headers.map(header => ({
            wch: Math.max(header.length, ...worksheetData.map(row => 
                (row[headers.indexOf(header)] || "").toString().length)) + 2
        }));
        
        if (!worksheet["!rows"]) worksheet["!rows"] = [];
        worksheet["!rows"][0] = { s: { font: { bold: true }, fill: { fgColor: { rgb: "FFD3D3D3" } } } };
        
        XLSX.utils.book_append_sheet(workbook, worksheet, "Solicitudes");
        
        // Generar nombre de archivo
        let fileName = "solicitudes";
        if (fechaInicio && fechaFin) {
            fileName += `_${fechaInicio}_a_${fechaFin}`;
        } else if (fechaInicio) {
            fileName += `_desde_${fechaInicio}`;
        } else if (fechaFin) {
            fileName += `_hasta_${fechaFin}`;
        }
        fileName += ".xlsx";
        
        XLSX.writeFile(workbook, fileName);
        
    } catch (error) {
        console.error("Error al generar Excel:", error);
        if (error.message !== "No hay datos") {
            alert(`Error al generar el archivo: ${error.message}`);
        }
    } finally {
        // Restaurar UI
        const boton = document.getElementById("exportarExcel");
        const progressBar = document.getElementById("exportProgress");
        
        boton.disabled = false;
        boton.innerHTML = '<i class="bi bi-file-earmark-excel me-2"></i> Exportar';
        progressBar.classList.add("d-none");
    }
}

// Inicialización cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", function() {
    setDefaultDates();
    document.getElementById("exportarExcel").addEventListener("click", generarExcel);
});