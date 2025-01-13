document.addEventListener("DOMContentLoaded", function () {


// Delegar evento click en el contenedor padre
document.querySelector("tbody").addEventListener("click", async function (event) {
    // Verificar si el clic fue en un botón con la clase "btn-editar"
    if (event.target.classList.contains("btn-editar")) {
        const id = event.target.getAttribute("data-id");

        try {
            // Llamada a fetchWithLoader para cargar datos del procedimiento
            const data = await fetchWithLoader(`/api/obtener_informacion/${id}/`);
            // const data = await fetchWithLoader(`/api/obtener_informacion/161/`);

            // Guardar la información en localStorage
            localStorage.setItem('fetchedData', JSON.stringify(data));

            // Redirigir a la página destino
            window.location.href = '/editar_procedimientos/';

        } catch (err) {
            alert("Hubo un problema al cargar los datos.");
        }
    }
});
});