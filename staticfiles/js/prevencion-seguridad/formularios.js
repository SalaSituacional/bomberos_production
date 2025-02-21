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

// Función para agregar mensajes de error
function showAdvertencia(input, message) {
  let errorSpan = input.nextElementSibling;
  if (!errorSpan || !errorSpan.classList.contains("warning-message")) {
    errorSpan = document.createElement("span");
    errorSpan.classList.add("warning-message");
    input.parentElement.appendChild(errorSpan);
  }
  errorSpan.innerText = message;
  errorSpan.style.display = "block";
}

// Función para eliminar mensajes de error
function clearAdvertencia(input) {
  let errorSpan = input.nextElementSibling;
  if (errorSpan && errorSpan.classList.contains("warning-message")) {
    errorSpan.style.display = "none";
  }
}

// Función para eliminar mensajes de error
function clearError(input) {
  let errorSpan = input.nextElementSibling;
  if (errorSpan && errorSpan.classList.contains("error-message")) {
    errorSpan.style.display = "none";
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const form = document.querySelector("form");
  const submitButton = document.querySelector(".registrar"); // Botón de enviar
  let timeoutId; // Variable para controlar el tiempo de espera antes de la petición

  document.getElementById("id_referencia").setAttribute("disabled", true);

  // Obtener parámetros de la URL
  const params = new URLSearchParams(window.location.search);
  // Obtener el valor de 'comercio_id'
  const comercioId = params.get("comercio_id");

  // Verificar si existe y usarlo
  if (comercioId) {
    document.getElementById("id_comercio").value = comercioId;
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

    cedulaInput.addEventListener("blur", function () {
      clearTimeout(timeoutId);

      timeoutId = setTimeout(() => {
        const cedula = cedulaInput.value.trim();
        const nacionalidad = document.getElementById("nacionalidad").value;
        const comercio = document.getElementById("id_comercio").value; // Obtener el comercio seleccionado
        const cedulaCompleta = `${nacionalidad}-${cedula}`;

        if (!cedula) {
          showError(cedulaInput, "⚠️ Ingresa la cédula.");
          return;
        }

        const cedulaPattern = /^[VE]-\d+$/;
        if (!cedulaPattern.test(cedulaCompleta)) {
          showError(
            cedulaInput,
            "⚠️ Formato inválido. Use V-12345678 o E-12345678."
          );
          return;
        }

        clearError(cedulaInput);

        fetchWithLoader(
          `/validar-cedula/?cedula=${cedulaCompleta}&comercio=${comercio}`
        )
          .then((response) => response)
          .then((data) => {
            if (data.existe) {
              if (!data.valido) {
                showError(cedulaInput, data.mensaje);
              } else {
                showAdvertencia(
                  cedulaInput,
                  `📌 La cédula está registrada en ${data.cantidad_comercios} comercio(s).`
                );
              }
            } else {
              console.log("✅ Cédula válida");
              clearError(cedulaInput);
              clearAdvertencia(cedulaInput);
            }
          })
          .catch((error) => console.error("Error:", error));
      }, 300);
    });

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
      showError(
        solicitanteNombre,
        "⚠️ Ingrese el Nombre y Apellido del Solicitante."
      );
      isValid = false;
    } else {
      clearError(solicitanteNombre);
    }

    // Validación de RIF del Representante Legal solo si el campo NO está deshabilitado
    if (!rifRepresentante.hasAttribute("disabled")) {
      if (!rifRepresentante.value) {
        showError(
          rifRepresentante,
          "⚠️ Ingrese el RIF del Representante Legal."
        );
        isValid = false;
      } else {
        clearError(rifRepresentante);
      }
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
      showError(
        numeroTelefono,
        "⚠️ El Numero de Telefono Solo debe Contener Numeros."
      );
      isValid = false;
    } else {
      clearError(numeroTelefono);
    }

    metodoPago.addEventListener("change", function () {
      if (
        metodoPago.value === "Transferencia" ||
        metodoPago.value === "Deposito"
      ) {
        referencia.removeAttribute("disabled");

        // Validación de fecha solicitud
        if (!referencia.value) {
          showError(referencia, "⚠️ Ingrese el Numero de Refererncia.");
          isValid = false;
        } else {
          clearError(referencia);
        }
      } else {
        referencia.setAttribute("disabled", true);
        clearError(referencia);
      }
    });

    // Activar o desactivar el botón de enviar
    submitButton.disabled = !isValid;
  }

  // Activar validaciones en tiempo real sin afectar a los checkbox
  document
    .querySelectorAll("input:not([type='checkbox']), select")
    .forEach((element) => {
      element.addEventListener("input", validateForm);
      element.addEventListener("change", validateForm);
    });

  // Función para manejar la activación de fechas según los checkboxes
  function toggleFechaVencimiento(checkboxId, fechaId) {
    const checkbox = document.getElementById(checkboxId);
    const fechaInput = document.getElementById(fechaId);

    checkbox.addEventListener("change", function () {
      fechaInput.disabled = !this.checked;
      if (!this.checked) {
        fechaInput.value = "";
        clearError(fechaInput);
      }
    });

    if (!checkbox.checked) {
      fechaInput.disabled = true;
      clearError(fechaInput);
    }
  }

  // Agregar selección de "V" o "E" para la cédula
  const cedulaInput = document.getElementById("id_solicitante_cedula");
  const cedulaContainer = cedulaInput.parentElement;
  const selectNacionalidad = document.createElement("select");

  selectNacionalidad.id = "nacionalidad";
  selectNacionalidad.innerHTML = `<option value="V">V</option><option value="E">E</option>`;
  selectNacionalidad.setAttribute("name", "nacionalidad");

  cedulaContainer.insertBefore(selectNacionalidad, cedulaInput);

  // Aplicar la función a cada checkbox-fecha
  toggleFechaVencimiento("id_cedula_identidad", "id_cedula_vecimiento");
  toggleFechaVencimiento("id_cedula_identidad", "id_solicitante_cedula");
  toggleFechaVencimiento("id_cedula_identidad", "nacionalidad");

  toggleFechaVencimiento(
    "id_rif_representante",
    "id_rif_representante_vencimiento"
  );
  toggleFechaVencimiento("id_rif_representante", "id_rif_representante_legal");

  toggleFechaVencimiento("id_rif_comercio", "id_rif_comercio_vencimiento");
  toggleFechaVencimiento(
    "id_cedula_catastral",
    "id_cedula_catastral_vencimiento"
  );
  toggleFechaVencimiento(
    "id_documento_propiedad",
    "id_documento_propiedad_vencimiento"
  );

  // Validar que solo haya números en la cédula
  cedulaInput.addEventListener("input", function () {
    this.value = this.value.replace(/\D/g, "");
  });
});

