// Obtiene el contexto del canvas para la gráfica de barras mensual, usando un nombre único
const ctxMonthBar = document.getElementById('bar-chart-911').getContext('2d');
let myMonthChart; // Variable para almacenar la instancia de la gráfica mensual
const apiUrlMonth = api_servicios_grafica; // Asumiendo que api_servicios_grafica es una variable global con la URL de la API

// Configuración común de la gráfica mensual, usando un nombre único
const chartConfigMonth = {
    type: 'bar', // Tipo de gráfica: barras
    data: {
        labels: [], // Etiquetas para el eje (nombres de servicios)
        datasets: [{
            label: 'Número de Servicios', // Etiqueta del conjunto de datos
            data: [], // Datos numéricos de los servicios
            backgroundColor: [ // Colores de fondo para las barras
                'rgba(75, 192, 192, 0.8)',
                'rgba(153, 102, 255, 0.8)',
                'rgba(255, 159, 64, 0.8)',
                'rgba(54, 162, 235, 0.8)',
                'rgba(255, 99, 132, 0.8)',
                'rgba(201, 203, 207, 0.8)',
                'rgba(255, 205, 86, 0.8)',
                'rgba(192, 75, 75, 0.8)',
                'rgba(75, 75, 192, 0.8)',
                'rgba(192, 192, 75, 0.8)'
            ],
            borderWidth: 1 // Ancho del borde de las barras
        }]
    },
    options: {
        indexAxis: 'y', // Eje de índice para las barras (vertical)
        responsive: true, // La gráfica se adapta al tamaño del contenedor
        maintainAspectRatio: false, // No mantiene la relación de aspecto original
        scales: {
            x: { 
                beginAtZero: true, // El eje X comienza en cero
                title: { 
                    display: true, 
                    text: 'Cantidad de Servicios', // Título del eje X
                    font: { size: 18 } 
                }, 
                ticks: { font: { size: 18 } } // Estilo de las etiquetas del eje X
            },
            y: { 
                // title: { display: true, text: 'Tipo de Servicio', font: { size: 18 } }, // Título del eje Y (comentado en tu original)
                ticks: { font: { size: 18 } } // Estilo de las etiquetas del eje Y
            }
        },
        plugins: {
            legend: { 
                display: true, 
                position: 'top', // Posición de la leyenda
                labels: { font: { size: 18 } } // Estilo de las etiquetas de la leyenda
            },
            tooltip: { 
                callbacks: { 
                    label: ctx => `${ctx.dataset.label}: ${ctx.parsed.x}` // Formato del tooltip
                } 
            },
            datalabels: { // Configuración del plugin ChartDataLabels para mostrar valores en las barras
                color: '#FFFFFF', 
                anchor: 'center', 
                align: 'start', 
                font: { size: 18, weight: 'bold' } 
            }
        }
    }
};

// Función para mostrar/ocultar un loader (simulado)
function showLoaderMonth() {
    // Implementa tu lógica para mostrar un loader visual para esta gráfica
    // console.log("Mostrando loader para gráfica mensual...");
}

function hideLoaderMonth() {
    // Implementa tu lógica para ocultar el loader para esta gráfica
    // console.log("Ocultando loader para gráfica mensual...");
}

// Función para realizar fetch con loader, específica para esta gráfica
async function fetchWithLoaderMonth(url) {
    showLoaderMonth(); // Muestra el loader antes de la petición
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } finally {
        hideLoaderMonth(); // Oculta el loader después de la petición (éxito o error)
    }
}

// Función única para cargar/actualizar datos de la gráfica mensual
async function loadMonthChartData(month = null) {
    try {
        // Construye la URL de la API con el parámetro 'month' si se proporciona
        const url = month ? `${apiUrlMonth}?month=${month}` : apiUrlMonth;
                                        
        const { labels, data } = await fetchWithLoaderMonth(url); // Llama a la API
        
        if (myMonthChart) {
            // Si la gráfica ya existe, actualiza sus datos
            myMonthChart.data.labels = labels;
            myMonthChart.data.datasets[0].data = data;
            myMonthChart.update(); // Actualiza la gráfica
        } else {
            // Si la gráfica no existe, la crea
            // Asegúrate de que ChartDataLabels esté importado y registrado si lo usas
            // <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.0.0"></script>
            Chart.register(ChartDataLabels); 
            chartConfigMonth.data.labels = labels;
            chartConfigMonth.data.datasets[0].data = data;
            myMonthChart = new Chart(ctxMonthBar, chartConfigMonth);
        }
        
        // --- Lógica para el total de la gráfica ---
        const totalGrafica = data.reduce((sum, value) => sum + value, 0); // Suma todos los valores
        // Asumiendo que tienes un ID único para el total de esta gráfica mensual
        const totalGraficaElement = document.getElementById('total-servicios-grafica_month'); 
        if (totalGraficaElement) {
            totalGraficaElement.textContent = `(${totalGrafica})`; // Muestra el total
        }

        // Actualizar el título de la gráfica para reflejar el mes
        // Asumiendo que tienes un ID único para el título de esta gráfica mensual
        const tituloGraficaPeriodoElement = document.getElementById('titulo-grafica-periodo_month');
        if (tituloGraficaPeriodoElement) {
            tituloGraficaPeriodoElement.textContent = month ? month : 'Total'; // Muestra el mes o 'Total'
        }
        
    } catch (error) {
        console.error('Error al cargar los datos de la gráfica mensual:', error);
        // Puedes mostrar un mensaje de error en la UI si lo deseas
        const totalGraficaElement = document.getElementById('total-servicios-grafica_month');
        if (totalGraficaElement) {
            totalGraficaElement.textContent = '(Error al cargar)';
        }
        const tituloGraficaPeriodoElement = document.getElementById('titulo-grafica-periodo_month');
        if (tituloGraficaPeriodoElement) {
            tituloGraficaPeriodoElement.textContent = 'Error';
        }
    }
}

// Función para manejar el filtrado por mes
function filterByMonthChart() {
    const month = document.getElementById('month').value; // Obtiene el valor del input de mes
    loadMonthChartData(month); // Carga los datos para el mes seleccionado
}

// Inicialización al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    const currentMonth = new Date().toISOString().slice(0, 7); // Formato 'YYYY-MM'
    // Asumiendo que el input de mes tiene el ID 'month'
    const monthInput = document.getElementById('month');
    if (monthInput) {
        monthInput.value = currentMonth; // Establece el mes actual como valor por defecto
    }
    loadMonthChartData(currentMonth); // Carga la gráfica con el mes actual por defecto
});
