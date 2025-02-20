const selectSolicitante = document.getElementById("id_form2-solicitante");
const selectJefeComision = document.getElementById("id_form2-jefe_comision");

selectSolicitante.innerHTML = `<option value="" selected="">Seleccione Una Opcion</option>`;

// const division = selectOpciones_Unidad.value;
async function cargarSolicitante() {
  const url = `/api/obtener_solicitante/`; // URL con la fecha como parámetro

  try {
    const data = await fetchWithLoader(url, {
      method: "GET",
      headers: {
        "X-Requested-With": "XMLHttpRequest",
        "Content-Type": "application/json",
      },
    });

    selectSolicitante.innerText = "";

    data.forEach((unidad) => {
      const option = document.createElement("option");
      option.value = unidad[0];
      if (!option.value) {
        option.setAttribute("disabled", true);
        option.setAttribute("selected", true);
      }
      option.innerText = unidad[1];
      selectSolicitante.appendChild(option);
    });

    data.forEach((unidad) => {
      const option = document.createElement("option");
      option.value = unidad[0];
      if (!option.value) {
        option.setAttribute("disabled", true);
        option.setAttribute("selected", true);
      }
      option.innerText = unidad[1];
      selectJefeComision.appendChild(option);
    });

    selectJefeComision.options[1].remove();

    if (storedData) {
      window.cargasCompletas.solicitante = true;
      verificarCargaCompleta();
    }

  } catch (error) {
    console.error("Error al cargar procedimientos:", error);
  }
}

document.addEventListener("DOMContentLoaded", function () {
  cargarSolicitante();
});
