const selectDivision = document.getElementById("id_form1-opciones");
const selectTipoProcedimiento = document.getElementById("id_form4-tipo_procedimiento");

// Variable para evitar peticiones repetidas con la misma división
let ultimaDivisionCargada2 = null;

selectTipoProcedimiento.innerHTML = `<option value="" selected="">Seleccione Una Opcion</option>`;

async function cargarTipos(division) {
    if (!division || division === ultimaDivisionCargada2) return; // Evita llamadas duplicadas

    ultimaDivisionCargada2 = division; // Guarda la última división para evitar repeticiones

    const url = `/api/obtener_tipos_procedimientos?division=${division}`;

    try {
        const data = await fetchWithLoader(url, {
            method: "GET",
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "Content-Type": "application/json",
            },
        });

        selectTipoProcedimiento.innerHTML = `<option value="" selected="">Seleccione Una Opcion</option>`; // Limpia antes de cargar

        data.forEach((tipo) => {
            const option = document.createElement("option");
            option.value = tipo[0];
            option.innerText = tipo[1];
            selectTipoProcedimiento.appendChild(option);
        });

        window.cargasCompletas.procedimientos = true;
        verificarCargaCompleta(); // Verifica si todas las cargas están completas

    } catch (error) {
        console.error("❌ Error al cargar procedimientos:", error);
    }
}

// Si hay datos en localStorage, cargar automáticamente
let storedData = localStorage.getItem("fetchedData");

if (storedData) {
    const data = JSON.parse(storedData);
    if (data.id_division) {
        cargarTipos(data.id_division);
    }
} else {
    console.log("⚠ No hay datos en localStorage, esperando selección manual...");
}

// Escuchar cambios en el select solo si no es la misma división
selectDivision.addEventListener("change", function () {
    cargarTipos(selectDivision.value);
});
