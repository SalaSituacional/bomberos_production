// Este script aplica estilos de Bootstrap a los formularios generados por ModelForm
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
    // Mapeo de switches a sus campos de fecha correspondientes
    const switchDateMap = {
        'id_cedula_identidad': 'id_cedula_vencimiento',
        'id_rif_representante': 'id_rif_representante_vencimiento',
        'id_rif_comercio': 'id_rif_comercio_vencimiento',
        'id_documento_propiedad': 'id_documento_propiedad_vencimiento',
        'id_cedula_catastral': 'id_cedula_catastral_vencimiento'
    };

    // Inicializar todos los campos de fecha como deshabilitados
    Object.values(switchDateMap).forEach(dateFieldId => {
        const dateField = document.getElementById(dateFieldId);
        if (dateField) {
            dateField.disabled = true;
            dateField.required = false;
        }
    });

    // Función para manejar el cambio en los switches
    function handleSwitchChange(event) {
        const switchId = event.target.id;
        const dateFieldId = switchDateMap[switchId];
        
        if (dateFieldId) {
            const dateField = document.getElementById(dateFieldId);
            if (dateField) {
                dateField.disabled = !event.target.checked;
                dateField.required = event.target.checked;
                
                // Si se desactiva el switch, limpiar el campo de fecha
                if (!event.target.checked) {
                    dateField.value = '';
                }
            }
        }
    }

    // Añadir event listeners a todos los switches
    Object.keys(switchDateMap).forEach(switchId => {
        const switchElement = document.getElementById(switchId);
        if (switchElement) {
            // Manejar el estado inicial
            handleSwitchChange({target: switchElement});
            
            // Añadir listener para cambios
            switchElement.addEventListener('change', handleSwitchChange);
        }
    });

    // Manejar también los switches que no tienen campo de fecha asociado
    const additionalSwitches = [
        'id_permiso_anterior',
        'id_registro_comercio',
        'id_carta_autorizacion',
        'id_plano_bomberil'
    ];
    
    additionalSwitches.forEach(switchId => {
        const switchElement = document.getElementById(switchId);
        if (switchElement) {
            // No necesitamos hacer nada especial con estos
        }
    });
});


document.addEventListener('DOMContentLoaded', function() {
    const metodoPagoSelect = document.getElementById('id_metodo_pago');
    const referenciaInput = document.getElementById('id_referencia');
    const referenciaGroup = referenciaInput.closest('.form-group');
    
    const metodosConReferencia = ['Transferencia', 'Deposito'];
    
    function actualizarEstadoReferencia() {
        const metodoSeleccionado = metodoPagoSelect.value;
        const requiereReferencia = metodosConReferencia.includes(metodoSeleccionado);
        
        // Actualizar estado del input
        referenciaInput.disabled = !requiereReferencia;
        referenciaInput.required = requiereReferencia;
        
        // Actualizar clases para estilos
        if (requiereReferencia) {
            referenciaGroup.classList.add('campo-activo');
            referenciaGroup.classList.remove('campo-inactivo');
            if (referenciaInput.value === 'No Hay Referencia') {
                referenciaInput.value = '';
            }
        } else {
            referenciaGroup.classList.add('campo-inactivo');
            referenciaGroup.classList.remove('campo-activo');
            referenciaInput.value = 'No Hay Referencia';
        }
    }
    
    // Configurar evento change
    metodoPagoSelect.addEventListener('change', actualizarEstadoReferencia);
    
    // Ejecutar al cargar para establecer estado inicial
    actualizarEstadoReferencia();
});

