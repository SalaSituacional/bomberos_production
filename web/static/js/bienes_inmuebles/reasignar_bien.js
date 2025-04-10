document.addEventListener("DOMContentLoaded", function () {
  const modal = document.getElementById("modalReasignarBien");
  modal.addEventListener("show.bs.modal", function (event) {
    const button = event.relatedTarget;
    const bienId = button.getAttribute("data-bien-id");

    // Asignamos el ID al input hidden
    document.getElementById("inputBienId").value = bienId;
    document.getElementById("id_bien").value = bienId;
    document.getElementById("id_bien").setAttribute("readonly", true);
  });
});