document.addEventListener("DOMContentLoaded", function () {
    document.body.addEventListener("click", async function (event) {
      if (event.target.classList.contains("generar-excel")) {
        try {
          const idUnidad = event.target.getAttribute("data-unidad"); // Obtener el ID del registro
          if (!idUnidad) {
            console.error("ID de unidad no encontrado.");
            return;
          }
  
          // Llamada a la API
          const response = await fetchWithLoader(`/reporte/${idUnidad}/`);
  
          const data = await response; // Convertir a JSON
          console.log("Datos recibidos:", data);
        } catch (error) {
          console.error("Error en la petición:", error);
        }
      }
    });
  });
  