    document.addEventListener('DOMContentLoaded', function() {
        const searchInput = document.getElementById('searchInput');
        const table = document.getElementById('inventary-insumos');
        const rows = table.getElementsByTagName('tr');

        searchInput.addEventListener('keyup', function() {
            const filter = searchInput.value.toLowerCase();

            for (let i = 1; i < rows.length; i++) { // Empezamos en 1 para saltar la fila de la cabecera (thead)
                const cells = rows[i].getElementsByTagName('td');
                const insumoCell = cells[0]; // La primera celda (índice 0) es la columna 'Insumo'

                if (insumoCell) {
                    const textValue = insumoCell.textContent || insumoCell.innerText;

                    if (textValue.toLowerCase().indexOf(filter) > -1) {
                        rows[i].style.display = ""; // Muestra la fila
                    } else {
                        rows[i].style.display = "none"; // Oculta la fila
                    }
                }
            }
        });
    });