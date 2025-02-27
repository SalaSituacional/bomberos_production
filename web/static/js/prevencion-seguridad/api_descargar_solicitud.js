async function descargarWordSolicitud() {
  tablaPrevencionContenido.addEventListener("click", async (event) => {
    if (event.target.closest("#Ver_documento")) {
      let boton = event.target.closest("#Ver_documento");
      let referencia = boton.getAttribute("data-solicitud");
      let tipo = boton.getAttribute("data-tipo-documento");

      let url = "";
      if (tipo === "Solicitud") {
        url = `/generar_documento_guia/${referencia}/`;
        nombreArchivo = `Solicitud_${referencia}.pdf`; // Nombre personalizado

      } else if (tipo === "Guia") {
        url = `/generar_documento_inspeccion/${referencia}/`;
        nombreArchivo = `Guia_${referencia}.pdf`; // Nombre personalizado

      }

      if (url) {
        try {
          const response = await fetchWithLoader2(url); // Se vuelve a incluir fetchWithLoader2

          if (!response.ok) {
            throw new Error(`Error al obtener el archivo: ${response.statusText}`);
          }

          const blob = await response.blob();
          const pdfUrl = URL.createObjectURL(blob);

          // Abre el PDF en una nueva pestaña
          window.open(pdfUrl, "_blank");
          // Asigna un nombre al archivo en la URL de la pestaña
          // pdfWindow.document.title = nombreArchivo; // Cambia el título de la pestaña

        } catch (error) {
          console.error("❌ Error al abrir el archivo:", error);
        }
      }
    }{}
  });
}

// Definición de fetchWithLoader2
async function fetchWithLoader2(url, options = {}) {
  activeRequests++; // Incrementa el contador de peticiones activas
  showLoader(); // Muestra el loader de carga

  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(`Error en la solicitud: ${response.status} ${response.statusText}`);
    }
    return response;
  } catch (error) {
    console.error("Error al consumir la API:", error);
    throw error;
  } finally {
    activeRequests--; // Decrementa el contador de peticiones activas
    hideLoader(); // Oculta el loader cuando se completa la petición
  }
}
