document.addEventListener("DOMContentLoaded", function () {
  document.body.addEventListener("click", async function (event) {
    if (event.target.classList.contains("generar-excel")) {
      try {
        const idUnidad = event.target.getAttribute("data-unidad");
        if (!idUnidad) {
          console.error("ID de unidad no encontrado.");
          return;
        }

        // Llamada a la API para obtener el PDF
        const blob = await fetchWithLoader2(`/reporte/${idUnidad}/`); // ⬅️ Ahora sí es un Blob

        // Crea un objeto URL para el Blob
        const url = URL.createObjectURL(blob);

        // Abrir el PDF en una nueva pestaña antes de la descarga
        window.open(url, "_blank");

        // Crear un enlace para la descarga
        const a = document.createElement("a");
        a.href = url;
        a.download = "Reporte_Vuelo.pdf";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

        // Liberar el objeto URL
        URL.revokeObjectURL(url);
      } catch (error) {
        console.error("Error en la petición:", error);
      }
    }
  });
});

async function fetchWithLoader2(url, options = {}) {
  activeRequests++;
  showLoader();

  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(
        `Error en la solicitud: ${response.status} ${response.statusText}`
      );
    }

    return await response.blob(); // ⬅️ Convertir la respuesta en un Blob
  } catch (error) {
    console.error("Error al consumir la API:", error);
    throw error;
  } finally {
    activeRequests--;
    hideLoader();
  }
}
