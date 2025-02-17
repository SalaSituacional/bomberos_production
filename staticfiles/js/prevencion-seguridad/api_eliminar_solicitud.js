function eliminarSolicitud() {
    tablaPrevencionContenido.addEventListener("click", async (event) => {
        if (event.target.closest("#Eliminar_documento")) {
            let boton = event.target.closest("#Eliminar_documento");
            let referencia = boton.getAttribute("data-solicitud");

            try {
                const response = await fetchWithLoader2(`/api/eliminar_solicitudes/${referencia}/`);

                if (!response.ok) {
                    throw new Error(`Error al obtener el archivo: ${response.statusText}`);
                }

                location.reload()

            } catch (error) {
                console.error("❌ Error al descargar el archivo:", error);
            }
        }
    });
}