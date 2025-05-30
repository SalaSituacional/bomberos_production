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
                title: { display: true, font: { size: 18 } },
                ticks: { font: { size: 18 } }
            },
            y: { 
                title: { display: true, font: { size: 18 } },
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