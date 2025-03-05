// Leer los datos del localStorage
const storedData = localStorage.getItem("datosSolicitud");

if (storedData) {
  let parsedData = JSON.parse(storedData); // Convertimos el string en un objeto

  let botonAggComercio = (document.querySelector(
    ".agg_comercio"
  ).parentElement.style = "display: none;");

  rellenarRequisitos(parsedData);
  rellenarDatos(parsedData);

  const form = document.getElementById("formularioCrearSolicitudes"); // Asegúrate de usar el ID correcto del formulario
  const solicitudId = ""; // Este sería el ID de la solicitud (puedes obtenerlo dinámicamente)

  // Crear el input hidden
  const inputHidden = document.createElement("input");
  inputHidden.type = "hidden";
  inputHidden.name = "id_solicitud"; // Nombre que se enviará en el POST
  inputHidden.value = parsedData.Id_Solicitud;

  // Agregarlo al formulario
  form.appendChild(inputHidden);

  document.querySelector(".registrar").removeAttribute("disabled");

  if (window.validacion) {
    validarCedulaYComercio(); // Llamar la función de archivo1.js
  } else {
    console.log("La función saludar no está disponible aún.");
  }
} else {
  console.log("ERRROR")
}

function rellenarRequisitos(data) {
  // Verificar que los checkboxes existen antes de asignar valores
  let cedulaIdentidad = document.getElementById("id_cedula_identidad");
  if (cedulaIdentidad) cedulaIdentidad.checked = !!data.Status_Cedula;

  let cedula = data.CI || ""; // Asegurar que no sea null o undefined

  // Extraer la nacionalidad (primer carácter)
  let nacionalidad = cedula.charAt(0);

  // Extraer el número de cédula (todo después del primer guion)
  let numeroCedula = cedula.substring(cedula.indexOf("-") + 1) || "";

  // Verificar que los elementos existen antes de asignar valores
  let nacionalidadInput = document.getElementById("nacionalidad");
  if (nacionalidadInput) nacionalidadInput.value = nacionalidad;

  let cedulaInput = document.getElementById("id_solicitante_cedula");
  if (cedulaInput) cedulaInput.value = numeroCedula;

  let fechaCedula = document.getElementById("id_cedula_vecimiento");
  if (fechaCedula) fechaCedula.value = data.Fecha_Vencimiento_Cedula || "";

  let rifRepresentante = document.getElementById("id_rif_representante");
  if (rifRepresentante) rifRepresentante.checked = !!data.Status_Rif;

  let rifRepresentanteLegal = document.getElementById(
    "id_rif_representante_legal"
  );
  if (rifRepresentanteLegal)
    rifRepresentanteLegal.value = data.Rif_Representante_Legal || "";

  let rifRepresentanteVencimiento = document.getElementById(
    "id_rif_representante_vencimiento"
  );
  if (rifRepresentanteVencimiento)
    rifRepresentanteVencimiento.value = data.Fecha_Vencimiento_Rif || "";

  let rifComercio = document.getElementById("id_rif_comercio");
  if (rifComercio) rifComercio.checked = !!data.Status_Comercio;

  let rifComercioVencimiento = document.getElementById(
    "id_rif_comercio_vencimiento"
  );
  if (rifComercioVencimiento)
    rifComercioVencimiento.value = data.Fecha_Vencimiento_Rif_Comercio || "";

  let cedulaCatastral = document.getElementById("id_cedula_catastral");
  if (cedulaCatastral) cedulaCatastral.checked = !!data.Status_Cedula_Catastral;

  let cedulaCatastralVencimiento = document.getElementById(
    "id_cedula_catastral_vencimiento"
  );
  if (cedulaCatastralVencimiento)
    cedulaCatastralVencimiento.value =
      data.Fecha_Vencimiento_Cedula_Catastral || "";

  let documentoPropiedad = document.getElementById("id_documento_propiedad");
  if (documentoPropiedad)
    documentoPropiedad.checked = !!data.Status_Documento_Propiedad;

  let documentoPropiedadVencimiento = document.getElementById(
    "id_documento_propiedad_vencimiento"
  );
  if (documentoPropiedadVencimiento)
    documentoPropiedadVencimiento.value =
      data.Fecha_Vencimiento_Documento_Propiedad || "";

  let permisoAnterior = document.getElementById("id_permiso_anterior");
  if (permisoAnterior) permisoAnterior.checked = !!data.Status_Permiso;

  let cartaAutorizacion = document.getElementById("id_carta_autorizacion");
  if (cartaAutorizacion)
    cartaAutorizacion.checked = !!data.Status_Carta_Autorizacion;

  let planoBomberil = document.getElementById("id_plano_bomberil");
  if (planoBomberil) planoBomberil.checked = !!data.Status_Plano;

  let registroComercio = document.getElementById("id_registro_comercio");
  if (registroComercio)
    registroComercio.checked = !!data.Status_Registro_Comercio;
}

function rellenarDatos(data) {
  document.getElementById("id_comercio").value = data.ID_Comercio;
  document.getElementById("id_fecha_solicitud").value = data.Fecha_Solicitud;
  document.getElementById("id_hora_solicitud").value = data.Hora;
  document.getElementById("id_tipo_servicio").value = data.Tipo_Servicio;
  document.getElementById("id_solicitante_nombre_apellido").value =
    data.Solicitante;
  document.getElementById("id_tipo_representante").value =
    data.Tipo_Representante;
  document.getElementById("id_direccion").value = data.Direccion;
  document.getElementById("id_estado").value = data.Estado;
  document.getElementById("id_municipio").value = data.Municipio;
  document.getElementById("id_parroquia").value = data.Parroquia;
  document.getElementById("id_numero_telefono").value = data.Telefono;
  document.getElementById("id_correo_electronico").value =
    data.Correo_Electronico;
  document.getElementById("id_pago_tasa").value = data.Pago_Tasa_Servicio;

  let metodoPago = document.getElementById("id_metodo_pago");
  metodoPago.value = data.Metodo_Pago;

  let referenciaInput = document.getElementById("id_referencia");
  referenciaInput.value = data.Referencia;

  if (metodoPago.value === "Transferencia" || metodoPago.value === "Deposito") {
    setTimeout(() => {
      referenciaInput.removeAttribute("disabled");
    }, 50);
  } else {
    referenciaInput.setAttribute("disabled", "");
    clearError(referenciaInput);
    referenciaInput.value = "";
  }
}

window.addEventListener("beforeunload", () => {
  // Eliminar la clave del localStorage
  localStorage.removeItem("fetchedData");
});

window.addEventListener("popstate", () => {
  // Eliminar la clave del localStorage al retroceder
  localStorage.removeItem("fetchedData");
});
