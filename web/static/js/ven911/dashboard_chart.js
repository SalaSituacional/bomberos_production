const ctx = document.getElementById('pie-chart-911');

new Chart(ctx, {
  type: 'bar', // Cambiado a 'bar'
  data: {
    labels: ['Red', 'Blue', 'Yellow', 'Green', 'Purple', 'Orange'],
    datasets: [{
      label: '# of Votes',
      data: [12, 19, 3, 5, 2, 3],
      borderWidth: 1
    }]
  },
  options: {
    indexAxis: 'y', // Configuración para barras invertidas
    plugins: {
      legend: {
        labels: {
          font: {
            size: 25 // Cambia este valor para ajustar el tamaño de los labels
          }
        }
      }
    },
    scales: {
      x: { // Cambiado de 'y' a 'x' para reflejar el eje horizontal
        beginAtZero: true
      }
    }
  }
});