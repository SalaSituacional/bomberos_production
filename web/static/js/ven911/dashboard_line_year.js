// Obtiene el contexto del canvas para la nueva gráfica de línea anual, usando un nombre único
const ctxYearLine = document.getElementById('line-chart-911').getContext('2d');
let myYearChart; // Variable para almacenar la instancia de la gráfica anual
// URL de la API para la gráfica anual, utilizando el motor de plantillas de Django

// Configuración común de la gráfica anual, usando un nombre único y tipo 'line'
const chartConfigYear = {
    type: 'line', // Tipo de gráfica: línea
    data: {
        labels: [], // Etiquetas para el eje (¡Ahora serán los nombres de los servicios, no los meses!)
        datasets: [{
            label: 'Número de Servicios', // Etiqueta del conjunto de datos
            data: [], // Datos numéricos de los servicios
            fill: false, // No rellenar el área bajo la línea
            borderColor: 'rgb(189, 18, 18)', // Color de la línea
            backgroundColor: 'rgb(189, 18, 18)', // Color de fondo de los puntos
            borderWidth: 2, // Ancho de la línea
            tension: 0.4, // Curvatura de la línea
            pointRadius: 5, // Tamaño de los puntos
            pointBackgroundColor: 'rgb(189, 18, 18)', // Color de fondo de los puntos
            pointBorderColor: '#fff', // Color del borde de los puntos
            pointHoverRadius: 7, // Tamaño de los puntos al pasar el ratón
            pointHoverBackgroundColor: 'rgb(189, 18, 18)', // Color de los puntos al pasar el ratón
            pointHoverBorderColor: '#fff' // Color del borde de los puntos al pasar el ratón
        }]
    },
    options: {
        responsive: true, // La gráfica se adapta al tamaño del contenedor
        maintainAspectRatio: false, // No mantiene la relación de aspecto original
        scales: {
            x: { 
                title: { 
                    display: true, 
                    font: { size: 15 } 
                }, 
                ticks: { font: { size: 15 } } // Estilo de las etiquetas del eje X
            },
            y: { 
                beginAtZero: true, // El eje Y comienza en cero
                title: { 
                    display: true, 
                    text: 'Cantidad de Servicios', // Título del eje Y
                    font: { size: 15 } 
                }, 
                ticks: { font: { size: 15 } } // Estilo de las etiquetas del eje Y
            }
        },
        plugins: {
            legend: { 
                display: true, 
                position: 'top', // Posición de la leyenda
                labels: { font: { size: 15 } } // Estilo de las etiquetas de la leyenda
            },
            tooltip: { 
                callbacks: { 
                    label: ctx => `${ctx.dataset.label}: ${ctx.parsed.y}` // Formato del tooltip (para eje Y)
                } 
            },
            datalabels: { // Configuración del plugin ChartDataLabels para mostrar valores en los puntos
                color: '#000', // Color del texto de los datalabels
                anchor: 'end', // Posición del datalabel respecto al punto
                align: 'top', // Alineación del datalabel
                font: { size: 12, weight: 'bold' }, // Estilo de la fuente
                formatter: (value, context) => value // Formato del valor
            }
        }
    }
};

// Función para mostrar/ocultar un loader (simulado)
function showLoaderYear() {
    // Implementa tu lógica para mostrar un loader visual para esta gráfica
    // console.log("Mostrando loader para gráfica anual...");
}

function hideLoaderYear() {
    // Implementa tu lógica para ocultar el loader para esta gráfica
    // console.log("Ocultando loader para gráfica anual...");
}

// Función para realizar fetch con loader, específica para esta gráfica
async function fetchWithLoaderYear(url) {
    showLoaderYear(); // Muestra el loader antes de la petición
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } finally {
        hideLoaderYear(); // Oculta el loader después de la petición (éxito o error)
    }
}

// Función para cargar/actualizar datos de la gráfica anual
async function loadYearChartData(year = null) {
    try {
        // Construye la URL de la API con el parámetro 'year' si se proporciona
        const url = year ? `${apiUrlYear}?year=${year}` : apiUrlYear;
                                        
        const { labels, data } = await fetchWithLoaderYear(url); // Llama a la API
        
        if (myYearChart) {
            // Si la gráfica ya existe, actualiza sus datos
            myYearChart.data.labels = labels;
            myYearChart.data.datasets[0].data = data;
            myYearChart.update(); // Actualiza la gráfica
        } else {
            // Si la gráfica no existe, la crea
            Chart.register(ChartDataLabels); 
            chartConfigYear.data.labels = labels;
            chartConfigYear.data.datasets[0].data = data;
            myYearChart = new Chart(ctxYearLine, chartConfigYear);
        }
        
        // --- Lógica para el total de la gráfica ---
        const totalGrafica = data.reduce((sum, value) => sum + value, 0); // Suma todos los valores
        // Asumiendo que tienes un ID único para el total de esta gráfica anual
        const totalGraficaElement = document.getElementById('total-servicios-grafica_year'); 
        if (totalGraficaElement) {
            totalGraficaElement.textContent = `(${totalGrafica})`; // Muestra el total
        }

        // Actualizar el título de la gráfica para reflejar el año
        // Asumiendo que tienes un ID único para el título de esta gráfica anual
        const tituloGraficaPeriodoElement = document.getElementById('titulo-grafica-periodo_year');
        if (tituloGraficaPeriodoElement) {
            tituloGraficaPeriodoElement.textContent = year ? year : 'Total'; // Muestra el año o 'Total'
        }
        
    } catch (error) {
        console.error('Error al cargar los datos de la gráfica anual:', error);
        // Puedes mostrar un mensaje de error en la UI si lo deseas
        const totalGraficaElement = document.getElementById('total-servicios-grafica_year');
        if (totalGraficaElement) {
            totalGraficaElement.textContent = '(Error al cargar)';
        }
        const tituloGraficaPeriodoElement = document.getElementById('titulo-grafica-periodo_year');
        if (tituloGraficaPeriodoElement) {
            tituloGraficaPeriodoElement.textContent = 'Error';
        }
    }
}

// Función para manejar el filtrado por año
function filterByYear() {
    const year = document.getElementById('year-filter-input').value; // Obtiene el valor del input de año
    loadYearChartData(year); // Carga los datos para el año seleccionado
}

// Inicialización al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    const currentYear = new Date().getFullYear(); // Obtiene el año actual
    // Asumiendo que el input de año tiene el ID 'year-filter-input'
    const yearInput = document.getElementById('year-filter-input');
    if (yearInput) {
        yearInput.value = currentYear; // Establece el año actual como valor por defecto
    }
    loadYearChartData(currentYear); // Carga la gráfica con el año actual por defecto
});