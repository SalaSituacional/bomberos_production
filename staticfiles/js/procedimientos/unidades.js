const selectOpciones_Unidad = document.getElementById("id_form1-opciones");
const selectUnidad = document.getElementById("id_form2-unidad");

// Variable para almacenar la última división cargada y evitar peticiones duplicadas
let ultimaDivisionCargada = null;

selectUnidad.innerHTML = `<option value="" selected="">Seleccione Una Opcion</option>`;

async function cargarUnidades(division) {
    if (!division || division === ultimaDivisionCargada) return; // Evita peticiones repetidas

    ultimaDivisionCargada = division; // Guarda la división para evitar llamadas repetidas

    const url = `/api/obtener_unidades?division=${division}`;

    try {
        const data = await fetchWithLoader(url, {
            method: "GET",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/json",
            },
        });

        selectUnidad.innerHTML = ""; // Limpia el select antes de cargar nuevos datos

        data.forEach((unidad) => {
            const option = document.createElement("option");
            option.value = unidad[0];
            option.innerText = unidad[1];
            selectUnidad.appendChild(option);
        });

        window.cargasCompletas.unidades = true;
        verificarCargaCompleta();

    } catch (error) {
        console.error("❌ Error al cargar unidades:", error);
    }
}

// Verifica si hay datos en localStorage y carga unidades automáticamente si es necesario
storedData = localStorage.getItem("fetchedData");

if (storedData) {
    const data = JSON.parse(storedData);
    if (data.id_division) {
        cargarUnidades(data.id_division);
    }
} else {
    console.log("⚠ No hay datos en localStorage, esperando selección manual...");
}

// Espera a que el usuario seleccione una opción si no hay datos en localStorage
selectOpciones_Unidad.addEventListener("change", function () {
    cargarUnidades(selectOpciones_Unidad.value);
});
