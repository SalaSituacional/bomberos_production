const selectOpciones_Unidad = document.getElementById("id_form1-opciones");
const selectUnidad = document.getElementById("id_form2-unidad");

selectUnidad.innerHTML = `<option value="" selected="">Seleccione Una Opcion</option>`

// const division = selectOpciones_Unidad.value;
async function cargarUnidades(division) {
  const url = `/api/obtener_unidades?division=${division}`; // URL con la fecha como parámetro

  try {
    const data = await fetchWithLoader(url, {
      method: "GET",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json",
      },
    });

    selectUnidad.innerText = ""

    data.forEach(unidad => {
      const option = document.createElement("option")
      option.value = unidad[0]
      if (!option.value) {
        option.setAttribute("disabled", true)
        option.setAttribute("selected", true)
      }
      option.innerText = unidad[1]
      selectUnidad.appendChild(option)
    });
    
  } catch (error) {
    console.error("Error al cargar procedimientos:", error);
  }
}

selectOpciones_Unidad.addEventListener("change", function () {
  cargarUnidades(selectOpciones_Unidad.value);
});
