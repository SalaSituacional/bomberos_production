document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("modalCambiarEstado");
    modal.addEventListener("show.bs.modal", function (event) {
      const button = event.relatedTarget;
      const bienId = button.getAttribute("data-bien-id");
      const estadoActual = button.getAttribute("data-estado-actual");
  
      // Asignamos el ID al input hidden
      document.getElementById("inputBienId").value = bienId;
      document.getElementById("id_bien_cambiar_estado").value = bienId;
      document.getElementById("id_bien_cambiar_estado").setAttribute("readonly", true);
      
      document.getElementById("id_estado_actual").value = estadoActual;
      document.getElementById("id_estado_actual").setAttribute("readonly", true);

    });
  });