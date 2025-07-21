document.addEventListener("DOMContentLoaded", function () {
    const inputIdentificador = document.getElementById("id_identificador");
  
    // Crear dinámicamente el div para mostrar el mensaje si no existe
    let mensajeError = document.createElement("div");
    mensajeError.className = "invalid-feedback";
    mensajeError.style.display = "none"
    mensajeError.textContent = "⚠️ Ya existe un bien con este identificador.";
    // inputIdentificador.parentNode.appendChild(mensajeError);
    
    inputIdentificador.parentElement.appendChild(mensajeError)
  
    inputIdentificador.addEventListener("blur", function () {
      const valor = inputIdentificador.value.trim();
  
      if (!valor) {
        inputIdentificador.classList.remove("is-invalid");
        mensajeError.style.display = "none";
        return;
      }
  
      fetchWithLoader(`/bienesMunicipales/api/verificar-identificador/?identificador=${encodeURIComponent(valor)}`)
        .then((response) => response)
        .then((data) => {
          if (data.existe) {
            mensajeError.style.display = "block";
          } else {
            mensajeError.style.display = "none";
          }
        })
        .catch((error) => {
          console.error("Error al verificar identificador:", error);
        });
    });
  });
  