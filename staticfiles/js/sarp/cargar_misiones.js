async function actualizarMisiones() {
  try {
    const response = await fetchWithLoader("/api/estadisticas-misiones/");
    const data = await response;

    // Actualizar valores en la UI
    document.getElementById("mision-diario").querySelector("b").textContent =
      data.mision_diario;
    document.getElementById("mision-semanal").querySelector("b").textContent =
      data.mision_semanal;
    document.getElementById("mision-mensual").querySelector("b").textContent =
      data.mision_mensual;
  } catch (error) {
    console.error("Error al obtener datos:", error);
  }
}

// Ejecutar la función al cargar la página
document.addEventListener("DOMContentLoaded", actualizarMisiones);

document.addEventListener("DOMContentLoaded", async function () {
    try {
        const response = await fetchWithLoader("/api/ultimo_reporte/"); // Endpoint de tu API
        const data = await response;

        if (data) {
            document.getElementById("reporte-id").textContent = data.id_vuelo;
            document.getElementById("reporte-fecha").textContent = data.fecha;
            document.getElementById("reporte-sitio").textContent = data.sitio;
            document.getElementById("reporte-dron").textContent = data.dron;
            document.getElementById("reporte-mision").textContent = data.tipo_mision;

            // Mostrar la tarjeta con animación
            const card = document.getElementById("ultimo-reporte-card");
            card.classList.add("mostrar");

            // Cerrar la tarjeta al hacer clic en el botón
            document.getElementById("cerrar-reporte").addEventListener("click", function () {
                card.classList.remove("mostrar");
            });

            // Ocultar después de 10 segundos
            setTimeout(() => {
                card.classList.remove("mostrar");
            }, 20000);
        }
    } catch (error) {
        console.error("Error obteniendo el último reporte:", error);
    }
});

