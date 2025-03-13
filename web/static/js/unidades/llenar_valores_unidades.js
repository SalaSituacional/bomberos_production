const storedData = localStorage.getItem("datosSolicitud");

if (storedData) {
  let parsedData = JSON.parse(storedData); // Convertimos el string en un objeto

  document.getElementById("id_nombre_unidad").value = parsedData.nombre_unidad || "";
  document.getElementById("id_division").setAttribute("disabled", true);
  document.getElementById("id_division").value = parsedData.divisiones.length > 0 ? parsedData.divisiones[0].id : "";
  document.getElementById("id_tipo_vehiculo").value = parsedData.tipo_vehiculo || "";
  document.getElementById("id_serial_carroceria").value = parsedData.serial_carroceria || "";
  document.getElementById("id_serial_chasis").value = parsedData.serial_chasis || "";
  document.getElementById("id_marca").value = parsedData.marca || "";
  document.getElementById("id_año").value = parsedData.año || "";
  document.getElementById("id_modelo").value = parsedData.modelo || "";
  document.getElementById("id_placas").value = parsedData.placas || "";
  document.getElementById("id_tipo_filtro_aceite").value = parsedData.tipo_filtro_aceite || "";
  document.getElementById("id_tipo_filtro_combustible").value = parsedData.tipo_filtro_combustible || "";
  document.getElementById("id_bateria").value = parsedData.bateria || "";
  document.getElementById("id_numero_tag").value = parsedData.numero_tag || "";
  document.getElementById("id_tipo_bujia").value = parsedData.tipo_bujia || "";
  document.getElementById("id_uso").value = parsedData.uso || "";
  document.getElementById("id_capacidad_carga").value = parsedData.capacidad_carga || "";
  document.getElementById("id_numero_ejes").value = parsedData.numero_ejes || "";
  document.getElementById("id_numero_puestos").value = parsedData.numero_puestos || "";
  document.getElementById("id_tipo_combustible").value = parsedData.tipo_combustible || "";
  document.getElementById("id_tipo_aceite").value = parsedData.tipo_aceite || "";
  document.getElementById("id_medida_neumaticos").value = parsedData.medida_neumaticos || "";
  document.getElementById("id_tipo_correa").value = parsedData.tipo_correa || "";
  document.getElementById("id_estado").value = parsedData.estado || "";

  document.getElementById("id_unidad").value = parsedData.id || "";
} else {
  console.log("⚠️ ERROR: No se encontraron datos de la solicitud.");
}


window.addEventListener("beforeunload", () => {
  // Eliminar la clave del localStorage
  localStorage.removeItem("datosSolicitud");
});

window.addEventListener("popstate", () => {
  // Eliminar la clave del localStorage al retroceder
  localStorage.removeItem("datosSolicitud");
});
