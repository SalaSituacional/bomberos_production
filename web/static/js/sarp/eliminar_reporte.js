function getCSRFToken() {
    const csrfToken = document.cookie.match(/csrftoken=([^;]+)/);
    return csrfToken ? csrfToken[1] : "";
}

// --- Nueva función para manejar la eliminación de vuelos ---
function setupDeleteVueloListeners() {
    // Selecciona todos los botones con la clase 'delete-vuelo-btn'
    const deleteButtons = document.querySelectorAll('.delete-vuelo-btn');

    // Itera sobre cada botón y añade un event listener
    deleteButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Obtiene el ID del vuelo del atributo data-id-vuelo
            const idVuelo = this.dataset.idVuelo; // 'dataset' es la forma de acceder a data-attributes
            
            if (!idVuelo) {
                console.error("No se encontró el ID del vuelo en el botón.");
                alert("Error: No se pudo obtener el ID del reporte para eliminar.");
                return;
            }

            if (confirm("¿Estás seguro de eliminar este reporte?")) {
                const urlCompletaEliminar = EliminarVueloBaseUrlPlaceholder.replace('0000', idVuelo);

                fetchWithLoader(urlCompletaEliminar, {
                    headers: {
                        "X-CSRFToken": getCSRFToken(),
                        "Content-Type": "application/json",
                    },
                })
                .then((response) => response)
                .then((data) => {
                    if (data.message) {
                        alert(data.message);
                        location.reload(); 
                    } else if (data.error) {
                        alert("Error: " + data.error);
                    } else {
                        location.reload();
                    }
                })
                .catch((error) => {
                    alert("Ocurrió un error al intentar eliminar el reporte.");
                });
            }
        });
    });
}

// Llama a esta función cuando el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', setupDeleteVueloListeners);