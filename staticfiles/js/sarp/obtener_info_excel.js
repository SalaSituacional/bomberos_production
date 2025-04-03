document.addEventListener("DOMContentLoaded", function () {
  document.body.addEventListener("click", async function (event) {
      if (event.target.classList.contains("generar-excel")) {
          try {
              const idUnidad = event.target.getAttribute("data-unidad"); // Obtener el ID del registro
              if (!idUnidad) {
                  console.error("ID de unidad no encontrado.");
                  return;
              }

              // Llamada a la API para obtener el PDF
              const response = await fetch(`/reporte/${idUnidad}/`);

              // Verificar si la respuesta es válida
              if (response.ok) {
                  const blob = await response.blob();  // Obtén la respuesta como un Blob (binario)

                  // Crea un objeto URL para el Blob
                  const url = URL.createObjectURL(blob);

                  // Abrir el PDF en una nueva pestaña antes de la descarga
                  window.open(url, "_blank");

                  // Crear un enlace para la descarga
                  const a = document.createElement('a');
                  a.href = url;
                  a.download = 'Reporte_Vuelo.pdf';
                  document.body.appendChild(a);
                  a.click();
                  document.body.removeChild(a);

                  // Liberar el objeto URL
                  URL.revokeObjectURL(url);
              } else {
                  console.error("Error en la API: ", response.statusText);
              }
          } catch (error) {
              console.error("Error en la petición:", error);
          }
      }
  });
});
