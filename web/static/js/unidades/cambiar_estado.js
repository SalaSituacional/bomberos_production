let botonesStatus = document.querySelectorAll(".cambiar-estado");

botonesStatus.forEach((boton) => {
    boton.addEventListener("click", function () {
      let id_unidad = this.getAttribute("data-unidad"); // ID de la unidad
      let unidad = this.getAttribute("data-unidad-nombre"); // Nombre de la unidad
      let estadoActual = this.getAttribute("data-estado-actual"); // Nombre de la unidad

  
      // Obtener el elemento input original
      document.getElementById("id_id_unidad_status").value = unidad;
      document.getElementById("id_id_unidad_status").setAttribute("readonly", true);

      document.getElementById("id_actual").value = estadoActual;
      document.getElementById("id_actual").setAttribute("readonly", true);

      // Crear o actualizar el input hidden para el id de la unidad
      let hiddenInput = document.getElementById("unidad_id_hidden");
      if (!hiddenInput) {
        hiddenInput = document.createElement("input");
        hiddenInput.type = "hidden";
        hiddenInput.id = "unidad_id_estatus_hidden";
        hiddenInput.name = "unidad_id_estatus";
        document.getElementById("id_id_unidad_status").parentNode.appendChild(hiddenInput);
      }
      hiddenInput.value = id_unidad;
    });
  });