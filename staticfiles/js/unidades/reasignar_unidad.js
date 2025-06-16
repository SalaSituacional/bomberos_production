let botonesDivision = document.querySelectorAll(".reasignar-unidad");

botonesDivision.forEach((boton) => {
  boton.addEventListener("click", function () {
    let id_unidad = this.getAttribute("data-unidad"); // ID de la unidad
    let unidad = this.getAttribute("data-unidad-nombre"); // Nombre de la unidad
    let divisionActual = this.getAttribute("data-division-actual"); // Nombre de la unidad

    // Obtener el elemento input original
    let input = document.getElementById("id_id_unidad_division");

    // Crear un nuevo elemento <select>
    let select = document.createElement("select");
    select.setAttribute("name", "id_unidad-division");
    select.id = input.id; // Mantener el mismo ID del input (opcional)
    select.disabled = true; // Deshabilitar para que no se pueda cambiar

    // Crear la opción dentro del select
    select.innerHTML = `<option value="${id_unidad}" selected>${unidad}</option>`;

    // Crear un input oculto para enviar el valor del select
    let hiddenInput = document.createElement("input");
    hiddenInput.type = "hidden";
    hiddenInput.name = "id_unidad-division"; // Mismo nombre para que el valor se envíe
    hiddenInput.value = id_unidad;

    // Reemplazar el input original con el select
    input.parentNode.replaceChild(select, input);

    // Agregar el input oculto después del select para que se envíe el valor
    select.parentNode.appendChild(hiddenInput);

    document.getElementById("id_actual_division").value = divisionActual;
    document.getElementById("id_actual_division").setAttribute("readonly", true);
  });
});
