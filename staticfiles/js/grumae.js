// Obtener elementos
const infoProcedimiento = document.getElementById("infoProcedimiento");
const confirmarEliminar = document.getElementById("confirmarEliminar");

// Abrir modal y mostrar información
document.querySelector('tbody').addEventListener('click', function(event) {
  // Acción de eliminar
  if (event.target && event.target.matches('.button_delete')) { 
    const id = event.target.getAttribute("data-id");
    const id_mostrar = event.target.getAttribute("data-id_mostrar");
    const solicitante = event.target.getAttribute("data-solicitante");
    const jefe_comision = event.target.getAttribute("data-jefeComision");
    const fecha = event.target.getAttribute("data-fecha");
    const tipo_procedimiento = event.target.getAttribute("data-tipoProcedimiento");

    // Mostrar la información del procedimiento en el modal
    infoProcedimiento.innerHTML = `
      <p><b>ID: </b>${id_mostrar} </p>
      <p><b>Solicitante:</b> ${solicitante}</p>
      <p><b>Jefe de Comision:</b> ${jefe_comision}</p>
      <p><b>Fecha:</b> ${fecha}</p>
      <p><b>Tipo De Procedimiento:</b> ${tipo_procedimiento}</p>`;

    // Establecer el ID en el botón de confirmación
    confirmarEliminar.setAttribute("data-id", id);
  }
});
// Confirmar eliminación
confirmarEliminar.onclick = function () {
  const id = this.getAttribute("data-id");
  eliminarProcedimiento(id);
};

// Función para eliminar procedimiento
async function eliminarProcedimiento(id) {
  try {
    const response = await fetchWithLoader("/operaciones/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"), // Asegúrate de incluir el token CSRF
      },
      body: JSON.stringify({ id: id }),
    });

    if (response.success) {
      // Eliminar el procedimiento de la vista
      document.querySelector(`button[data-id="${id}"]`).parentElement.remove();
      location.reload();
    } else {
      alert("Error al eliminar el procedimiento");
    }
  } catch (error) {
    console.error("Error al intentar eliminar el procedimiento:", error);
    alert("Ocurrió un error al eliminar el procedimiento. Inténtalo nuevamente.");
  }
}

// Función para obtener el token CSRF
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}