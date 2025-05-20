// Función para eliminar un servicio (se llama desde el botón de eliminar)
function eliminarServicio(id) {
    if (confirm("¿Estás seguro de eliminar este servicio?")) {
       const url = URL_ELIMINAR.replace('__id__', id);  // Reemplaza el marcador con el ID real
        fetch(url, {  // Ajusta la URL según tu endpoint en Django
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),  // Necesario para Django CSRF
                'Content-Type': 'application/json',
            },
        })
            .then(response => {
                if (response.ok) {
                    alert("Servicio eliminado correctamente");
                    location.reload();  // Recarga la página para reflejar los cambios
                } else {
                    throw new Error("Error al eliminar");
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("No se pudo eliminar el servicio");
            });
    }
}

// Función auxiliar para obtener el token CSRF de Django
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}