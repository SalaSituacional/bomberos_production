document.addEventListener("DOMContentLoaded", function () {
    document.body.addEventListener("click", async function (event) {
        // Usamos .closest() para manejar clics en elementos hijos del botón
        const clickedButton = event.target.closest(".generar-excel");

        if (clickedButton) {
            try {
                const idUnidad = clickedButton.getAttribute("data-unidad");
                if (!idUnidad) {
                    console.error("ID de unidad no encontrado en el atributo data-unidad.");
                    return;
                }
                const REPORTE_BASE_URL_PLACEHOLDER = "/sarp/reporte/0000/";
                const urlReporte = REPORTE_BASE_URL_PLACEHOLDER.replace('0000', idUnidad);
                // const blob = await fetchWithLoader(urlReporte);
                // const url = URL.createObjectURL(blob);

                window.open(urlReporte, "_blank");

                const a = document.createElement("a");
                a.href = url;
                a.download = `Reporte_Vuelo_${idUnidad}.pdf`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);

                // Liberar el objeto URL
                URL.revokeObjectURL(url);

            } catch (error) {
                console.error("Error global en el proceso de reporte:", error);
            }
        }
    });
});