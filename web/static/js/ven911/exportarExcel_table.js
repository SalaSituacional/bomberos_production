document.addEventListener('DOMContentLoaded', function() {
    const exportBtn = document.getElementById('exportarExcel');
    const mesInput = document.getElementById('mes_excel');
    
    exportBtn.addEventListener('click', function() {
        const mesSeleccionado = mesInput.value;
        
        if (!mesSeleccionado) {
            alert('Por favor seleccione un mes');
            return;
        }
        
        // URL correctamente ordenada
        const url = url_excel + `?mes=${encodeURIComponent(mesSeleccionado)}`;
        
        // Descargar el archivo
        const link = document.createElement('a');
        link.href = url;
        link.download = `servicios_${mesSeleccionado}.xlsx`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
});