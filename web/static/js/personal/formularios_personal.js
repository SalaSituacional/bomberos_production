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




// Codigo para Validar Campos Del Formulario
document.addEventListener('DOMContentLoaded', function() {
    // Elementos del formulario
    const form = document.querySelector('form.needs-validation');
    const cedulaInput = document.getElementById('id_cedula');
    const nombresInput = document.getElementById('id_nombres');
    const apellidosInput = document.getElementById('id_apellidos');
    const emailInput = document.getElementById('id_email');
    const telefonoInput = document.getElementById('id_telefono');
    const nroCuentaInput = document.getElementById('id_nro_cuenta');
    const nroRifInput = document.getElementById('id_nro_rif');
    const fechaNacimientoInput = document.getElementById('id_fecha_nacimiento');

    // Expresiones regulares para validación
    const regexCedula = /^(V|E|J|P|G)-\d{6,9}$/i;
    const regexSoloLetras = /^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$/;
    const regexEmail = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    const regexTelefono = /^\d{10,15}$/;
    const regexNroCuenta = /^\d+$/;
    const regexRif = /^[VEJPGvejpg]-\d{8,9}$/i;

    // Validar cédula
    function validarCedula() {
        const value = cedulaInput.value.trim();
        if (!value) return true; // No es requerido en el HTML, puedes cambiar esto
        
        if (!regexCedula.test(value)) {
            mostrarError(cedulaInput, 'Formato inválido. Ejemplo: V-12345678 o E-123456789');
            return false;
        }
        mostrarExito(cedulaInput);
        return true;
    }

    // Validar nombres y apellidos (solo letras)
    function validarSoloLetras(input, campo) {
        const value = input.value.trim();
        if (!value) {
            mostrarError(input, `El ${campo} es requerido`);
            return false;
        }
        
        if (!regexSoloLetras.test(value)) {
            mostrarError(input, `El ${campo} solo puede contener letras`);
            return false;
        }
        
        mostrarExito(input);
        return true;
    }

    // Validar email
    function validarEmail() {
        const value = emailInput.value.trim();
        if (!value) return true; // No es requerido
        
        if (!regexEmail.test(value)) {
            mostrarError(emailInput, 'Ingrese un email válido');
            return false;
        }
        mostrarExito(emailInput);
        return true;
    }

    // Validar teléfono
    function validarTelefono() {
        const value = telefonoInput.value.trim();
        if (!value) return true; // No es requerido
        
        if (!regexTelefono.test(value)) {
            mostrarError(telefonoInput, 'El teléfono debe contener solo números (10-15 dígitos)');
            return false;
        }
        mostrarExito(telefonoInput);
        return true;
    }

    // Validar número de cuenta
    function validarNroCuenta() {
        const value = nroCuentaInput.value.trim();
        if (!value) return true; // No es requerido
        
        if (!regexNroCuenta.test(value)) {
            mostrarError(nroCuentaInput, 'El número de cuenta debe contener solo números');
            return false;
        }
        mostrarExito(nroCuentaInput);
        return true;
    }

    // Validar RIF
    function validarRif() {
        const value = nroRifInput.value.trim();
        if (!value) return true; // No es requerido
        
        if (!regexRif.test(value)) {
            mostrarError(nroRifInput, 'Formato inválido. Ejemplo: V-123456789');
            return false;
        }
        mostrarExito(nroRifInput);
        return true;
    }

    // Validar fecha de nacimiento
    function validarFechaNacimiento() {
        const value = fechaNacimientoInput.value;
        if (!value) return true; // No es requerido
        
        const fechaNac = new Date(value);
        const hoy = new Date();
        const edadMinima = new Date();
        edadMinima.setFullYear(hoy.getFullYear() - 18); // Mínimo 18 años
        
        if (fechaNac > edadMinima) {
            mostrarError(fechaNacimientoInput, 'El personal debe ser mayor de 18 años');
            return false;
        }
        mostrarExito(fechaNacimientoInput);
        return true;
    }

    // Mostrar mensaje de error
    function mostrarError(input, mensaje) {
        input.classList.add('is-invalid2');
        input.classList.remove('is-valid');
        
        let feedback = input.nextElementSibling;
        if (!feedback || !feedback.classList.contains('invalid-feedback')) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            input.parentNode.insertBefore(feedback, input.nextSibling);
        }
        feedback.textContent = mensaje;
    }

    // Mostrar éxito (validación correcta)
    function mostrarExito(input) {
        input.classList.remove('is-invalid2');
        input.classList.add('is-valid');
        
        const feedback = input.nextElementSibling;
        if (feedback && feedback.classList.contains('invalid-feedback')) {
            feedback.textContent = '';
        }
    }

    // Validar todo el formulario
    function validarFormulario(e) {
        e.preventDefault();
        
        let valido = true;
        valido = validarCedula() && valido;
        valido = validarSoloLetras(nombresInput, 'nombre') && valido;
        valido = validarSoloLetras(apellidosInput, 'apellido') && valido;
        valido = validarEmail() && valido;
        valido = validarTelefono() && valido;
        valido = validarNroCuenta() && valido;
        valido = validarRif() && valido;
        valido = validarFechaNacimiento() && valido;
        
        if (valido) {
            form.submit();
        } else {
            // Desplazarse al primer error
            const primerError = document.querySelector('.is-invalid2');
            if (primerError) {
                primerError.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }
    }

    // Event listeners
    if (cedulaInput) cedulaInput.addEventListener('blur', validarCedula);
    if (nombresInput) nombresInput.addEventListener('blur', () => validarSoloLetras(nombresInput, 'nombre'));
    if (apellidosInput) apellidosInput.addEventListener('blur', () => validarSoloLetras(apellidosInput, 'apellido'));
    if (emailInput) emailInput.addEventListener('blur', validarEmail);
    if (telefonoInput) telefonoInput.addEventListener('blur', validarTelefono);
    if (nroCuentaInput) nroCuentaInput.addEventListener('blur', validarNroCuenta);
    if (nroRifInput) nroRifInput.addEventListener('blur', validarRif);
    if (fechaNacimientoInput) fechaNacimientoInput.addEventListener('change', validarFechaNacimiento);
    if (statusSelect) {
        statusSelect.addEventListener('change', actualizarFechaCese);
        actualizarFechaCese(); // Validar estado inicial
    }
    if (form) form.addEventListener('submit', validarFormulario);

    // Validación en tiempo real para algunos campos
    if (nombresInput) nombresInput.addEventListener('input', function() {
        this.value = this.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, '');
    });
    
    if (apellidosInput) apellidosInput.addEventListener('input', function() {
        this.value = this.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, '');
    });
    
    if (telefonoInput) telefonoInput.addEventListener('input', function() {
        this.value = this.value.replace(/\D/g, '');
    });
    
    if (nroCuentaInput) nroCuentaInput.addEventListener('input', function() {
        this.value = this.value.replace(/\D/g, '');
    });
    
    // Formateo automático para cédula y RIF
    if (cedulaInput) {
        cedulaInput.addEventListener('input', function(e) {
            // Eliminar cualquier carácter que no sea letra o número
            this.value = this.value.replace(/[^a-zA-Z0-9-]/g, '');
            
            // Convertir la letra a mayúscula
            if (this.value.length > 0) {
                this.value = this.value.charAt(0).toUpperCase() + this.value.slice(1);
            }
            
            // Asegurar que solo haya un guión
            const parts = this.value.split('-');
            if (parts.length > 2) {
                this.value = parts[0] + '-' + parts.slice(1).join('');
            }
        });
    }
    
    if (nroRifInput) {
        nroRifInput.addEventListener('input', function(e) {
            // Eliminar cualquier carácter que no sea letra o número
            this.value = this.value.replace(/[^a-zA-Z0-9-]/g, '');
            
            // Convertir la letra a mayúscula
            if (this.value.length > 0) {
                this.value = this.value.charAt(0).toUpperCase() + this.value.slice(1);
            }
            
            // Asegurar que solo haya un guión
            const parts = this.value.split('-');
            if (parts.length > 2) {
                this.value = parts[0] + '-' + parts.slice(1).join('');
            }
        });
    }
});


