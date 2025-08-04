    // Obtiene el contexto del canvas para la gráfica, usando un nombre único
    const ctx911 = document.getElementById('bar-chart-horizontal-911').getContext('2d');
    let myChart2; // Variable para almacenar la instancia de la gráfica
    // Usamos un nombre único para la URL de la API para evitar conflictos
    const apiUrl911 = api_servicios_grafica_dia; // Asegúrate de que esta URL sea la correcta para tu API

    // Configuración común de la gráfica, usando un nombre único
    const chartConfig911 = {
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
        indexAxis: 'y', // Eje de índice para las barras (horizontal)
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
                title: { 
                    display: true, 
                    text: 'Tipo de Servicio', // Título del eje Y
                    font: { size: 18 } 
                }, 
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

    // Función para realizar fetch con loader
    async function fetchWithLoader(url) {
        showLoader(); // Muestra el loader antes de la petición
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } finally {
            hideLoader(); // Oculta el loader después de la petición (éxito o error)
        }
    }

    // Función única para cargar/actualizar datos de la gráfica
    async function loadChartData(day = null) {
        try {
            // Construye la URL de la API con el parámetro 'day' si se proporciona
            const url = day ? `${apiUrl911}?day=${day}` : apiUrl911; // Usamos apiUrl911 aquí
                                            
            const { labels, data } = await fetchWithLoader(url); // Llama a la API
            
            if (myChart2) { // Usamos myChart2 para esta instancia de la gráfica
                // Si la gráfica ya existe, actualiza sus datos
                myChart2.data.labels = labels;
                myChart2.data.datasets[0].data = data;
                myChart2.update(); // Actualiza la gráfica
            } else {
                // Si la gráfica no existe, la crea
                // Asegúrate de que ChartDataLabels esté importado y registrado si lo usas
                // <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.0.0"></script>
                Chart.register(ChartDataLabels); 
                chartConfig911.data.labels = labels; // Usamos chartConfig911 aquí
                chartConfig911.data.datasets[0].data = data; // Usamos chartConfig911 aquí
                myChart2 = new Chart(ctx911, chartConfig911); // Usamos ctx911 y chartConfig911 para crear la gráfica
            }
            
            // --- Lógica para el total de la gráfica ---
            const totalGrafica = data.reduce((sum, value) => sum + value, 0); // Suma todos los valores
            const totalGraficaElement = document.getElementById('total-servicios-grafica-day');
            if (totalGraficaElement) {
                totalGraficaElement.textContent = `(${totalGrafica})`; // Muestra el total
            }

            // Actualizar el título de la gráfica para reflejar el día
            const tituloGraficaPeriodoElement = document.getElementById('titulo-grafica-periodo-day');
            if (tituloGraficaPeriodoElement) {
                tituloGraficaPeriodoElement.textContent = day ? day : 'Total'; // Muestra el día o 'Total'
            }
            
        } catch (error) {
            console.error('Error al cargar los datos de la gráfica:', error);
            // Puedes mostrar un mensaje de error en la UI si lo deseas
            const totalGraficaElement = document.getElementById('total-servicios-grafica-day');
            if (totalGraficaElement) {
                totalGraficaElement.textContent = '(Error al cargar)';
            }
            const tituloGraficaPeriodoElement = document.getElementById('titulo-grafica-periodo-day');
            if (tituloGraficaPeriodoElement) {
                tituloGraficaPeriodoElement.textContent = 'Error';
            }
        }
    }

    // Función para manejar el filtrado por día
    function filterByDay() {
        const day = document.getElementById('day').value; // Obtiene el valor del input de fecha
        loadChartData(day); // Carga los datos para el día seleccionado
    }

    // Inicialización al cargar la página
    document.addEventListener('DOMContentLoaded', () => {
        // Obtiene la fecha actual en formato 'YYYY-MM-DD'
        const today = new Date().toISOString().slice(0, 10); 
        document.getElementById('day').value = today; // Establece la fecha actual como valor por defecto
        loadChartData(today); // Carga la gráfica con el día actual por defecto
    });
