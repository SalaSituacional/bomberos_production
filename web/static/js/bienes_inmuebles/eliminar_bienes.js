const eliminarModal = document.getElementById('modalEliminarBien');
  eliminarModal.addEventListener('show.bs.modal', function (event) {
    const button = event.relatedTarget;
    const bienId = button.getAttribute('data-id-bien');
    const input = eliminarModal.querySelector('#inputEliminarBienId');
    input.value = bienId;
  });