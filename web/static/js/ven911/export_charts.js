function exportCanvasAsImage(canvasId, filename) {
    const canvas = document.getElementById(canvasId);

    if (!canvas) {
        console.error(`Error: No se encontró un elemento canvas con el ID "${canvasId}".`);
        alert(`No se pudo encontrar el gráfico para exportar. Por favor, asegúrese de que el ID del canvas sea correcto.`);
        return;
    }

    const imageDataURL = canvas.toDataURL('image/png');

    const downloadLink = document.createElement('a');
    downloadLink.href = imageDataURL;
    downloadLink.download = filename + '.png';

    document.body.appendChild(downloadLink);
    downloadLink.click();
    document.body.removeChild(downloadLink);

    // console.log(`El gráfico del canvas "${canvasId}" ha sido exportado como "${filename}.png".`);
}

// --- Asignar los Event Listeners a los botones ---
document.addEventListener('DOMContentLoaded', () => {
    const exportBarChartBtn = document.getElementById('export-bar-chart-btn');
    if (exportBarChartBtn) {
        exportBarChartBtn.addEventListener('click', () => {
            exportCanvasAsImage('bar-chart-911', 'grafico_barras_vertical');
        });
    } else {
        console.warn('El botón con ID "export-bar-chart-btn" no fue encontrado.');
    }

    const exportBarChartHorizontalBtn = document.getElementById('export-bar-chart-horizontal-btn');
    if (exportBarChartHorizontalBtn) {
        exportBarChartHorizontalBtn.addEventListener('click', () => {
            exportCanvasAsImage('bar-chart-horizontal-911', 'grafico_barras_horizontal');
        });
    } else {
        console.warn('El botón con ID "export-bar-chart-horizontal-btn" no fue encontrado.');
    }
});