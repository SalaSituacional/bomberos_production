document.addEventListener('DOMContentLoaded', function() {
    const inputFilter = document.querySelector('.inventario-filter input');
    const tableRows = document.querySelectorAll('.div-responsive-table tbody tr');
  
    inputFilter.addEventListener('input', function() {
      const searchTerm = this.value.toLowerCase().trim(); // trim() para eliminar espacios en blanco
  
      tableRows.forEach(row => {
        // Obtenemos el texto de la celda de Unidad (primera columna)
        const unidadText = row.querySelector('td:first-child').textContent.toLowerCase();
        const isVisible = unidadText.includes(searchTerm);
        
        // Mostrar/ocultar fila según coincidencia
        row.style.display = isVisible ? '' : 'none';
        
        // Resaltar la celda de Unidad si hay coincidencia
        row.querySelector('td:first-child').style.backgroundColor = 
          searchTerm && isVisible ? 'yellow' : '';
      });
    });
  });