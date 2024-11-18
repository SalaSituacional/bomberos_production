let loadingActive = false;

async function fetchWithLoader(url, options = {}) {
  try {
    const loadingScreen = document.getElementById("loadingScreen");
    if (loadingScreen) {
      loadingScreen.style.display = "flex";
      loadingActive = true;
    }

    const response = await fetch(url, options);
    if (!response.ok) {
      throw new Error(
        `Error en la solicitud: ${response.status} ${response.statusText}`
      );
    }
    return await response.json();
  } catch (error) {
    console.error("Error al consumir la API:", error);

    // Revisa si `response` está definido antes de arrojar el error
    const responseStatus = error.response?.status || "sin definir";
    const responseText = error.response?.statusText || "sin definir";
    throw new Error(`Error en la API: ${responseStatus} ${responseText}`);
  } finally {
    const loadingScreen = document.getElementById("loadingScreen");
    if (loadingScreen && loadingActive) {
      loadingScreen.style.display = "none";
      loadingActive = false;
    }
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const loadingScreen = document.getElementById("loadingScreen");

  // Mostrar loader al enviar formularios
  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", function () {
      if (loadingScreen) {
        loadingScreen.style.display = "flex";
      }
    });
  });

  // Mostrar loader al cambiar de página
  window.addEventListener("beforeunload", function () {
    if (loadingScreen) {
      loadingScreen.style.display = "flex";
    }
  });
});

document.addEventListener("DOMContentLoaded", function () {
  const loadingScreen = document.getElementById("loadingScreen");

  // Mostrar loader al hacer clic en enlaces de descarga
  document.querySelectorAll(".download-link").forEach((link) => {
    link.addEventListener("click", function () {
      if (loadingScreen) {
        loadingScreen.style.display = "flex";
        loadingActive = true;

        // Detectar cierre de la ventana de descarga usando focus y blur
        let windowBlurred = false;

        window.addEventListener("blur", function () {
          windowBlurred = true; // El usuario sale de la ventana
        });

        window.addEventListener("focus", function () {
          if (windowBlurred) {
            // Cuando vuelve el foco, asumimos que la descarga terminó
            if (loadingScreen) {
              loadingScreen.style.display = "none";
              loadingActive = false;
            }
            windowBlurred = false; // Resetear estado
          }
        });
      }
    });
  });
});