document.addEventListener('DOMContentLoaded', function() {
  const originalSelect = document.getElementById('id_id_solicitud');
  const searchInput = document.getElementById('comercio-search');
  const dropdown = document.getElementById('comercio-dropdown');
  
  // Extraer opciones del select original
  const options = Array.from(originalSelect.options).map(option => ({
    value: option.value,
    text: option.text,
    element: option
  })).filter(option => option.value !== '');
  
  // Función para filtrar opciones
  function filterOptions(searchTerm) {
    return options.filter(option => 
      option.text.toLowerCase().includes(searchTerm.toLowerCase())
    );
  }
  
  // Función para mostrar resultados
  function showResults(filteredOptions) {
    dropdown.innerHTML = '';
    
    if (filteredOptions.length === 0) {
      dropdown.innerHTML = '<div class="dropdown-item">No se encontraron resultados</div>';
      dropdown.style.display = 'block';
      return;
    }
    
    filteredOptions.forEach(option => {
      const item = document.createElement('div');
      item.className = 'dropdown-item';
      item.textContent = option.text;
      item.addEventListener('click', () => {
        searchInput.value = option.text;
        originalSelect.value = option.value;
        dropdown.style.display = 'none';
      });
      dropdown.appendChild(item);
    });
    
    dropdown.style.display = 'block';
  }
  
  // Evento de entrada en el buscador
  searchInput.addEventListener('input', function() {
    const searchTerm = this.value.trim();
    if (searchTerm.length > 0) {
      const filteredOptions = filterOptions(searchTerm);
      showResults(filteredOptions);
    } else {
      dropdown.style.display = 'none';
    }
  });
  
  // Cerrar dropdown al hacer clic fuera
  document.addEventListener('click', function(e) {
    if (!e.target.closest('.select-autocomplete')) {
      dropdown.style.display = 'none';
    }
  });
  
  // Mostrar todas las opciones al hacer clic en el input
  searchInput.addEventListener('focus', function() {
    if (this.value.trim() === '') {
      showResults(options);
    }
  });
  
  // Mantener sincronizado el valor seleccionado
  originalSelect.addEventListener('change', function() {
    const selectedOption = options.find(opt => opt.value === this.value);
    if (selectedOption) {
      searchInput.value = selectedOption.text;
    }
  });
  
  // Inicializar con el valor seleccionado si existe
  if (originalSelect.value) {
    const selectedOption = options.find(opt => opt.value === originalSelect.value);
    if (selectedOption) {
      searchInput.value = selectedOption.text;
    }
  }
});

document.addEventListener('DOMContentLoaded', function() {
    const cedulaInput = document.getElementById('id_solicitante_cedula');
    const comercioSelect = document.getElementById('id_id_solicitud');
    const formulario = document.querySelector('form');
    let cedulaValida = false;
    
    // Crear elemento para mensajes
    const mensajeError = document.createElement('div');
    mensajeError.className = 'mensaje-cedula';
    mensajeError.style.color = '#dc3545';
    mensajeError.style.marginTop = '5px';
    mensajeError.style.display = 'none';
    cedulaInput.parentNode.appendChild(mensajeError);
    
    async function validarCedula() {
        const cedula = cedulaInput.value.trim();
        const comercioId = comercioSelect.value;
        
        if (!cedula) {
            mensajeError.style.display = 'none';
            cedulaValida = true;  // Permitir enviar si no hay cédula
            return;
        }
        
        // Validar formato básico
        if (!cedula.startsWith('V-') && !cedula.startsWith('E-')) {
            mostrarError('Formato inválido. Use V-12345678 o E-12345678.');
            cedulaValida = false;
            return;
        }
        
        try {
            mensajeError.textContent = 'Validando cédula...';
            mensajeError.style.color = '#007bff';
            mensajeError.style.display = 'block';
            
            const response = await fetchWithLoader(`/seguridad_prevencion/validar-cedula/?cedula=${encodeURIComponent(cedula)}&comercio=${encodeURIComponent(comercioId)}`);
            const data = await response;
            
            if (!data.valido) {
                mostrarError(data.mensaje || '❌ La cédula no es válida para este comercio');
                cedulaValida = false;
            } else {
                mensajeError.textContent = data.existe ? 
                    '✓ Cédula válida (ya registrada en ' + data.cantidad_comercios + ' comercios)' : 
                    '✓ Cédula válida';
                mensajeError.style.color = '#28a745';
                cedulaValida = true;
            }
        } catch (error) {
            console.error('Error al validar cédula:', error);
            mostrarError('Error al validar la cédula. Intente nuevamente.');
            cedulaValida = false;
        }
    }
    
    function mostrarError(mensaje) {
        mensajeError.textContent = mensaje;
        mensajeError.style.color = '#dc3545';
        mensajeError.style.display = 'block';
    }
    
    // Eventos
    cedulaInput.addEventListener('blur', validarCedula);
    comercioSelect.addEventListener('change', function() {
        if (cedulaInput.value.trim()) validarCedula();
    });
    
    formulario.addEventListener('submit', async function(e) {
        if (cedulaInput.value.trim()) {
            if (!cedulaValida) await validarCedula();
            
            if (!cedulaValida) {
                e.preventDefault();
                cedulaInput.focus();
            }
        }
    });
});