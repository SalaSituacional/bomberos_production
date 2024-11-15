// Obtener elementos
const infoProcedimiento = document.getElementById("infoProcedimiento");
const confirmarEliminar = document.getElementById("confirmarEliminar");

// Función fetch con pantalla de carga
async function fetchWithLoader(url, options = {}) {
  try {
    // Muestra la pantalla de carga
    document.getElementById("loadingScreen").style.display = "block";

    // Realiza la petición fetch
    const response = await fetch(url, options);

    // Verifica si la respuesta es exitosa
    if (!response.ok) {
      throw new Error("Error en la solicitud: " + response.status);
    }

    // Intenta convertir la respuesta a JSON
    return await response.json();
  } catch (error) {
    console.error("Error al consumir la API:", error);
    throw error;
  } finally {
    // Oculta la pantalla de carga, independientemente de si la solicitud fue exitosa o falló
    document.getElementById("loadingScreen").style.display = "none";
  }
}

// Manejo de formularios y navegación
document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", function () {
      document.getElementById("loadingScreen").style.display = "block";
    });
  });

  window.addEventListener("beforeunload", function () {
    document.getElementById("loadingScreen").style.display = "block";
  });
});

// Abrir modal y mostrar información
document.querySelectorAll(".button_delete").forEach((button) => {
  button.onclick = function () {
    const id = this.getAttribute("data-id");
    const id_mostrar = this.getAttribute("data-id_mostrar");
    const solicitante = this.getAttribute("data-solicitante");
    const jefe_comision = this.getAttribute("data-jefeComision");
    const fecha = this.getAttribute("data-fecha");
    const tipo_procedimiento = this.getAttribute("data-tipoProcedimiento");
    infoProcedimiento.innerHTML = `
      <p><b>ID: </b>${id_mostrar} </p>
      <p><b>Solicitante:</b> ${solicitante}</p>
      <p><b>Jefe de Comision:</b> ${jefe_comision}</p>
      <p><b>Fecha:</b> ${fecha}</p>
      <p><b>Tipo De Procedimiento:</b> ${tipo_procedimiento}</p>`;
    confirmarEliminar.setAttribute("data-id", id);
  };
});

// Confirmar eliminación
confirmarEliminar.onclick = function () {
  const id = this.getAttribute("data-id");
  eliminarProcedimiento(id);
};

// Función para eliminar procedimiento
function eliminarProcedimiento(id) {
  fetchWithLoader("/operaciones/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"), // Asegúrate de incluir el token CSRF
    },
    body: JSON.stringify({ id: id }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Eliminar el procedimiento de la vista
        document
          .querySelector(`button[data-id="${id}"]`)
          .parentElement.remove();
        location.reload();
      } else {
        alert("Error al eliminar el procedimiento");
      }
    });
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
