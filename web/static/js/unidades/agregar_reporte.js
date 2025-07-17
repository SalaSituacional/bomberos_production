let botones = document.querySelectorAll(".agg-reportes");

botones.forEach((boton) => {
  boton.addEventListener("click", function () {
    let id_unidad = this.getAttribute("data-unidad"); // ID de la unidad
    let unidad = this.getAttribute("data-unidad-nombre"); // Nombre de la unidad

    // Obtener el elemento input original
    let input = document.getElementById("id_id_unidad");
    input.value = unidad; // Asignar el valor correctamente
    input.setAttribute("readonly", true);

    // Crear o actualizar el input hidden para el id de la unidad
    let hiddenInput = document.getElementById("unidad_id_hidden");
    if (!hiddenInput) {
      hiddenInput = document.createElement("input");
      hiddenInput.type = "hidden";
      hiddenInput.id = "unidad_id_hidden";
      hiddenInput.name = "unidad_id";
      input.parentNode.appendChild(hiddenInput);
    }
    hiddenInput.value = id_unidad;
  });
});
