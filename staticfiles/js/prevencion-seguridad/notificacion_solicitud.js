async function mostrarUltimoReporte() {
    try {
      const res = await fetchWithLoader("/seguridad_prevencion/api/ultimo_reporte_solicitudes/");

      const data = await res;
      const mensaje = `📋 Servicio: <strong>${data.tipo_servicio}</strong><br>🏢 Empresa: <strong>${data.comercio}</strong><br>🕒 Fecha: ${data.fecha_solicitud}`;
      lanzarNotificacion("📢 ¡Nuevo reporte registrado!", mensaje);
    } catch (error) {
      lanzarNotificacion("❌ No Existen Reportes", "No se han encontrado reportes recientes", true);
    }
  }

  function lanzarNotificacion(titulo, mensaje, esError = false) {
    const noti = document.getElementById("notificacion");
    const notiTitulo = document.getElementById("noti-titulo");
    const notiMensaje = document.getElementById("noti-mensaje");
    const notiEmoji = document.getElementById("noti-emoji");

    notiTitulo.innerHTML = titulo;
    notiMensaje.innerHTML = mensaje;
    notiEmoji.textContent = esError ? "⚠️" : "📢";

    noti.classList.remove("hidden");
    setTimeout(() => {
      noti.classList.add("show");
    }, 100);

    setTimeout(() => {
      noti.classList.remove("show");
      setTimeout(() => {
        noti.classList.add("hidden");
      }, 500);
    }, 6000);
  }

  // Llamada automática al cargar la página
  window.addEventListener("DOMContentLoaded", mostrarUltimoReporte);  
  