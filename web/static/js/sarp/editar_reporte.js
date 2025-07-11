async function fetchWithLoader(url, options = {}) {
  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      const errorBody = await response.text();
      throw new Error(
        `Error en la solicitud: ${response.status} ${response.statusText} - ${errorBody}`
      );
    }
    return await response.json(); // <-- Asumimos que esta API devuelve JSON
  } catch (error) {
    console.error("Error en fetchWithLoader:", error);
    throw error;
  }
}

document.addEventListener("DOMContentLoaded", function () {
  document.body.addEventListener("click", async function (event) {
    // Usa .closest() para manejar clics en SVG o hijos del botón
    if (event.target.closest(".editar_unidad")) {
      try {
        const button = event.target.closest(".editar_unidad");
        const idVuelo = button.getAttribute("data-unidad");

        if (!idVuelo) {
          console.error("ID de vuelo no encontrado en el botón.");
          return;
        }

        const urlApiParaObtenerDatosVuelo = EDITAR_REPORTE_BASE_URL_PLACEHOLDER.replace("0000", idVuelo);
        const datosVuelo = await fetchWithLoader(urlApiParaObtenerDatosVuelo);

        // Asegúrate de que 'datosVuelo' sea un objeto/array válido
        if (!datosVuelo) {
          console.error(
            "No se pudieron obtener los datos del vuelo para edición."
          );
          return;
        }

        // Guardar en localStorage para que el formulario de edición los recupere
        localStorage.setItem("vueloEditar", JSON.stringify(datosVuelo));

        // Redirigir al formulario de edición
        // ✅ Usa la variable 'FormularioSarp' para la redirección.
        window.location.href = FormularioSarp;
      } catch (error) {
        console.error(
          "Error en el proceso de edición (obtención de datos o redirección):",
          error
        );
      }
    }
  });
});
