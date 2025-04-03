document.addEventListener("DOMContentLoaded", function () {
  const vueloData = localStorage.getItem("vueloEditar");

  if (vueloData) {
    const vuelo = JSON.parse(vueloData);

    // Rellenar los formularios
    document.getElementById("id_vuelo").value = vuelo.vuelo.id_vuelo || "";
    document.getElementById("id_id_operador").value =
      vuelo.vuelo.id_operador || "";
    document.getElementById("id_id_observador").value =
      vuelo.vuelo.id_observador || "";
    document.getElementById("id_observador_externo").value =
      vuelo.vuelo.observador_externo || "";
    document.getElementById("id_fecha").value = vuelo.vuelo.fecha || "";
    document.getElementById("id_sitio").value = vuelo.vuelo.sitio || "";
    document.getElementById("id_hora_despegue").value =
      vuelo.vuelo.hora_despegue || "";
    document.getElementById("id_hora_aterrizaje").value =
      vuelo.vuelo.hora_aterrizaje || "";
    document.getElementById("id_tipo_mision").value =
      vuelo.vuelo.tipo_mision || "";
    document.getElementById("id_observaciones_vuelo").value =
      vuelo.vuelo.observaciones_vuelo || "";
    document.getElementById("id_apoyo_realizado_a").value =
      vuelo.vuelo.apoyo_realizado_a || "";

    document.getElementById("id_id_dron").value = vuelo.vuelo.id_dron || "";
    document.getElementById("id_id_dron").disabled = true; // Deshabilita el select
    document.getElementById("id_id_dron").removeAttribute("required"); // Deshabilita el select

    // Asigna el valor al campo oculto para que se envíe al backend
    document.getElementById("hidden_id_dron").value = vuelo.vuelo.id_dron || "";

    // Estado del Dron
    document.getElementById("id_cuerpo").value = vuelo.estado_dron.cuerpo || "";
    document.getElementById("id_observacion_cuerpo").value =
      vuelo.estado_dron.observacion_cuerpo || "";
    document.getElementById("id_camara").value = vuelo.estado_dron.camara || "";
    document.getElementById("id_observacion_camara").value =
      vuelo.estado_dron.observacion_camara || "";
    document.getElementById("id_helices").value =
      vuelo.estado_dron.helices || "";
    document.getElementById("id_observacion_helices").value =
      vuelo.estado_dron.observacion_helices || "";
    document.getElementById("id_sensores").value =
      vuelo.estado_dron.sensores || "";
    document.getElementById("id_observacion_sensores").value =
      vuelo.estado_dron.observacion_sensores || "";
    document.getElementById("id_motores").value =
      vuelo.estado_dron.motores || "";
    document.getElementById("id_observacion_motores").value =
      vuelo.estado_dron.observacion_motores || "";

    // Estado de la Batería
    document.getElementById("id_bateria1").value =
      vuelo.estado_baterias.bateria1 || "";
    document.getElementById("id_bateria2").value =
      vuelo.estado_baterias.bateria2 || "";
    document.getElementById("id_bateria3").value =
      vuelo.estado_baterias.bateria3 || "";
    document.getElementById("id_bateria4").value =
      vuelo.estado_baterias.bateria4 || "";

    // Estado del Control
    document.getElementById("id_cuerpo_control").value =
      vuelo.estado_control.cuerpo || "";
    document.getElementById("id_joysticks").value =
      vuelo.estado_control.joysticks || "";
    document.getElementById("id_pantalla").value =
      vuelo.estado_control.pantalla || "";
    document.getElementById("id_antenas").value =
      vuelo.estado_control.antenas || "";
    document.getElementById("id_bateria").value =
      vuelo.estado_control.bateria || "";

    // Detalles del Vuelo
    document.getElementById("id_viento").value =
      vuelo.detalles_vuelo.viento || "";
    document.getElementById("id_nubosidad").value =
      vuelo.detalles_vuelo.nubosidad || "";
    document.getElementById("id_riesgo_vuelo").value =
      vuelo.detalles_vuelo.riesgo_vuelo || "";
    document.getElementById("id_zona_vuelo").value =
      vuelo.detalles_vuelo.zona_vuelo || "";
    document.getElementById("id_numero_satelites").value =
      vuelo.detalles_vuelo.numero_satelites || "";

    let distancia = vuelo.detalles_vuelo.distancia_recorrida;
    // Dividir número y unidad de medida
    let [numero, unidad] = distancia.split(" ");

    document.getElementById("id_distancia_recorrida").value = numero || "";
    document.getElementById("id_magnitud_distancia").value = unidad || "";

    document.getElementById("id_altitud").value =
      vuelo.detalles_vuelo.altitud || "";
    document.getElementById("id_duracion_vuelo").value =
      vuelo.detalles_vuelo.duracion_vuelo || "";
    document.getElementById("id_observaciones").value =
      vuelo.detalles_vuelo.observaciones || "";
  } else {
    console.warn("No se encontraron datos en localStorage.");
  }

  window.addEventListener("beforeunload", () => {
    // Eliminar la clave del localStorage
    localStorage.removeItem("vueloEditar");
  });

  window.addEventListener("popstate", () => {
    // Eliminar la clave del localStorage al retroceder
    localStorage.removeItem("vueloEditar");
  });
});
