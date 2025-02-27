document.addEventListener("DOMContentLoaded", () => {
    const comercioSearch = document.getElementById("comercioSearch");
    const comercioList = document.getElementById("comercioList");
    const comercioSelect = document.getElementById("id_comercio");

    // Obtener opciones del select original
    let comercios = [];
    for (let option of comercioSelect.options) {
        if (option.value) {
            comercios.push({ 
                value: option.value, 
                text: option.textContent 
            });
        }
    }

    // Mostrar opciones filtradas en la lista
    comercioSearch.addEventListener("input", () => {
        let filtro = comercioSearch.value.toLowerCase();
        comercioList.innerHTML = ""; // Limpiar lista

        if (filtro) {
            let opcionesFiltradas = comercios.filter(c => c.text.toLowerCase().includes(filtro));

            if (opcionesFiltradas.length > 0) {
                comercioList.style.display = "block"; // Mostrar lista

                opcionesFiltradas.forEach(comercio => {
                    let li = document.createElement("li");
                    li.textContent = comercio.text;
                    li.dataset.value = comercio.value; // Guardar valor real

                    li.addEventListener("click", () => {
                        comercioSearch.value = comercio.text; // Rellenar input
                        comercioSelect.value = comercio.value; // Seleccionar en el <select>
                        comercioList.style.display = "none"; // Ocultar lista
                    });

                    comercioList.appendChild(li);
                });
            } else {
                comercioList.style.display = "none";
            }
        } else {
            comercioList.style.display = "none";
        }
    });

    // Ocultar lista al hacer clic fuera
    document.addEventListener("click", (e) => {
        if (!comercioSearch.contains(e.target) && !comercioList.contains(e.target)) {
            comercioList.style.display = "none";
        }
    });
});
