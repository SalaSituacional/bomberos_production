document.addEventListener("DOMContentLoaded", function () {
    document.body.addEventListener("click", async function (event) {
      if (event.target.closest(".editar_unidad")) {
        try {
          const button = event.target.closest(".editar_unidad");
          const idVuelo = button.getAttribute("data-unidad");
  
          if (!idVuelo) {
            console.error("ID de vuelo no encontrado.");
            return;
          }

          // Llamada a la API para obtener los datos
          const response = await fetchWithLoader(`/editar_reporte/${idVuelo}/`);  
  
          const data = await response;
  
          // Guardar en localStorage
          localStorage.setItem("vueloEditar", JSON.stringify(data));
  
          // Redirigir al formulario de edición
          window.location.href = "/formularios_sarp/";
        } catch (error) {
          console.error("Error obteniendo datos:", error);
        }
      }
    });
  });
  