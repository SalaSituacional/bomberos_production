async function editarSolicitud() {
  tablaPrevencionContenido.addEventListener("click", async (event) => {
    if (event.target.closest("#Modificar_documento")) {
      let boton = event.target.closest("#Modificar_documento");
      let referencia = boton.getAttribute("data-solicitud");

      try {
        const response = await fetchWithLoader(
          `/api/modificar_solicitudes/${referencia}/`
        );

        let data = await response;

        // Guardar la información en localStorage
        localStorage.setItem("datosSolicitud", JSON.stringify(data));

        // Redirigir a la página destino
        window.location.href = "/formulariocertificados/";
      } catch (error) {
        console.error("❌ Error al Obtener los Datos:", error);
      }
    }
  });
}