document.addEventListener("DOMContentLoaded", () => {
  const nombreInput = document.getElementById("id_nombre_comercio");
  const rifInput = document.getElementById("id_rif_empresarial");
  const botonAgregarComercio = document.getElementById(
    "boton-agregar-comercio"
  );
  let timeoutId;

  // Deshabilitar el botón al inicio
  botonAgregarComercio.setAttribute("disabled", true);

  // Función para formatear el nombre del comercio
  function formatearNombreComercio(nombre) {
    return nombre
      .toLowerCase()
      .replace(/\b\w/g, (char) => char.toUpperCase()) // Primera letra de cada palabra en mayúscula
      .replace(/\bC\.A\b/gi, "C.A.") // Mantener formato "C.A."
      .replace(/\bS\.A\b/gi, "S.A."); // Mantener formato "S.A."
  }

  // Función para validar los campos
  function validarCampos() {
    let nombre = nombreInput.value.trim();
    let rif = rifInput.value.trim();
    let valido = true;

    // Limpiar errores previos
    clearError(nombreInput);
    clearError(rifInput);

    if (!nombre) {
      showError(nombreInput, "⚠️ El nombre del comercio es obligatorio.");
      valido = false;
    } else {
      nombreInput.value = formatearNombreComercio(nombre);
    }

    if (!rif) {
      showError(rifInput, "⚠️ El RIF es obligatorio.");
      valido = false;
    }

    // Habilitar el botón solo si ambos campos son válidos
    botonAgregarComercio.disabled = !valido;
  }

  // Validar RIF en la base de datos al perder el foco
  rifInput.addEventListener("blur", () => {
    let rif = rifInput.value.trim();
    clearTimeout(timeoutId);

    if (!rif) return; // No ejecutar si el RIF está vacío

    timeoutId = setTimeout(async () => {
      try {
        const response = await fetchWithLoader(`/validar-rif/?rif=${rif}`);
        if (response.existe) {
          showError(
            rifInput,
            "❌ El RIF ya está registrado para otro comercio."
          );
          botonAgregarComercio.disabled = true;
        } else {
          clearError(rifInput);
          validarCampos(); // Volver a validar para habilitar el botón si todo está bien
        }
      } catch (error) {
        console.error("Error validando el RIF:", error);
      }
    }, 300);
  });

  // Validar campos al perder el foco
  nombreInput.addEventListener("blur", validarCampos);
});
