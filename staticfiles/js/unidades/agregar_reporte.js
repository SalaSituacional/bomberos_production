let botones = document.querySelectorAll(".agg-reportes");

botones.forEach((boton) => {
  boton.addEventListener("click", function () {
    let id_unidad = this.getAttribute("data-unidad"); // ID de la unidad
    let unidad = this.getAttribute("data-unidad-nombre"); // Nombre de la unidad

    console.log(id_unidad, unidad);

    // Obtener el elemento input original
    let input = document.getElementById("id_id_unidad");

    // Crear un nuevo elemento <select>
    let select = document.createElement("select");
    select.setAttribute("name", "id_unidad");
    select.id = input.id; // Mantener el mismo ID del input (opcional)
    select.disabled = true; // Deshabilitar para que no se pueda cambiar

    // Crear la opción dentro del select
    select.innerHTML = `<option value="${id_unidad}" selected>${unidad}</option>`;

    // Crear un input oculto para enviar el valor del select
    let hiddenInput = document.createElement("input");
    hiddenInput.type = "hidden";
    hiddenInput.name = "id_unidad"; // Mismo nombre para que el valor se envíe
    hiddenInput.value = id_unidad;

    // Reemplazar el input original con el select
    input.parentNode.replaceChild(select, input);

    // Agregar el input oculto después del select para que se envíe el valor
    select.parentNode.appendChild(hiddenInput);
  });
});
