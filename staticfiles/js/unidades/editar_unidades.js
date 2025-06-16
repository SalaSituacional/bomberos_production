let botonesEditar = document.querySelectorAll(".editar_unidad");

botonesEditar.forEach((boton) => {
    boton.addEventListener("click", async function () {
      let id_unidad = this.getAttribute("data-unidad"); // ID de la unidad

      try {
        const response = await fetchWithLoader(
          `/mecanica/obtener_info_unidad/${id_unidad}/`
        );

        let data = await response;

        // Guardar la información en localStorage
        localStorage.setItem("datosSolicitud", JSON.stringify(data));

        // Redirigir a la página destino
        window.location.href = "/mecanica/formularioUnidades/";
      } catch (error) {
        console.error("❌ Error al Obtener los Datos:", error);
      }
  
    });
  });