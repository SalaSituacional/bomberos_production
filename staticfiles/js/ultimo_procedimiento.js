document.addEventListener("DOMContentLoaded", async function () {
    try {
        const response = await fetchWithLoader("/api/ultimo_procedimiento/"); // Endpoint de tu API
        const data = await response;

        if (data) {
            document.getElementById("procedimiento-division").textContent = data.division;
            document.getElementById("procedimiento-ubicacion").textContent = data.ubicacion;
            document.getElementById("procedimiento-fecha").textContent = data.fecha;
            document.getElementById("procedimiento-direccion").textContent = data.direccion;
            document.getElementById("procedimiento-tipo").textContent = data.tipo_procedimiento;

            // Mostrar la tarjeta con animación
            const card = document.getElementById("ultimo-procedimiento-card");
            card.classList.add("mostrar");

            // Cerrar la tarjeta al hacer clic en el botón
            document.getElementById("cerrar-procedimiento").addEventListener("click", function () {
                card.classList.remove("mostrar");
            });

            // Ocultar después de 10 segundos
            setTimeout(() => {
                card.classList.remove("mostrar");
            }, 20000);
        }
    } catch (error) {
        console.error("Error obteniendo el último procedimiento:", error);
    }
});
