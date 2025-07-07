// Generar Familiares Dinamicamente
document.addEventListener('DOMContentLoaded', function() {
    const container = document.getElementById('familiares-forms-container');
    const addButton = document.getElementById('add-familiar-btn');
    const totalForms = document.getElementById('id_familiares-TOTAL_FORMS');
    
    // Función para actualizar índices
    function updateFormIndices() {
        const forms = container.querySelectorAll('.dynamic-form');
        totalForms.value = forms.length;
        
        forms.forEach((form, index) => {
            // Actualizar IDs, names y for attributes
            form.querySelectorAll('input, select, textarea, label').forEach(element => {
                ['id', 'name', 'for'].forEach(attr => {
                    if (element.hasAttribute(attr)) {
                        element.setAttribute(
                            attr, 
                            element.getAttribute(attr)
                                .replace(/familiares-\d+-/, `familiares-${index}-`)
                        );
                    }
                });
            });
            
            // Actualizar el ID del formulario
            form.id = `familiares-${index}-form`;
        });
    }

    // Función para agregar nuevo formulario
    function addForm() {
        const formCount = parseInt(totalForms.value);
        const template = container.querySelector('.dynamic-form').cloneNode(true);
        
        // Limpiar valores y actualizar IDs
        template.querySelectorAll('input:not([type="hidden"]), select, textarea').forEach(input => {
            input.value = '';
            if (input.type === 'checkbox' || input.type === 'radio') {
                input.checked = false;
            }
        });
        
        // Asegurar que solo tenga el botón de eliminar (no el switch)
        const deleteSwitch = template.querySelector('.form-check');
        if (deleteSwitch) {
            deleteSwitch.remove();
        }
        
        // Agregar botón de eliminar
        const deleteBtn = template.querySelector('.remove-familiar-btn') || document.createElement('button');
        deleteBtn.type = 'button';
        deleteBtn.className = 'btn btn-danger btn-sm remove-familiar-btn';
        deleteBtn.innerHTML = '<i class="bi bi-trash"></i> Eliminar';
        deleteBtn.onclick = function() { this.closest('.dynamic-form').remove(); updateFormIndices(); };
        
        // Insertar el botón en la posición correcta
        const headerDiv = template.querySelector('.d-flex');
        if (!template.querySelector('.remove-familiar-btn')) {
            headerDiv.appendChild(deleteBtn);
        }
        
        // Agregar al contenedor
        container.appendChild(template);
        updateFormIndices();
    }

    // Manejar el cambio en los switches de eliminación
    container.addEventListener('change', function(e) {
        if (e.target && e.target.matches('input[name$="-DELETE"]')) {
            const formRow = e.target.closest('.dynamic-form').querySelector('.row');
            if (e.target.checked) {
                formRow.style.opacity = '0.5';
                formRow.style.pointerEvents = 'none';
            } else {
                formRow.style.opacity = '1';
                formRow.style.pointerEvents = 'auto';
            }
        }
    });

    // Event listeners
    addButton.addEventListener('click', addForm);
    
    // Inicializar índices
    updateFormIndices();
});





// Codigo para Activar o Desactivar la Seccion de Fecha del Cese
document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const statusSelect = document.getElementById('id_status');
    const fechaCeseContainer = document.getElementById('fechaCeseContainer');
    const fechaTerminacionInput = document.getElementById('fechaTerminacion');
    
    // Valores de estado que consideramos "activo"
    const estadosActivos = ['ACTIVO', 'Activo', '1', ''];  // Ajusta según tus valores reales
    
    // Función para mostrar/ocultar el campo de fecha
    function actualizarVisibilidadFecha() {
        if (!statusSelect || !fechaCeseContainer) return;
        
        const estadoSeleccionado = statusSelect.value;
        const mostrarFecha = !estadosActivos.includes(estadoSeleccionado);
        
        fechaCeseContainer.style.display = mostrarFecha ? 'block' : 'none';
        
        // Hacer el campo requerido solo si es visible
        if (fechaTerminacionInput) {
            fechaTerminacionInput.required = mostrarFecha;
        }
    }
    
    // Configurar el event listener
    if (statusSelect) {
        statusSelect.addEventListener('change', actualizarVisibilidadFecha);
        
        // Verificar el estado inicial al cargar la página
        actualizarVisibilidadFecha();
    }
});




