  async function fetchWithLoader(url, options = {}) {
        // Lógica para mostrar/ocultar loaders, manejar errores HTTP, etc.
        // Debe devolver la respuesta de la red, no directamente el JSON/Blob
        // para que la cadena de .then().then() funcione.
        try {
            const response = await fetch(url, options);
            if (!response.ok) {
                const errorBody = await response.text(); // Intenta leer el cuerpo del error
                throw new Error(`Error en la solicitud: ${response.status} ${response.statusText} - ${errorBody}`);
            }
            return response; // Retorna la respuesta completa para encadenar .json() o .text()
        } catch (error) {
            console.error("Error en fetchWithLoader:", error);
            throw error;
        }
    }

    // Función para obtener el token CSRF (esencial para solicitudes POST/PUT/DELETE en Django)
    function getCSRFToken() {
        const csrfToken = document.cookie.match(/csrftoken=([^;]+)/);
        return csrfToken ? csrfToken[1] : "";
    }

    function eliminarVuelo(idVuelo) {
        if (confirm("¿Estás seguro de eliminar este reporte?")) {
            // 🚀 Construye la URL completa reemplazando el marcador de posición con el ID real.
            const urlCompletaEliminar = EliminarVueloBaseUrlPlaceholder.replace('0000', idVuelo);

            console.log("Intentando eliminar vuelo de URL:", urlCompletaEliminar); // Para depuración

            // ⚠️ Corrección aquí: Pasa la URL completa como primer argumento,
            //    y las opciones (method, headers) como segundo argumento a fetchWithLoader.
            fetchWithLoader(urlCompletaEliminar, {
                method: "DELETE",
                headers: {
                    "X-CSRFToken": getCSRFToken(), // Para seguridad CSRF de Django
                    "Content-Type": "application/json",
                },
                // Si tu API DELETE espera un cuerpo (body), por ejemplo para un ID en el cuerpo,
                // lo añadirías aquí, pero para DELETE por URL generalmente no es necesario.
                // body: JSON.stringify({ id: idVuelo }),
            })
            .then((response) => response.json()) // Asume que tu API de eliminación devuelve un JSON
            .then((data) => {
                if (data.message) {
                    alert(data.message);
                    location.reload(); // Recargar la página después de eliminar para actualizar la tabla
                } else if (data.error) { // Asegúrate de manejar la propiedad 'error' si tu API la usa
                    alert("Error: " + data.error);
                } else {
                    // Si la respuesta no tiene 'message' ni 'error' pero es exitosa
                    alert("Reporte eliminado exitosamente.");
                    location.reload();
                }
            })
            .catch((error) => {
                console.error("Error al eliminar el vuelo:", error);
                alert("Ocurrió un error al intentar eliminar el reporte.");
            });
        }
    }