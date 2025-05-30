async function actualizarMisiones() {
  try {
    const response = await fetchWithLoader("/api/estadisticas-misiones/");
    const data = await response;

    // Actualizar valores en la UI
    document.getElementById("mision-diario").querySelector("b").textContent =
      data.mision_diario;
    document.getElementById("mision-semanal").querySelector("b").textContent =
      data.mision_semanal;
    document.getElementById("mision-mensual").querySelector("b").textContent =
      data.mision_mensual;
  } catch (error) {
    console.error("Error al obtener datos:", error);
  }
}

// Ejecutar la función al cargar la página
document.addEventListener("DOMContentLoaded", actualizarMisiones);

document.addEventListener("DOMContentLoaded", async function () {
    try {
        const response = await fetchWithLoader("/api/ultimo_reporte/");
        const data = await response;

        const card = document.getElementById("ultimo-reporte-card");
        const cardContent = document.getElementById("card-content");
        
        // Limpiar contenido previo
        cardContent.innerHTML = '<button id="cerrar-reporte">&times;</button>';

        if (data.status === "empty") {
            // Caso cuando no hay reportes
            cardContent.innerHTML += `<h2>${data.error}</h2>`;
        } else if (data.status === "success") {
            // Caso cuando hay reportes
            cardContent.innerHTML += `
                <h2>Último Reporte</h2>
                <p><strong>ID Vuelo:</strong> <span id="reporte-id">${data.id_vuelo}</span></p>
                <p><strong>Fecha:</strong> <span id="reporte-fecha">${data.fecha}</span></p>
                <p><strong>Sitio:</strong> <span id="reporte-sitio">${data.sitio}</span></p>
                <p><strong>Dron:</strong> <span id="reporte-dron">${data.dron}</span></p>
                <p><strong>Misión:</strong> <span id="reporte-mision">${data.tipo_mision}</span></p>
            `;
        }

        // Mostrar la tarjeta con animación
        card.classList.add("mostrar");

        // Cerrar la tarjeta al hacer clic en el botón
        document.getElementById("cerrar-reporte").addEventListener("click", function () {
            card.classList.remove("mostrar");
        });

        // Ocultar después de 20 segundos
        setTimeout(() => {
            card.classList.remove("mostrar");
        }, 20000);

    } catch (error) {
        console.error("Error obteniendo el último reporte:", error);
        
        const card = document.getElementById("ultimo-reporte-card");
        card.innerHTML = `
            <button id="cerrar-reporte">&times;</button>
            <h2>Error al cargar los reportes</h2>
            <p>Por favor intente más tarde</p>
        `;
        card.classList.add("mostrar");

        // Cerrar la tarjeta al hacer clic en el botón
        document.getElementById("cerrar-reporte").addEventListener("click", function () {
            card.classList.remove("mostrar");
        });

        // Ocultar después de 20 segundos
        setTimeout(() => {
            card.classList.remove("mostrar");
        }, 20000);
    }
});

