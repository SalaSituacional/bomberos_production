function eliminarVuelo(idVuelo) {
  if (confirm("¿Estás seguro de eliminar este reporte?")) {
    fetchWithLoader(`/api/eliminar_vuelo/${idVuelo}/`, {
      method: "DELETE",
      headers: {
        "X-CSRFToken": getCSRFToken(), // Para seguridad (si usas CSRF)
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.message) {
          alert(data.message);
          location.reload(); // Recargar la página después de eliminar
        } else {
          alert("Error: " + data.error);
        }
      })
      .catch((error) => console.error("Error al eliminar:", error));
  }
}

// Función para obtener el token CSRF (si lo usas en Django)
function getCSRFToken() {
  const csrfToken = document.cookie.match(/csrftoken=([^;]+)/);
  return csrfToken ? csrfToken[1] : "";
}
