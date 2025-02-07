const selectDivision = document.getElementById("id_form1-opciones");
const selectTipoProcedimiento = document.getElementById("id_form4-tipo_procedimiento");

selectTipoProcedimiento.innerHTML = `<option value="" selected="">Seleccione Una Opcion</option>`

// const division = selectOpciones_Unidad.value;
async function cargarTipos(division) {
  const url = `/api/obtener_tipos_procedimientos?division=${division}`; // URL con la fecha como parámetro

  try {
    const data = await fetchWithLoader(url, {
      method: "GET",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json",
      },
    });

    selectTipoProcedimiento.innerText = ""

    data.forEach(unidad => {
      const option = document.createElement("option")
      option.value = unidad[0]
      if (!option.value) {
        option.setAttribute("disabled", true)
        option.setAttribute("selected", true)
      }
      option.innerText = unidad[1]
      selectTipoProcedimiento.appendChild(option)
    });
    
  } catch (error) {
    console.error("Error al cargar procedimientos:", error);
  }
}

selectDivision.addEventListener("change", function () {
  cargarTipos(selectDivision.value);
});
