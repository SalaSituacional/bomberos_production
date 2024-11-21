let activeRequests = 0; // Contador de peticiones activas
let loadingActive = false;

function showLoader() {
  const loadingScreen = document.getElementById("loadingScreen");
  if (loadingScreen) {
    loadingScreen.style.display = "flex";
    loadingActive = true;
  }
}

function hideLoader() {
  const loadingScreen = document.getElementById("loadingScreen");
  if (loadingScreen && activeRequests === 0) {
    loadingScreen.style.display = "none";
    loadingActive = false;
  }
}

async function fetchWithLoader(url, options = {}) {
  activeRequests++; // Incrementa el contador de peticiones activas
  showLoader();

  try {
    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(
        `Error en la solicitud: ${response.status} ${response.statusText}`
      );
    }
    return await response.json();
  } catch (error) {
    console.error("Error al consumir la API:", error);
    throw error;
  } finally {
    activeRequests--; // Decrementa el contador de peticiones activas
    hideLoader();
  }
}

// Control del loader para la carga completa de la página
window.addEventListener("load", async function () {
  // El evento `load` asegura que todos los recursos están cargados
  showLoader();

  // Si tienes peticiones iniciales, agrégalas aquí
  const initialLoadPromises = [
  ];

  try {
    // Espera tanto las peticiones iniciales como el evento `load`
    await Promise.all(initialLoadPromises);
  } catch (error) {
    console.error("Error durante la carga inicial:", error);
  } finally {
    // Asegurar que el loader no se oculte hasta que todo esté listo
    hideLoader();
  }
});

document.addEventListener("DOMContentLoaded", function () {
  // Mostrar loader al enviar formularios
  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", function () {
      showLoader();
    });
  });

  // Mostrar loader al cambiar de página
  window.addEventListener("beforeunload", function () {
    showLoader();
  });

  // Mostrar loader al hacer clic en enlaces de descarga
  document.querySelectorAll(".download-link").forEach((link) => {
    link.addEventListener("click", function () {
      showLoader();

      // Detectar cierre de la ventana de descarga usando focus y blur
      let windowBlurred = false;

      window.addEventListener("blur", function () {
        windowBlurred = true;
      });

      window.addEventListener("focus", function () {
        if (windowBlurred) {
          hideLoader();
          windowBlurred = false;
        }
      });
    });
  });

  // Manejar visibilidad del documento
  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "visible" && loadingActive) {
      showLoader();
    }
  });
});
