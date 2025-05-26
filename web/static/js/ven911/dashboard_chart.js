// const ctx = document.getElementById('bar-chart-911').getContext('2d');
// let myChart;
// url = api_servicios_grafica; // Asumiendo que api_servicios_grafica es una variable global con la URL de la API

// // Función para obtener datos con loader
// async function fetchWithLoader(url) {
//     try {
//         // Mostrar loader (implementa tu lógica aquí)
//         // document.getElementById('loader').style.display = 'block';
        
//         const response = await fetch(url);
//         if (!response.ok) throw new Error('Error en la respuesta');
//         return await response.json();
//     } catch (error) {
//         console.error('Error:', error);
//         throw error;
//     } finally {
//         // Ocultar loader (implementa tu lógica aquí)
//         // document.getElementById('loader').style.display = 'none';
//     }
// }

// // Función principal para obtener y mostrar datos de la gráfica
// async function obtenerDatosGrafica(month = null) {
//     try {
//         let url = api_servicios_grafica;
//         if (month) {
//             url += `?month=${month}`;
//         }

//         const chartData = await fetchWithLoader(url);

//         if (myChart) {
//             myChart.destroy();
//         }

//         Chart.register(ChartDataLabels);

//         myChart = new Chart(ctx, {
//             type: 'bar',
//             data: {
//                 labels: chartData.labels,
//                 datasets: [{
//                     label: 'Número de Servicios',
//                     data: chartData.data,
//                     backgroundColor: [
//                         'rgba(75, 192, 192, 0.8)',
//                         'rgba(153, 102, 255, 0.8)',
//                         'rgba(255, 159, 64, 0.8)',
//                         'rgba(54, 162, 235, 0.8)',
//                         'rgba(255, 99, 132, 0.8)',
//                         'rgba(201, 203, 207, 0.8)',
//                         'rgba(255, 205, 86, 0.8)',
//                         'rgba(192, 75, 75, 0.8)',
//                         'rgba(75, 75, 192, 0.8)',
//                         'rgba(192, 192, 75, 0.8)'
//                     ],
//                     borderColor: [
//                         'rgba(75, 192, 192, 1)',
//                         'rgba(153, 102, 255, 1)',
//                         'rgba(255, 159, 64, 1)',
//                         'rgba(54, 162, 235, 1)',
//                         'rgba(255, 99, 132, 1)',
//                         'rgba(201, 203, 207, 1)',
//                         'rgba(255, 205, 86, 1)',
//                         'rgba(192, 75, 75, 1)',
//                         'rgba(75, 75, 192, 1)',
//                         'rgba(192, 192, 75, 1)'
//                     ],
//                     borderWidth: 1
//                 }]
//             },
//             options: {
//                 indexAxis: 'y',
//                 responsive: true,
//                 maintainAspectRatio: false,
//                 scales: {
//                     x: {
//                         beginAtZero: true,
//                         title: {
//                             display: true,
//                             text: 'Cantidad de Servicios',
//                             font: { size: 16 }
//                         },
//                         ticks: { font: { size: 14 } }
//                     },
//                     y: {
//                         title: {
//                             display: true,
//                             text: 'Tipo de Servicio',
//                             font: { size: 16 }
//                         },
//                         ticks: { font: { size: 16 } }
//                     }
//                 },
//                 plugins: {
//                     legend: {
//                         display: true,
//                         position: 'top',
//                         labels: { font: { size: 16 } }
//                     },
//                     tooltip: {
//                         callbacks: {
//                             label: function(context) {
//                                 return `${context.dataset.label || ''}: ${context.parsed.x || ''}`;
//                             }
//                         }
//                     },
//                     datalabels: {
//                         color: '#FFFFFF',
//                         anchor: 'center',
//                         align: 'start',
//                         offset: 4,
//                         font: { size: 14, weight: 'bold' },
//                         formatter: function(value) { return value; }
//                     }
//                 }
//             }
//         });

//     } catch (error) {
//         console.error('Error al obtener datos de la gráfica:', error);
//         // Mostrar mensaje de error al usuario si es necesario
//     }
// }

// // Función para filtrar por mes
// function filtrarPorMes() {
//     const monthValue = document.getElementById('month').value;
//     obtenerDatosGrafica(monthValue);
// }

// // Inicializar gráfica al cargar la página
// document.addEventListener('DOMContentLoaded', function() {
//     // Establecer mes actual por defecto
//     const currentDate = new Date();
//     const currentMonth = currentDate.toISOString().slice(0, 7);
//     document.getElementById('month').value = currentMonth;
    
//     // Cargar datos iniciales
//     obtenerDatosGrafica(currentMonth);
// });

const ctx = document.getElementById('bar-chart-911').getContext('2d');
let myChart;
const apiUrl = api_servicios_grafica; // Asumiendo que api_servicios_grafica es una variable global con la URL de la API
// Configuración común de la gráfica
const chartConfig = {
    type: 'bar',
    data: {
        labels: [],
        datasets: [{
            label: 'Número de Servicios',
            data: [],
            backgroundColor: [
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
            borderWidth: 1
        }]
    },
    options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        scales: {
            x: { 
                beginAtZero: true, 
                title: { display: true, text: 'Cantidad de Servicios', font: { size: 18 } },
                ticks: { font: { size: 18 } }
            },
            y: { 
                title: { display: true, text: 'Tipo de Servicio', font: { size: 18 } },
                ticks: { font: { size: 18 } }
            }
        },
        plugins: {
            legend: { display: true, position: 'top', labels: { font: { size: 18 } } },
            tooltip: { callbacks: { label: ctx => `${ctx.dataset.label}: ${ctx.parsed.x}` } },
            datalabels: { color: '#FFFFFF', anchor: 'center', align: 'start', font: { size: 18, weight: 'bold' } }
        }
    }
};

// Función única para cargar/actualizar datos
async function loadChartData(month = null) {
    try {
        const url = month ? `${apiUrl}?month=${month}` : apiUrl;
        const response = await fetchWithLoader(url);
                
        const { labels, data } = await response;
        
        if (myChart) {
            myChart.data.labels = labels;
            myChart.data.datasets[0].data = data;
            myChart.update();
        } else {
            Chart.register(ChartDataLabels);
            chartConfig.data.labels = labels;
            chartConfig.data.datasets[0].data = data;
            myChart = new Chart(ctx, chartConfig);
        }
        
        // Actualizar el input de mes si se proporcionó
        if (month) document.getElementById('month').value = month;
        
    } catch (error) {
        console.error('Error:', error);
        // Aquí puedes mostrar un mensaje al usuario
    }
}

// Función para manejar el filtrado
function filterByMonth() {
    const month = document.getElementById('month').value;
    loadChartData(month);
}

// Inicialización al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    const currentMonth = new Date().toISOString().slice(0, 7);
    document.getElementById('month').value = currentMonth;
    loadChartData(currentMonth);
});