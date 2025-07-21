let botonesDivision = document.querySelectorAll(".reasignar-unidad");

botonesDivision.forEach((boton) => {
  boton.addEventListener("click", function () {
    let id_unidad = this.getAttribute("data-unidad"); // ID de la unidad
    let unidad = this.getAttribute("data-unidad-nombre"); // Nombre de la unidad
    let divisionActual = this.getAttribute("data-division-actual"); // Nombre de la unidad

    // Obtener el elemento input original
    document.getElementById("id_id_unidad_division").value = unidad
    document.getElementById("id_id_unidad_division").setAttribute("readonly", true)

    document.getElementById("id_actual_division").value = divisionActual;
    document.getElementById("id_actual_division").setAttribute("readonly", true);

    // Crear o actualizar el input hidden para el id de la unidad
      let hiddenInput = document.getElementById("unidad_id_hidden");
      if (!hiddenInput) {
        hiddenInput = document.createElement("input");
        hiddenInput.type = "hidden";
        hiddenInput.id = "unidad_id_division_hidden";
        hiddenInput.name = "unidad_id_division";
        document.getElementById("id_id_unidad_division").parentNode.appendChild(hiddenInput);
      }
      hiddenInput.value = id_unidad;
  });
});
