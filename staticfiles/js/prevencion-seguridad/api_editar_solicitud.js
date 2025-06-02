
document.addEventListener("DOMContentLoaded", () => {
  // Aplicar estilos a los formularios generados por ModelForm
  function applyFormStyles() {
    // Aplicar estilos a los campos de formulario
    document
      .querySelectorAll('input:not([type="checkbox"]), textarea, select')
      .forEach((el) => {
        if (el.tagName === "SELECT") {
          el.classList.add("form-select");
        } else {
          el.classList.add("form-control");
        }
      });

    // Aplicar estilos a los checkboxes
    document.querySelectorAll('input[type="checkbox"]').forEach((el) => {
      el.classList.add("form-check-input");
      // Opcional: agregar un wrapper para mejor estilo
      const wrapper = document.createElement("div");
      wrapper.classList.add("form-check", "form-switch");
      el.parentNode.insertBefore(wrapper, el);
      wrapper.appendChild(el);
    });

    // Aplicar estilos a las etiquetas
    document.querySelectorAll("label").forEach((el) => {
      el.classList.add("form-label");
    });
  }

  applyFormStyles();
});

document.addEventListener('DOMContentLoaded', function() {
    // 1. Manejo de switches y fechas de vencimiento
    const switchDateMap = {
        'id_cedula_identidad': 'id_cedula_vencimiento',
        'id_rif_representante': 'id_rif_representante_vencimiento',
        'id_rif_comercio': 'id_rif_comercio_vencimiento',
        'id_documento_propiedad': 'id_documento_propiedad_vencimiento',
        'id_cedula_catastral': 'id_cedula_catastral_vencimiento'
    };

    // Función para manejar el estado de los campos de fecha
    function handleSwitchChange(switchId) {
        const dateFieldId = switchDateMap[switchId];
        if (!dateFieldId) return;
        
        const switchElement = document.getElementById(switchId);
        const dateField = document.getElementById(dateFieldId);
        
        if (switchElement && dateField) {
            dateField.disabled = !switchElement.checked;
            dateField.required = switchElement.checked;
            
            if (!switchElement.checked) {
                dateField.value = '';
            }
        }
    }

    // Inicializar y configurar listeners para los switches
    Object.keys(switchDateMap).forEach(switchId => {
        const switchElement = document.getElementById(switchId);
        if (switchElement) {
            // Configurar estado inicial
            handleSwitchChange(switchId);
            
            // Añadir event listener
            switchElement.addEventListener('change', () => handleSwitchChange(switchId));
        }
    });

    // 2. Manejo del campo referencia según método de pago
    const metodoPago = document.getElementById('id_metodo_pago');
    const referenciaInput = document.getElementById('id_referencia');
    
    if (metodoPago && referenciaInput) {
        metodoPago.addEventListener('change', updateReferenciaField);
        updateReferenciaField();
    }

    function updateReferenciaField() {
        if (metodoPago.value === 'Transferencia' || metodoPago.value === 'Deposito') {
            referenciaInput.disabled = false;
            referenciaInput.required = true;
        } else {
            referenciaInput.disabled = true;
            referenciaInput.required = false;
            referenciaInput.value = 'No Hay Referencia';
        }
    }
    
    metodoPago.addEventListener('change', updateReferenciaField);
    updateReferenciaField(); // Configurar estado inicial

    // 3. Validación de cédula
    const nacionalidad = document.getElementById('nacionalidad');
    const cedulaInput = document.getElementById('id_solicitante_cedula');
    const mensajeCedula = document.getElementById('cedula-mensaje');
    let cedulaValida = false;
    
    // Función para validar la cédula
    async function validarCedula() {
        const tipo = nacionalidad.value;
        const numero = cedulaInput.value.trim();
        const cedulaCompleta = `${tipo}-${numero}`;
        
        if (!numero) {
            mensajeCedula.style.display = 'none';
            cedulaValida = true;
            return;
        }
        
        try {
            mensajeCedula.textContent = 'Validando cédula...';
            mensajeCedula.style.display = 'block';
            mensajeCedula.className = 'form-text text-info';
            
            const response = await fetch(`/seguridad_prevencion/validar-cedula/?cedula=${encodeURIComponent(cedulaCompleta)}&comercio={{ form.instance.id_solicitud.id_comercio.id_comercio }}`);
            const data = await response.json();
            
            if (data.valido) {
                mensajeCedula.textContent = data.existe ? 
                    '✓ Cédula válida (registrada en ' + data.cantidad_comercios + ' comercios)' : 
                    '✓ Cédula válida';
                mensajeCedula.className = 'form-text text-success';
                cedulaValida = true;
            } else {
                mensajeCedula.textContent = data.mensaje || '❌ La cédula no es válida';
                mensajeCedula.className = 'form-text text-danger';
                cedulaValida = false;
            }
        } catch (error) {
            console.error('Error al validar cédula:', error);
            mensajeCedula.textContent = 'Error al validar la cédula';
            mensajeCedula.className = 'form-text text-danger';
            cedulaValida = false;
        }
    }
    
    // Event listeners para validación de cédula
    cedulaInput.addEventListener('blur', validarCedula);
    nacionalidad.addEventListener('change', function() {
        if (cedulaInput.value.trim()) {
            validarCedula();
        }
    });
    
    // Validar antes de enviar el formulario
    document.getElementById('formularioEditarSolicitudes').addEventListener('submit', function(e) {
        if (cedulaInput.value.trim() && !cedulaValida) {
            e.preventDefault();
            validarCedula();
            cedulaInput.focus();
        }
    });
});