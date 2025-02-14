function descargarWordSolicitud() {
    tablaPrevencionContenido.addEventListener("click", async (event) => {
        if (event.target.closest("#Ver_documento")) {
            let boton = event.target.closest("#Ver_documento");
            let referencia = boton.getAttribute("data-solicitud");
            let tipo = boton.getAttribute("data-tipo-documento")

            if (tipo==="Solicitud") {
              try {
                  const response = await fetchWithLoader2(`/generar_documento_guia/${referencia}/`);
  
                  if (!response.ok) {
                      throw new Error(`Error al obtener el archivo: ${response.statusText}`);
                  }
  
                  const blob = await response.blob(); // Convertir la respuesta en un archivo
                  const url = window.URL.createObjectURL(blob);
  
                  // Crear un enlace oculto y simular el clic
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = `Guia_Solicitud.docx`; // Nombre personalizado
                  document.body.appendChild(a);
                  a.click();
                  document.body.removeChild(a);
  
                  // Liberar memoria
                  window.URL.revokeObjectURL(url);
  
              } catch (error) {
                  console.error("❌ Error al descargar el archivo:", error);
              }
            } else if (tipo==="Guia") {
              try {
                  const response = await fetchWithLoader2(`/generar_documento_inspeccion/${referencia}/`);
  
                  if (!response.ok) {
                      throw new Error(`Error al obtener el archivo: ${response.statusText}`);
                  }
  
                  const blob = await response.blob(); // Convertir la respuesta en un archivo
                  const url = window.URL.createObjectURL(blob);
  
                  // Crear un enlace oculto y simular el clic
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = `Guia de Inspeccion.docx`; // Nombre personalizado
                  document.body.appendChild(a);
                  a.click();
                  document.body.removeChild(a);
  
                  // Liberar memoria
                  window.URL.revokeObjectURL(url);
  
              } catch (error) {
                  console.error("❌ Error al descargar el archivo:", error);
              }
              
            }
        }
    });
}


async function fetchWithLoader2(url, options = {}) {
    activeRequests++; // Incrementa el contador de peticiones activas
    showLoader();
  
    try {
      const response = await fetch(url, options);
      if (!response.ok) {
        throw new Error(
          `Error en la solicitud: ${response.status} ${response.statusText}`
        );
      }
      return await response;
    } catch (error) {
      console.error("Error al consumir la API:", error);
      throw error;
    } finally {
      activeRequests--; // Decrementa el contador de peticiones activas
      hideLoader();
    }
  }

