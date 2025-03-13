fetchWithLoader("/api/reportes_combustible/")
  .then((response) => response)
  .then((data) => conteoReportesCombustible(data))
  .catch((error) => console.error("Error al obtener los datos", error));

function conteoReportesCombustible(data) {
  document.getElementById("combustible-mensual").innerHTML = data.reportes_mes;
  document.getElementById("combustible-semanal").innerHTML =
    data.reportes_semana;
  document.getElementById("combustible-diario").innerHTML = data.reportes_hoy;
}

fetchWithLoader("/api/reportes_lubricantes/")
  .then((response) => response)
  .then((data) => conteoReportesLubricantes(data))
  .catch((error) => console.error("Error al obtener los datos", error));

function conteoReportesLubricantes(data) {
  document.getElementById("lubricantes-mensual").innerHTML = data.reportes_mes;
  document.getElementById("lubricantes-semanal").innerHTML =
    data.reportes_semana;
  document.getElementById("lubricantes-diario").innerHTML = data.reportes_hoy;
}

fetchWithLoader("/api/reportes_neumaticos/")
  .then((response) => response)
  .then((data) => conteoReportesNeumaticos(data))
  .catch((error) => console.error("Error al obtener los datos", error));

function conteoReportesNeumaticos(data) {
  document.getElementById("neumaticos-mensual").innerHTML = data.reportes_mes;
  document.getElementById("neumaticos-semanal").innerHTML =
    data.reportes_semana;
  document.getElementById("neumaticos-diario").innerHTML = data.reportes_hoy;
}

fetchWithLoader("/api/reportes_reparaciones/")
  .then((response) => response)
  .then((data) => conteoReportesReparaciones(data))
  .catch((error) => console.error("Error al obtener los datos", error));

function conteoReportesReparaciones(data) {
  document.getElementById("reparaciones-mensual").innerHTML = data.reportes_mes;
  document.getElementById("reparaciones-semanal").innerHTML =
    data.reportes_semana;
  document.getElementById("reparaciones-diario").innerHTML = data.reportes_hoy;
}

fetchWithLoader("/api/reportes_electricas/")
  .then((response) => response)
  .then((data) => conteoReportesElectricas(data))
  .catch((error) => console.error("Error al obtener los datos", error));

function conteoReportesElectricas(data) {
  document.getElementById("electricas-mensual").innerHTML = data.reportes_mes;
  document.getElementById("electricas-semanal").innerHTML =
    data.reportes_semana;
  document.getElementById("electricas-diario").innerHTML = data.reportes_hoy;
}

fetchWithLoader("/api/reportes_cambio_repuestos/")
  .then((response) => response)
  .then((data) => conteoReportesCambioRepuestos(data))
  .catch((error) => console.error("Error al obtener los datos", error));

function conteoReportesCambioRepuestos(data) {
  document.getElementById("cambio-repuestos-mensual").innerHTML = data.reportes_mes;
  document.getElementById("cambio-repuestos-semanal").innerHTML =
    data.reportes_semana;
  document.getElementById("cambio-repuestos-diario").innerHTML = data.reportes_hoy;
}
