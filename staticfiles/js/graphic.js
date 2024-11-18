// Variable global para almacenar los datos de procedimientos
let procedimientosMensuales = [];

// Función para obtener procedimientos por mes
async function obtenerProcedimientosPorMes() {
  try {
    const data = await fetchWithLoader("/api/meses/"); // Asegúrate de que esta URL sea correcta

    // Asignar los datos a la variable global
    procedimientosMensuales = [
      data.enero,
      data.febrero,
      data.marzo,
      data.abril,
      data.mayo,
      data.junio,
      data.julio,
      data.agosto,
      data.septiembre,
      data.octubre,
      data.noviembre,
      data.diciembre,
    ];

    // Llamar a la función para actualizar el gráfico
    actualizarGrafico();
  } catch (error) {
    console.error("Error al obtener los datos:", error);
  }
}

// Función para actualizar el gráfico
function actualizarGrafico() {
  const ctx = document.getElementById("myChart").getContext("2d");
  const labels = [
    "Enero",
    "Febrero",
    "Marzo",
    "Abril",
    "Mayo",
    "Junio",
    "Julio",
    "Agosto",
    "Septiembre",
    "Octubre",
    "Noviembre",
    "Diciembre",
  ];

  // Crear el gráfico o actualizarlo
  new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [
        {
          label: "Operaciones Anuales",
          data: procedimientosMensuales, // Usar los datos obtenidos
          fill: false,
          borderColor: "rgb(200, 36, 58)",
          tension: 0.4,
          pointStyle: "circle",
          borderWidth: 2,
          pointRadius: 4,
        },
      ],
    },
    options: {
      maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true },
      },
      plugins: {
        legend: {
          labels: {
            font: { size: 14, lineHeight: 1.5 },
            padding: 18,
          },
        },
      },
    },
  });
}

// Llama a la función para obtener los datos cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", obtenerProcedimientosPorMes);

function updateProgressBar(id, progressValues) {
  const progressBar = document.getElementById(`progress-bar-${id}`);
  const progressText = document.getElementById(`progress-text-${id}`);
  progressBar.style.width = progressValues + "%";
  progressText.textContent = progressValues.toFixed(1) + "%"; // Muestra un decimal
}

// Función para restablecer todas las barras de progreso y textos a 0%
function resetProgressBars(id) {
  document.getElementById(`progress-bar-${id}`).style.width = "0%";
  document.getElementById(`progress-text-${id}`).textContent = "0%";
}

// Función para llamar a la API según el periodo
async function fetchPorcentajes(periodo) {
  try {
    const porcentajes = await fetchWithLoader(`/api/porcentajes/${periodo}/`);

    // Función para animar las barras de progreso
    function animateProgress(id, targetValue) {
      let progress = 0;
      resetProgressBars(id); // Reinicia los valores antes de obtener nuevos datos
      const increment = targetValue / 100; // Aumentar en pasos de 1% de la meta

      const interval = setInterval(() => {
        if (progress >= targetValue) {
          clearInterval(interval);
        } else {
          progress += increment;
          updateProgressBar(id, Math.min(progress, targetValue));
        }
      }, 10);
    }

    if (periodo == "mes") {
      document.getElementById("porcentajes").textContent = " Mensuales";
    } else {
      document.getElementById("porcentajes").textContent = "Totales";
    }

    // Valores fijos para cada barra de progreso
    const progressValues = {
      operaciones: porcentajes.operaciones,
      prehospitalaria: porcentajes.prehospitalaria,
      rescate: porcentajes.rescate,
      grumae: porcentajes.grumae,
      servicios_medicos: porcentajes.servicios_medicos,
      prevencion: porcentajes.prevencion,
    };

    // Inicia la animación para cada barra con los valores actualizados
    for (const id in progressValues) {
      animateProgress(id, progressValues[id]);
    }
  } catch (error) {
    console.error("Error al consumir la API:", error);
  }
}
fetchPorcentajes("mes");

async function fetchProcedimientos(condicion) {
  let usuario = document.getElementById("usuario");
  try {
    const data = await fetchWithLoader("/api/parroquias/", {
      headers: {
        "X-User-Name": usuario.textContent,
      },
    });

    const fields = {
      Total: "total",
      Mes: "del_mes",
      Hoy: "hoy",
    };

    document.getElementById("parroquias").textContent =
      condicion === "Total"
        ? "Totales"
        : condicion === "Mes"
        ? "Mensuales"
        : "Diarios";

    for (const [key, value] of Object.entries(fields)) {
      if (condicion === key) {
        document.getElementById(
          "concordia"
        ).textContent = `${data.concordia[value]}`;
        document.getElementById(
          "otros_municipios"
        ).textContent = `${data.otros_municipios[value]}`;
        document.getElementById(
          "san_sebastian"
        ).textContent = `${data.san_sebastian[value]}`;
        document.getElementById(
          "san_juan"
        ).textContent = `${data.san_juan[value]}`;
        document.getElementById(
          "pedro_m"
        ).textContent = `${data.pedro_m[value]}`;
        document.getElementById(
          "francisco_romero"
        ).textContent = `${data.francisco_romero_lobo[value]}`;
      }
    }
  } catch (error) {
    console.error("Error fetching procedimientos:", error);
  }
}
fetchProcedimientos("Hoy");

//--------------------------- divisiones ------------------

async function fetchDivisiones() {
  try {
    return await fetchWithLoader("/api/divisiones/");
  } catch (error) {
    console.error("Error fetching divisiones:", error);
    return {};
  }
}

function updateCards(data, type) {
  for (const [division, detalles] of Object.entries(data)) {
    const count =
      type === "total"
        ? detalles.total
        : type === "del_mes"
        ? detalles.del_mes
        : detalles.hoy;
    document.getElementById("divisiones").textContent =
      type === "total"
        ? "Totales"
        : type === "del_mes"
        ? "Mensuales"
        : "Diarios";

    const card = document.querySelector(
      `li[data-division="${division}"] .count`
    );
    if (card) {
      card.textContent = count;
    }
  }
}

document.getElementById("btn-today").addEventListener("click", async () => {
  const data = await fetchDivisiones();
  updateCards(data, "hoy");
});

document.getElementById("btn-month").addEventListener("click", async () => {
  const data = await fetchDivisiones();
  updateCards(data, "del_mes");
});

document.getElementById("btn-total").addEventListener("click", async () => {
  const data = await fetchDivisiones();
  updateCards(data, "total");
});

// Llama a fetchDivisiones al cargar la página para mostrar los datos de hoy
window.onload = async () => {
  const data = await fetchDivisiones();
  updateCards(data, "hoy");
};
