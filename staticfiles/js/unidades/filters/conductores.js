document.addEventListener('DOMContentLoaded', function() {
    const filterInput = document.getElementById('filterid');
    const tableBody = document.getElementById('conductoresBody');
    
    filterInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase().trim();
        const rows = tableBody.getElementsByTagName('tr');
        
        Array.from(rows).forEach(row => {
            const nameCell = row.cells[0]; // Primera celda (Nombre)
            const nameText = nameCell.textContent.toLowerCase();
            const isVisible = nameText.includes(searchTerm);
            
            // Mostrar/ocultar fila
            row.style.display = isVisible ? '' : 'none';
            
            // Remover cualquier resaltado previo (corregí el nombre de la clase)
            nameCell.classList.remove('highlight');
            
            // Aplicar resaltado amarillo si hay coincidencia
            if (searchTerm && isVisible) {
                nameCell.classList.add('highlight');
            }
        });
    });
});