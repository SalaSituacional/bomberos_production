 document.addEventListener("DOMContentLoaded", function () {
        document.body.addEventListener("click", async function (event) {
            if (event.target.classList.contains("generar-excel")) { // Cambié a 'generar-excel' por tu comentario, aunque tu script original dice '.generar-excel'
                try {
                    const idUnidad = event.target.getAttribute("data-unidad");
                    if (!idUnidad) {
                        console.error("ID de unidad no encontrado.");
                        return;
                    }

                    // 🚀 Construye la URL completa reemplazando el marcador de posición con el ID real.
                    const urlReporte = REPORTE_BASE_URL_PLACEHOLDER.replace('0000', idUnidad);

                    // Llamada a la API para obtener el PDF
                    // Ahora fetchWithLoader2 usará la URL generada por Django
                    const blob = await fetchWithLoader2(urlReporte); // ⬅️ Sigue siendo un Blob

                    // Crea un objeto URL para el Blob
                    const url = URL.createObjectURL(blob);

                    // Abrir el PDF en una nueva pestaña antes de la descarga
                    window.open(url, "_blank");

                    // Crear un enlace para la descarga
                    const a = document.createElement("a");
                    a.href = url;
                    a.download = `Reporte_Vuelo_${idUnidad}.pdf`; // Sugerencia: Añadir el ID al nombre del archivo
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

    // Tu función fetchWithLoader2 sin cambios, ya que ahora recibe la URL correcta.
    async function fetchWithLoader2(url, options = {}) {
        // Asegúrate de que `activeRequests`, `showLoader()`, y `hideLoader()` estén definidos globalmente o en un alcance accesible.
        // Por ejemplo:
        let activeRequests = 0; // Si no está definida en otro lugar

        activeRequests++;
        showLoader();

        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                // Mejora la visibilidad del error si la respuesta no es OK
                const errorBody = await response.text();
                throw new Error(
                    `Error en la solicitud: ${response.status} ${response.statusText} - ${errorBody}`
                );
            }

            return await response.blob(); // ⬅️ Convertir la respuesta en un Blob
        } catch (error) {
            console.error("Error al consumir la API:", error);
            throw error; // Propaga el error para que el bloque `catch` externo pueda manejarlo
        } finally {
            activeRequests--;
            hideLoader();
        }
    }