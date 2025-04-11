async function mostrarUltimoPersonal() {
  try {
    const res = await fetchWithLoader("/api/ultimo_personal/");

    const data = await res;
    const mensaje = `
        <strong>${data.nombres} ${data.apellidos}</strong><br>
        📌 Jerarquía: ${data.jerarquia}<br>
        💼 Cargo: ${data.cargo}<br>
        🆔 Cédula: ${data.cedula}<br>
        🎭 Rol: ${data.rol}<br>
        📶 Estado: ${data.status}
      `;
    lanzarNotiPersonal("👤 Último Personal Registrado", mensaje);
  } catch (error) {
    lanzarNotiPersonal("⚠️ Sin registros", error.message, true);
  }
}

function lanzarNotiPersonal(titulo, mensaje, esError = false) {
  const noti = document.getElementById("notificacionPersonal");
  const notiTitulo = document.getElementById("noti-titulo-p");
  const notiMensaje = document.getElementById("noti-mensaje-p");
  const notiEmoji = document.getElementById("noti-emoji-p");

  notiTitulo.innerHTML = titulo;
  notiMensaje.innerHTML = mensaje;
  notiEmoji.textContent = esError ? "🚫" : "👤";

  notiEmoji.style.visibility = "hidden";

  noti.classList.remove("hidden");
  setTimeout(() => noti.classList.add("show"), 100);
  setTimeout(() => {
    noti.classList.remove("show");
    setTimeout(
      () => noti.classList.add("hidden"),
      mostrarNotificacionGeneral(),
      500
    );
  }, 7000);
}

function mostrarNotificacionGeneral() {
  fetch("/api/personal_comandante/")
    .then(response => {
      if (!response.ok) throw new Error("No hay datos");
      return response.json();
    })
    .then(data => {
      const mensaje = document.getElementById("noti-mensaje-g");
      if (Array.isArray(data) && data.length > 0) {
        const p = data[0]; // Mostramos solo el primero
        mensaje.innerHTML = `
        <p>👤 <strong>Nombre:</strong> <span>${p.nombres} ${p.apellidos}</span></p>
        <p>🎖️ <strong>Jerarquía:</strong> <span>${p.jerarquia}</span></p>
        <p>🧭 <strong>Cargo:</strong> <span >Primer Comandante</span></p>
        <p>🆔 <strong>Cédula:</strong> ${p.cedula}</p>
        <p>🛡️ <strong>Rol:</strong> ${p.rol}</p>
        <p>${p.status === "Activo" ? "✅" : "❌"} <strong>Status:</strong> <span style="color:${p.status === "Activo" ? "#28a745" : "#dc3545"}">${p.status}</span></p>
      `;
      } else {
        mensaje.innerHTML = `<p>No hay datos del Primer Comandante.</p>`;
      }

      const noti = document.getElementById("notificacionGeneral");
      noti.classList.remove("hidden");
      setTimeout(() => noti.classList.add("show"), 100);
    })
    .catch(() => {
      const mensaje = document.getElementById("noti-mensaje-g");
      mensaje.innerHTML = `<p><strong>⚠️ No se encontró ningún Primer Comandante.</strong></p>`;
      const noti = document.getElementById("notificacionGeneral");
      noti.classList.remove("hidden");
      setTimeout(() => noti.classList.add("show"), 100);
    });
}

function cerrarNotificacion() {
  const notificacion = document.getElementById('notificacionGeneral');
  if (notificacion) {
    notificacion.classList.add('hidden');
  }
}


// Ejecutar al cargar
window.addEventListener("DOMContentLoaded", mostrarUltimoPersonal);
