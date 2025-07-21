document.addEventListener('DOMContentLoaded', function() {
    const checkboxes = document.querySelectorAll('.herramienta-checkbox:not(:disabled)');
    
    checkboxes.forEach(checkbox => {
        const toolId = checkbox.dataset.herramientaId;
        const cantidadInput = document.querySelector(`.cantidad-input[data-herramienta-id="${toolId}"]`);
        
        checkbox.addEventListener('change', function() {
            cantidadInput.disabled = !this.checked;
            if (!this.checked) {
                cantidadInput.value = 1;
            }
        });
        
        // Habilitar inicialmente si está marcado (en caso de error de validación)
        if (checkbox.checked) {
            cantidadInput.disabled = false;
        }
    });
});