// let loadingActive = false;

// async function fetchWithLoader(url, options = {}) {
//   try {
//     const loadingScreen = document.getElementById("loadingScreen");
//     if (loadingScreen) {
//       loadingScreen.style.display = "block";
//       loadingActive = true;
//     }

//     const response = await fetch(url, options);
//     if (!response.ok) {
//       throw new Error(
//         `Error en la solicitud: ${response.status} ${response.statusText}`
//       );
//     }
//     return await response.json();
//   } catch (error) {
//     console.error("Error al consumir la API:", error);

//     // Revisa si `response` está definido antes de arrojar el error
//     const responseStatus = error.response?.status || "sin definir";
//     const responseText = error.response?.statusText || "sin definir";
//     throw new Error(`Error en la API: ${responseStatus} ${responseText}`);
//   } finally {
//     const loadingScreen = document.getElementById("loadingScreen");
//     if (loadingScreen && loadingActive) {
//       loadingScreen.style.display = "none";
//       loadingActive = false;
//     }
//   }
// }

// document.addEventListener("DOMContentLoaded", function () {
//   document.querySelectorAll("form").forEach((form) => {
//     form.addEventListener("submit", function () {
//       const loadingScreen = document.getElementById("loadingScreen");
//       if (loadingScreen) {
//         loadingScreen.style.display = "block";
//       }
//     });
//   });

//   window.addEventListener("beforeunload", function () {
//     const loadingScreen = document.getElementById("loadingScreen");
//     if (loadingScreen) {
//       loadingScreen.style.display = "block";
//     }
//   });
// });
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
  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", function () {
      const loadingScreen = document.getElementById("loadingScreen");
      if (loadingScreen) {
        loadingScreen.style.display = "flex";
      }
    });
  });

  window.addEventListener("beforeunload", function () {
    const loadingScreen = document.getElementById("loadingScreen");
    if (loadingScreen) {
      loadingScreen.style.display = "flex";
    }
  });
});
