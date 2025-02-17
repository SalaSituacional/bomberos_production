document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const submitButton = document.querySelector(".registrar"); // Botón de enviar

    document.getElementById("id_referencia").setAttribute("disabled", true)

    // Función para agregar mensajes de error
    function showError(input, message) {
        let errorSpan = input.nextElementSibling;
        if (!errorSpan || !errorSpan.classList.contains("error-message")) {
            errorSpan = document.createElement("span");
            errorSpan.classList.add("error-message");
            input.parentElement.appendChild(errorSpan);
        }
        errorSpan.innerText = message;
        errorSpan.style.display = "block";
    }

    // Función para eliminar mensajes de error
    function clearError(input) {
        let errorSpan = input.nextElementSibling;
        if (errorSpan && errorSpan.classList.contains("error-message")) {
            errorSpan.style.display = "none";
        }
    }

    // Función para validar los campos y activar/desactivar el botón de envío
    function validateForm() {
        let isValid = true;

        // Obtener valores
        let comercio = document.getElementById("id_comercio");
        let cedulaInput = document.getElementById("id_solicitante_cedula");
        let email = document.getElementById("id_correo_electronico");
        let pagoTasa = document.getElementById("id_pago_tasa");
        let fechaSolicitud = document.getElementById("id_fecha_solicitud");
        let horaSolicitud = document.getElementById("id_hora_solicitud");
        let tipoServicio = document.getElementById("id_tipo_servicio");
        let tipoRepresentante = document.getElementById("id_tipo_representante");
        let solicitanteNombre = document.getElementById("id_solicitante_nombre_apellido");
        let rifRepresentante = document.getElementById("id_rif_representante_legal");
        let direccion = document.getElementById("id_direccion");
        let estado = document.getElementById("id_estado");
        let municipio = document.getElementById("id_municipio");
        let parroquia = document.getElementById("id_parroquia");
        let numeroTelefono = document.getElementById("id_numero_telefono");
        let referencia = document.getElementById("id_referencia");
        let metodoPago = document.getElementById("id_metodo_pago");

        // Validación de comercio
        if (!comercio.value) {
            showError(comercio, "⚠️ Selecciona un comercio.");
            isValid = false;
        } else {
            clearError(comercio);
        }

        // Validación de cédula
        const cedulaPattern = /^[0-9]+$/;
        if (!cedulaInput.value) {
            showError(cedulaInput, "⚠️ Ingresa la cédula.");
            isValid = false;
        } else if (!cedulaPattern.test(cedulaInput.value)) {
            showError(cedulaInput, "⚠️ La cédula solo debe contener números.");
            isValid = false;
        } else {
            clearError(cedulaInput);
        }

        // Validación de correo
        const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!email.value) {
            showError(email, "⚠️ Ingresa un correo.");
            isValid = false;
        } else if (!emailPattern.test(email.value)) {
            showError(email, "⚠️ Formato de correo inválido.");
            isValid = false;
        } else {
            clearError(email);
        }

        // Validación de pago tasa
        if (!pagoTasa.value) {
            showError(pagoTasa, "⚠️ Ingresa el monto del pago.");
            isValid = false;
        } else {
            clearError(pagoTasa);
        }
        
        // Validación de fecha solicitud
        if (!fechaSolicitud.value) {
            showError(fechaSolicitud, "⚠️ Ingresa la Fecha de Solicitud.");
            isValid = false;
        } else {
            clearError(fechaSolicitud);
        }
        
        // Validación de hora solicitud
        if (!horaSolicitud.value) {
            showError(horaSolicitud, "⚠️ Ingresa la Hora de la Solicitud.");
            isValid = false;
        } else {
            clearError(horaSolicitud);
        }
        
        // Validación de fecha solicitud
        if (!tipoServicio.value) {
            showError(tipoServicio, "⚠️ Ingresa el Tipo de Servicio.");
            isValid = false;
        } else {
            clearError(tipoServicio);
        }
        
        // Validación de fecha solicitud
        if (!tipoRepresentante.value) {
            showError(tipoRepresentante, "⚠️ Ingresa el Tipo de Representante.");
            isValid = false;
        } else {
            clearError(tipoRepresentante);
        }
        
        // Validación de fecha solicitud
        if (!solicitanteNombre.value) {
            showError(solicitanteNombre, "⚠️ Ingrese el Nombre y Apellido del Solicitante.");
            isValid = false;
        } else {
            clearError(solicitanteNombre);
        }
        
        // Validación de fecha solicitud
        if (!rifRepresentante.value) {
            showError(rifRepresentante, "⚠️ Ingrese el RIF del Representante Legal.");
            isValid = false;
        } else {
            clearError(rifRepresentante);
        }
        
        // Validación de fecha solicitud
        if (!direccion.value) {
            showError(direccion, "⚠️ Ingrese la Direccion.");
            isValid = false;
        } else {
            clearError(direccion);
        }
        
        // Validación de fecha solicitud
        if (!estado.value) {
            showError(estado, "⚠️ Ingrese el Estado.");
            isValid = false;
        } else {
            clearError(estado);
        }
        
        // Validación de fecha solicitud
        if (!municipio.value) {
            showError(municipio, "⚠️ Ingrese el Municipio.");
            isValid = false;
        } else {
            clearError(municipio);
        }
        
        // Validación de fecha solicitud
        if (!parroquia.value) {
            showError(parroquia, "⚠️ Ingrese la Parroquia.");
            isValid = false;
        } else {
            clearError(parroquia);
        }
        
        
        
        // Validación de Metoodo de Pago
        if (!metodoPago.value) {
            showError(metodoPago, "⚠️ Ingrese el Metodo de Pago.");
            isValid = false;
        } else {
            clearError(metodoPago);
        }

        // Validación de cédula
        const telefonoPattern = /^[0-9]+$/;
        if (!numeroTelefono.value) {
            showError(numeroTelefono, "⚠️ Ingrese el Numero de Telefono.");
            isValid = false;
        } else if (!telefonoPattern.test(numeroTelefono.value)) {
            showError(numeroTelefono, "⚠️ El Numero de Telefono Solo debe Contener Numeros.");
            isValid = false;
        } else {
            clearError(numeroTelefono);
        }

        metodoPago.addEventListener("change", function () {
            if (metodoPago.value === "Transferencia" || metodoPago.value === "Deposito") {
                referencia.removeAttribute("disabled")

                // Validación de fecha solicitud
                if (!referencia.value) {
                    showError(referencia, "⚠️ Ingrese el Numero de Refererncia.");
                    isValid = false;
                } else {
                    clearError(referencia);
                }   
            } else{
                referencia.setAttribute("disabled", true)
                clearError(referencia);
            }
        })
   

        // Activar o desactivar el botón de enviar
        submitButton.disabled = !isValid;
    }

    // Activar validaciones en tiempo real
    document.querySelectorAll("input, select").forEach((element) => {
        element.addEventListener("input", validateForm);
        element.addEventListener("change", validateForm);
    });

    // Validar al enviar
    // form.addEventListener("submit", function (event) {
    //     if (!validateForm()) {
    //         event.preventDefault();
    //     }
    // });

    // Función para manejar la activación de fechas según los checkboxes
    function toggleFechaVencimiento(checkboxId, fechaId) {
        const checkbox = document.getElementById(checkboxId);
        const fechaInput = document.getElementById(fechaId);

        checkbox.addEventListener("change", function () {
            fechaInput.disabled = !this.checked;
            if (!this.checked) fechaInput.value = "";
        });

        if (!checkbox.checked) fechaInput.disabled = true;
    }

    // Aplicar la función a cada checkbox-fecha
    toggleFechaVencimiento("id_cedula_identidad", "id_cedula_vecimiento");
    toggleFechaVencimiento("id_rif_representante", "id_rif_representante_vencimiento");
    toggleFechaVencimiento("id_rif_comercio", "id_rif_comercio_vencimiento");
    toggleFechaVencimiento("id_cedula_catastral", "id_cedula_catastral_vencimiento");

    // Agregar selección de "V" o "E" para la cédula
    const cedulaInput = document.getElementById("id_solicitante_cedula");
    const cedulaContainer = cedulaInput.parentElement;
    const selectNacionalidad = document.createElement("select");

    selectNacionalidad.id = "nacionalidad";
    selectNacionalidad.innerHTML = `<option value="V">V</option><option value="E">E</option>`;
    selectNacionalidad.setAttribute("name", "nacionalidad");

    cedulaContainer.insertBefore(selectNacionalidad, cedulaInput);

    // Validar que solo haya números en la cédula
    cedulaInput.addEventListener("input", function () {
        this.value = this.value.replace(/\D/g, "");
    });

});