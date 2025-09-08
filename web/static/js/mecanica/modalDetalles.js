document.addEventListener('DOMContentLoaded', function() {
    // Seleccionar todas las filas de la tabla (excluyendo el encabezado)
    const filas = document.querySelectorAll('#tabla-herramientas tbody tr');
    
    // Obtener referencia al modal
    const modal = new bootstrap.Modal(document.getElementById('detalleHerramientaModal'));
    
    // Modificar la parte donde se llena el modal para manejar el estado con colores
    const modalEstado = document.getElementById('modal-estado');
    
    // Sobrescribir la función que llena el modal para manejar el estado con colores
    const fillModal = function(estado) {
        // Limpiar contenido previo
        modalEstado.innerHTML = '';
        
        // Crear badge según el estado
        const badge = document.createElement('span');
        badge.className = 'badge';
        
        switch(estado) {
            case 'Bueno':
                badge.classList.add('bg-success', 'text-light');
                break;
            case 'Regular':
                badge.classList.add('bg-warning', 'text-dark');
                break;
            case 'Malo':
            case 'Dañado':
                badge.classList.add('bg-danger', 'text-light');
                break;
            default:
                badge.classList.add('bg-secondary', 'text-light');
        }
        
        badge.textContent = estado;
        modalEstado.appendChild(badge);
    };

    // Agregar evento click a cada fila
    filas.forEach(fila => {
        fila.addEventListener('click', function(e) {
            // Prevenir que se active si se hizo clic en un enlace de acción
            if (e.target.tagName === 'A' || e.target.closest('a')) {
                return;
            }
            
            // Obtener los datos de la herramienta desde los atributos data
            const herramientaId = this.getAttribute('data-herramienta-id');
            const nombre = this.getAttribute('data-nombre');
            const serial = this.getAttribute('data-serial');
            const categoria = this.getAttribute('data-categoria');
            const cantidad = this.getAttribute('data-cantidad');
            const estado = this.getAttribute('data-estado');
            const asignadas = this.getAttribute('data-asignadas');
            const disponibles = this.getAttribute('data-disponibles');
            
            // Llenar el modal con los datos
            document.getElementById('modal-nombre').textContent = nombre;
            document.getElementById('modal-serial').textContent = serial;
            document.getElementById('modal-categoria').textContent = categoria;
            document.getElementById('modal-cantidad').textContent = cantidad;
            
            // Usar la nueva función para el estado
            fillModal(estado);
            
            document.getElementById('modal-asignadas').textContent = asignadas > 0 ? 
                `${asignadas} asignada(s)` : 'Ninguna';
            document.getElementById('modal-disponibles').textContent = disponibles > 0 ? 
                `${disponibles} disponible(s)` : 'Agotadas';
            
            // Mostrar el modal
            modal.show();
        });
    });
});