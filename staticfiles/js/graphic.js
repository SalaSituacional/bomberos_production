// Variable global para almacenar los datos de procedimientos
let procedimientosMensuales = [];
let chartInstance = null;

// Función para obtener procedimientos por mes
async function obtenerProcedimientosPorMes() {
  try {
    const data = await fetchWithLoader("/api/meses/");
    
    procedimientosMensuales = [
      data.enero, data.febrero, data.marzo, data.abril, 
      data.mayo, data.junio, data.julio, data.agosto,
      data.septiembre, data.octubre, data.noviembre, data.diciembre
    ];

    actualizarGrafico();
  } catch (error) {
    console.error("Error al obtener los datos mensuales:", error);
  }
}

// Función para actualizar el gráfico
function actualizarGrafico() {
  const ctx = document.getElementById("myChart")?.getContext("2d");
  if (!ctx) return;

  const labels = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
  ];

  // Destruir instancia previa si existe
  if (chartInstance) {
    chartInstance.destroy();
  }

  chartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels: labels,
      datasets: [{
        label: "Operaciones Anuales",
        data: procedimientosMensuales,
        fill: false,
        borderColor: "rgb(200, 36, 58)",
        tension: 0.4,
        pointStyle: "circle",
        borderWidth: 2,
        pointRadius: 4,
      }],
    },
    options: {
      maintainAspectRatio: false,
      scales: { y: { beginAtZero: true } },
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

// ======================================= Fetchs Para Actualizar Porcentajes

// Función para actualizar barra de progreso
function updateProgressBar(id, progressValue) {
  const progressBar = document.getElementById(`progress-bar-${id}`);
  const progressText = document.getElementById(`progress-text-${id}`);
  
  if (progressBar && progressText) {
    progressBar.style.width = `${progressValue}%`;
    progressText.textContent = `${progressValue.toFixed(1)}%`;
  }
}

// Función para animar las barras de progreso
function animateProgress(id, targetValue) {
  let progress = 0;
  const increment = targetValue / 100;
  const duration = 10; // ms

  const interval = setInterval(() => {
    if (progress >= targetValue) {
      clearInterval(interval);
    } else {
      progress += increment;
      updateProgressBar(id, Math.min(progress, targetValue));
    }
  }, duration);
}

// Función para obtener porcentajes
async function fetchPorcentajes(periodo) {
  try {
    const porcentajes = await fetchWithLoader(`/api/porcentajes/${periodo}/`);
    
    // Actualizar título
    const titleElement = document.getElementById("porcentajes");
    if (titleElement) {
      titleElement.textContent = periodo === "mes" ? " Mensuales" : "Totales";
    }

    // Lista de todas las posibles barras de progreso
    const allProgressBars = [
      'operaciones',
      'prehospitalaria',
      'rescate',
      'grumae',
      'servicios_medicos',
      'prevencion'
    ];

    // Filtrar solo las barras que existen en el DOM
    const availableBars = allProgressBars.filter(id => 
      document.getElementById(`progress-bar-${id}`)
    );

    // Animar solo las barras disponibles
    availableBars.forEach(id => {
      if (porcentajes[id] !== undefined) {
        updateProgressBar(id, 0); // Resetear a 0 antes de animar
        animateProgress(id, porcentajes[id]);
      }
    });
  } catch (error) {
    console.error("Error al obtener porcentajes:", error);
  }
}

// Inicializar porcentajes al cargar si hay al menos una barra de progreso
document.addEventListener('DOMContentLoaded', () => {
  // Verificar si existe al menos una barra de progreso
  const hasAnyProgressBar = [
    'operaciones',
    'prehospitalaria',
    'rescate',
    'grumae',
    'servicios_medicos',
    'prevencion'
  ].some(id => document.getElementById(`progress-bar-${id}`));

  if (hasAnyProgressBar) {
    fetchPorcentajes("mes");
  }
});

// ============================================== Fetch Procedimientos

// Función para obtener procedimientos por parroquia
async function fetchProcedimientos(condicion) {
  try {
    const usuario = document.getElementById("usuario");
    if (!usuario) return;

    const data = await fetchWithLoader("/api/parroquias/", {
      headers: { "X-User-Name": usuario.textContent }
    });

    // Actualizar título
    const titleElement = document.getElementById("parroquias");
    if (titleElement) {
      titleElement.textContent = 
        condicion === "Total" ? "Totales" :
        condicion === "Mes" ? "Mensuales" : "Diarios";
    }

    // Mapeo de condiciones a campos de datos
    const fieldMap = {
      "Total": "total",
      "Mes": "del_mes",
      "Hoy": "hoy"
    };
    const field = fieldMap[condicion] || "hoy";

    // Actualizar valores
    const updateField = (id, value) => {
      const element = document.getElementById(id);
      if (element) element.textContent = value;
    };

    updateField("concordia", data.concordia[field]);
    updateField("otros_municipios", data.otros_municipios[field]);
    updateField("san_sebastian", data.san_sebastian[field]);
    updateField("san_juan", data.san_juan[field]);
    updateField("pedro_m", data.pedro_m[field]);
    updateField("francisco_romero", data.francisco_romero_lobo[field]);
  } catch (error) {
    console.error("Error al obtener procedimientos:", error);
  }
}

// Inicializar procedimientos al cargar (si el elemento existe)
document.addEventListener('DOMContentLoaded', () => {
  if (document.getElementById('concordia')) {
    fetchProcedimientos("Hoy");
  }
});

//--------------------------- divisiones ------------------

// Función para obtener datos de divisiones
async function fetchDivisiones() {
  try {
    return await fetchWithLoader("/api/divisiones/");
  } catch (error) {
    console.error("Error al obtener divisiones:", error);
    return {};
  }
}

// Función para actualizar tarjetas de divisiones
function updateCards(data, type) {
  const titleElement = document.getElementById("divisiones");
  if (titleElement) {
    titleElement.textContent = 
      type === "total" ? "Totales" :
      type === "del_mes" ? "Mensuales" : "Diarios";
  }

  Object.entries(data).forEach(([division, detalles]) => {
    const count = detalles[type] || 0;
    const card = document.querySelector(`li[data-division="${division}"] .count`);
    if (card) {
      card.textContent = count;
    }
  });
}

// Asignar event listeners cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', async () => {
  const divisionesContainer = document.querySelector('[data-division]');
  if (!divisionesContainer) return;

  const data = await fetchDivisiones();
  updateCards(data, "hoy");

  // Asignar eventos a los botones
  document.getElementById("btn-today")?.addEventListener("click", () => updateCards(data, "hoy"));
  document.getElementById("btn-month")?.addEventListener("click", () => updateCards(data, "del_mes"));
  document.getElementById("btn-total")?.addEventListener("click", () => updateCards(data, "total"));
});
