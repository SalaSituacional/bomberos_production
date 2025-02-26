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






















  let comercioSelect = document.getElementById("id_comercio");
  let cedulaInput = document.getElementById("id_solicitante_cedula");
  let emailInput = document.getElementById("id_correo_electronico");
  let pagoTasaInput = document.getElementById("id_pago_tasa");
  let fechaSolicitudInput = document.getElementById("id_fecha_solicitud");
  let horaSolicitudInput = document.getElementById("id_hora_solicitud");
  let tipoServicioInput = document.getElementById("id_tipo_servicio");
  let tipoRepresentanteInput = document.getElementById("id_tipo_representante");
  let solicitanteNombreInput = document.getElementById(
    "id_solicitante_nombre_apellido"
  );
  let rifRepresentanteInput = document.getElementById(
    "id_rif_representante_legal"
  );
  let direccionInput = document.getElementById("id_direccion");
  let estadoInput = document.getElementById("id_estado");
  let municipioInput = document.getElementById("id_municipio");
  let parroquiaInput = document.getElementById("id_parroquia");
  let numeroTelefonoInput = document.getElementById("id_numero_telefono");
  let referenciaInput = document.getElementById("id_referencia");
  let metodoPagoInput = document.getElementById("id_metodo_pago");

  let cedulaValida = false; // 🔹 Variable para controlar si la cédula es válida

  function showError(input, message) {
    let errorContainer = input.nextElementSibling;
    if (
      !errorContainer ||
      !errorContainer.classList.contains("error-message")
    ) {
      errorContainer = document.createElement("span");
      errorContainer.classList.add("error-message");
      input.parentNode.insertBefore(errorContainer, input.nextSibling);
    }
    errorContainer.textContent = message;
    input.classList.add("input-error");
  }

  function clearError(input) {
    let errorContainer = input.nextElementSibling;
    if (errorContainer && errorContainer.classList.contains("error-message")) {
      errorContainer.textContent = "";
    }
    input.classList.remove("input-error");
  }

  function validateForm() {
    let isValid = true;

    function checkField(input, message) {
      if (!input.value.trim()) {
        showError(input, message);
        isValid = false;
      } else {
        clearError(input);
      }
    }

    checkField(emailInput, "⚠️ Ingresa un correo.");
    checkField(pagoTasaInput, "⚠️ Ingresa el monto del pago.");
    checkField(fechaSolicitudInput, "⚠️ Ingresa la Fecha de Solicitud.");
    checkField(horaSolicitudInput, "⚠️ Ingresa la Hora de la Solicitud.");
    checkField(tipoServicioInput, "⚠️ Ingresa el Tipo de Servicio.");
    checkField(tipoRepresentanteInput, "⚠️ Ingresa el Tipo de Representante.");
    checkField(
      solicitanteNombreInput,
      "⚠️ Ingrese el Nombre y Apellido del Solicitante."
    );
    checkField(direccionInput, "⚠️ Ingrese la Dirección.");
    checkField(estadoInput, "⚠️ Ingrese el Estado.");
    checkField(municipioInput, "⚠️ Ingrese el Municipio.");
    checkField(parroquiaInput, "⚠️ Ingrese la Parroquia.");
    checkField(numeroTelefonoInput, "⚠️ Ingrese el Número de Teléfono.");
    checkField(metodoPagoInput, "⚠️ Ingrese el Método de Pago.");

    if (
      metodoPagoInput.value === "Transferencia" ||
      metodoPagoInput.value === "Deposito"
    ) {
      checkField(referenciaInput, "⚠️ Ingrese el Número de Referencia.");
    } else {
      referenciaInput.setAttribute("disabled", true);
      clearError(referenciaInput);
    }

    if (!rifRepresentanteInput.hasAttribute("disabled")) {
      checkField(
        rifRepresentanteInput,
        "⚠️ Ingrese el RIF del Representante Legal."
      );
    }

    // 🔹 Se activa el botón solo si la cédula es válida Y todos los campos están completos
    submitButton.disabled = !(isValid && cedulaValida);
  }

  function validarCedulaYComercio() {
    clearTimeout(timeoutId);

    timeoutId = setTimeout(() => {
      const cedula = cedulaInput.value.trim();
      const nacionalidad = document.getElementById("nacionalidad").value;
      const comercio = comercioSelect.value.trim();
      const cedulaCompleta = `${nacionalidad}-${cedula}`;

      if (!cedula) {
        showError(cedulaInput, "⚠️ Ingresa la cédula.");
        cedulaValida = false;
        validateForm();
        return;
      }

      const cedulaPattern = /^[VE]-\d+$/;
      if (!cedulaPattern.test(cedulaCompleta)) {
        showError(
          cedulaInput,
          "⚠️ Formato inválido. Use V-12345678 o E-12345678."
        );
        cedulaValida = false;
        validateForm();
        return;
      }

      clearError(cedulaInput);

      if (!comercio) {
        showError(comercioSelect, "⚠️ Selecciona un comercio.");
        cedulaValida = false;
        validateForm();
        return;
      }

      if (comercio && cedula) {
        fetchWithLoader(
          `/validar-cedula/?cedula=${cedulaCompleta}&comercio=${comercio}`
        )
          .then((response) => response)
          .then((data) => {
            if (data.error) {
              showError(cedulaInput, data.error);
              cedulaValida = false;
            } else if (data.existe && !data.valido) {
              showError(cedulaInput, data.mensaje);
              cedulaValida = false;
            } else {
              clearError(cedulaInput);
              cedulaValida = true;
              if (data.existe) {
                showError(
                  cedulaInput,
                  `📌 La cédula está registrada en ${data.cantidad_comercios} comercio(s).`
                );
              }
            }
            validateForm(); // 🔹 Se revalida el formulario para actualizar el botón
          })
          .catch((error) => {
            console.error("Error:", error);
            showError(cedulaInput, "⚠️ Error al validar la cédula.");
            cedulaValida = false;
            validateForm();
          });
      }
    }, 300);
  }

  // Escucha cambios en la cédula
  cedulaInput.addEventListener("blur", validarCedulaYComercio);

  // Escucha cambios en el comercio
  comercioSelect.addEventListener("change", validarCedulaYComercio);

  // Validaciones generales en otros campos
  emailInput.addEventListener("input", validateForm);
  pagoTasaInput.addEventListener("input", validateForm);
  fechaSolicitudInput.addEventListener("input", validateForm);
  horaSolicitudInput.addEventListener("input", validateForm);
  tipoServicioInput.addEventListener("change", validateForm);
  tipoRepresentanteInput.addEventListener("change", validateForm);
  solicitanteNombreInput.addEventListener("input", validateForm);
  rifRepresentanteInput.addEventListener("input", validateForm);
  direccionInput.addEventListener("input", validateForm);
  estadoInput.addEventListener("change", validateForm);
  municipioInput.addEventListener("change", validateForm);
  parroquiaInput.addEventListener("change", validateForm);
  numeroTelefonoInput.addEventListener("input", validateForm);
  metodoPagoInput.addEventListener("change", validateForm);
  referenciaInput.addEventListener("input", validateForm);

















































  // // Activar validaciones en tiempo real sin afectar a los checkbox
  // document
  //   .querySelectorAll("input:not([type='checkbox']), select")
  //   .forEach((element) => {
  //     element.addEventListener("input", validateForm);
  //     element.addEventListener("change", validateForm);
  //   });

  // Función para manejar la activación de fechas según los checkboxes
  function toggleFechaVencimiento(checkboxId, fechaId) {
    const checkbox = document.getElementById(checkboxId);
    const fechaInput = document.getElementById(fechaId);

    checkbox.addEventListener("change", function () {
      fechaInput.disabled = !this.checked;
      fechaInput.setAttribute("required", true)
      if (!this.checked) {
        fechaInput.value = "";
        fechaInput.removeAttribute("required")
        clearError(fechaInput);
      }
    });
    
    if (!checkbox.checked) {
      fechaInput.disabled = true;
      fechaInput.removeAttribute("required")
      clearError(fechaInput);
    }
  }

  // Agregar selección de "V" o "E" para la cédula
  cedulaInput = document.getElementById("id_solicitante_cedula");
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
