document.addEventListener('DOMContentLoaded', function() {
    const inputFilter = document.querySelector('.inventario-filter input');
    const tableRows = document.querySelectorAll('tbody tr');
  
    inputFilter.addEventListener('input', function() {
      const searchTerm = this.value.toLowerCase();
  
      tableRows.forEach(row => {
        const itemName = row.querySelector('td:first-child').textContent.toLowerCase();
        const isVisible = itemName.includes(searchTerm);
        
        // Mostrar/ocultar fila según coincidencia
        row.style.display = isVisible ? '' : 'none';
        
        // Resaltar (amarillo) si hay coincidencia y término no está vacío
        row.querySelector('td:first-child').style.backgroundColor = 
          searchTerm && isVisible ? 'yellow' : '';
      });
    });
  });